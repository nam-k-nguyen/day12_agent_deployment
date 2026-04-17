import time
from collections import defaultdict, deque
from .guards import GraphState

class RateLimiter:
    def __init__(self, max_requests=10, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_windows = defaultdict(deque)

    def check(self, user_id):
        now = time.time()
        window = self.user_windows[user_id]
        while window and now - window[0] > self.window_seconds:
            window.popleft()
        if len(window) >= self.max_requests:
            wait_time = int(self.window_seconds - (now - window[0]))
            return GraphState(
                blocked=True,
                reason=f"Rate limit exceeded. Wait {wait_time}s"
            )
        window.append(now)
        return GraphState(blocked=False)
