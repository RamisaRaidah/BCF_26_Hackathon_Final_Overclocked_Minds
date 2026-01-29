import time
from collections import deque
 
_WINDOW_SECONDS = 30
 
class RollingLatency:
    def __init__(self):
        self.samples = deque()  # (timestamp, latency_ms)
 
    def add(self, latency_ms: int):
        now = time.time()
        self.samples.append((now, latency_ms))
        self._trim(now)
 
    def _trim(self, now=None):
        now = now or time.time()
        cutoff = now - _WINDOW_SECONDS
        while self.samples and self.samples[0][0] < cutoff:
            self.samples.popleft()
 
    def avg_ms(self) -> float:
        self._trim()
        if not self.samples:
            return 0.0
        return sum(ms for _, ms in self.samples) / len(self.samples)
 
    def status(self) -> str:
        # Red if avg > 1000ms
        return "red" if self.avg_ms() > 1000 else "green"