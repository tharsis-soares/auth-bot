from utils.interfaces import Logger

class ConsoleLogger(Logger):
    def info(self, message: str):
        print(f"[*] {message}")

    def error(self, message: str):
        print(f"[❌] {message}")

    def success(self, message: str):
        print(f"[✅] {message}")