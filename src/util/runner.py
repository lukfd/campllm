from concurrent.futures import ThreadPoolExecutor, as_completed
import os


class Runner:
    def __init__(self, max_workers=None):
        default_workers = min(32, (os.cpu_count() or 4) * 2)
        self.max_workers = max_workers or default_workers

    def run(self, func, *args, **kwargs):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future = executor.submit(func, *args, **kwargs)
            return future.result()

    def run_many(self, func, items):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(func, item) for item in items]
            for future in as_completed(futures):
                yield future.result()
