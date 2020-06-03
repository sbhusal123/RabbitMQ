# Routing 
- Route or publish the message from the exchange to specific queue
- Example : Log severity level to the log receiver using direct binding with custom routing based on routing key.

## 1. Direct Exchange:
- Routes messages with a routing key equal to the routing key declared by the binding queue.

![Direct Exchange](../../Images/direct_exchange.png)

## 2. Basic Flow
**Producer**
```text
1. Take message from the console
2. Establish connection to server and create channel
3. Declare exchange with name and type
4. Publish message to exchange with routing ket
5. Close the connection
```

**Consumer**
```text
1. Take input from console.
2. Create connection to server.
3. Create/Get the exchange type with name.
4. Create a random temporary queue and get it's name.
5. Bind the queue to the exchange with routing_key.
6. Define callback method.
7. Consume with basic_consume passing callback, queue_name and auto_ack.
8. Start consuming.
```


## 3. Syntax
- **Bind to queue with routing_key:** ``channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key='black')``
- **Publish with routing_key:** ``channel.basic_publish(exchange='<name>',routing_key='<key>', body=message)``


