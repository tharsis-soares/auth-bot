# Auth Bot

Automação de três níveis de autenticação com complexidade progressiva, desenvolvida como solução para processo seletivo.

---

## Níveis

| Nível | Mecanismo | Tempo médio |
|-------|-----------|-------------|
| Easy | HTTP básico com credenciais | < 1s |
| Hard | mTLS + challenge JavaScript emulado | < 2s |
| Extreme | WebSocket + Proof of Work + AES-256-CBC | 5–30s |

---

## Requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)
- Arquivo `client.pfx` (fornecido para o Hard Mode)

---

## Instalação

```bash
git clone https://github.com/tharsis-soares/auth-bot
cd auth-bot
poetry install
```

---

## Execução

```bash
# Easy Mode
poetry run python easy.py

# Hard Mode
poetry run python hard.py

# Extreme Mode
poetry run python extreme.py
```

O tempo de execução de cada desafio é impresso automaticamente ao final da saída.

---

## Configuração

Edite `config/config.py` ou exporte variáveis de ambiente antes de executar:

```bash
export API_BASE_URL="https://localhost:3000"
export EXTREME_USERNAME="root"
export EXTREME_SECRET_SALT="extreme_secret_key"
```

### Certificado para Hard Mode

O Hard Mode requer um certificado client-side em formato PFX. Caso precise converter de `.p12`:

```bash
openssl pkcs12 -in certificate.p12 -out client.pfx -nodes
```

Coloque o arquivo gerado na raiz do projeto como `client.pfx`. A senha padrão está em `config/config.py` (`PFX_PASSWORD`).

---

## Estrutura do Projeto

```
doc9/
├── easy_mode.py
├── hard_mode.py
├── extreme_mode.py
├── client.pfx
├── config/
│   └── config.py           # URLs, credenciais e secrets
├── services/
│   ├── auth_service.py     # Login easy e hard
│   ├── challenge_service.py# Emulação do generateChallenge() JS
│   ├── cert_service.py     # Parsing PFX → mTLS client
│   ├── extreme_service.py  # Fluxo WebSocket + token
│   └── pow_service.py      # Resolução do Proof of Work
└── utils/
    ├── http_client.py      # Wrapper httpx
    ├── interfaces.py       # ABCs (HttpClient, Logger)
    └── logger.py           # ConsoleLogger
```

---

## Fluxos de Autenticação

### Easy

```
POST /api/easy/login  { username, password }
  └─ ← { token }
```

### Hard

```
gera challenge = SHA256(timestamp + nonce + secret)

POST /api/hard/login  { username, password, challenge, timestamp, nonce }
  └─ ← { redirect: "https://localhost:3001/api/hard/validate-cert" }

GET  https://localhost:3001/api/hard/validate-cert  (mTLS: client.crt + client.key)
  └─ ← "Certificado digital validado"
```

### Extreme

```
POST /api/extreme/init
  └─ ← { session_id, ws_ticket }

WSS  wss://localhost:3000/ws?session_id=...&ticket=...
  ├─ ← { type: "pow_challenge", prefix, difficulty }
  ├─ resolve SHA256(prefix + nonce) com N zeros
  ├─ → { nonce: "string" }
  └─ ← { intermediate_token, ttl_seconds: 10 }

POST /api/extreme/verify-token  { session_id, intermediate_token }
  └─ ← { encrypted_payload: "IV:ciphertext" }

decrypt AES-256-CBC
  key = SHA256(session_id + "extreme_secret_key")
  └─ → { otp }
```

---

## Tecnologias

- [`httpx`](https://www.python-httpx.org/) — cliente HTTP com suporte a mTLS
- [`websockets`](https://websockets.readthedocs.io/) — cliente WebSocket assíncrono
- [`pycryptodome`](https://pycryptodome.readthedocs.io/) — decriptação AES-256-CBC
- [`cryptography`](https://cryptography.io/) — parsing de certificados PKCS#12

---

## Solução de Problemas

| Erro | Causa | Solução |
|------|-------|---------|
| `CERTIFICATE_VERIFY_FAILED` | Cert self-signed do servidor | `verify=False` já configurado no `httpx` |
| `SSL: CERTIFICATE_REQUIRED` | mTLS sem cert client-side | Verificar `client.pfx` na raiz e senha em `config.py` |
| `did not receive a valid HTTP response` | WebSocket em `ws://` em vez de `wss://` | Usar `wss://` com `SSLContext` — já tratado |
| `ConnectionClosedOK` após PoW | Comportamento normal — servidor fecha WS após enviar token | Fazer POST `/verify-token` imediatamente após |
| OTP expirado | TTL de 10s do `intermediate_token` | Não interromper o fluxo entre o WS e o POST |

---

## Licença

Desenvolvido para desafio de engenharia reversa e automação de autenticação.