from datetime import datetime
from typing import List, Dict, Optional, Any
from .base import Repository

class ChatMessageRepository(Repository):
    async def init_tables(self):
        sql = """
        CREATE TABLE IF NOT EXISTS "chat_messages" (
            "id" varchar UNIQUE PRIMARY KEY,
            "chat_id" varchar NOT NULL,
            "user_id" varchar NOT NULL,
            "username" varchar,
            "message_text" text,
            "created_at" timestamp
        );
        """
        await self.db.execute(sql)
        
    async def drop_tables(self):
        await self.db.execute('DROP TABLE IF EXISTS chat_messages CASCADE;')
        
    async def add(self, message_id: str, chat_id: str, user_id: str, 
                 username: str, message_text: str, created_at: datetime):
        sql = """
        INSERT INTO chat_messages (id, chat_id, user_id, username, message_text, created_at)
        VALUES ($1, $2, $3, $4, $5, $6);
        """
        await self.db.execute(sql, message_id, chat_id, user_id, username, message_text, created_at)
        
    async def get_count(self, chat_id: str) -> int:
        sql = "SELECT COUNT(*) FROM chat_messages WHERE chat_id = $1;"
        row = await self.db.fetchrow(sql, chat_id)
        return row["count"] if row else 0
        
    async def get_oldest_message_id(self, chat_id: str) -> Optional[str]:
        sql = """
        SELECT id FROM chat_messages 
        WHERE chat_id = $1 
        ORDER BY created_at ASC 
        LIMIT 1;
        """
        row = await self.db.fetchrow(sql, chat_id)
        return row["id"] if row else None
        
    async def delete(self, message_id: str):
        sql = "DELETE FROM chat_messages WHERE id = $1;"
        await self.db.execute(sql, message_id)
        
    async def get_dialogue_messages(self, message_id: str, chat_id: str, count: int) -> List[Dict[str, Any]]:
        sql = """
        SELECT id, chat_id, user_id, username, message_text, created_at
        FROM chat_messages
        WHERE chat_id = $1 AND created_at >= (
            SELECT created_at FROM chat_messages WHERE id = $2
        )
        ORDER BY created_at ASC
        LIMIT $3;
        """
        return await self.db.fetch(sql, str(chat_id), str(message_id), count)