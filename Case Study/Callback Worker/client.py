import pika

from constants import ADDITION_QUEUE, ADDITION_CALLBACK_QUEUE


class AddClient:
    def __init__(self, host='localhost'):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host)
        )
        self.channel = self.connection.channel()

    def add(self, x, y):
        """Send a request to the server to add x and y."""
        self.channel.basic_publish(
            exchange='',
            routing_key=ADDITION_QUEUE,
            properties=pika.BasicProperties(
                reply_to=ADDITION_CALLBACK_QUEUE
            ),
            body=f"{x},{y}"
        )

if __name__ == "__main__":
    x = input("Enter first number")
    y = input("Enter second number")
    client  = AddClient()
    print(f" [x] Requesting {x} + {y}")
    response = client.add(x, y)
