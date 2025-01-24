import asyncpg
import os

INIT_DB_QUERIES = [
    """
    CREATE TABLE IF NOT EXISTS "users" (
        "telegram_user_id" varchar UNIQUE PRIMARY KEY NOT NULL,
        "nickname" varchar,
        "gender" boolean,
        "voice" boolean, 
        "vmm" boolean 
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
    # """
    # DO $$
    # BEGIN
    #     IF NOT EXISTS (
    #         SELECT 1
    #         FROM information_schema.table_constraints
    #         WHERE table_name = 'chat_messages'
    #         AND constraint_name = 'fk_user_id'
    #     ) THEN
    #         ALTER TABLE chat_messages
    #         ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id)
    #         REFERENCES users (telegram_user_id)
    #         ON DELETE CASCADE;
    #     END IF;
    # END $$;
    # """
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

    # удаление таблиц
    async def drop_all_tables(self):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # отключаем ограничения внешних ключей
                # await conn.execute("SET session_replication_role = 'replica';")
                
                tables = ["users", "chat_messages"]

                for table_name in tables:
                    await conn.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE;')

                # включаем ограничения внешних ключей обратно
                # await conn.execute("SET session_replication_role = 'origin';")

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

    # меняет значение vmm на true
    async def set_vmm_true(self, telegram_user_id: str):
        sql = """
        UPDATE users
        SET vmm = TRUE
        WHERE telegram_user_id = $1;
        """
        await self.execute(sql, telegram_user_id)

    # меняет значение vmm на False
    async def set_vmm_false(self, telegram_user_id: str):
        sql = """
        UPDATE users
        SET vmm = FALSE
        WHERE telegram_user_id = $1;
        """
        await self.execute(sql, telegram_user_id)

    # проверяет наличие пользователя в БД 
    async def is_user_exist(self, telegram_user_id: str) -> bool:
        sql = """
        SELECT 1
        FROM users
        WHERE telegram_user_id = $1;
        """
        row = await self.fetchrow(sql, telegram_user_id)
        return row is not None

    async def add_user(self, telegram_user_id: str, gender: bool, nickname: str, voice: bool):
        sql = """
        INSERT INTO users (telegram_user_id, gender, nickname, voice, vmm)
        VALUES ($1, $2, $3, $4, FALSE)
        ON CONFLICT (telegram_user_id)
        DO UPDATE SET 
            gender = EXCLUDED.gender,
            nickname = EXCLUDED.nickname,
            voice = EXCLUDED.voice,
            vmm = EXCLUDED.vmm;
        """
        await self.execute(sql, telegram_user_id, gender, nickname, voice)