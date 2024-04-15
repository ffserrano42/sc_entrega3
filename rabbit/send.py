import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='pdfs')
# Assuming you have a JSON object called 'data'
data = {
    'name': 'Libro 2'    
}
# Convert the JSON object to a string
body = json.dumps(data)

channel.basic_publish(exchange='',
                      routing_key='pdfs',
                      body=body)
print(" [x] Sent body message")
connection.close()