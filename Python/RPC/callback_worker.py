import constants
import utils

import multiprocessing

class CallBackWorker(utils.BaseRpcServer):
    def __init__(self, queue_name):
        super().__init__(queue_name=queue_name)

    def on_request(self, ch, method, props, body):
        item = body.decode()
        process_nam = multiprocessing.process.current_process().name
        process_id = multiprocessing.process.current_process().pid
        print(f" [x] {self.queue_name} worker with (Process: {process_nam}) (PID: {process_id}) recieved item '{item}'")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def start(self):
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.on_request
        )
        process_nam = multiprocessing.process.current_process().name
        process_id = multiprocessing.process.current_process().pid
        print(f" [x] {self.queue_name} worker (Process: {process_nam}) (PID: {process_id}) started on queue '{self.queue_name}'")
        self.channel.start_consuming()

def run_callback_worker(queue_name):
    worker = CallBackWorker(queue_name=queue_name)
    worker.start()



if __name__ == "__main__":
    process = []
    for i in range(2):
        fibonaci_callback_worker = multiprocessing.Process(
            target=run_callback_worker,
            args=(constants.FIBONACI_CALLBACK_RPC_QUEUE,),
            name=f"FibonacciCallbackWorker-{i}"
        )

        addition_callback_worker = multiprocessing.Process(
            target=run_callback_worker,
            args=(constants.ADDITION_CALLBACK_RPC_QUEUE,),
            name=f"FibonacciCallbackWorker-{i}"
        )

        process.append(fibonaci_callback_worker)
        process.append(addition_callback_worker)

    for p in process:
        p.start()
    
    for p in process:
        p.join()
    

