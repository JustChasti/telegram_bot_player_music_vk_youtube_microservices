from config import server_password
from pydantic import BaseModel, validator
from db.db import client
from bson.objectid import ObjectId


users = client['users']
playlists = client['playlists']
songs = client['songs']


class UserModel(BaseModel):
    # модель для создания пользователя
    telegram_id: str

    @validator('telegram_id')
    def find_user(telegram_id):
        user = users.find_one({
            'telegram_id': telegram_id
        })
        if user:
            raise ValueError('User already created')
        return telegram_id


class AllMailModel(BaseModel):
    password: str
    text: str
    @validator('password')
    def check_pass(password):
        if password == server_password:
            return password
        else:
            raise ValueError('Password Error')

class EssenceModel(BaseModel):
    telegram_id: str
    essence_id: str

    @validator('telegram_id')
    def find_user(cls, field_value):
        user = users.find_one({
            'telegram_id': field_value
        })
        if not user:
            raise ValueError('User must be registrated')
        return field_value


class PlayListModel(BaseModel):
    # модель для создания плейлиста
    telegram_id: str
    name: str
    description = ''
    songs = []

    @validator('telegram_id')
    def find_user(cls, field_value):
        user = users.find_one({
            'telegram_id': field_value
        })
        if not user:
            raise ValueError('User must be registrated to create_playlists')
        return field_value

    @validator('name')
    def find_duplicate(cls, field_value, values):
        if values == {}:
            values['telegram_id'] = -1
        duplicate = playlists.find_one({
            'telegram_id': values['telegram_id'],
            'name': field_value
        })
        if duplicate:
            raise ValueError("You can't use same names for playlists")
        return field_value


class LinkModel(BaseModel):
    # модель для добавки url в плейлисты
    telegram_id: str
    playlist_id: str
    url: str  # youtube, profile or playlist

    @validator('telegram_id')
    def find_user(cls, field_value):
        user = users.find_one({
            'telegram_id': field_value
        })
        if not user:
            raise ValueError('User must be registrated to create_playlists')
        return field_value

    @validator('playlist_id')
    def find_playlist(cls, field_value):
        playlist = playlists.find_one({
            '_id': ObjectId(field_value)
        })
        if not playlist:
            raise ValueError('Cant find that playlist')
        return field_value


class SongModel(LinkModel):
    telegram_id: str
    playlist_id: str
    hash: str
    title: str


class RelationshipModel(BaseModel):
    telegram_id: str
    playlist_id: str
    song_id: str

    @validator('telegram_id')
    def find_user(cls, field_value):
        user = users.find_one({
            'telegram_id': field_value
        })
        if not user:
            raise ValueError('User must be registrated')
        return field_value

    @validator('playlist_id')
    def find_playlist(cls, field_value):
        playlist = playlists.find_one({
            '_id': ObjectId(field_value)
        })
        if not playlist:
            raise ValueError('Cant find that playlist')
        return field_value
    
    @validator('song_id')
    def find_song(cls, field_value):
        song = songs.find_one({
            '_id': ObjectId(field_value)
        })
        if not song:
            raise ValueError('Cant find that song')
        return field_value