import pika
import sys


"""
Summary:
    - Take message from the console
    - Establish connection to server and create channel
    - Declare exchange with name and type
    - Publish message to exchange with routing ket
    - Close the connection
"""

"""
Message format: python file.py [severity] [message]
"""

# ------------------- Message Format --------------------------------------

"""
Take severity(info, warning, error) level info 1st argument
Default severity = info
"""
severity = sys.argv[1] if len(sys.argv) > 1 else 'info'


"""
Message corresponding to severity
"""
message = ' '.join(sys.argv[2:]) or 'Hello World'

# ------------------- Message Format ---------------------------------------


"""
Create connection to server and channel
"""
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", port=5672))
channel = connection.channel()

"""
Declare default exchange with name "severity_logs"
"""
channel.exchange_declare(
    exchange="severity_logs",
    exchange_type="direct"
)

"""
Publish message to the severity_logs exchange
with roting key set to level of severity set to  
argument passed
"""
channel.basic_publish(
    exchange='severity_logs',
    routing_key=severity,  # set routing key to severity passed as argument
    body=message
)

print("[X] Sent %r:%r" % (severity, message))
connection.close()
