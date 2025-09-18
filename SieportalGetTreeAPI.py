import logging

from typing import List, Dict, Optional, Any

import aiohttp

from SieportalTyping import NodeInfo, NodeChild
from SieportalToken import Token
from SieportalRequests import requests

class GetTreeAPI:
    def __init__(
        self, 
        session: aiohttp.ClientSession,
        language: str,
        region: str,
        *,
        proxy_list: Optional[List[str]] = None,
        use_proxy: bool = False,
        sleep_time: float | int = 1.0,
        max_try: int = 3
    ):
        self._session: aiohttp.ClientSession = session
        self.proxy_list: list[str] = proxy_list
        self.use_proxy: bool = use_proxy
        
        self.language = language
        self.region = region
        self.token = Token(session)
        self.requests = requests(self._session, self.token, max_try = max_try, proxy_list=proxy_list, use_proxy=use_proxy, sleep_time=sleep_time)
    
    async def get_node_info(self, node_id: int | str) -> Optional[NodeInfo]:
        """Получает информацию о узле каталога по его ID"""
        
        URL = 'https://sieportal.siemens.com/api/mall/CatalogTreeApi/GetNodeInformation'
        params = self._default_params({
            'NodeId': node_id,
            'TreeName': 'CatalogTree'
        })
        response = await self.requests.get(URL, params = params)
        try:
            return NodeInfo(
                [
                    NodeChild(node_id=child['id'], 
                    save_product=child.get('containsProducts', False)) 
                    for child in response.get('childNodes', [])
                ],
                
                response.get('containsProductInformation', False),
                response.get('containsProductVariants', False),
                response.get('containsRelatedProducts', False),
                response['id'] # Если id не существует то это уже не ветвь!
            )
        except (KeyError, TypeError, AttributeError) as error:
            logging.error(error)
            return None
        
    def _default_params(self, new_dict: Dict[str, Any]):
        return {
            'RegionId': self.region,
            'Language': self.language,
        } | new_dict