import pytest
from app.voice_processing.task_counter import AudioTaskCounter

class TestAudioTaskCounter:
    @pytest.mark.asyncio
    async def test_counter_operations(self):
        counter = AudioTaskCounter(max_tasks=2)
        
        # Проверяем начальное состояние
        assert await counter.get_count() == 0
        assert not await counter.has_high_load()
        
        # Увеличиваем счетчик
        assert await counter.increment() == 1
        assert await counter.get_count() == 1
        assert not await counter.has_high_load()
        
        # Проверяем лимит
        await counter.increment()
        assert await counter.has_high_load()
        
        # Уменьшаем счетчик
        assert await counter.decrement() == 1
        assert not await counter.has_high_load()
        
        # Не может быть меньше 0
        await counter.decrement()
        await counter.decrement()
        assert await counter.get_count() == 0