from config import bot
from modules import requests
from modules import keyboards
from modules import playlists


@bot.message_handler(commands=['help', 'start'])
def start_message(message):
    text = """
Привет, я самый продвинутый музыкальный бот! Вот что я уже умею:\n
1) Я могу скачивать музыку из вк и из youtube\n
2) Сохранять треки в ваши плейлисты и выгружать их\n
"""
    requests.create_user(message.chat.id)
    requests.create_playlist(message.chat.id, 'Добавленные')
    img = open('images/lightning.jpg', 'rb')
    bot.send_photo(
        message.chat.id,
        img,
        text,
        reply_markup=keyboards.start_keyboard
    )


@bot.message_handler(content_types=['text'])
def raw_text_handler(message):
    if message.text == 'Мои плейлисты':
        data = requests.get_playlists(message.chat.id)['message']
        playlists.send_playlists(message, data)
    elif message.text == 'Назад':
        text = 'вы в главном меню бота'
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


@bot.callback_query_handler(func=lambda call: True)
def playlist_worker(call):
    element_id, element, func = call.data.split('/')
    if func == 'add':
        text = f"""
На данный момент я могу скачать музыку через 3 доступными способами:
1) С ОТКРЫТОЙ для других страницы в вк и ОТКРЫТОЙ музыкой,
вам нужно  отправить лишь id вашей страницы, например: 111111111 \n
2) С ОТКРЫТОГО плейлиста в вк, отправьте для этого id плейлиста, который
состоит из id страницы и номера плейлиста, например: 111111111_2 \n
3) Ещё вы можете отправить ссылку на ютуб ролик, он будет скачан как аудио
и добавлен в ваш плейлист
"""
        bot.send_message(
            call.message.chat.id,
            text,
            reply_markup=keyboards.add_music_keyboard
        )
        bot.register_next_step_handler(
            call.message,
            playlists.insert_to_playlist,
            element_id
        )
    elif func == 'get':
        data = requests.get_playlist_songs(call.message.chat.id, element_id)
        text = f"Плейлист: {data['name']}\nОписание: {data['description']}\n"
        bot.send_message(
            call.message.chat.id,
            text,
            reply_markup=keyboards.start_keyboard
        )
        text = f"{data['message']}"
        bot.send_message(
            call.message.chat.id,
            text,
            reply_markup=keyboards.start_keyboard
        )
    elif func == 'del':
        bot.send_message(
            call.message.chat.id,
            'Вы уверены?',
            reply_markup=keyboards.yes_not_keyborad
        )
        bot.register_next_step_handler(
            call.message,
            playlists.deletion_confirm,
            element_id
        )

    elif func == 'delete':
        result = requests.delete_song(playlist=element, song=element_id)
        if result:
            text = f"Песня будет удалена из этого плейлиста"
        else:
            text = f"Ошибка, попробуйте позже"
        bot.send_message(
            call.message.chat.id,
            text,
            reply_markup=keyboards.start_keyboard
        )
    else:
        print(call.data)
        text = 'Такой комманды я не знаю'
        bot.send_message(
            call.message.chat.id,
            text,
            reply_markup=keyboards.start_keyboard
        )


bot.infinity_polling()
