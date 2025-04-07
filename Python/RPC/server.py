import multiprocessing
import pika
import multiprocessing

import utils
import constants


class FibonacciRpcServer(utils.BaseRpcServer):
    def __init__(self):
        super().__init__(constants.FIBONACI_RPC_QUEUE)

    def fib(self, n):
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            return self.fib(n - 1) + self.fib(n - 2)

    def on_request(self, ch, method, props, body):
        n = int(body)
        print(f" [.] fib({n})")
        response = self.fib(n)
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(
                correlation_id=props.correlation_id,
                reply_to=props.reply_to,
            ),
            body=str(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

class AdditionRpcServer(utils.BaseRpcServer):
    def __init__(self):
        super().__init__('rpc_addition_queue')

    def add(self, x, y):
        import time
        time.sleep(5)
        return x + y

    def on_request(self, ch, method, props, body):
        x, y = map(int, body.decode().split(","))

        process_name = multiprocessing.current_process().name
        process_id = multiprocessing.current_process().pid

        response = self.add(x, y)

        print(f" [X] (Process: {process_name}) (PID: {process_id}) => add({x}, {y}) => {response}")
        
        # publish and acknowledge
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=str(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

def run_fibonacci_server():
    server = FibonacciRpcServer()
    server.start()

def run_addition_server():
    server = AdditionRpcServer()
    server.start()

if __name__ == "__main__":
    # Create a process pool to run both RPC servers in parallel
    process_pool = []

    print("Staritng RPC servers...")

    for i in range(2):
        fibonaci_server_process = multiprocessing.Process(target=run_fibonacci_server, name=f"FibonacciServer-{i}")
        addition_server_process = multiprocessing.Process(target=run_addition_server, name=f"AdditionServer-{i}")
        process_pool.append(fibonaci_server_process)
        process_pool.append(addition_server_process)

    for process in process_pool:
        process.start()

    for process in process_pool:
        process.join()
