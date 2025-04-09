import pika
import multiprocessing

class BaseServer:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()


    def start(self):
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.on_request
        )
        process_nam = multiprocessing.process.current_process().name
        process_id = multiprocessing.process.current_process().pid
        print(f" [x] Server {process_nam} (PID: {process_id}) started on queue '{self.queue_name}'")
        self.channel.start_consuming()