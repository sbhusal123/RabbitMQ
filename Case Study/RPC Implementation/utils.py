import pika
import uuid

import multiprocessing


class BaseRPCClient:

    def __init__(self, queue_name):
        self.connection = pika.BlockingConnection(
            parameters=pika.ConnectionParameters(host='localhost')
        )
        self.channel = self.connection.channel()
        self.queue_name = queue_name

        self.response = None
        self.correlation_id = None

    def create_callback_queue_and_consume(self):
        """Creates callback queue and listen for rpc response"""
        # callback queue to which rpc server enques data to
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue


        # consume items from callback queue, handled by rpc_response
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )


    def on_response(self, ch, method, props, data):
        """If correlation id matches for request and response"""
        if props.correlation_id == self.correlation_id:
            self.response = data


    def call(self, data):
        """Creates callback queue and listens on it, publishes item to rpc queue """
        self.create_callback_queue_and_consume()
        self.correlation_id = str(uuid.uuid4())
        self.response = None
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            properties=pika.BasicProperties(
                correlation_id=self.correlation_id,
                reply_to=self.callback_queue
            ),
            body=str(data)
        )
        while self.response is None:
            self.connection.process_data_events(time_limit=None)
        return int(self.response)



class BaseRPCServer:

    def __init__(self, queue_name):
        connection = pika.BlockingConnection(
            parameters=pika.ConnectionParameters(host='localhost')
        )
        self.channel = connection.channel()
        self.queue_name = queue_name

    
    def handle_message(self, body):
        raise NotImplementedError("handle_message(self, body) not implemented.")

    

    def on_request(self, ch, method, props, body):
        response = self.handle_message(body)
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(
                correlation_id =props.correlation_id
            ),
            body=str(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        self.channel.queue_declare(queue=self.queue_name)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.on_request,
            auto_ack=False
        )
        process = multiprocessing.current_process()
        print(f"[x] [PID={process.pid}] [Name={process.name}] Awaiting RPC requests on queue: {self.queue_name}")
        self.channel.start_consuming()

