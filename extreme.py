"""
Versão refatorada do extreme_mode.py usando abstrações SOLID.
"""
import asyncio
from services.extreme_service import ExtremeService
from utils.http_client import HttpxClient
from config.config import Config
from utils.logger import ConsoleLogger


async def refactored_final_solution():
    config = Config()
    http_client = HttpxClient()
    logger = ConsoleLogger()
    extreme_service = ExtremeService(http_client, logger, config)

    session_id, ws_ticket = await extreme_service.init_session()
    final = await extreme_service.solve_and_verify(session_id, ws_ticket)
    return final

if __name__ == "__main__":
    asyncio.run(refactored_final_solution())