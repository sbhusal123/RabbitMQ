import pika
import multiprocessing

class BaseRpcServer:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        self.channel.basic_qos(prefetch_count=1)

    def on_request(self, ch, method, props, body):
        # Override this method in subclasses
        pass


    def start(self):
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.on_request
        )
        process_nam = multiprocessing.process.current_process().name
        process_id = multiprocessing.process.current_process().pid
        print(f" [x] RPC server {process_nam} (PID: {process_id}) started on queue '{self.queue_name}'")
        self.channel.start_consuming()