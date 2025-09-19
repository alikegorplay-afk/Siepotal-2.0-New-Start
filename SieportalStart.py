import os
import logging
import asyncio

from typing import Awaitable
from pathlib import Path

import aiohttp
import dotenv
import argparse

from SieportalGetTreeAPI import GetTreeAPI as TreeAPI
from SieportalGetProductAPI import GetTreeAPI as ProductAPI
from SieportalTyping import NodeProduct
from SieportalWriter import CsvWriter

dotenv.load_dotenv()

PROXY_LIST = os.getenv("PROXY")
PROXY_LIST = PROXY_LIST.split(',') if PROXY_LIST else []

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(message)s | %(asctime)s"
)

logger = logging.getLogger(__name__)

def parse():
    parser = argparse.ArgumentParser(
    description='Парсер каталога Siemens SiePortal',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='''
        Примеры использования:
        python SieportalStart.py --region cn --language en
        python SieportalStart.py -r de -l de -n 10045207 10313567 -c 5
        python SieportalStart.py --proxy --max-try 10 --sleep 2.0
    '''
    )

    # Обязательные аргументы
    parser.add_argument('--region', '-r', type=str, required=True,
                       help='Регион (например: cn, de, us)')
    parser.add_argument('--language', '-l', type=str, required=True,
                       help='Язык (например: en, de, zh)')

    # Опциональные аргументы
    parser.add_argument('--nodes', '-n', type=int, nargs='+', default=[9990173, 10045207, 10313567, 10047631, 9990301, 10008397, 9990314, 10008397, 1000000],
                       help='ID начальных узлов для парсинга')
    parser.add_argument('--concurrent', '-c', type=int, default=8,
                       help='Максимальное количество одновременных запросов')
    parser.add_argument('--max-try', '-m', type=int, default=3,
                       help='Максимальное количество попыток для запроса')
    parser.add_argument('--sleep', '-s', type=float, default=1.0,
                       help='Время ожидания между запросами (секунды)')
    parser.add_argument('--output', '-o', type=str,
                       help='Путь к выходному файлу (по умолчанию: files/{language}-{region}.csv)')
    parser.add_argument('--proxy', action='store_true',
                       help='Использовать прокси из переменной окружения PROXY')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод')

    # Парсим аргументы
    return parser.parse_args()

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
    if node_info is None:
        return
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
    args = parse()
    
    DEFAULT_REGION: str = args.region
    DEFAULT_LANGUAGE = args.language
    FILE_PATH = Path("files") / f"{DEFAULT_LANGUAGE}-{DEFAULT_REGION}.csv"
    
    async with aiohttp.ClientSession() as session:
        SETTING = {
            'session': session, 
            'language': DEFAULT_LANGUAGE, 
            'region': DEFAULT_REGION,
            'proxy_list': PROXY_LIST,
            'use_proxy': args.proxy,
            'max_try': args.max_try,
            'sleep_time': args.sleep
        }
        tree_api = TreeAPI(**SETTING)
        product_api = ProductAPI(**SETTING)
        writer = CsvWriter(FILE_PATH)
        
        for node_id in args.nodes:
            logger.info(f"Старт обработки узла {node_id}!")
            await spider(node_id, tree_api, product_api, writer, max_concurrent= args.concurrent)
        
        logger.info(f"РЕЗУЛЬТАТ: {tree_api.requests.get_stats()}, {product_api.requests.get_stats()}!")
   
    await writer.save()
    logger.info("Парсинг завершен!")

if __name__ == "__main__":
    asyncio.run(main())