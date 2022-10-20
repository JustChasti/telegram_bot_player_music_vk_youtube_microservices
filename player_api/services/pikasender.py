import pika
import json
from config import bot_token
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger


def send(message):
    connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost')
            )
    channel = connection.channel()
    channel.queue_declare(queue='music_links')
    channel.basic_publish(
        exchange='',
        routing_key='music_links',
        body=json.dumps(message)
    )
    connection.close()


def send_to_telegram(telegram_id, music_bytes, title, song_id, playlist_id):
    try:
        bot = telebot.TeleBot(bot_token)
        callback_keyboard = InlineKeyboardMarkup()
        button0 = InlineKeyboardButton(
            text='Удалить',
            callback_data=f"{song_id}/{playlist_id}/delete"
        )
        callback_keyboard.row(button0)
        if len(str(song_id)) == 24:
            bot.send_audio(
                telegram_id,
                title=title,
                audio=music_bytes,
                reply_markup=callback_keyboard
            )
        else:
            bot.send_audio(
                telegram_id,
                title=title,
                audio=music_bytes
            )
    except Exception as e:
        logger.exception(e)


def send_telegram_text(telegram_id, text):
    try:
        bot = telebot.TeleBot(bot_token)
        bot.send_message(telegram_id, text)
    except Exception as e:
        logger.exception(e)
