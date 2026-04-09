"""
Versão refatorada do easy_mode.py usando abstrações SOLID.
"""
from services.auth_service import AuthService
from utils.http_client import HttpxClient
from config.config import Config
from utils.logger import ConsoleLogger

if __name__ == "__main__":
    config = Config()
    http_client = HttpxClient()
    logger = ConsoleLogger()
    auth_service = AuthService(http_client, logger, config)
    bot_client, auth_token = auth_service.login_easy()