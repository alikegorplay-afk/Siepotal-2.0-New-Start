import logging
import asyncio

from typing import List, Dict, Optional, Any
from itertools import cycle
from http import HTTPStatus

import aiohttp

from SieportalToken import Token
from SieprotalTools import find_first_key

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(message)s | %(asctime)s"
)

logger = logging.getLogger(__name__)

class requests:
    def __init__(
        self, 
        session: aiohttp.ClientSession, 
        token: Token,
        max_try: int = 3,
        *,
        proxy_list: List[str] = None,
        use_proxy: bool = False,
        sleep_time: int | float = 1.0 
        ):
        """Инцилизяция класса
        
        Args:
            - session: aiohttp.ClientSession - Хранит сеццию
            - max_try: Максимальное количество попыток (при -1 будут бесконечные попытки [НЕ РЕКЕМЕНДУЕСТЯ])
        """
        
        self.total_requests = 0
        self.error_requests = 0
        self.sleep_time = sleep_time
        
        self.max_try = max_try
        self.session = session
        self.token = token
        
        self.proxy_list = cycle(proxy_list if proxy_list else [])
        self.use_proxy = use_proxy
        self.current_proxy = None
        
    async def request(self, method: str, url: str, *args, **kwargs) -> Optional[Dict[str, Any]]:
        current_requests = self.max_try
        current_node = find_first_key(kwargs, 'NodeId') or url
        
        while current_requests != 0:
            current_requests -= 1
            try:
                self.total_requests += 1
                async with self.session.request(
                    method, 
                    url, 
                    *args, **kwargs,
                    proxy = self.current_proxy,
                    headers = await self.token.get_headers()
                ) as response:
                    response.raise_for_status()
                    logger.info(f"200 - для '{current_node}'")
                    return await response.json()
                
            except aiohttp.ClientResponseError as error:
                if error.status == HTTPStatus.BAD_REQUEST:
                    self.error_requests += 1
                    logger.warning(f"400 - для '{current_node}' попытка {self.max_try - current_requests} из {self.max_try}")
                    return None
                
                elif error.status == HTTPStatus.UNAUTHORIZED:
                    logger.info(f"401 - для '{current_node}' попытка {self.max_try - current_requests} из {self.max_try}")
                    await self.token.update()
                
                elif error.status == HTTPStatus.FORBIDDEN:
                    logger.warning(f"403 - для '{current_node}' попытка {self.max_try - current_requests} из {self.max_try}")
                    if self.use_proxy and self.proxy_list:
                        self.current_proxy = next(self.proxy_list)
                        logger.info(f"Используем прокси: {self.current_proxy}")
                        
                elif 500 <= error.status <= 599:
                    logger.warning(f"Ошибка сервера попытка {self.max_try - current_requests} из {self.max_try} для {current_node}")
                
                else:
                    logger.error(f"Неизвестный код: '{error.status}' для {current_node}")
                
                await asyncio.sleep(self.sleep_time)
            
            except aiohttp.ClientError as error:
                logger.warning(f"Ошибка {error} для '{current_node}'")
                await asyncio.sleep(self.sleep_time)
            
            except asyncio.TimeoutError:
                logger.warning(f"Таймаут для '{current_node}' попытка {self.max_try - current_requests} из {self.max_try}")
                await asyncio.sleep(self.sleep_time)
                
            except Exception as error:
                logger.error(f"Неизвестная ошибка {error} для {current_node}")
                await asyncio.sleep(self.sleep_time)
        self.error_requests += 1
        logger.warning(f"{current_node} не был получен за {self.max_try} попытки")
    
    async def get(self, url: str, *args, **kwargs):
        return await self.request("GET", url, *args, **kwargs)
    
    async def post(self, url: str, *args, **kwargs):
        return await self.request("POST", url, *args, **kwargs)
    
    def get_stats(self) -> Dict[str, int]:
        """Возвращает статистику запросов"""
        success_requests = self.total_requests - self.error_requests
        success_rate = (success_requests / self.total_requests * 100) if self.total_requests > 0 else 0
        return {
            "total_requests": self.total_requests,
            "error_requests": self.error_requests,
            "success_requests": success_requests,
            "success_rate": round(success_rate, 2)
        }
        
