# services/pow_service.py - VERSÃO CORRIGIDA (sem debug)
import hashlib
import json
import asyncio
import websockets
import ssl
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from typing import Tuple
from utils.interfaces import Logger
from config.config import Config

class PowService:
    def __init__(self, logger: Logger, config: Config):
        self.logger = logger
        self.config = config

    async def _solve_pow_parallel(self, prefix: str, difficulty: int, timeout: float = 30.0) -> str:
        """
        Resolve PoW usando múltiplas threads em paralelo.
        Retorna o nonce como string.
        """
        target = "0" * difficulty
        stop_event = Event()
        result_nonce = None
        max_attempts = 10_000_000

        def search(start_nonce: int, step: int, thread_id: int):
            nonlocal result_nonce
            nonce = start_nonce
            attempts = 0

            while not stop_event.is_set() and nonce < max_attempts:
                h = hashlib.sha256(f"{prefix}{nonce}".encode()).hexdigest()
                attempts += 1

                if h.startswith(target):
                    result_nonce = nonce
                    stop_event.set()
                    return nonce

                nonce += step
            return None

        loop = asyncio.get_running_loop()

        # Usa número de threads = número de CPUs (mínimo 4, máximo 16)
        import os
        num_threads = min(max(4, os.cpu_count() or 8), 16)
        self.logger.info(f"Iniciando PoW paralelo com {num_threads} threads (difficulty={difficulty})")

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for i in range(num_threads):
                future = loop.run_in_executor(executor, search, i, num_threads, i)
                futures.append(future)

            # Aguarda o primeiro resultado ou timeout
            done, pending = await asyncio.wait(futures, timeout=timeout, return_when=asyncio.FIRST_COMPLETED)

            # Cancela threads ainda rodando
            for future in pending:
                future.cancel()

            # Verifica resultados
            for future in done:
                try:
                    result = future.result()
                    if result is not None:
                        return str(result)
                except Exception as e:
                    self.logger.error(f"Erro na thread: {e}")

        raise TimeoutError(f"PoW não resolvido após {timeout}s")

    async def solve_pow(self, session_id: str, ws_ticket: str) -> Tuple[str, int]:
        """
        Resolve o desafio PoW via WebSocket.
        Retorna (intermediate_token, ttl_seconds).
        """
        # Configuração SSL para certificado auto-assinado
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        uri = f"{self.config.WS_URL}?session_id={session_id}&ticket={ws_ticket}"

        async with websockets.connect(uri, ssl=ssl_ctx) as ws:
            # Recebe o desafio
            raw = await asyncio.wait_for(ws.recv(), timeout=10)
            challenge = json.loads(raw)
            self.logger.info(f"Desafio PoW: difficulty={challenge['difficulty']}")

            prefix = challenge["prefix"]
            difficulty = challenge["difficulty"]

            # Resolve PoW usando versão paralela OTIMIZADA
            nonce = await self._solve_pow_parallel(prefix, difficulty)
            self.logger.success(f"PoW resolvido! Nonce={nonce}")

            # Envia solução
            await ws.send(json.dumps({"nonce": nonce}))

            # Recebe resultado
            raw2 = await asyncio.wait_for(ws.recv(), timeout=10)
            result = json.loads(raw2)

            if not result.get("success"):
                raise Exception(f"PoW rejeitado pelo servidor: {result}")

            intermediate_token = result["intermediate_token"]
            ttl = result.get("ttl_seconds", 10)

            self.logger.info(f"Token recebido (TTL: {ttl}s)")

            return intermediate_token, ttl