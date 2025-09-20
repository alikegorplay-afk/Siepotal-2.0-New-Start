from typing import List, Optional, Dict, Any

import aiohttp

from SieportalTyping import NodeProduct, BaseChild, BaseAPI

class GetProductAPI(BaseAPI):
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
    
    async def get_node_products(
        self, 
        node_id: int | str, 
        page_number: int | str = 0
    ) -> NodeProduct:
        """get_node_products получает MAIN продукты из каталога
        
        Args:
        
            node_id: [int] ссылка на ветвь пример .../10539284?tree=CatalogTree#productVariants здесь 10539284 это node_id
            
            page_number: [int] это номер страницы
            
        Returns:
        
            NodeProduct - Возращает артикулы и количество найденных атрибутов
        """
        
        URL = 'https://sieportal.siemens.com/api/mall/CatalogTreeApi/GetNodeProducts'
        json_data = self._default_params(
            {
                'nodeId': node_id,
                'pageNumberIndex': page_number,
            }
        )
        response = await self.requests.post(URL, json=json_data)
        return NodeProduct(
            [BaseChild(product.get('articleNumber', "N/a")) for product in response.get('products', [])],
            response.get('productCount', 0)
        ) if response is not None else None
    
    async def get_node_accessories(
        self,
        node_id: int | str,
        page_number: int | str = 0
    ) -> Optional[NodeProduct]:
        """get_node_accesories получает АКСЕССУАРЫ продукта из каталога
        
        Args:
        
            node_id: [int] ссылка на ветвь пример .../10539284?tree=CatalogTree#productVariants здесь 10539284 это node_id
            page_number: [int] это номер страницы
            
        Returns:
        
            NodeProduct - Возращает артикулы и количество найденных атрибутов
        """
        URL = 'https://sieportal.siemens.com/api/mall/CatalogTreeApi/GetProductAccessories'
        json_data = self._default_params(
            {
                'nodeId': node_id,
                'pageNumberIndex': page_number,
            }
        )
        response = await self.requests.post(URL, json=json_data)
        return NodeProduct(
            [BaseChild(product.get('articleNumber', "N/a")) for product in response.get('products', [])],
            response.get('productCount', 0)
        ) if response is not None else None
    
    def _default_params(self, new_dict: Dict[str, Any]):
        return super()._default_params(
            {
                'treeName': 'CatalogTree',
                'limit': 50,
            } | new_dict)