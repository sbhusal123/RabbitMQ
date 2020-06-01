"""
    Receiver which receives the message from the queue.
"""

import pika


"""Create a connection to the RabbitMQ server and establish a channel"""
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", port=5672))
channel = connection.channel()


"""
    - Create or get the existing channel from the Queue
    - So far we have already created a channel in send.py so it won't be created again.
"""
channel.queue_declare(queue="hello")


def callback(ch, method, properties, body):
    """Function to be called by Pika Library on receiving message"""
    # %r -> converts to representation
    print("[X] Received %s" % body)


channel.basic_consume(
    queue="hello",  # subscribe to hello queue
    on_message_callback=callback,  # call function on receiving a message
    auto_ack=True
)


print('[*] Waiting for messages. To exit press CTRL+C')

"""enter a never-ending loop that waits for data and runs callbacks"""
channel.start_consuming()