import time
import os
import logging
import asyncio
from typing import Dict, Any, Optional
import aiohttp
import dotenv
from fake_headers import Headers

from SieprotalTools import second_readable

dotenv.load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(message)s | %(asctime)s"
)

logger = logging.getLogger(__name__)

class Token:
    """
    Класс Token для управления аутентификационными токенами
    """
    URL = "https://auth.sieportal.siemens.com/connect/token"
    
    def __init__(self, session: aiohttp.ClientSession, proxy: Optional[str] = None):
        """Инициализация токена
        
        Args:
            session: HTTP сессия для запросов
            proxy: Прокси сервер (опционально)
        """
        logger.debug("Инициализация токена...")
        
        self._headers_generator = Headers()
        self._token: Optional[str] = None
        self._expires_at: Optional[float] = None
        self.proxy = proxy
        self._session = session
        
        # Данные для запроса токена
        self._data = {
            'client_id': 'Siemens.SiePortal.UI',
            'client_secret': os.getenv("CLIENT_SECRET"),
            'grant_type': 'client_credentials',
        }
        
        # Проверяем наличие обязательных данных
        if not self._data['client_secret']:
            logger.warning("CLIENT_SECRET не найден в переменных окружения")

    def is_token_valid(self) -> bool:
        """Проверяет валидность токена
        
        Returns:
            bool: True если токен валиден, иначе False
        """
        if self._token is None or self._expires_at is None:
            return False
        
        return time.time() < (self._expires_at - 10)

    async def update(self) -> bool:
        """Принудительно обновляет токен не зависимо от его времени 'Жизни'"""
        return await self.get_token(False)
    
    async def get_token(self, check_valid: bool = True) -> str:
        """Получает новый токен или возвращает существующий валидный
        
        Returns:
            str: Токен авторизации
        """
        if self.is_token_valid() and check_valid:
            logger.debug("Используется существующий валидный токен")
            return self._token
        
        logger.info("Запрос нового токена...")
        
        try:
            async with self._session.post(
                self.URL, 
                data=self._data,
                headers=self._headers_generator.generate(),
                proxy=self.proxy,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response.raise_for_status()
                json_response: Dict[str, Any] = await response.json()
                
                self._expires_at = time.time() + json_response.get('expires_in', 3600)
                token_type = json_response.get('token_type', 'Bearer')
                access_token = json_response['access_token']
                self._token = f"{token_type} {access_token}"
                
                logger.info(f"Токен успешно получен! Срок действия: {second_readable(self._expires_at - time.time())}")
                return self._token
                
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка при получении токена: {e}")
            raise
        except asyncio.TimeoutError:
            logger.error("Таймаут при получении токена")
            raise

    async def get_headers(self) -> Dict[str, str]:
        """Возвращает заголовки с актуальным токеном
        
        Returns:
            Dict[str, str]: Заголовки для HTTP запросов
        """
        token = await self.get_token()
        return self._headers_generator.generate() | {'Authorization': token}