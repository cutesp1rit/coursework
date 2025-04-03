import pytest

class TestUserRepository:
    @pytest.mark.asyncio
    async def test_user_crud(self, db):
        """Тест CRUD операций для пользователей"""
        # Создаем пользователя
        await db.users.add("test_user", True, "Test", False, "en")
        
        # Читаем данные пользователя
        user = await db.users.get_by_id("test_user")
        assert user["nickname"] == "Test"
        
        # Обновляем никнейм
        await db.users.update_nickname("test_user", "Updated")
        updated = await db.users.get_by_id("test_user")
        assert updated["nickname"] == "Updated"
        
        # Удаляем пользователя
        await db.users.delete("test_user")
        assert await db.users.get_by_id("test_user") is None

    @pytest.mark.asyncio
    async def test_get_all_users(self, db_with_data):
        """Тест получения всех пользователей"""
        # Получаем список всех пользователей
        users = await db_with_data.users.get_all()
        assert len(users) == 2
        assert {u["nickname"] for u in users} == {"Alice", "Bob"}

    @pytest.mark.asyncio
    async def test_upsert_behavior(self, db):
        """Тест обновления при конфликте"""
        # Первое добавление пользователя
        await db.users.add("user1", False, "Original", False)
        
        # Обновление при повторном добавлении того же пользователя
        await db.users.add("user1", True, "Updated", True, "fr")
        
        # Проверяем, что данные обновились
        user = await db.users.get_by_id("user1")
        assert user["nickname"] == "Updated"
        assert user["gender"] is True
        assert user["language"] == "fr"
    

    @pytest.mark.asyncio
    async def test_exists(self, db_with_data):
        """Тест проверки существования пользователя"""
        # Сначала создаем тестового пользователя
        test_user_id = "test_user_1"
        await db_with_data.users.add(user_id=test_user_id, nickname="test_user", voice=False, gender=False)
        
        # Проверяем существующего пользователя
        exists = await db_with_data.users.exists(test_user_id)
        assert exists is True
        
        # Проверяем несуществующего пользователя
        exists = await db_with_data.users.exists("non_existent_user")
        assert exists is False

    @pytest.mark.asyncio
    async def test_update_methods(self, db_with_data):
        """Тест методов обновления данных пользователя"""
        test_user_id = "test_user_1"
        
        # Создаем тестового пользователя
        await db_with_data.users.add(user_id=test_user_id, nickname="test_user", voice=False, gender=False)
        
        # Обновляем VMM статус и проверяем
        await db_with_data.users.update_vmm(test_user_id, True)
        user = await db_with_data.users.get_by_id(test_user_id)
        assert user["vmm"] is True
        
        # Обновляем никнейм и проверяем
        new_nickname = "new_nickname"
        await db_with_data.users.update_nickname(test_user_id, new_nickname)
        user = await db_with_data.users.get_by_id(test_user_id)
        assert user["nickname"] == new_nickname
        
        # Обновляем пол и проверяем
        await db_with_data.users.update_gender(test_user_id, False)
        user = await db_with_data.users.get_by_id(test_user_id)
        assert user["gender"] is False
        
        # Обновляем голосовой статус и проверяем
        await db_with_data.users.update_voice(test_user_id, True)
        user = await db_with_data.users.get_by_id(test_user_id)
        assert user["voice"] is True
        
        # Обновляем язык и проверяем
        new_language = "fr"
        await db_with_data.users.update_language(test_user_id, new_language)
        user = await db_with_data.users.get_by_id(test_user_id)
        assert user["language"] == new_language

    @pytest.mark.asyncio
    async def test_update_non_existent_user(self, db_with_data):
        """Тест обновления несуществующего пользователя"""
        non_existent_id = "non_existent_user"
        
        # Проверяем, что методы не вызывают ошибок при обновлении несуществующего пользователя
        await db_with_data.users.update_vmm(non_existent_id, True)
        await db_with_data.users.update_nickname(non_existent_id, "test")
        await db_with_data.users.update_gender(non_existent_id, False)
        await db_with_data.users.update_voice(non_existent_id, True)
        await db_with_data.users.update_language(non_existent_id, "en")
        
        # Проверяем, что пользователь не был создан автоматически
        exists = await db_with_data.users.exists(non_existent_id)
        assert exists is False