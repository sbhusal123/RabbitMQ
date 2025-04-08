# Pika API Reference

Reference to Pika Library API.

- Message is never pushed to queue instead to a exchange.
- Queue are bounded to exchange. Many queues can be bounded to a single queue.
- While publishing a message, we define exchange and routing key.
- Routing key is what defines 

## 1. API Reference

```python
import pika
```

- **Connect to rabbit server:** ``connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))``

- **Get channel:** ``channel = connection.channel()``

- **Declaring a queue:** ``channel.queue_declare(queue='<queue_name>')``

- **Declaring an exchange:** ``channel.exchange_declare(exchange='<exchange_name>', exchange_type='<fanout/topic/direct>')``
    - **Direct Exchange** pushes item to the queue whose 

- **Binding queue to exchange:** ``channel.queue_bind(exchange='<exchange_name>', queue='<queue_name>', routing_key='<routing_key>')``

- **Publishing An Item:** ``channel.basic_publish(exchange='<exchange_name>', routing_key='<routing_key>', body='<data>')``

- **Consuming From A Queue:** ``channel.basic_consume(queue=queue_name,on_message_callback=<callback_func>)``

    Callback Function Definition Looks Like Below

    ```python
        def on_request(ch, method, props, body):
            # item pushed
            item = body.decode()
            
            # acknowledge delivered
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=on_request
        )
    ```


## 2. Working Of Topic Exchange

```python
import pika

# .....

# Declare a topic exchange
channel.exchange_declare(exchange='logs_topic', exchange_type='topic')

# Declare queues
channel.queue_declare(queue='queue_all')
channel.queue_declare(queue='queue_errors')
channel.queue_declare(queue='queue_kernel')

# Bind queues to exchange with topic patterns
channel.queue_bind(exchange='logs_topic', queue='queue_all', routing_key='#')               # All messages
channel.queue_bind(exchange='logs_topic', queue='queue_errors', routing_key='*.error')      # Matches "any.error"
channel.queue_bind(exchange='logs_topic', queue='queue_kernel', routing_key='kernel.*')     # Matches "kernel.info", "kernel.error"
```

```sh
Exchange: logs_topic (type: topic)

Bindings:
- queue_all       ← binding_key: ←  #
- queue_errors    ← binding_key: ←  *.error
- queue_kernel    ← binding_key: ←  kernel.*
```

**Let's push item:**

```python

# Routing Pattern         =>>>      #         *.error
# Message pushed to queue =>>>  queue_all, queue_error
channel.basic_publish(
    exchange='logs_topic',
    routing_key='app.error',
    body="<Message>"
)

# Routing Pattern         =>>>      #      
# Message pushed to queue =>>>  queue_all
channel.basic_publish(
    exchange='logs_topic',
    routing_key='hello',
    body="<Message>"
)
```


- First message with routing key ``app.error`` is enqued to:
    - ``queue_all`` => routing key wildcard ``#``.
    - ``queue_errors`` => routing key wildcard ``*.error``.

- Second message with routing key ``hello`` is enqued to:
    - ``queue_all`` => routing key wildcard ``#``.

## 3. Working Of Direct Exchange:

```python
import pika

# .....

# Declare a topic exchange
channel.exchange_declare(exchange='my_exchange', exchange_type='direct')

# Declare queues
channel.queue_declare(queue='queue_1')
channel.queue_declare(queue='queue_2')
channel.queue_declare(queue='queue_3')

# Bind queues to exchange with topic patterns
channel.queue_bind(exchange='my_exchange', queue='queue_1', routing_key='sales') -> 
channel.queue_bind(exchange='my_exchange', queue='queue_2', routing_key='order')
channel.queue_bind(exchange='my_exchange', queue='queue_3', routing_key='inventory')
```

```sh
Exchange: my_exchange (type: direct)

Bindings:
- queue_1  ← binding_key: ←  sales
- queue_2  ← binding_key: ←  order
- queue_3  ← binding_key: ←  inventory
```

**Let's push item:**

```python

# Routing Key             =>>>  sales
# Message pushed to queue =>>>  queue_1
channel.basic_publish(
    exchange='my_exchange',
    routing_key='sales',
    body="Sales xxxxx"
)

# Routing Key             =>>>  order
# Message pushed to queue =>>>  queue_2
channel.basic_publish(
    exchange='my_exchange',
    routing_key='order',
    body="Order xxxx"
)
```


- First message with routing key ``sales`` is enqued to:
    - ``queue_1`` => routing key wildcard ``sales``.

- Second message with routing key ``order`` is enqued to:
    - ``queue_2`` => routing key wildcard ``order``.


## 