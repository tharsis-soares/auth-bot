"""
Serviço para operações do modo extreme.
"""
import asyncio
import json
from utils.interfaces import HttpClient, Logger
from config.config import Config
from services.pow_service import PowService

class ExtremeService:
    def __init__(self, http_client: HttpClient, logger: Logger, config: Config):
        self.http_client = http_client
        self.logger = logger
        self.config = config
        self.pow_service = PowService(logger, config)

    async def init_session(self):
        self.logger.info("Inicializando...")
        payload = {"username": self.config.EXTREME_USERNAME}
        response = self.http_client.post(self.config.EXTREME_INIT_URL, json=payload)
        data = response.json()
        session_id = data["session_id"]
        ws_ticket = data["ws_ticket"]
        self.logger.info(f"Session ID: {session_id}")
        self.logger.info(f"WS Ticket: {ws_ticket}")
        return session_id, ws_ticket

    async def solve_and_verify(self, session_id: str, ws_ticket: str):
        intermediate_token, ttl = await self.pow_service.solve_pow(session_id, ws_ticket)
        self.logger.info(f"Token: {intermediate_token} (TTL: {ttl}s)")

        self.logger.info("POST /verify-token...")
        payload = {
            "session_id": session_id,
            "intermediate_token": intermediate_token,
        }
        response = self.http_client.post(self.config.EXTREME_VERIFY_URL, json=payload)
        self.logger.info(f"Status: {response.status_code}")
        self.logger.info(f"Response: {response.text}")

        final = response.json()
        if "encrypted_payload" in final:
            self.logger.success(f"PAYLOAD:\n{final['encrypted_payload']}")
        elif final.get("success"):
            self.logger.success(f"SUCESSO: {final}")
        else:
            self.logger.error(f"Falhou: {final}")
        return final