# Implementing Basic RPC Call

Here, we implement a RPC call with callback queue. Basically client initiating a RPC call will listen on a callback queue to handle response.

**References:**
- [Implementing RPC Server: RabbitMQ Docs](https://www.rabbitmq.com/tutorials/tutorial-six-python)

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

In above case, message is dlrectly pushed to queue with same as routing_name. Let's see few other cases.

```python
# ---------------------------------------------------------------------------------------------------
Exchange Type: direct
Routing Key: 'info'
Binding Key: 'info'
Match: ✅ YES

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')
channel.queue_bind(exchange='direct_logs', queue='info_queue', routing_key='info')
channel.basic_publish(exchange='direct_logs', routing_key='info', body='Log: info')
# Message with routing_key='info' is delivered to info_queue.
# ---------------------------------------------------------------------------------------------------
Routing Key: 'user.signup'
Binding Key: 'user.*'
Match: ✅ YES

channel.exchange_declare(exchange='topic_logs', exchange_type='topic')
channel.queue_bind(exchange='topic_logs', queue='signup_queue', routing_key='user.*')

channel.basic_publish(exchange='topic_logs', routing_key='user.signup', body='Signup Event')
# Message is routed based on pattern in binding key.
# ---------------------------------------------------------------------------------------------------
```

Note, that the exchange_type and routing key is what defines in which queue the message is going to be routed to.

## b. Consuming an Item:

```python

def callback(ch, method, properties, body):
    print(f" [x] Received: {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # if responding back to queue specified by client
    ch.basic_publish(
        exchange='', # if exchange is empty then item pushed to queue with name routing_key
        routing_key=props.reply_to, # client specifies which queue to reply to.
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
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
    routing_key=ADDITION_RPC_QUEUE,
    properties=pika.BasicProperties(
        # queue name where we will listen for response
        reply_to=ADDITION_CALLBACK_RPC_QUEUE
    ),
    body=f"{x},{y}"
)
```


## 1. Base Class for Our Worker

Base class implementation for Server looks like below:

```python
import pika
import multiprocessing

class BaseRpcServer:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        self.channel.basic_qos(prefetch_count=1)

    def on_request(self, ch, method, props, body):
        # Override this method in subclasses
        pass


    def start(self):
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.on_request
        )
        process_nam = multiprocessing.process.current_process().name
        process_id = multiprocessing.process.current_process().pid
        print(f" [x] RPC server {process_nam} (PID: {process_id}) started on queue '{self.queue_name}'")
        self.channel.start_consuming()

```

## 2. Fibonacci RPC Server implementing Base RPC Server

Now, we can use a ``BaseRpcServer`` class to implement our custom RPC Server.

```python
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
```

Note that:

```python
def on_request(self, ch, method, props, body):
    n = int(body)

    # calculate a response
    response = self.fib(n)

    # publish back the response to the callback queue client listens on
    # here we havent declared a exchange, so the message will be routed directly to the queue defined with routing_key.
    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(
            correlation_id=props.correlation_id
        ),
        body=str(response)
    )

    # acknowledge that message has been recieved
    ch.basic_ack(delivery_tag=method.delivery_tag)
```


**1. When message is recieved, callback function recieves following params:**
- ``ch:`` The channel object through which the message was received.
- ``method:`` Contains delivery information like delivery_tag.
- ``properties:`` The properties of the message — includes things like **reply_to (the callback queue)** and **correlation_id (used to match request with response)**.
- ``body:`` The actual message payload **(as bytes => decode it)**, which in this case is expected to contain two integers separated by a comma (like "3,5").


**2. basic_publish Parameters: => Putting item to callback queue for client**
- ``exchange`` =>  The exchange to publish to, ``''`` represents default exchange.

- ``routing_key`` => The name of the queue (if using the default exchange), or a routing key that the exchange uses to route the message.

- ``body`` => Actual message payload.

- ``properties`` => Allows you to attach metadata to your RabbitMQ message. This metadata is useful for things like message tracking, reply routing, content type, and more.
    - ``correlation_id`` => Used to track request-response pairs (very useful for RPC).
    - ``reply_to`` => Tells the consumer where to send the response (queue name).

Note that, when 


**3. acknowledging with basic_ack**
- “I got it, processed it, no need to requeue.”
- If you don’t call basic_ack, the message stays "unacknowledged" and could be redelivered.



## 3. Runnig With Multiple Processes:


If we have wan to create a multiple consumers listening on different process then we can use multi processing:

```python


def run_fibonacci_server():
    """Run RPC server"""
    server = FibonacciRpcServer()
    server.start()


if __name__ == "__main__":
    # Create a process pool to run both RPC servers in parallel
    process_pool = []

    print("Staritng RPC servers...")

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

from constants import ADDITION_CALLBACK_RPC_QUEUE, ADDITION_RPC_QUEUE


class AddRpcClient:
    def __init__(self, host='localhost'):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host)
        )
        self.channel = self.connection.channel()

        # Create a callback queue
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

    def on_response(self, ch, method, props, body):
        """Callback to capture the response."""
        if self.corr_id == props.correlation_id:
            self.response = body

    def add(self, x, y):
        """Send a request to the RPC server to add x and y."""
        self.channel.basic_publish(
            exchange='',
            # queue name of rpc queue
            routing_key=ADDITION_RPC_QUEUE,
            properties=pika.BasicProperties(
                # queue name where we will listen for response
                reply_to=ADDITION_CALLBACK_RPC_QUEUE
            ),
            body=f"{x},{y}"
        )
    
client  = AddRpcClient()
print(" [x] Requesting 5 + 3")
response = client.add(5, 3)
```

Here, we are sending the values of ``x, y`` to the worker listening on queue ``ADDITION_RPC_QUEUE`` and we expect a reply on ``ADDITION_CALLBACK_RPC_QUEUE`` queue.

## 5. Client Callback Worker

We can spin up a worker that basically listens on q callback queue after rpc server processes our data.

```python
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
```