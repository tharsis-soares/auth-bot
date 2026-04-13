# test_async.py
import asyncio
import time
from config.config import Config
from utils.logger import ConsoleLogger
from utils.http_client import HttpxClient
from services.pow_service import PowService
from services.extreme_service import ExtremeService


async def test_extreme_async():
    """Testa se as operações assíncronas não bloqueiam"""
    config = Config()
    logger = ConsoleLogger()
    http_client = HttpxClient()
    pow_service = PowService(logger, config)
    extreme_service = ExtremeService(http_client, logger, config, pow_service)

    logger.info("Teste: Extreme Mode com async verdadeiro")

    start = time.time()

    # Simula múltiplas chamadas concorrentes (se tivesse mais de uma)
    session_id, ws_ticket = await extreme_service.init_session()
    result = await extreme_service.solve_and_verify(session_id, ws_ticket)

    elapsed = time.time() - start

    logger.success(f"Concluído em {elapsed:.2f}s")

    # Verifica se o TTL foi respeitado
    assert elapsed < 10, f"Demorou {elapsed}s, TTL é 10s!"

    return result


async def test_concurrent_extreme():
    """Testa se o event loop não bloqueia (simula concorrência)"""
    config = Config()
    logger = ConsoleLogger()
    http_client = HttpxClient()

    async def fake_task(name: str, delay: float):
        logger.info(f"Task {name} iniciada")
        await asyncio.sleep(delay)
        logger.info(f"Task {name} concluída")
        return name

    # Roda o Extreme Mode enquanto outras tasks rodam
    extreme_task = asyncio.create_task(test_extreme_async())
    background_tasks = [asyncio.create_task(fake_task(f"BG{i}", 0.5)) for i in range(3)]

    results = await asyncio.gather(extreme_task, *background_tasks)

    logger.success(f"Todas as tasks concluídas: {results}")


if __name__ == "__main__":
    # Teste básico
    asyncio.run(test_extreme_async())

    # Teste de concorrência (descomente para testar)
    # asyncio.run(test_concurrent_extreme())