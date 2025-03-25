from abc import ABC, abstractmethod
import asyncpg
import os

class DatabaseConnection(ABC):
    @abstractmethod
    async def connect(self):
        pass
    
    @abstractmethod
    async def execute(self, sql: str, *args):
        pass
    
    @abstractmethod 
    async def fetchrow(self, sql: str, *args):
        pass
    
    @abstractmethod
    async def fetch(self, sql: str, *args):
        pass

class PostgresConnection(DatabaseConnection):
    def __init__(self):
        self.pool = None
        
    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"], 
            database=os.environ["DB_NAME"],
            host="db",
            port=os.environ["DB_PORT"]
        )
    
    async def execute(self, sql: str, *args):
        async with self.pool.acquire() as conn:
            await conn.execute(sql, *args)
            
    async def fetchrow(self, sql: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(sql, *args)
            
    async def fetch(self, sql: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql, *args)