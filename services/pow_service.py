# services/pow_service.py - Versão com stop_event funcionando
import hashlib
import json
import asyncio
import websockets
import ssl
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event
from typing import Tuple, Optional
from utils.interfaces import Logger
from config.config import Config


class PowService:
    def __init__(self, logger: Logger, config: Config):
        self.logger = logger
        self.config = config

    async def _solve_pow_parallel(self, prefix: str, difficulty: int, timeout: float = 30.0) -> str:
        """
        Resolve PoW usando múltiplas threads em paralelo.
        Quando uma thread encontra, todas as outras são IMEDIATAMENTE interrompidas.
        """
        target = "0" * difficulty
        stop_event = Event()
        result_nonce = None

        def search(start_nonce: int, step: int, thread_id: int) -> Optional[str]:
            nonlocal result_nonce
            nonce = start_nonce
            attempts = 0
            max_attempts = 10_000_000

            while not stop_event.is_set() and nonce < max_attempts:
                # Calcula hash
                h = hashlib.sha256(f"{prefix}{nonce}".encode()).hexdigest()
                attempts += 1

                # Verifica se encontrou
                if h.startswith(target):
                    result_nonce = nonce
                    stop_event.set()  # SINALIZA PARA TODAS AS THREADS PARAREM
                    self.logger.debug(f"[Thread {thread_id}] ✓ Encontrou nonce={nonce} após {attempts} tentativas")
                    return str(nonce)

                nonce += step

            return None

        loop = asyncio.get_running_loop()

        # Número de threads = número de CPUs
        num_threads = min(max(4, os.cpu_count() or 8), 16)
        self.logger.info(f"Iniciando PoW paralelo com {num_threads} threads (difficulty={difficulty})")

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submete todas as tarefas
            futures = []
            for i in range(num_threads):
                future = loop.run_in_executor(executor, search, i, num_threads, i)
                futures.append(future)

            # Aguarda a primeira completar
            start_time = asyncio.get_event_loop().time()

            while True:
                # Verifica timeout
                if asyncio.get_event_loop().time() - start_time > timeout:
                    # Cancela todas as futures
                    for future in futures:
                        future.cancel()
                    raise TimeoutError(f"PoW não resolvido após {timeout}s")

                # Verifica se alguma future já completou
                for future in futures:
                    if future.done():
                        try:
                            result = future.result()
                            if result is not None:
                                # Cancela as outras futures
                                for f in futures:
                                    if f != future:
                                        f.cancel()
                                return result
                        except Exception as e:
                            self.logger.error(f"Erro na thread: {e}")

                await asyncio.sleep(0.01)  # Pequeno delay para não sobrecarregar

    async def solve_pow(self, session_id: str, ws_ticket: str) -> Tuple[str, int]:
        """
        Resolve o desafio PoW via WebSocket.
        Retorna (intermediate_token, ttl_seconds).
        """
        # Configuração SSL
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        uri = f"{self.config.WS_URL}?session_id={session_id}&ticket={ws_ticket}"

        try:
            async with websockets.connect(uri, ssl=ssl_ctx, close_timeout=5) as ws:
                # Recebe o desafio
                raw = await asyncio.wait_for(ws.recv(), timeout=10)
                challenge = json.loads(raw)

                if challenge.get("type") != "pow_challenge":
                    raise ValueError(f"Esperava 'pow_challenge', recebeu '{challenge.get('type')}'")

                prefix = challenge["prefix"]
                difficulty = challenge["difficulty"]

                self.logger.info(f"Desafio PoW: difficulty={difficulty}")

                # Resolve PoW
                nonce = await self._solve_pow_parallel(prefix, difficulty)
                self.logger.success(f"PoW resolvido! Nonce={nonce}")

                # Envia solução
                await ws.send(json.dumps({"nonce": nonce}))

                # Recebe resultado (aumentado timeout para 30s)
                raw2 = await asyncio.wait_for(ws.recv(), timeout=30)
                result = json.loads(raw2)

                if not result.get("success"):
                    raise RuntimeError(f"PoW rejeitado: {result}")

                intermediate_token = result["intermediate_token"]
                ttl = result.get("ttl_seconds", 10)

                self.logger.info(f"Token recebido (TTL: {ttl}s)")

                return intermediate_token, ttl

        except websockets.exceptions.ConnectionClosed as e:
            self.logger.error(f"WebSocket fechou: code={e.code}")
            raise ConnectionError(f"WebSocket closed: {e}")
        except asyncio.TimeoutError as e:
            self.logger.error(f"Timeout: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erro: {e}")
            raise