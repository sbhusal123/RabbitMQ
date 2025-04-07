# Rabit MQ

- Message broker server(Message-oriented middleware)

- Supports sending and receiving messages between distributed systems.



## 1. Procuder, Consumer, Queue

- **Producer** is a user application that sends messages.

- **Queue** is a buffer that stores messages.

- **Consumer** is a user application that receives messages or is listening on queue.

- **Exchange:** receives messages from producers and the other side it pushes them to queues.

- **Channel:** Acts as a multiplexer to perform multiple logical connection to the broker, can be thought as "lightweight connections that share a single TCP connection". [Read More...](https://www.rabbitmq.com/channels.html#basics)

- **Routing Key:** Routing Key and Exchange Type Together Defines which queue from the exchange will message be delivered to.


**Produce**
- Message is pushed to exchange with a routing key.
- Routing Key with Exchange type defines which queue to push item to.

**Consumer:**
- Is not concerned with exchange.
- Is more of concerned directly with queue. So, whenever a message is recieved on queue, performs action.


## 2. Messaging Model:

- Producer never sends any messages directly to a queue. Actually, quite often the producer doesn't even know if a message will be delivered to any queue at all.

- Producer can only send messages to an **exchange**.

-  The exchange must know exactly what to do with a message it receives. Should it be appended to a particular queue? Should it be appended to many queues? Or should it get discarded. The rules for that are defined by the exchange type.

- **Exchange Type:** direct, topic, headers and fanout

    ![](https://www.cloudamqp.com/img/blog/exchanges-topic-fanout-direct.png)

## 3. Setup:
- To run the codes in the files you need RabbitMQ server installed or you can.
- Spin up RabbitMQ Docker Container: ``docker run --name rabbitmq -p 5672:5672 rabbitmq``

## 4. Contents
- [Publish/Subscribe](./Python/Publish-Subscribe)
- [Messages Routing](./Python/Routing)
- [Topic Based Exchange](./Python/Topic)
- [Message Durability and Acknowledgment, Fair Dispatch of Workload](./Python/Working%20Queue)
- [RPC Clients And Server and Few Summary](./Python/RPC)
