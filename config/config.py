# config/config.py
import os
from pathlib import Path

BASE_URL = os.getenv("API_BASE_URL", "https://localhost:3000")
BASE_URL_MTLS = os.getenv("API_BASE_URL_MTLS", "https://localhost:3001")

class Config:
    # Easy Mode
    EASY_LOGIN_URL = f"{BASE_URL}/api/easy/login"
    EASY_USERNAME = "admin"
    EASY_PASSWORD = "rpa@2026!"

    # Hard Mode (mTLS)
    HARD_LOGIN_URL = f"{BASE_URL}/api/hard/login"
    HARD_USERNAME = "operator"
    HARD_PASSWORD = "cert#Secure2026"
    HARD_CHALLENGE_SECRET = 'rpa_hard_challenge_2026'

    # Extreme Mode
    EXTREME_INIT_URL = f"{BASE_URL}/api/extreme/init"
    EXTREME_VERIFY_URL = f"{BASE_URL}/api/extreme/verify-token"
    EXTREME_USERNAME = "root"
    EXTREME_SECRET_KEY = "extreme_secret_key"
    WS_URL = f"{BASE_URL.replace('https', 'wss')}/ws"

    # Certificates
    PFX_PATH = os.getenv("PFX_PATH", "client.pfx")
    PFX_PASSWORD = os.getenv("PFX_PASSWORD", "test123")
    CA_CERT_PATH = os.getenv("CA_CERT_PATH", "ca.crt")