# Working Queue

- Avoid doing a resource-intensive task
immediately and having to wait for it to complete. 
Instead we schedule the task to be done later

- Useful in web applications where it's impossible to handle 
a complex task during a short HTTP request window

- Demo Example includes  an example to distribute a task to the multiple workers and
making message, channel persistent.

## 1. What if we have multiple worker subscribed to the publisher?(Round Robin Dispatch)
- Dispatched in **round robin fashion** so that task is uniformly 
distributed to worker nodes.

**Publishing message**
```bash
# task we passed as message 
python new_task.py task1.
python new_task.py task2..
```

**Task received by workers**
```bash
# worker 1
[X] Received task1.
[Done]
```

```bash
# worker 2
[X] Received task2..
[Done]
```

## 2. Message Acknowledgment
- What if a worker node dies completing task partially.
- To make sure message is never lost, RabbitMQ suports **message acknowledgment.**

    ### 2.1. What if consumer(worker) dies?
    - Channel, Communication closed without sending ack.
    - RabbitMQ will understand that a message wasn't processed fully and will re-queue it.
    - If other consumers(workers) are online, then will be delivered to 
    another consumer.
    
    ### 2.2 How?
    - Manual acknowledgment turned on by default. 
    i.e ``channel.basic_consume(auto_ack=False)``.
    - Make sure **auto_ack is set to False** in channel.basic_consume(..)
    - Then acknowledge the message after completing task in callback.
    ``h.basic_ack(delivery_tag = method.delivery_tag)``
    
    ```python
      def callback(ch, method, properties, body):
          """Action to perform on receiving a message"""
          #  what to do with message?????
          ch.basic_ack(delivery_tag = method.delivery_tag)
      
      channel.basic_consume(
          queue="<queue_name>",
          on_message_callback=callback,
          auto_ack=False  # manual ack turned on
      )
    ```

## 3. Message Durability:
- What if RabbitMQ server stops?
- If RabbitMQ quits or crashes,  it will forget the queues and messages 
unless we tell it not to.
- To ensure durability: **mark queue and messages as durable**

    ### 3.1. How?
    - Make queue persistent while declaring it.
    ``channel.queue_declare(queue='<queue_name>', durable=True)``
    - Make messages on a queue persistent while publishing it.
    
    ```python
        channel.basic_publish(exchange='',
                          routing_key="<queue_name>",
                          body=message,
                          properties=pika.BasicProperties(
                          delivery_mode = 2, # make message persistent
         ))
    ```
    
    > Note:  there is still a short time window when RabbitMQ 
    has accepted a message and hasn't saved it yet, it may be 
    just saved to cache and not really written to the disk.
    If stronger persistence is required then use [publisher confirms](https://www.rabbitmq.com/confirms.html).
   
## 3. Fair Dispatch(Even tasks are time consuming and odd tasks are lightweight)
- Thought we guaranteed that tasks are assigned to worker in 
a round robin fashion. But in such case one worker will be constantly busy and other
one will do hardly any work.

    ### 3.1. How?
    - Use ``channel.basic_qos(prefetch_count=1)``
    - This tell RabbitMQ not to give more than one message to a worker at a time.
    - Don't dispatch a new message to a worker until it has processed and acknowledged the previous one.
    
    > Note: A situation might occur where both even and odd task are time consuming. And our queue might fill up. 
    This situation can be prevented **Running multiple RabbitMQ workers**.
     
    
    

## 4. Handy Commands:
- **Queues and no of messages:** ``sudo rabbitmqctl list_queues``
- **Un-acknowledged mesages:** ``sudo rabbitmqctl list_queues name messages_ready messages_unacknowledged
``
- **Purge/delete messages from queue:** ``rabbitmqctl purge_queue <queue_name>``
- **Delete queue:** ``rabbitmqctl delete_queue <queue_name>``

