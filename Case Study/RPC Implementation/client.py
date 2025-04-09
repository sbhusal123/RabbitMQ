import threading

from constants import SUM_RPC_QUEUE

from utils import BaseRPCClient


class SumRpcClient(BaseRPCClient):

    def __init__(self):
        super().__init__(queue_name=SUM_RPC_QUEUE)


import random

def call_rpc(x, y):
    thread = threading.current_thread()
    print(f"[x] [TID={thread.native_id}] sum({x}, {y})")
    sum_rpc = SumRpcClient()
    res = sum_rpc.call(f"{x},{y}")
    print(f"[x] [TID={thread.native_id}] sum({x}, {y})={res}")
    return res

if __name__ == "__main__":
    threads = []
    for i in range(10):
        x, y = random.randint(0, 100), random.randint(0, 100)
        thread = threading.Thread(
            target=call_rpc,
            kwargs={'x': x, 'y': y}
        )

        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
