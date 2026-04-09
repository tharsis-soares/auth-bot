import httpx
import time
import urllib3
from datetime import datetime

# Silenciar avisos de certificado autoassinado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RPAClient:
    def __init__(self):
        self.base_url = "https://localhost:3000"
        self.login_url = f"{self.base_url}/api/easy/login"
        # O Client mantém os cookies e a conexão aberta (HTTP Keep-Alive)
        self.session = httpx.Client(verify=False, timeout=10.0)
        self.token = None
        self.start_time = None

    def login(self, username="admin", password="rpa@2026!"):
        payload = {"username": username, "password": password}

        try:
            print(f"[*] [{self._now()}] Tentando autenticação...")
            response = self.session.post(self.login_url, json=payload)
            response.raise_for_status()

            data = response.json()
            if data.get("success"):
                self.token = data.get("token")
                self.start_time = time.time() # Inicia o cronômetro do bot
                print(f"[✅] Login realizado com sucesso!")
                print(f"[!] Token: {self.token[:15]}...")
                return True

            print(f"[❌] Falha: {data.get('message')}")
            return False

        except Exception as e:
            print(f"[❗] Erro na conexão: {e}")
            return False

    def get_session_duration(self):
        """Retorna o tempo decorrido desde o login em segundos."""
        if self.start_time:
            return round(time.time() - self.start_time, 2)
        return 0

    def _now(self):
        return datetime.now().strftime("%H:%M:%S")

    def status(self):
        """Imprime o status atual do bot."""
        if self.token:
            print(f"[*] [{self._now()}] Bot Online | Tempo de Sessão: {self.get_session_duration()}s")
        else:
            print(f"[*] [{self._now()}] Bot Offline")

    def close(self):
        self.session.close()

# Bloco de teste
if __name__ == "__main__":
    bot = RPAClient()

    if bot.login():
        # Loop simples para demonstrar que ele mantém a conexão e conta o tempo
        try:
            for _ in range(3):
                bot.status()
                time.sleep(2) # Simula o bot esperando ou processando algo

            print(f"\n[🏁] Desafio concluído em {bot.get_session_duration()} segundos.")
        except KeyboardInterrupt:
            print("\n[!] Bot interrompido pelo usuário.")
        finally:
            bot.close()