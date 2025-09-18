import os
import asyncio
from typing import Awaitable
from pathlib import Path
import aiohttp
import dotenv
from SieportalGetTreeAPI import GetTreeAPI as TreeAPI
from SieportalGetProductAPI import GetTreeAPI as ProductAPI
from SieportalTyping import NodeProduct
from SieportalWriter import CsvWriter

dotenv.load_dotenv()
PROXY_LIST = os.getenv("PROXY").split(',')

async def getter_items(node_id: int | str, func: Awaitable, writer: CsvWriter):
    page = 0
    while True:
        response: NodeProduct = await func(node_id, page)
        if not response or not response.products or not response.product_count:
            break
        for article in response.products:
            await writer.add(article.node_id)
        page += 1

async def process_node(node_id: str | int, tree_api: TreeAPI, product_api: ProductAPI, writer: CsvWriter):
    """Обрабатывает один узел и возвращает список дочерних узлов"""
    node_info = await tree_api.get_node_info(node_id)
    
    if node_info.save_product:
        await getter_items(node_id, product_api.get_node_products, writer)
    if node_info.save_accessory:
        await getter_items(node_id, product_api.get_node_accesories, writer)
    
    return [child.node_id for child in node_info.children]

async def spider(node_id: str | int, tree_api: TreeAPI, product_api: ProductAPI, writer: CsvWriter, max_concurrent: int = 10):
    """Рекурсивно обрабатывает дерево каталога с ограничением количества одновременных запросов"""
    # Обрабатываем текущий узел и получаем дочерние узлы
    child_nodes = await process_node(node_id, tree_api, product_api, writer)
    
    # Обрабатываем дочерние узлы параллельно с ограничением количества одновременных задач
    while child_nodes:
        # Берем первую порцию узлов для параллельной обработки
        batch, child_nodes = child_nodes[:max_concurrent], child_nodes[max_concurrent:]
        
        # Создаем задачи для параллельного выполнения
        tasks = [
            spider(child_id, tree_api, product_api, writer, max_concurrent)
            for child_id in batch
        ]
        
        # Запускаем все задачи параллельно и ждем их завершения
        await asyncio.gather(*tasks)

async def main():
    DEFAULT_REGION = 'cn'
    DEFAULT_LANGUAGE = 'en'
    FILE_PATH = Path("files") / f"{DEFAULT_LANGUAGE}-{DEFAULT_REGION}.csv"
    
    async with aiohttp.ClientSession() as session:
        SETTING = {
            'session': session, 
            'language': DEFAULT_LANGUAGE, 
            'region': DEFAULT_REGION,
            'proxy_list': PROXY_LIST,
            'use_proxy': True
        }
        tree_api = TreeAPI(**SETTING)
        product_api = ProductAPI(**SETTING)
        writer = CsvWriter(FILE_PATH)
        
        for node_id in (9990173, 10045207, 10313567, 10047631, 10008397):
            await spider(node_id, tree_api, product_api, writer, max_concurrent=8)
    
    await writer.save()

if __name__ == "__main__":
    asyncio.run(main())