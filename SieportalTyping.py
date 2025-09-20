import aiohttp

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from SieportalToken import Token
from SieportalRequests import requests


class BaseAPI:
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

    
    def _default_params(self, new_dict: Dict[str, Any]):
        return {
            'RegionId': self.region,
            'Language': self.language,
        } | new_dict

@dataclass
class BaseChild:
    node_id: int

@dataclass
class NodeChild(BaseChild):
    save_product: bool

@dataclass
class PriceChild(BaseChild):
    price: str

@dataclass
class NodeInfo:
    children: List[BaseChild]
    save_info: bool
    save_product: bool
    save_accessory: bool
    node_id: int

@dataclass
class NodeProduct:
    products: List[BaseChild]
    product_count: int