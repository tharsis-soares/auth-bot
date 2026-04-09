"""
Serviço para manipulação de certificados digitais (mTLS).
"""
from utils.http_client import HttpxClient
from config.config import Config
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

class CertService:
    def __init__(self, config: Config):
        self.config = config

    def init_mtls_client(self) -> HttpxClient:
        with open(self.config.PFX_PATH, "rb") as f:
            pfx_data = f.read()
        pk, cert, _ = pkcs12.load_key_and_certificates(pfx_data, self.config.PFX_PASSWORD.encode())

        cert_pem = cert.public_bytes(serialization.Encoding.PEM)
        key_pem = pk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        with open("client.crt", "wb") as f:
            f.write(cert_pem)
        with open("client.key", "wb") as f:
            f.write(key_pem)

        return HttpxClient(verify_ssl=False, cert=("client.crt", "client.key"), follow_redirects=True)