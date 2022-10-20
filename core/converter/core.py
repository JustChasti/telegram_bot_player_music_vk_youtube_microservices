import binascii
import m3u8
from moviepy.editor import AudioFileClip
from Crypto.Cipher import AES
from urllib.request import urlopen
import youtube_dl
import os

import pika
import json
from config import rabbit_host, queue_misic_name, music_folder
from loguru import logger


def get_key(data):
    host_uri = None
    for i in range(data.media_sequence):
        try:
            key_uri = data.keys[i].uri
            host_uri = "/".join(key_uri.split("/")[:-1])
            return host_uri
        except Exception as e:
            continue


def read_keys(path):
    content = b""
    data_response = urlopen(path)
    content = data_response.read()
    return content


def get_ts(url):
    data = m3u8.load(url)
    key_link = get_key(data)
    ts_content = b""
    key = None
    for i, segment in enumerate(data.segments):
        decrypt_func = lambda x: x
        if segment.key.method == "AES-128":
            if not key:
                key_uri = segment.key.uri
                key = read_keys(key_uri)
            ind = i + data.media_sequence
            iv = binascii.a2b_hex('%032x' % ind)
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            decrypt_func = cipher.decrypt

        ts_url = f'{key_link}/{segment.uri}'
        coded_data = read_keys(ts_url)
        ts_content += decrypt_func(coded_data)
    return ts_content


def m3u8_to_mp3_advanced(filename, url, songname, folder_name='files'):
    logger.info(f'start converting {filename}')
    try:
        os.mkdir(folder_name)
    except FileExistsError as e:
        pass
    ts_content = get_ts(url)
    if ts_content is None:
        raise TypeError("Empty mp3 content to save.")
    with open(f'{folder_name}/{filename}x.mp3', 'wb') as out:
        out.write(ts_content)
    audioclip = AudioFileClip(f'{folder_name}/{filename}x.mp3')
    audioclip.write_audiofile(f'{folder_name}/{filename}.mp3')
    audioclip.close()
    os.remove(f'{folder_name}/{filename}x.mp3')
    return f'{folder_name}/{filename}.mp3'


def download_from_youtube(name, url, songname, folder_name=music_folder):
    try:
        os.mkdir(folder_name)
    except FileExistsError as e:
        pass
    video_info = youtube_dl.YoutubeDL().extract_info(
        url=url,
        download=False
    )
    filename = f"{folder_name}/{name}.mp3"
    options={
        'format':'bestaudio/best',
        'keepvideo':False,
        'outtmpl':filename,
    }

    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])

    return f"{folder_name}/{name}.mp3"


def download_audio(filename:str, url:str, songname, telegram_id, playlist_id, song_id, folder_name=music_folder):
    if 'vkuseraudio' in url:
        link = m3u8_to_mp3_advanced(filename, url, songname, folder_name)
    else:
        link = download_from_youtube(filename, url, songname, folder_name)
    message = {
        'file': link,
        'songname': songname,
        'telegram_id': telegram_id,
        'playlist_name': playlist_id,
        'song_id': song_id,
        'url': url
    }
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_misic_name)
    channel.basic_publish(exchange='', routing_key=queue_misic_name, body=json.dumps(message))
    connection.close()
