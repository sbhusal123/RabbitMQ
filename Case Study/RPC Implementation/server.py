import constants

import utils

import threading
import time

class SumRpcServer(utils.BaseRPCServer):

    def __init__(self):
        super().__init__(
            queue_name=constants.SUM_RPC_QUEUE
        )

    
    def handle_message(self, body):
        thread = threading.current_thread()
        print(f"[X] [Queue: {self.queue_name}] [TID: {thread.native_id}] [Name={thread.name}] Recieved = {body.decode()}")
        time.sleep(2)
        a, b = body.decode().split(',')
        result = int(a) + int(b)
        print(f"[X] [Queue: {self.queue_name}] [TID: {thread.native_id}] [Name={thread.name}] [Data={body.decode()}] [Result = {result}]")
        return result


if __name__ == "__main__":
    threads = []

    for i in range(0, 5):
        srpc = SumRpcServer()
        rpc_server_proc = threading.Thread(
            target=srpc.start,
            name=f'SumRpcServer-{i}'
        )
        threads.append(rpc_server_proc)

    for process in threads:
        process.start()

    for process in threads:
        process.join()
