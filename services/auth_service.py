from utils.interfaces import HttpClient, Logger
from config.config import Config

class AuthService:
    def __init__(self, http_client: HttpClient, logger: Logger, config: Config):
        self.http_client = http_client
        self.logger = logger
        self.config = config

    def login_easy(self):
        payload = {
            "username": self.config.EASY_USERNAME,
            "password": self.config.EASY_PASSWORD
        }

        try:
            response = self.http_client.post(self.config.EASY_LOGIN_URL, json=payload)
            data = response.json()
            if data.get("success"):
                token = data.get("token")
                self.logger.success(f"Token: {token}")
                self.logger.info(f"Tempo: {data.get('elapsed_ms')}ms")
                return self.http_client, token
            else:
                self.logger.error(f"Falha: {data.get('message')}")
        except Exception as e:
            self.logger.error(f"Erro na requisição: {e}")
        return None, None

    def login_hard(self, challenge_data):
        payload = {
            "username": self.config.HARD_USERNAME,
            "password": self.config.HARD_PASSWORD,
            **challenge_data
        }
        self.logger.info("Enviando credenciais para a Porta 3000...")
        try:
            response = self.http_client.post(self.config.HARD_LOGIN_URL, json=payload)
            data = response.json()
            if data.get('redirect'):
                self.logger.success("Redirecionando para validação de certificado...")
                return data.get('redirect')
            else:
                self.logger.error(f"Falha no Login: {data}")
        except Exception as e:
            self.logger.error(f"Erro na requisição: {e}")
        return None