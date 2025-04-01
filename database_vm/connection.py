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
    
    async def disconnect(self):
        """Закрывает соединение с базой данных."""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def get_connection(self):
        """Получение соединения с базой данных."""
        if not self.pool:
            await self.connect()
        return self.pool.acquire()
    
    async def execute(self, sql: str, *args):
        """Выполнение SQL-запроса без возврата результатов."""
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            await conn.execute(sql, *args)
            
    async def fetchrow(self, sql: str, *args):
        """Получение одной строки результата SQL-запроса."""
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(sql, *args)
            
    async def fetch(self, sql: str, *args):
        """Получение всех строк результата SQL-запроса."""
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql, *args)
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()