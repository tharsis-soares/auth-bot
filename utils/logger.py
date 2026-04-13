# utils/logger.py
class ConsoleLogger:
    def __init__(self):
        # seu código existente...
        pass

    def debug(self, message: str):
        """Método debug para logs detalhados"""
        # Opção 1: Mostrar sempre
        print(f"[DEBUG] {message}")

        # Opção 2: Mostrar apenas se DEBUG=True (recomendado)
        # import os
        # if os.getenv("DEBUG", "").lower() == "true":
        #     print(f"[DEBUG] {message}")

    def info(self, message: str):
        print(f"[*] {message}")

    def success(self, message: str):
        print(f"[✅] {message}")

    def error(self, message: str):
        print(f"[❌] {message}")

    def warning(self, message: str):
        print(f"[⚠️] {message}")