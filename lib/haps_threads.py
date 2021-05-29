from concurrent.futures import ThreadPoolExecutor

def run_thread(func_name, workers=2):
    executor = ThreadPoolExecutor(max_workers=workers)
    executor.submit(func_name)


