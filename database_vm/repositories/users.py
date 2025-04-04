from .base import Repository
from typing import Optional, List, Dict, Any

class UserRepository(Repository):
    async def init_tables(self):
        sql = """
        CREATE TABLE IF NOT EXISTS "users" (
            "telegram_user_id" bigint UNIQUE PRIMARY KEY NOT NULL,
            "nickname" varchar(50),
            "gender" boolean,
            "voice" boolean,
            "vmm" boolean,
            "language" varchar(10) DEFAULT 'ru'
        );
        """
        await self.db.execute(sql)
        
    async def drop_tables(self):
        await self.db.execute('DROP TABLE IF EXISTS users CASCADE;')
        
    async def add(self, user_id: int, gender: bool, nickname: str, voice: bool, language: str = 'ru'):
        sql = """
        INSERT INTO users (telegram_user_id, gender, nickname, voice, vmm, language)
        VALUES ($1, $2, $3, $4, FALSE, $5)
        ON CONFLICT (telegram_user_id) 
        DO UPDATE SET
            gender = EXCLUDED.gender,
            nickname = EXCLUDED.nickname, 
            voice = EXCLUDED.voice,
            vmm = EXCLUDED.vmm,
            language = EXCLUDED.language;
        """
        await self.db.execute(sql, user_id, gender, nickname, voice, language)
        
    async def delete(self, user_id: int):
        sql = "DELETE FROM users WHERE telegram_user_id = $1;"
        await self.db.execute(sql, user_id)
        
    async def get_all(self) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM users;"
        return await self.db.fetch(sql)
        
    async def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT telegram_user_id, nickname, gender, voice, vmm, language
        FROM users WHERE telegram_user_id = $1;
        """
        row = await self.db.fetchrow(sql, user_id)
        return dict(row) if row else None
        
    async def exists(self, user_id: int) -> bool:
        sql = "SELECT 1 FROM users WHERE telegram_user_id = $1;"
        row = await self.db.fetchrow(sql, user_id)
        return row is not None
        
    async def update_vmm(self, user_id: int, value: bool):
        sql = "UPDATE users SET vmm = $2 WHERE telegram_user_id = $1;"
        await self.db.execute(sql, user_id, value)
        
    async def update_nickname(self, user_id: int, nickname: str):
        sql = "UPDATE users SET nickname = $2 WHERE telegram_user_id = $1;"
        await self.db.execute(sql, user_id, nickname)
        
    async def update_gender(self, user_id: int, gender: bool):
        sql = "UPDATE users SET gender = $2 WHERE telegram_user_id = $1;"
        await self.db.execute(sql, user_id, gender)
        
    async def update_voice(self, user_id: int, voice: bool):
        sql = "UPDATE users SET voice = $2 WHERE telegram_user_id = $1;"
        await self.db.execute(sql, user_id, voice)
        
    async def update_language(self, user_id: int, language: str):
        sql = "UPDATE users SET language = $2 WHERE telegram_user_id = $1;"
        await self.db.execute(sql, user_id, language)