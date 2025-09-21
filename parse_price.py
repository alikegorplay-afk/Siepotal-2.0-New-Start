import asyncio
import os
import logging

from SieprotalPrice import GetPriceAPI

import aiohttp
import aiofiles
import aiocsv
import dotenv

from SieportalTyping import NodeProduct
from SieportalWriter import CsvWriter

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

PROXY_LIST = os.getenv("PROXY")
PROXY_LIST = PROXY_LIST.split(',') if PROXY_LIST else []

async def main():
    writer = CsvWriter("files\\NEW_EN_KR.csv", 200)
    
    async with aiofiles.open("new_en_kr.csv", 'r', newline='') as file_read:
        csv = aiocsv.AsyncReader(file_read)
        async with aiohttp.ClientSession() as session:
            api = GetPriceAPI(session, 'en', 'kr', proxy_list=PROXY_LIST, use_proxy=True, sleep_time=0.5, max_try=round(len(PROXY_LIST) * 1.5))
            tasks = []
            
            async for line in csv:
                if line and line[0]:  # Проверка на пустую строку
                    tasks.append(asyncio.create_task(api.get_pice(line[0], "KRW")))
                    if len(tasks) >= 50:
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        for response in results:
                            if isinstance(response, Exception):
                                logger.error(f"Ошибка при запросе: {response}")
                                continue
                            if response and response.products:
                                await writer.add([response.products[0].node_id, response.products[0].price])
                        tasks.clear()

    await writer.save()
    
asyncio.run(main())