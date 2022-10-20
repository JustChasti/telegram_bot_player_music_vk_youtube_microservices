from loguru import logger
from config import bot
from modules import requests
from modules import keyboards
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def send_playlists(message, playlists):
    for i in playlists:
        callback_keyboard = InlineKeyboardMarkup()
        button0 = InlineKeyboardButton(
            text='Добавить',
            callback_data=f"{i['id']}/playlist/add"
        )
        button1 = InlineKeyboardButton(
            text='Выгрузить',
            callback_data=f"{i['id']}/playlist/get"
        )
        button2 = InlineKeyboardButton(
            text='Удалить',
            callback_data=f"{i['id']}/playlist/del"
        )
        callback_keyboard.row(button0)
        callback_keyboard.row(button1)
        callback_keyboard.row(button2)

        bot.send_message(
            message.chat.id,
            i['name'],
            reply_markup=callback_keyboard
        )
    text = 'выберите вариант'
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=keyboards.playlists_keyboard
    )
    bot.register_next_step_handler(message, new_playlist_creation)


def new_playlist_creation(message):
    if message.text == 'Добавить плейлист':
        text = 'Введите название плейлиста'
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=keyboards.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, add_playlist_name)
    elif message.text == 'Назад':
        text = 'вы в главном меню бота'
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=keyboards.start_keyboard
        )
    else:
        data = requests.get_playlists(message.chat.id)['message']
        send_playlists(message, data)


def add_playlist_name(message):
    requests.create_playlist(message.chat.id, message.text, '')
    data = requests.get_playlists(message.chat.id)['message']
    send_playlists(message, data)


def insert_to_playlist(message, playlist_id):
    if message.text == 'Назад':
        bot.send_message(
            message.chat.id,
            'Выберете вариант',
            reply_markup=keyboards.start_keyboard
        )
    else:
        url = message.text
        if '_' in url:
            vk_id, v_pl = url.split('_')
            try:
                int(vk_id)
                int(v_pl)
                url = 'playlist' + url
            except Exception as e:
                pass
        response = requests.insert_to_playlist(
            message.chat.id,
            playlist_id,
            url
        )
        if response.status_code != 200:
            bot.send_message(
                message.chat.id,
                f"Ошибка вставки в плейлист: {response.json()['detail'][0]['msg']}",
                reply_markup=keyboards.start_keyboard
            )


def add_song_choser(message, playlist_id):
    if message.text == 'Плейлист ВК':
        bot.register_next_step_handler(
            message,
            insert_to_playlist,
            playlist_id,
            chose=0
        )
        bot.send_message(
            message.chat.id,
            "введите id",
            reply_markup=keyboards.ReplyKeyboardRemove
        )
    elif message.text == 'Страница ВК':
        bot.register_next_step_handler(
            message,
            insert_to_playlist,
            playlist_id,
            chose=1
        )
        bot.send_message(
            message.chat.id,
            "введите id",
            reply_markup=keyboards.ReplyKeyboardRemove
        )
    elif message.text == 'Youtube видео':
        bot.register_next_step_handler(
            message,
            insert_to_playlist,
            playlist_id,
            chose=2
        )
        bot.send_message(
            message.chat.id,
            "введите url",
            reply_markup=keyboards.ReplyKeyboardRemove
        )
    elif message.text == 'Назад':
        text = 'Вы в главном меню'
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=keyboards.start_keyboard
        )
    else:
        text = 'Такой комманды я не знаю'
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=keyboards.start_keyboard
        )


def deletion_confirm(message, element_id):
    if message.text == 'Да':
        result = requests.delete_playlist(playlist=element_id)
        if result:
            text = f"Плейлист был удален"
        else:
            text = f"Ошибка, попробуйте позже"
    else:
        text = 'Удаление отменено'
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=keyboards.start_keyboard
    )
