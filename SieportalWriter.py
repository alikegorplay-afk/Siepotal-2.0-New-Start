import logging

from typing import List
from pathlib import Path

import aiocsv
import aiofiles

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(message)s | %(asctime)s"
)

logger = logging.getLogger(__name__)

class CsvWriter:
    def __init__(
        self,
        fp: str | Path,
        buffer: int = 500,
    ):
        self.buffer_size = buffer
        self.fp = Path(fp)
        self.fp.parent.mkdir(parents=True, exist_ok=True)
        

        self.buffer: List[str | int] = list()
        
    async def add(self, item: List[str] | str | int):
        if isinstance(item, list):
            self.buffer.append(item)
        else:
            self.buffer.append([item])
        if len(self.buffer) >= self.buffer_size:
            await self.save()
    
    async def save(self):
        logger.info(f"Сохранения {len(self.buffer)} элементов...")
        async with aiofiles.open(self.fp, 'a', newline='') as file:
            _writer = aiocsv.AsyncWriter(file)
            await _writer.writerows(self.buffer)
        self.flush()
        
    def flush(self):
        self.buffer.clear()