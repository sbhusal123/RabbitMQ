import multiprocessing

import utils
import constants


class FibonacciServer(utils.BaseServer):
    def __init__(self):
        super().__init__(constants.FIBONACI_QUEUE)

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

        # replies back to the client in a queue to which client is listening
        # Note that, reply_to is a property of the message that the client sends
        # This property defines where the server should send the response
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            body=str(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

class AdditionServer(utils.BaseRpcServer):
    def __init__(self):
        super().__init__(constants.ADDITION_QUEUE)

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
        
        # replies back to the client in a queue to which client is listening
        # Note that, reply_to is a property of the message that the client sends
        # This property defines where the server should send the response
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            body=str(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

def run_fibonacci_server():
    server = FibonacciServer()
    server.start()

def run_addition_server():
    server = AdditionServer()
    server.start()

if __name__ == "__main__":
    # Create a process pool to run both RPC servers in parallel
    process_pool = []

    print("Staritng Worker servers...")

    for i in range(2):
        fibonaci_server_process = multiprocessing.Process(target=run_fibonacci_server, name=f"FibonacciServer-{i}")
        addition_server_process = multiprocessing.Process(target=run_addition_server, name=f"AdditionServer-{i}")
        process_pool.append(fibonaci_server_process)
        process_pool.append(addition_server_process)

    for process in process_pool:
        process.start()

    for process in process_pool:
        process.join()
