import hashlib
import json
import asyncio
import websockets
import ssl
from utils.interfaces import Logger
from config.config import Config

class PowService:
    def __init__(self, logger: Logger, config: Config):
        self.logger = logger
        self.config = config

    async def solve_pow(self, session_id: str, ws_ticket: str):
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        uri = f"{self.config.WS_URL}?session_id={session_id}&ticket={ws_ticket}"

        async with websockets.connect(uri, ssl=ssl_ctx) as ws:
            raw = await asyncio.wait_for(ws.recv(), timeout=5)
            challenge = json.loads(raw)
            self.logger.info(f"Challenge: {raw}")

            prefix = challenge["prefix"]
            difficulty = challenge["difficulty"]
            target = "0" * difficulty

            self.logger.info(f"Resolvendo PoW (difficulty={difficulty})...")
            nonce = 0
            while True:
                nonce_str = str(nonce)
                h = hashlib.sha256(f"{prefix}{nonce_str}".encode()).hexdigest()
                if h.startswith(target):
                    self.logger.success(f"Nonce: {nonce_str}  Hash: {h}")
                    break
                nonce += 1
                if nonce % 100000 == 0:
                    self.logger.info(f"... {nonce}")

            await ws.send(json.dumps({"nonce": nonce_str}))
            raw2 = await asyncio.wait_for(ws.recv(), timeout=5)
            result = json.loads(raw2)
            self.logger.info(f"Resultado: {raw2}")

            if not result.get("success"):
                raise Exception("PoW rejeitado!")

            return result["intermediate_token"], result.get("ttl_seconds", 10)