import pika


connection = pika.BlockingConnection(pika.ConnectionParameters(hos="localhost", port=5672))
channel = connection.channel()

channel.exchange_declare(
    exchange='logs',
    exchange_type='fanout'
)

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.bind_queue(exchange='logs', queue=queue_name)

def callback(ch, method, properties, body):
    print(" [X] %r" % body)


channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True
)

channel.start_consuming()