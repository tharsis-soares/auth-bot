# services/cert_service.py - Versão corrigida para cryptography >= 42.0.0
import ssl
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import httpx
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, NoEncryption
from utils.interfaces import Logger
from config.config import Config


class CertService:
    def __init__(self, logger: Logger, config: Config):
        self.logger = logger
        self.config = config
        self._cert_path: Optional[Path] = None
        self._key_path: Optional[Path] = None

    def init_mtls_client(self) -> httpx.Client:
        """Inicializa cliente HTTP com mTLS"""
        cert_path, key_path = self._ensure_certificate()
        ssl_context = self._create_mtls_context(cert_path, key_path)

        self.logger.success("Cliente mTLS inicializado")
        return httpx.Client(verify=ssl_context, timeout=30.0, http2=False)

    def _ensure_certificate(self) -> Tuple[Path, Path]:
        """Garante que temos certificado e chave em formato PEM"""
        if self._cert_path and self._key_path:
            return self._cert_path, self._key_path

        # Tenta PEM local primeiro
        pem_cert = Path("client.crt")
        pem_key = Path("client.key")
        if pem_cert.exists() and pem_key.exists():
            self.logger.info("Usando certificado PEM local")
            return pem_cert, pem_key

        # Tenta PFX local
        pfx_path = Path(self.config.PFX_PATH)
        if pfx_path.exists():
            self.logger.info("Convertendo PFX para PEM...")
            return self._convert_pfx_to_pem(pfx_path)

        raise FileNotFoundError(f"Nenhum certificado encontrado em {pfx_path}")

    def _convert_pfx_to_pem(self, pfx_path: Path) -> Tuple[Path, Path]:
        """Converte PFX para PEM usando a senha correta"""
        cert_path = pfx_path.with_suffix(".crt")
        key_path = pfx_path.with_suffix(".key")

        # Se já existe, reutiliza
        if cert_path.exists() and key_path.exists():
            self.logger.info("Reutilizando PEM existente")
            return cert_path, key_path

        # Lê o arquivo PFX
        with open(pfx_path, "rb") as f:
            pfx_data = f.read()

        # Tenta as senhas possíveis
        passwords_to_try = [
            self.config.PFX_PASSWORD,  # test123
            "test123",
            "",
            "password",
            "changeit",
        ]

        for password in passwords_to_try:
            try:
                pwd_bytes = password.encode() if password else None
                pwd_display = password if password else "(vazio)"

                self.logger.debug(f"Tentando senha: {pwd_display}")

                # CORREÇÃO: load_pkcs12 retorna um objeto, não uma tupla
                p12 = pkcs12.load_pkcs12(pfx_data, password=pwd_bytes)

                # Acessa os atributos do objeto
                private_key = p12.key
                certificate = p12.cert

                self.logger.success(f"PFX decriptado com sucesso! (senha: {pwd_display})")

                # Salva certificado
                with open(cert_path, "wb") as f:
                    f.write(certificate.public_bytes(Encoding.PEM))

                # Salva chave privada
                with open(key_path, "wb") as f:
                    f.write(private_key.private_bytes(
                        Encoding.PEM,
                        PrivateFormat.PKCS8,
                        NoEncryption()
                    ))

                return cert_path, key_path

            except Exception as e:
                self.logger.debug(f"Falhou com senha '{pwd_display}': {type(e).__name__}")
                continue

        raise ValueError(
            f"Não foi possível decriptar {pfx_path} com nenhuma senha testada.\n"
            f"Senhas testadas: {passwords_to_try}\n"
            f"Tente extrair manualmente: openssl pkcs12 -in client.pfx -out client.crt -nodes -passin pass:test123"
        )

    def _create_mtls_context(self, cert_path: Path, key_path: Path) -> ssl.SSLContext:
        """Cria SSLContext para mTLS"""
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.load_cert_chain(str(cert_path), str(key_path))
        return ssl_context