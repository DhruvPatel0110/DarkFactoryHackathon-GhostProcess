import asyncio
import time
from collections import deque
from typing import Optional

class AsyncRateLimiter:
    """
    Sliding window & token bucket rate limiter for LLM API calls.
    Prevents 429 Too Many Requests errors by pacing outgoing calls.
    """
    def __init__(self, max_rpm: int = 20, min_interval_seconds: float = 2.5):
        """
        :param max_rpm: Maximum requests allowed per 60-second sliding window (default 20 for Groq free tier).
        :param min_interval_seconds: Minimum time spacing between consecutive calls (default 2.5s).
        """
        self.max_rpm = max_rpm
        self.min_interval = min_interval_seconds
        self.timestamps = deque()
        self.last_call_time = 0.0
        self.lock = asyncio.Lock()

    async def acquire(self):
        """
        Acquires permission to make an API call.
        If limits are approached, asynchronously sleeps until a slot opens.
        """
        async with self.lock:
            now = time.monotonic()
            
            # 1. Enforce minimum interval between consecutive requests
            time_since_last = now - self.last_call_time
            if time_since_last < self.min_interval:
                sleep_needed = self.min_interval - time_since_last
                await asyncio.sleep(sleep_needed)
                now = time.monotonic()

            # 2. Enforce sliding window RPM limit (last 60 seconds)
            while self.timestamps and (now - self.timestamps[0] > 60.0):
                self.timestamps.popleft()

            if len(self.timestamps) >= self.max_rpm:
                # Wait until the oldest request falls outside the 60-second window
                wait_time = 60.0 - (now - self.timestamps[0]) + 0.1
                if wait_time > 0:
                    print(f"   [RATE LIMITER] Sliding window full ({len(self.timestamps)}/{self.max_rpm} RPM). Pacing for {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
                    now = time.monotonic()
                while self.timestamps and (now - self.timestamps[0] > 60.0):
                    self.timestamps.popleft()

            # Record this call timestamp
            self.timestamps.append(now)
            self.last_call_time = now
