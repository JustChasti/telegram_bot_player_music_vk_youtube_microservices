from models import UserModel
from db.db import client
from datetime import datetime
from services.decorators import default_decorator
from services.pikasender import send_telegram_text


@default_decorator('User creation error, open logs to get more info')
def creation(user: UserModel):
    users = client['users']
    users.insert_one({
        'telegram_id': user.telegram_id,
        'premium': False,
        'last_visit': datetime.today()
    })
    return {'message': "creation succesfull"}


@default_decorator('User playlists info error')
def get_user_playlists(telegram_id):
    playlists = client['playlists']
    playlists = playlists.find({
            'telegram_id': telegram_id,
    })
    message = []
    for i in playlists:
        message.append({
            'id': str(i['_id']),
            'name': i['name']
        })
    return {'message': message}


@default_decorator('User playlists info error')
def send_all(mail):
    users = client['users'].find({})
    for i in users:
        send_telegram_text(i['telegram_id'], mail.text)
