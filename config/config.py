class Config:
    BASE_URL = "https://localhost:3000"
    CERT_URL = "https://localhost:3001"
    WS_URL = "wss://localhost:3000/ws"

    # Easy mode
    EASY_LOGIN_URL = f"{BASE_URL}/api/easy/login"
    EASY_USERNAME = "admin"
    EASY_PASSWORD = "rpa@2026!"

    # Hard mode
    HARD_LOGIN_URL = f"{BASE_URL}/api/hard/login"
    HARD_USERNAME = "operator"
    HARD_PASSWORD = "cert#Secure2026"
    HARD_CHALLENGE_SECRET = 'rpa_hard_challenge_2026'
    PFX_PATH = "client.pfx"
    PFX_PASSWORD = "test123"

    # Extreme mode
    EXTREME_BASE = f"{BASE_URL}/api/extreme"
    EXTREME_INIT_URL = f"{EXTREME_BASE}/init"
    EXTREME_VERIFY_URL = f"{EXTREME_BASE}/verify-token"
    EXTREME_USERNAME = "root"