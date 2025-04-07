import pika

from constants import ADDITION_CALLBACK_RPC_QUEUE, ADDITION_RPC_QUEUE


class AddRpcClient:
    def __init__(self, host='localhost'):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host)
        )
        self.channel = self.connection.channel()

        # Create a callback queue
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

    def on_response(self, ch, method, props, body):
        """Callback to capture the response."""
        if self.corr_id == props.correlation_id:
            self.response = body

    def add(self, x, y):
        """Send a request to the RPC server to add x and y."""
        self.channel.basic_publish(
            exchange='',
            routing_key=ADDITION_RPC_QUEUE,
            properties=pika.BasicProperties(
                reply_to=ADDITION_CALLBACK_RPC_QUEUE
            ),
            body=f"{x},{y}"
        )
    
client  = AddRpcClient()
print(" [x] Requesting 5 + 3")
response = client.add(5, 3)
