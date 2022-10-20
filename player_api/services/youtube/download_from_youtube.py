from loguru import logger
import youtube_dl
from services.pikasender import send
from db.db import client
import hashlib


playlists = client['playlists']


def download_youtube_video(url, telegram_id, playlist_name):
    try:
        # добавить библиотеку с ютубом для получения songname
        video_info = youtube_dl.YoutubeDL().extract_info(
            url=url,
            download=False
        )
        hash_name = hashlib.sha256(str.encode(url)).hexdigest()
        logger.info(f"filename {hash_name} sended to pika")
        message = {
            'filename': f'{telegram_id}_{hash_name}',
            'url': url,
            'songname': video_info['title'],
            'telegram_id': telegram_id,
            'playlist_id': playlist_name,
            'song_id': hash_name
        }
        send(message)
    except Exception as e:
        logger.exception(e)
