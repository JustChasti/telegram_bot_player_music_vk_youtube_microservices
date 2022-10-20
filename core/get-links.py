import pika, json
from config import rabbit_host, queue_misic_name


def callback(ch, method, properties, body):
    data = json.loads(body.decode("utf-8"))
    print(data)


connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
channel = connection.channel()
channel.queue_declare(queue=queue_misic_name)
channel.basic_consume(
    on_message_callback=callback,
    queue=queue_misic_name,
    auto_ack=True
)
channel.start_consuming()