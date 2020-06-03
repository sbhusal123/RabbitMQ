import pika
import sys

"""Take message from the console"""
message = ' '.join(sys.argv[1:]) or "Hello World"


"""Create a connection to RabbitMQ server and establish a channel based connection"""
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", port=5672))
channel = connection.channel()

"""Create a exchange to enqueue message into message queue"""
channel.exchange_declare(
    exchange='logs',
    exchange_type='fanout'
)

"""Pass the message to the exchange"""
channel.basic_publish(
    exchange="logs",
    routing_key='',
    body='message'
)

print(" [X] Sent %r" % message)

connection.close()
