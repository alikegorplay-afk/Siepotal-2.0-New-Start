from typing import List, Optional

import aiohttp
from SieportalTyping import PriceChild, NodeProduct, BaseAPI

class GetPriceAPI(BaseAPI):
    def __init__(
        self, 
        session: aiohttp.ClientSession,
        language: str,
        region: str,
        *,
        proxy_list: Optional[List[str]] = None,
        use_proxy: bool = False,
        sleep_time = 1,
        max_try = 3):
        super().__init__(session, language, region, proxy_list=proxy_list, use_proxy=use_proxy, sleep_time=sleep_time, max_try=max_try)
    
    async def get_pice(self, article: str, currency_code: str) -> Optional[NodeProduct]:
        URL = 'https://sieportal.siemens.com/api/mall/ProductInformation/GetProductsAndPrices'
        json_data = {
            'countryCode': self.region,
            'language': self.language,
            'products': [
                {
                    'itemId': '1',
                    'articleNumber': article,
                }
            ],
            'currencyCode': currency_code,
            'regionId': self.region,
            'projectNumber': None,
        }
        
        data = await self.requests.post(URL, json = json_data)
        return NodeProduct(
            [PriceChild(article, item['productPrice']['uiValueListPrice']) for item in data['products']],
            len(data['products'])
        ) if data is not None else None