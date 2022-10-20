from telebot import types
from telebot.types import ReplyKeyboardRemove

start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
button1 = types.KeyboardButton('Мои плейлисты')
button2 = types.KeyboardButton('Назад')
start_keyboard.row(button1)
start_keyboard.row(button2)

playlists_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
button1 = types.KeyboardButton('Добавить плейлист')
button2 = types.KeyboardButton('Назад')
playlists_keyboard.row(button1)
playlists_keyboard.row(button2)

add_music_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
button1 = types.KeyboardButton('Плейлист ВК')
button2 = types.KeyboardButton('Страница ВК')
button3 = types.KeyboardButton('Youtube видео')
button4 = types.KeyboardButton('Назад')
add_music_keyboard.row(button1)
add_music_keyboard.row(button2)
add_music_keyboard.row(button3)
add_music_keyboard.row(button4)

yes_not_keyborad = types.ReplyKeyboardMarkup(resize_keyboard=True)
button1 = types.KeyboardButton('Да')
button2 = types.KeyboardButton('Нет')
yes_not_keyborad.row(button1)
yes_not_keyborad.row(button2)
