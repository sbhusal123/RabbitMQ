# Callback Queue Usage Case Study

Here, we implement a callback queue 

**Queue management commands:**
- **📄 List all queues:** ``sudo rabbitmqctl list_queues``
- **🧾 List queues with more details:** ``sudo rabbitmqctl list_queues name messages consumers``
- **🧹 Purge a queue (delete all messages):** ``sudo rabbitmqctl purge_queue myqueue``
- **❌ Delete a queue:** ``sudo rabbitmqctl delete_queue myqueue``

**🔁 Exchange & Binding Management:**
- **📃 List all exchanges:** ``sudo rabbitmqctl list_exchanges``
- **List exchange bindings:**  ``sudo rabbitmqctl list_bindings``


## a. Pushing data to queue (Publishing Item)

Since, we dont push / publish directly to queue, instead we basic_publish to exchange with routing_key.

```python
    # if exchange name is empty, then the message is pushed to the queue with exact name of routing key.
    ch.basic_publish(
        exchange='',
        routing_key="<routing_key>",
        properties=pika.BasicProperties(
            # reply back to queue
            reply_to="<reply_to>"
        ),
        body="<message>"
    )
```

In above case, message is dlrectly pushed to queue with same as routing_name (**since its a Direct Exchange**). Let's see few other cases.

Note, that the exchange_type and routing key is what defines in which queue the message is going to be routed to.

## b. Consuming an Item:

```python

def on_request(ch, method, properties, body):
    print(f" [x] Received: {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # if responding back to queue specified by client
    ch.basic_publish(
        exchange='', # if exchange is empty then item pushed to queue with name routing_key
        routing_key=props.reply_to, # client specifies which queue to reply to.
        body=str(response)
    )

channel.basic_consume(
    queue=queue_name,
    on_message_callback=on_request
)

# client must basic_publish with reply to params
channel.basic_publish(
    exchange='',
    # queue name of rpc queue
    routing_key=ADDITION_QUEUE,
    properties=pika.BasicProperties(
        # queue name where we will listen for response
        reply_to=ADDITION_CALLBACK_QUEUE
    ),
    body=f"{x},{y}"
)
```


## 1. Base Class for Our Worker

Base class implementation for Server looks like below:

```python
import pika
import multiprocessing

class BaseServer:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()


    def start(self):
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.on_request
        )
        process_nam = multiprocessing.process.current_process().name
        process_id = multiprocessing.process.current_process().pid
        print(f" [x] Server {process_nam} (PID: {process_id}) started on queue '{self.queue_name}'")
        self.channel.start_consuming()
```

## 2. Fibonacci Worker Server implementing Base Server

Now, we can use a ``BaseServer`` class to implement our custom Worker Server.

```python
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
```

Note that:

```python
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
```


**1. When message is recieved, callback function recieves following params:**

- ``ch:`` The channel object through which the message was received.

- ``method:`` Contains delivery information like delivery_tag.

- ``properties:`` The properties of the message — includes things like **reply_to 
(the callback queue)** and **correlation_id (used to match request with response)**.

- ``body:`` The actual message payload **(as bytes => decode it)**, which in this case is expected to contain two integers separated by a comma (like "3,5").


**2. basic_publish Parameters: => Putting item to callback queue for client**

- ``exchange`` =>  The exchange to publish to, ``''`` represents default exchange.

- ``routing_key`` => The name of the queue (if using the default exchange), or a routing key that the exchange uses to route the message.

- ``body`` => Actual message payload.

- ``properties`` => Allows you to attach metadata to your RabbitMQ message. This metadata is useful for things like message tracking, reply routing, content type, and more.
    - ``reply_to`` => Tells the consumer where to send the response (queue name).

Note that, when 


**3. acknowledging with basic_ack**
- “I got it, processed it, no need to requeue.”
- If you don’t call basic_ack, the message stays "unacknowledged" and could be redelivered.



## 3. Runnig With Multiple Processes:


If we have wan to create a multiple consumers listening on different process then we can use multi processing:

```python


def run_fibonacci_server():
    server = FibonacciServer()
    server.start()


if __name__ == "__main__":
    # Create a process pool to run both RPC servers in parallel
    process_pool = []

    print("Staritng Worker servers...")

    for i in range(2):
        fibonaci_server_process = multiprocessing.Process(target=run_fibonacci_server, name=f"FibonacciServer-{i}")
        process_pool.append(fibonaci_server_process)

    for process in process_pool:
        process.start()

    for process in process_pool:
        process.join()
```

## 4. Client Implementation:

Basically, here a client will listen on a callback queue specified when making a RPC call with ``basic_publish``

Here, we are specifying from a client script, in which queue should the rpc server respond back after finishing computation.

```python
import pika

from constants import ADDITION_QUEUE, ADDITION_CALLBACK_QUEUE


class AddClient:
    def __init__(self, host='localhost'):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host)
        )
        self.channel = self.connection.channel()

    def add(self, x, y):
        """Send a request to the RPC server to add x and y."""
        self.channel.basic_publish(
            exchange='',
            routing_key=ADDITION_QUEUE,
            properties=pika.BasicProperties(
                reply_to=ADDITION_CALLBACK_QUEUE
            ),
            body=f"{x},{y}"
        )

if __name__ == "__main__":
    x = input("Enter first number")
    y = input("Enter second number")
    client  = AddClient()
    print(f" [x] Requesting {x} + {y}")
    response = client.add(x, y)

```

Here, we are sending the values of ``x, y`` to the worker listening on queue ``ADDITION_QUEUE`` and we expect a reply on ``ADDITION_CALLBACK_QUEUE`` queue.

## 5. Client Callback Worker

We can spin up a worker that basically listens on q callback queue after rpc server processes our data.

```python
import constants
import utils

import multiprocessing

class CallBackWorker(utils.BaseServer):
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
            args=(constants.FIBONACI_CALLBACK_QUEUE,),
            name=f"FibonacciCallbackWorker-{i}"
        )

        addition_callback_worker = multiprocessing.Process(
            target=run_callback_worker,
            args=(constants.ADDITION_CALLBACK_QUEUE,),
            name=f"AdditionCallbackWorker-{i}"
        )

        process.append(fibonaci_callback_worker)
        process.append(addition_callback_worker)

    for p in process:
        p.start()
    
    for p in process:
        p.join()

```