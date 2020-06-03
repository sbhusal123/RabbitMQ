import pika

"""
Summary:
    - Create connection and channel.
    - Get the defined fanout exchange in our emitter.
    - Declare a random queue.
    - Bind the random queue to the exchange.
    - Start consuming message from the randomly generated queue.
"""


"""
Establish a connection to the RabbitMQ server and create channel
"""
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", port=5672))
channel = connection.channel()


"""
Create or get our logs exchange of type fanout.
"""
channel.exchange_declare(
    exchange='logs',
    exchange_type='fanout'
)

"""
Create a queue with random name and get queue name
- Random queue are deleted when the consumer connection is closed
"""
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

"""
Bind the randomly generated queue to the exchange
"""
channel.queue_bind(exchange='logs', queue=queue_name)


def callback(ch, method, properties, body):
    """Function to be executed on receiving messages"""
    print(" [X] %r" % body)


"""Start consuming messages from the randomly generated queue and perform callback."""
channel.basic_consume(
    queue=queue_name,  # which queue to consume
    on_message_callback=callback,  # handle to incoming message performing callback
    auto_ack=True  # perform automatic acknowledge that consumer has received message
)


channel.start_consuming()
