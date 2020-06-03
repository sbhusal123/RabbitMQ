import pika
import sys

"""
Usage:
> python receive_logs_topic.py <binding_key1> <binding_key2>
Example
    > python receive_logs_topic.py "kern.*" "*.critical"
"""


# --------------------- Inputs -------------------------- #
binding_keys = sys.argv[1:]

if not binding_keys:
    sys.stderr.write("Usage: %s [binding_keys]" % sys.argv[0])
    sys.exit(1)
# --------------------- Inputs -------------------------- #


# Create connection and establish channel
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", port=5672))
channel = connection.channel()

# Declare topic type Exchange
channel.exchange_declare(
    exchange="topic_logs",
    exchange_type="topic"
)

# Declare temporary, random queue and get its name
result = channel.queue_declare(
    queue="",
    exclusive=True  # temporary queue
)
queue_name = result.method.queue


# Bind queue to the exchange based on routing keys = binding_keys
for binding_key in binding_keys:
    channel.queue_bind(
        exchange="topic_logs",
        routing_key=binding_key,  # binding with routing key
        queue=queue_name
    )


# Function to be called on receiving new messages
def callback(ch, method, properties, body):
    print("[X] %s:%s" % (method.routing_key, body))


# Start consuming message from the queue, perform callback and acknowledge automatically
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True  # ack auto
)

print(' [*] Waiting for logs. To exit press CTRL+C')

# Start consuming: infinite loop
channel.start_consuming()
