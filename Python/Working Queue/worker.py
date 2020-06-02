import pika
import time

"""
What are we doing here??
-> Worker for performing long running task. 
   Basically we simulate the time taken by considering number of dots(.) in argument.
"""


connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", port=5672))
channel = connection.channel()

"""Listen to incoming message on task queue"""
channel.queue_declare(queue='task')


def callback(ch, method, properties, body):
    """Function to be called on receiving message"""
    print(f"[X] Received %r" % body)

    # wait for certain time until task is completed
    time.sleep(body.count(b'.'))
    print("[X] Done")

    """Acknowledge after completing task this prevents message
       message loss when the worker dies. And when worker
       dies message will be passes to another online worker.
       Caution: We are not talking about worker node of RabbitMQ.
    """
    ch.basic_ack(delivery_tag=method.delivery_tag)


"""
In case of odd task being time consumings and even being lighter.
Make sure one of the worker is not free. i.e resource are utilized in better manner.  
"""
channel.basic_qos(prefetch_cont=1)


"""Consume the messages and perform callback in response to incoming message"""
channel.basic_consume(
    queue="task",  # consume message from task queue
    on_message_callback=callback,  # pass handle to callback method
    auto_ack=False  # disable auto ack, we want manual ack
)


print("[X] Waiting for message. Press CTRL+C to exit.")
channel.start_consuming()