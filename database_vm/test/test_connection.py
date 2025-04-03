import pytest
import asyncpg
from database_vm.connection import PostgresConnection

class TestPostgresConnection:
    @pytest.mark.asyncio
    async def test_connection_flow(self, db):
        """Тест жизненного цикла подключения"""
        conn = db.connection
        
        # Проверка выполнения запросов
        await conn.execute("CREATE TEMP TABLE test(id SERIAL PRIMARY KEY)")
        await conn.execute("INSERT INTO test DEFAULT VALUES")
        
        result = await conn.fetchrow("SELECT COUNT(*) FROM test")
        assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_error_handling(self, db):
        """Тест обработки ошибок"""
        with pytest.raises(asyncpg.PostgresError):
            await db.connection.execute("INVALID SQL")

    @pytest.mark.asyncio
    async def test_connect_disconnect(self):
        """Тест подключения и отключения от БД"""
        conn = PostgresConnection()
        await conn.connect()
        assert conn.pool is not None
        
        await conn.disconnect()
        assert conn.pool is None

    @pytest.mark.asyncio
    async def test_get_connection(self):
        """Тест получения соединения из пула"""
        conn = PostgresConnection()
        await conn.connect()
        
        async with await conn.get_connection() as connection:
            assert connection is not None
            await connection.execute("SELECT 1")
        
        await conn.disconnect()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Тест работы контекстного менеджера"""
        async with PostgresConnection() as conn:
            assert conn.pool is not None
            await conn.execute("SELECT 1")
        
        # Проверяем, что соединение закрылось после выхода из контекста
        assert conn.pool is None

    @pytest.mark.asyncio
    async def test_fetch_methods(self, db):
        """Тест методов fetch и fetchrow"""
        conn = db.connection
        
        await conn.execute("CREATE TEMP TABLE test(id SERIAL PRIMARY KEY, name TEXT)")
        await conn.execute("INSERT INTO test(name) VALUES($1)", "Test")
        
        # Проверка fetchrow
        row = await conn.fetchrow("SELECT * FROM test WHERE name = $1", "Test")
        assert row["name"] == "Test"
        
        # Проверка fetch
        rows = await conn.fetch("SELECT * FROM test")
        assert len(rows) == 1
        assert rows[0]["name"] == "Test"

    @pytest.mark.asyncio
    async def test_execute_with_args(self, db):
        """Тест выполнения запроса с параметрами"""
        conn = db.connection
        
        await conn.execute("CREATE TEMP TABLE test(id SERIAL PRIMARY KEY, name TEXT)")
        await conn.execute("INSERT INTO test(name) VALUES($1)", "Alice")
        
        result = await conn.fetchrow("SELECT COUNT(*) FROM test WHERE name = $1", "Alice")
        assert result["count"] == 1