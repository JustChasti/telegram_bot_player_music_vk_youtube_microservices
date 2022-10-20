import pika
import json

url = 'https://www.youtube.com/watch?v=Mz3EoinTFbI'

message = {
    'filename': 'test1',
    'url': 'https://cs9-1v4.vkuseraudio.net/s/v1/ac/v_1Wu4yC_vkq1dPcKbyT0-CbmjlbehsFZfsvyNEfRIqRTgEfTzfkORSWpf7f3sqx04RuxK-jL1827XiorLsjZVhEJl2isdN_vDVSswIHZedMzI0CnajMwJZo6sjm9oArVrTlxuhflNO4L1CxC5z1-j3pAPAHs9pIhLrQQ8oLg2B60uo/index.m3u8'
}

# Вы можете подключить пульт дистанционного управления, localhost заменяется на IP-адрес или доменное имя.
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='music_links')

channel.basic_publish(exchange='', routing_key='music_links', body=json.dumps(message))
print('Sent message: {}'.format(message))
connection.close()