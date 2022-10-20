from os.path import exists
import os
import json
from threading import Thread

from fastapi import APIRouter, HTTPException
from loguru import logger
from fastapi.responses import FileResponse, JSONResponse
import pika
from pydantic import BaseModel, validator
from fastapi.encoders import jsonable_encoder

from config import rabbit_host, queue_url_name, music_folder
from converter.core import download_audio


main_router = APIRouter()


class InvalidUrl(Exception):

    def __init__(self, url) -> None:
        message = f'url {url} not valid'
        super().__init__(message)


class MusicFile(BaseModel):
    path: str

    @validator('path')
    def path_must_contain_space(path):
        if music_folder not in path:
            raise ValueError('must contain a music_folder')
        return path


def callback(ch, method, properties, body):
    try:
        data = json.loads(body.decode("utf-8"))
        if 'vkuseraudio' not in data['url'] and 'youtube' not in data['url']:
            raise InvalidUrl(data['url'])
        download_audio(
            filename=data['filename'],
            url=data['url'],
            songname=data['songname'],
            telegram_id=data['telegram_id'],
            playlist_id=data['playlist_id'],
            song_id=data['song_id']
        )
    except Exception as e:
        logger.exception(e)


def starter():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbit_host)
            )
            channel = connection.channel()
            channel.queue_declare(queue=queue_url_name)
            channel.basic_consume(
                queue=queue_url_name, 
                on_message_callback=callback,
                auto_ack=True
            )
            logger.info('ran pika listener')
            channel.start_consuming()
        except pika.exceptions.StreamLostError:
            logger.warning('Core and Pika connection dropped and restarted')


@main_router.on_event("startup")
async def main():
    rabbit_thread = Thread(target=starter)
    rabbit_thread.start() 
    logger.info('rabbit_thread started')


@main_router.get("/get_file", response_class=FileResponse)
async def get_file(data: MusicFile):
    """
    accept:
        'path': 'C:/example/file.mp3'
    return:
        200: file,
        422
        404
    """
    data = jsonable_encoder(data)
    if exists(data['path']):
        return data['path']
    else:
        raise HTTPException(status_code=404, detail="file not found")


@main_router.delete("/remove_file", response_class=JSONResponse)
async def remove_file(data: MusicFile):
    """
    accept:
        'path': 'C:/example/file.mp3'
    return:
        200: Json({'info': 'some information about file'}),
        422
        404
    """
    data = jsonable_encoder(data)
    if exists(data['path']):
        os.remove(data['path'])
        return {'info': f"File named: {data['path']} removed"}
    else:
        raise HTTPException(status_code=404, detail="file not found")
