import time
import asyncio
from collections import deque
from fastapi import HTTPException
from app.core.config import settings

class RateLimiter:
    def __init__(self, max_per_second: int):
        self.max_per_second = max_per_second
        self.timestamps = deque()
        self._lock = asyncio.Lock()

    async def check(self):
        async with self._lock:
            now = time.time()
            while self.timestamps and self.timestamps[0] < now - 1:
                self.timestamps.popleft()
            if len(self.timestamps) >= self.max_per_second:
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Slow down signal ingestion.")
            self.timestamps.append(now)

rate_limiter = RateLimiter(settings.RATE_LIMIT_PER_SECOND)
