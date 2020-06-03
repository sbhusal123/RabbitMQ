import pika
import sys

"""
Format:
> python emmit_logs_topic.py <key> <message>
Example:
    > python emmit_logs_topic.py "kern.critical" "Kernel failure"  
"""

# --------------------- Message -------------------------- #
routing_key = sys.argv[1] if len(sys.argv[1]) > 1 else 'anonymous.info'
message = ' '.join(sys.argv[2:]) or "Hello world!"

# --------------------- Message -------------------------- #

# Establish connection to RabbitMQ and create a channel
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", port=5672))
channel = connection.channel()

# Declare a topic type exchange
channel.exchange_declare(
    exchange="topic_logs",
    exchange_type="topic"
)

# Publish message to exchange with routing key
channel.basic_publish(
    exchange="topic_logs",
    routing_key=routing_key,
    body=message
)

print("[X] %s:%s" % (routing_key, message))

connection.close()
