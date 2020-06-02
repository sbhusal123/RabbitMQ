import pika
import sys

"""Take message from the console. Last argument"""
message = ' '.join(sys.argv[1:]) or 'Hello World'


"""Initialize the connection to the RabbitMQ server and channel"""
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", port=5672))
channel = connection.channel()


"""
Create a queue named task to which worker subscribes
Mark it as durable so that even if task is not completed and server dies.
Then it will be passed after the RabbitMQ server survives failure.
"""
channel.queue_declare(
    'task',
    durable=True  # make messages on this queue persistence
)


"""
Publish a message to the channel and make sure it is persistence.
i.e until the message is not acknowledge by the consumer and if consumer dies
then it's still not de-queued from the queue. 
"""
channel.basic_publish(
    exchange='',  # use default exchange
    routing_key='task',  # queue name to which message needs to be enqued
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=2,  # make Message persistent
    )
)

print(f"[X] Sent %r" % message)