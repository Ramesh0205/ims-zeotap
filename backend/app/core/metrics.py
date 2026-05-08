import asyncio
import time
import logging
from collections import deque

logger = logging.getLogger(__name__)

signal_timestamps = deque()

def record_signal():
    signal_timestamps.append(time.time())

async def metrics_reporter():
    while True:
        await asyncio.sleep(5)
        now = time.time()
        # Keep only last 5 seconds
        while signal_timestamps and signal_timestamps[0] < now - 5:
            signal_timestamps.popleft()
        rate = len(signal_timestamps) / 5
        logger.info(f"📊 Throughput: {rate:.1f} signals/sec | Total in window: {len(signal_timestamps)}")
