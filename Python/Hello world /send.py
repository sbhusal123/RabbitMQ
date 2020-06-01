"""
A producer to send the message to the RabbitMQ server.
"""

import pika


"""Create a connection to the RabbitMQ server and channel"""
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',port=5672))
channel = connection.channel()


"""Create a queue named 'hello'. If no queue name is defined, message may drop."""
channel.queue_declare(queue='hello')


"""
- Now ready to send message
- Point to Note:
    RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange
    exchange='' uses default exchange in AMQP
"""
channel.basic_publish(
    exchange='',  # use default exchange
    routing_key='hello',  # queue name to which message needs to be enqued
    body='Hello world'  # message content
)


"""
Make sure network buffer is cleared. i.e make sure to close the connection 
"""
connection.close()


"""
Note:
    List the queues available: sudo rabbitmqctl list_queues
"""