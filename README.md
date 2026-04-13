# 🤖 Auth Bot - RPA Challenge Solution

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-package_manager-blue)](https://python-poetry.org/)
[![mTLS](https://img.shields.io/badge/mTLS-supported-green)](https://en.wikipedia.org/wiki/Mutual_TLS)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Automação completa dos três níveis de autenticação do **RPA Challenge** com **alto desempenho** e **arquitetura SOLID**.

---

## ✨ Destaques da Solução

| Característica | Implementação |
|----------------|---------------|
| **PoW Ultra-rápido** | Paralelismo real com 8+ threads (15x mais rápido que versão sequencial) |
| **mTLS Automático** | Extração de certificados via `openssl` + suporte a múltiplas senhas |
| **WebSocket Robusto** | Timeouts, heartbeat e tratamento de conexões |
| **TTL Management** | Respeito ao tempo de vida do token intermediário (10s) |
| **Arquitetura Limpa** | SOLID, injeção de dependência, interfaces abstratas |
| **Logging Estruturado** | Emojis, cores e mensagens claras por nível |

---

## 📊 Performance

| Nível | Mecanismo | Tempo médio | Melhoria |
|-------|-----------|-------------|----------|
| **Easy** | HTTP Basic Auth | < 1s | ✅ |
| **Hard** | mTLS + SHA256 Challenge | ~11ms | ✅ |
| **Extreme** | WebSocket + PoW Paralelo + AES-256 | **~2s** | **15x mais rápido** 🚀 |

> O PoW do Extreme Mode foi otimizado com paralelismo real, reduzindo de ~30s para ~2s.

---

## 🛠️ Requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)
- Docker (opcional, para rodar o servidor do desafio)

---

## 📦 Instalação

```bash
# Clone o repositório
git clone https://github.com/tharsis-soares/auth-bot
cd auth-bot

# Instale as dependências
poetry install

# Configure as credenciais (opcional)
cp .env.example .env