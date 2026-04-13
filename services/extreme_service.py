# services/extreme_service.py
import asyncio
import time
from utils.interfaces import HttpClient, Logger
from config.config import Config
from services.pow_service import PowService

class ExtremeService:
    def __init__(self, http_client: HttpClient, logger: Logger, config: Config, pow_service: PowService = None):
        self.http_client = http_client
        self.logger = logger
        self.config = config
        self.pow_service = pow_service or PowService(logger, config)

    async def init_session(self):
        """Inicializa sessão HTTP sem bloquear o event loop"""
        self.logger.info("Inicializando...")
        payload = {"username": self.config.EXTREME_USERNAME}

        try:
            # Torna o POST não-bloqueante
            response = await asyncio.to_thread(
                self.http_client.post,
                self.config.EXTREME_INIT_URL,
                json=payload
            )

            data = response.json()
            session_id = data.get("session_id")
            ws_ticket = data.get("ws_ticket")

            # Validação robusta
            if not session_id or not ws_ticket:
                raise KeyError(f"Resposta incompleta: {data}")

            self.logger.info(f"Session ID: {session_id}")
            self.logger.info(f"WS Ticket: {ws_ticket[:20]}...")
            return session_id, ws_ticket

        except Exception as e:
            self.logger.error(f"Falha na inicialização: {e}")
            raise

    async def solve_and_verify(self, session_id: str, ws_ticket: str):
        """Resolve PoW e verifica token com TTL management"""
        start_time = time.perf_counter()

        # Resolve PoW
        intermediate_token, ttl = await self.pow_service.solve_pow(session_id, ws_ticket)

        # Calcula tempo gasto no PoW
        elapsed = time.perf_counter() - start_time
        remaining_ttl = ttl - elapsed

        # TTL Management
        if remaining_ttl <= 0:
            raise TimeoutError(f"Token expirou antes do POST! TTL={ttl}s, gastou={elapsed:.2f}s")
        elif remaining_ttl < 2:
            self.logger.warning(f"⚠️ Token expira em {remaining_ttl:.1f}s! Correndo risco...")
        else:
            self.logger.info(f"Token válido por mais {remaining_ttl:.1f}s (TTL={ttl}s, gastou={elapsed:.2f}s)")

        self.logger.info(f"Token: {intermediate_token[:32]}... (TTL: {ttl}s)")

        # POST de verificação (também não-bloqueante)
        self.logger.info("POST /verify-token...")
        payload = {
            "session_id": session_id,
            "intermediate_token": intermediate_token,
        }

        try:
            response = await asyncio.to_thread(
                self.http_client.post,
                self.config.EXTREME_VERIFY_URL,
                json=payload
            )

            self.logger.info(f"Status: {response.status_code}")

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

            final = response.json()

            if "encrypted_payload" in final:
                self.logger.success(f"PAYLOAD:\n{final['encrypted_payload'][:80]}...")
            elif final.get("success"):
                self.logger.success(f"SUCESSO: {final}")
            else:
                self.logger.error(f"Falhou: {final}")

            return final

        except Exception as e:
            self.logger.error(f"Erro no verify-token: {e}")
            raise