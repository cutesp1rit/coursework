import asyncpg
import os

INIT_DB_QUERIES = [
    """
    CREATE TABLE IF NOT EXISTS "users" (
        "telegram_user_id" varchar UNIQUE PRIMARY KEY NOT NULL,
        "nickname" varchar,
        "gender" boolean,
        "voice" boolean
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS "chat_messages" (
        "id" varchar UNIQUE PRIMARY KEY,
        "chat_id" varchar NOT NULL,
        "user_id" varchar NOT NULL,
        "username" varchar,
        "message_text" text,
        "created_at" timestamp
    );
    """,
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.table_constraints
            WHERE table_name = 'chat_messages'
            AND constraint_name = 'fk_user_id'
        ) THEN
            ALTER TABLE chat_messages
            ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id)
            REFERENCES users (telegram_user_id)
            ON DELETE CASCADE;
        END IF;
    END $$;
    """
]

class Database:
    def __init__(self):
        self.pool = None

    # установление соединения с базой данных
    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            host="db",
            port=os.environ["DB_PORT"]
        )

    # для выполнения SQL-запросов, которые не возвращают данные
    async def execute(self, sql, *args):
        async with self.pool.acquire() as conn:
            await conn.execute(sql, *args)

    # используется для выполнения SQL-запросов, которые возвращают одну строку результата
    async def fetchrow(self, sql, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(sql, *args)

    # используется для выполнения SQL-запросов, которые возвращают несколько строк
    async def fetch(self, sql, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql, *args)
    
    # инициализация таблиц
    async def init_tables(self):
        async with self.pool.acquire() as conn:
            for query in INIT_DB_QUERIES:
                await conn.execute(query)

    # добавление пользователя
    async def add_user(self, telegram_user_id: str, nickname: str):
        """Добавляет пользователя в базу данных."""
        sql = """
        INSERT INTO "users" (telegram_user_id, nickname)
        VALUES ($1, $2)
        ON CONFLICT (telegram_user_id) DO NOTHING;
        """
        await self.execute(sql, telegram_user_id, nickname)

    # удаление пользователя
    async def delete_user(self, telegram_user_id: str):
        sql = """
        DELETE FROM users WHERE telegram_user_id = $1;
        """
        await self.execute(sql, telegram_user_id)

    # возвращает всех пользователей
    async def get_all_users(self):
        sql = "SELECT * FROM users;"
        return await self.fetch(sql)