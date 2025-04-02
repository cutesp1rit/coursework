import asyncio

class AudioTaskCounter:
    def __init__(self, max_tasks=3):
        self._count = 0
        self._lock = asyncio.Lock()
        self.max_tasks = max_tasks
        
    async def increment(self):
        """Увеличивает счетчик задач и возвращает новое значение"""
        async with self._lock:
            self._count += 1
            return self._count
            
    async def decrement(self):
        """Уменьшает счетчик задач и возвращает новое значение"""
        async with self._lock:
            self._count = max(0, self._count - 1)
            return self._count
            
    async def get_count(self):
        """Возвращает текущее количество задач"""
        async with self._lock:
            return self._count
            
    async def has_high_load(self):
        """Проверяет, есть ли высокая нагрузка на генерацию аудио"""
        async with self._lock:
            return self._count >= self.max_tasks