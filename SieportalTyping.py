from dataclasses import dataclass
from typing import List

@dataclass
class BaseChild:
    node_id: int

@dataclass
class NodeChild(BaseChild):
    save_product: bool

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