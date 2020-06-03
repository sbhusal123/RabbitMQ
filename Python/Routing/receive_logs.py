import pika
import sys


"""
Summary:
- Take input from console.
- Create connection to server.
- Create/Get the exchange type with name.
- Create a random temporary queue and get it's name.
- Bind the queue to the exchange.
- Define callback method.
- Consume with basic_consume passing callback, queue_name and auto_ack.
- Start consuming.
"""

"""
Input format: python file.py [severities]
Example: python file.py info warning  
"""

# --------------------------- Input Format -------------------------------------- #
"""
List of severities to listen for
"""
severities = sys.argv[1:]

"""
Display error when severities arguments are not passed
"""
if not severities:
    sys.stderr.write("Usage: %s [info] [warning] [error]" % sys.argv[0])
    sys.exit(1)
# --------------------------- Input Format -------------------------------------- #

"""
Create connection to server and create a channel
"""
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", port=5672))
channel = connection.channel()

"""
Declare or get the direct exchange "severity_logs"   
"""
channel.exchange_declare(
    exchange="severity_logs",
    exchange_type="direct"
)

"""
Create a temporary queue with random name:
"""
result = channel.queue_declare(
    queue='',  # assign random name
    exclusive=True  # make queue temporary
)

"""Get the name of randomly generated queue"""
queue_name = result.method.queue


"""Bind queues with the severity type exchange"""
for severity in severities:
    channel.queue_bind(
        exchange='severity_logs',
        queue=queue_name,  # bind to queue
        routing_key=severity  # use severity level argument passed to bind
    )


def callback(ch, method, properties, body):
    print("[X] %s:%s" % (method.routing_key, body))


channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True
)

print(' [*] Waiting for logs. To exit press CTRL+C')

channel.start_consuming()
