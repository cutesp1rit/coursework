import pytest
import asyncpg
import os

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