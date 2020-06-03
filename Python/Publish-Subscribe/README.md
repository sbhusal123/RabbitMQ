# Publish/Subscribe
- Deliver a message to multiple consumer.
- Distributed Publisher Subscriber Pattern.
- Demo Example: consist of two programs -- the first will emit log messages and 
the second will receive and print them using fanout exchange.

## 1. Exchange
- Producer never sends any messages directly to a queue, can only send messages to an exchange.
- Exchange on one side receives messages from producers and the other side it pushes them to queues
- It **must know exactly what to with received messages** from producers and the other side it pushes them to queues.
(**Should it be appended to a particular queue?, Should it be appended to many queues?, or discard**)

![Exchange in RabbitMQ](https://www.javainuse.com/rabbit-min.JPG)

- **Exchange Types:** direct, topic, headers and fanout.

    ### 1.1. Direct Exchange
    - Routes messages with a routing key equal to the routing key declared by the binding queue
    
    ![Direct Exchange](../../Images/direct_exchange.png)
    
    ### 1.2. Fanout Exchange
    - Routes messages to all bound queues indiscriminately.
    - If routing key available, ignored.
    
    ![Fanout Exchange](../../Images/fanout_exchange.png)
    
    ### 1.3. Topic Exchange
    - Routes messages to queues whose routing key matches all, or a portion of a routing key.
    
    ![Topic Exchange](../../Images/topic_exchange.png)

    ### 1.4. How?
    - **Exchange Type Declaration:** ``channel.exchange_declare(exchange='<name>',exchange_type='<type>')``
    - **Publish message to exchange** ``channel.basic_publish(exchange='<name>',routing_key='<key>',body=message)``

## 2. Random Queue generation
- Can be declared passing **empty string to queue in queue_declare**: ``my_queue = channel.queue_declare(queue='')``
- Get the queue name : ``my_queue.method.name``
    

## 3. Using Temporary Queue
- Fresh queue is created when connected to RabbitMQ.
- Once the consumer connection is closed, the queue is deleted.
- Declaration using **exclusive=True in queue_declare method**: ``channel.queue_declare(queue='<name>', exclusive=True)``

## 4. Binding
- Relationship between exchange and a queue is called a binding.
- Useful to enqueue a message received by exchange to the queue. 
- Messages will be lost if no queue is bound to the exchange.
- Bind **using queue_bind method of channel object**: ``channel.queue_bind(exchange='<ex_name>',queue=<q_name>)``

## 5.Handy Commands
- **List Exchange:** ``rabbitmqctl list_exchanges``
- **List Bindings:** ``rabbitmqctl list_bindings``
