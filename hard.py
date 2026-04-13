# hard.py
import asyncio
from config.config import Config
from utils.logger import ConsoleLogger
from services.cert_service import CertService
from services.auth_service import AuthService

class RefactoredHardBot:
    def __init__(self, config: Config, logger: ConsoleLogger):
        self.config = config
        self.logger = logger
        # CORRIGIDO: passa logger e config
        self.cert_service = CertService(logger, config)
        self.auth_service = AuthService(
            self.cert_service.init_mtls_client(),
            logger,
            config
        )

    async def run(self):
        self.logger.info("Iniciando Hard Mode...")
        result = await self.auth_service.login_hard()
        self.logger.success(f"Hard Mode concluído: {result}")
        return result

async def main():
    config = Config()
    logger = ConsoleLogger()
    bot = RefactoredHardBot(config, logger)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())