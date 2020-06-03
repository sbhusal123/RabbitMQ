import pika
import sys

"""
Summary:
    - Create connection and channel.
    - Declare a fanout exchange.
    - Publish message to the exchange.
    - Close connection.
    
Note that we haven't created a queue here, this will be done by consumer by binding the random queue
to the exchange name we declared.
"""

"""Take message from the console"""
message = ' '.join(sys.argv[1:]) or "Hello World"


"""Create a connection to RabbitMQ server and establish a channel based connection"""
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", port=5672))
channel = connection.channel()

"""
- Create a fanout type exchange to enqueue message into our queue.
- Fanout Exchange routes message to all bound indiscriminately.
- Name of exchange is logs
"""
channel.exchange_declare(
    exchange='logs',
    exchange_type='fanout'
)

"""
- Pass the message to the logs exchange
- Routing key set to '' as we don't care routing-key in fanout exchange. 
"""
channel.basic_publish(
    exchange="logs",
    routing_key='',
    body=message
)

print(" [X] Sent %r" % message)

connection.close()
