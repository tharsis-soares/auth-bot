# services/auth_service.py
import hashlib
import time
import secrets
from utils.interfaces import Logger
from config.config import Config


class AuthService:
    def __init__(self, http_client, logger: Logger, config: Config):
        self.http_client = http_client
        self.logger = logger
        self.config = config

    def login_easy(self):
        """Login no Easy Mode"""
        payload = {
            "username": self.config.EASY_USERNAME,
            "password": self.config.EASY_PASSWORD
        }

        self.logger.info("POST /api/easy/login...")
        response = self.http_client.post(self.config.EASY_LOGIN_URL, json=payload)

        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            self.logger.success(f"Easy Mode concluído! Token: {token}")
            return self.http_client, token
        else:
            raise Exception(f"Easy login failed: {response.status_code} - {response.text}")

    async def login_hard(self) -> str:
        """Executa o fluxo completo do Hard Mode (mTLS)"""
        # Gera o challenge
        timestamp = str(int(time.time() * 1000))
        nonce = secrets.token_hex(16)
        secret = self.config.HARD_CHALLENGE_SECRET

        challenge_input = f"{timestamp}{nonce}{secret}"
        challenge = hashlib.sha256(challenge_input.encode()).hexdigest()

        self.logger.info(f"Challenge gerado: {challenge[:16]}...")

        # Faz o POST /api/hard/login
        payload = {
            "username": self.config.HARD_USERNAME,
            "password": self.config.HARD_PASSWORD,
            "challenge": challenge,
            "timestamp": timestamp,
            "nonce": nonce
        }

        self.logger.info("POST /api/hard/login...")
        response = self.http_client.post(self.config.HARD_LOGIN_URL, json=payload)
        self.logger.info(f"Status: {response.status_code}")

        if response.status_code != 200:
            raise Exception(f"Login failed: {response.text}")

        data = response.json()
        redirect_url = data.get("redirect")

        if not redirect_url:
            raise Exception(f"No redirect URL in response: {data}")

        self.logger.info(f"Redirect: {redirect_url}")

        # Valida o certificado via mTLS
        self.logger.info("Validando certificado via mTLS...")
        validate_response = self.http_client.get(redirect_url)

        if validate_response.status_code == 200:
            result = validate_response.text
            self.logger.success(f"Hard Mode concluído!")

            # Extrai o token do HTML
            import re
            token_match = re.search(r'Token:</strong> <code>([a-f0-9]+)\.\.\.</code>', result)
            if token_match:
                token = token_match.group(1)
                self.logger.success(f"Token extraído: {token}")
                return token
            return result
        else:
            raise Exception(f"mTLS validation failed: {validate_response.status_code}")