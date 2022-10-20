import vk_api
from vk_api import audio
from loguru import logger
from config import vk_login, vk_password
from services.pikasender import send
from db.db import client
import hashlib


vk_session = vk_api.VkApi(login=vk_login, password=vk_password)
vk_session.auth()
vk = vk_session.get_api()
vk_audio = audio.VkAudio(vk_session)
playlists = client['playlists']


def download_album_music(link, telegram_id, playlist_name):
    link = link.split('_')
    for i in vk_audio.get(owner_id=link[0],album_id=link[1]):
        try:
            hash_name = hashlib.sha256(str.encode(i["title"])).hexdigest()
            filename = f'{telegram_id}_{hash_name}'
            logger.info(f"filename {filename} sended to pika")
            message = {
                'filename': filename,
                'url': i["url"],
                'songname': i["title"],
                'telegram_id': telegram_id,
                'playlist_id': playlist_name,
                'song_id': hash_name
            }
            send(message)
        except Exception as e:
            logger.exception(e)
