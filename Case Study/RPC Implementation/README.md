# RPC Server And Client:


## 1. Server Side:

- Is listening / consuming for an item in a rpc queue.

- Computes a result and

- Publishes result back to a callback queue client defined.


```python
class BaseRPCServer:

    def __init__(self, queue_name):
        connection = pika.BlockingConnection(
            parameters=pika.ConnectionParameters(host='localhost')
        )
        self.channel = connection.channel()
        self.queue_name = queue_name

    
    def handle_message(self, body):
        raise NotImplementedError("handle_message(self, body) not implemented.")

    

    def on_request(self, ch, method, props, body):
        response = self.handle_message(body)
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(
                correlation_id =props.correlation_id
            ),
            body=str(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        self.channel.queue_declare(queue=self.queue_name)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.on_request,
            auto_ack=False
        )
        process = multiprocessing.current_process()
        print(f"[x] [PID={process.pid}] [Name={process.name}] Awaiting RPC requests on queue: {self.queue_name}")
        self.channel.start_consuming()
```

Now Let's create a RPC Server out of it, code below has:
- 5 threads working as a worker / consumer for a queue.

```python
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

```


## 2. Client Side:

- Client requests a rpc call by passing an item to a predefined queue (rpc queue). 

- It also maintains its own internal queue, whose it is subscribed to consume an item from.

- While publishing a message we define a correlation id and callback queue.

- Since result of every rpc call is passed to callback queue defined by client. Client also subscribes to items from callback queue.


```python
import pika
import uuid

import multiprocessing


class BaseRPCClient:

    def __init__(self, queue_name):
        self.connection = pika.BlockingConnection(
            parameters=pika.ConnectionParameters(host='localhost')
        )
        self.channel = self.connection.channel()
        self.queue_name = queue_name

        self.response = None
        self.correlation_id = None

    def create_callback_queue_and_consume(self):
        """Creates callback queue and listen for rpc response"""
        # callback queue to which rpc server enques data to
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue


        # consume items from callback queue, handled by rpc_response
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )


    def on_response(self, ch, method, props, data):
        """If correlation id matches for request and response"""
        if props.correlation_id == self.correlation_id:
            self.response = data


    def call(self, data):
        """Creates callback queue and listens on it, publishes item to rpc queue """
        self.create_callback_queue_and_consume()
        self.correlation_id = str(uuid.uuid4())
        self.response = None
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            properties=pika.BasicProperties(
                correlation_id=self.correlation_id, # correlation id for request response tracking purpose
                reply_to=self.callback_queue # queue to which result to be enqued to, specified by client during message publish
            ),
            body=str(data)
        )

        # wait untill the server responds on a callback queue
        while self.response is None:
            self.connection.process_data_events(time_limit=None)
        return int(self.response)
```

- ``self.connection.process_data_events(time_limit=None)`` This method is part of the pika connection object and is used to process any data events or I/O activity that have occurred on the connection.

Let's create a RPC client for a summing up server.
- In code below we simulate 10 request at once with threads.

```python
import threading

from constants import SUM_RPC_QUEUE

from utils import BaseRPCClient


class SumRpcClient(BaseRPCClient):
    """RPC Client for Summing two numbers"""
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
        # simulating 10 request at once
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

```
