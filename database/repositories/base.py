from abc import ABC, abstractmethod
from connection import DatabaseConnection

class Repository(ABC):
    def __init__(self, db: DatabaseConnection):
        self.db = db
        
    @abstractmethod
    async def init_tables(self):
        pass
        
    @abstractmethod
    async def drop_tables(self):
        pass