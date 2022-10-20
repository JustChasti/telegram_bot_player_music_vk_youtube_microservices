import hashlib
from threading import Thread
import json

import requests
import uvicorn
from fastapi import FastAPI
from loguru import logger
import pika

from config import rabbit_host, queue_misic_name
from config import core_host
from services import pikasender
from models import SongModel
from views.playlist import playlists_router
from views.user import user_router
from services.playlists import insert_playlist

app = FastAPI()
logger.add("test.log", rotation="100 MB")


def callback(ch, method, properties, body):
    try:
        data = json.loads(body.decode("utf-8"))
        logger.info(f"get file{data['file']}")
        file_data = {
            'path': data['file']
        }
        response = requests.get(f'{core_host}/get_file', json=file_data)
        telegram_id = data['file'].split('/')[-1].split('_')[0]
        title = data['songname']
        if response.status_code == 200:
            pikasender.send_to_telegram(
                telegram_id,
                response.content,
                title,
                data['song_id'],
                data['playlist_name']
            )
            song_hash = hashlib.sha256(response.content).hexdigest()
            song = SongModel(
                telegram_id=data['telegram_id'],
                playlist_id=data['playlist_name'],
                url=data['url'],
                hash=str(song_hash),
                title=title
            )
            insert_playlist(song)
        else:
            raise ValueError(str(response.content))
        response = requests.delete(f'{core_host}/remove_file', json=file_data)
        if response.status_code != 200:
            raise ValueError(str(response.content))
    except Exception as e:
        logger.exception(e)


def starter():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_misic_name)
    channel.basic_consume(
        queue=queue_misic_name, 
        on_message_callback=callback,
        auto_ack=True
    )
    logger.info('ran pika listener')
    channel.start_consuming()


@app.on_event("startup")
async def main():
    rabbit_thread = Thread(target=starter)
    rabbit_thread.start()


app.include_router(playlists_router)
app.include_router(user_router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
