import time
from services.auth_service import AuthService
from services.challenge_service import ChallengeService
from services.cert_service import CertService
from config.config import Config
from utils.interfaces import Logger
from utils.logger import ConsoleLogger

class RefactoredHardBot:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.cert_service = CertService(config)
        self.challenge_service = ChallengeService(config)
        self.auth_service = AuthService(self.cert_service.init_mtls_client(), logger, config)

    def solve(self):
        start = time.time()
        self.logger.info("Gerando challenge...")
        challenge, timestamp, nonce = self.challenge_service.generate_challenge_locally()
        challenge_data = {
            "challenge": challenge,
            "timestamp": timestamp,
            "nonce": nonce
        }
        self.logger.info(f"Challenge gerado: {challenge[:15]}...")

        redirect_url = self.auth_service.login_hard(challenge_data)
        if redirect_url:
            self.logger.info(f"{redirect_url}")
            final_res = self.auth_service.http_client.get(redirect_url)
            elapsed = time.time() - start
            if "Certificado digital validado" in final_res.text or final_res.status_code == 200:
                self.logger.success("O certificado foi aceito com sucesso.")
                self.logger.info(f"Tempo total: {elapsed:.2f}s")
            else:

                self.logger.error(f"Erro na validação final: {final_res.status_code}")
                self.logger.info(f"Tempo total: {elapsed:.2f}s")

if __name__ == "__main__":
    config = Config()
    logger = ConsoleLogger()
    bot = RefactoredHardBot(config, logger)
    bot.solve()