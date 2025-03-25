from .connection import PostgresConnection
from .repositories.users import UserRepository
from .repositories.messages import ChatMessageRepository

class Database:
    def __init__(self):
        self.connection = PostgresConnection()
        self.users = UserRepository(self.connection)
        self.messages = ChatMessageRepository(self.connection)
        
    async def connect(self):
        await self.connection.connect()
        
    async def init_tables(self):
        await self.users.init_tables()
        await self.messages.init_tables()
        
    async def drop_all_tables(self):
        await self.users.drop_tables()
        await self.messages.drop_tables()