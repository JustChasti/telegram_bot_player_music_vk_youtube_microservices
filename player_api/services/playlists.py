from db.db import client
from datetime import datetime
from bson.objectid import ObjectId
from models import PlayListModel, LinkModel, SongModel, EssenceModel, RelationshipModel
from services.decorators import default_decorator
import services.songs as songs
import services.pikasender as sender


playlists = client['playlists']
users = client['users']


@default_decorator('Playlist creation error, open logs to get more info')
def creation(playlist: PlayListModel):
    playlists.insert_one(playlist.dict())
    users.update_one(
        {'telegram_id': playlist.telegram_id},
        {"$set": {'last_visit': datetime.today()}}
    )
    return {'message': 'playlist_created'}


@default_decorator('Playlist creation error, open logs to get more info')
def deletion(playlist_id):
    playlist = playlists.delete_one({'_id': ObjectId(playlist_id)})
    message = {
        'playlist': playlist_id,
        'message': 'плейлист был удален',
    }
    return message

    

@default_decorator('Playlist insertion error, open logs to get more info')
def insertion(link: LinkModel):
    songs.get_songs_from_structure(
        link.url,
        link.telegram_id,
        link.playlist_id
    )
    return {'message': 'music starts downloading'}


def insert_playlist(link: SongModel):
    song_id = songs.create_or_update_song(link)
    music_urls = playlists.find_one({
        '_id': ObjectId(link.playlist_id)
    })['songs']
    element = {
        'song_id': song_id
    }
    if element not in music_urls:
        music_urls.append(element)
        playlists.update_one(
            {
                '_id': ObjectId(link.playlist_id)
            },
            {"$set": {
                'songs': music_urls
            }}
        )


@default_decorator('Get playlist info error, open logs to more info')
def get_info(essence: EssenceModel):
    playlist = playlists.find_one({'_id': ObjectId(essence.essence_id)})
    elements = []
    count = 0
    for i in playlist['songs']:
        song = client['songs'].find_one({'_id': i['song_id']})
        element = {
            'title': song['title'],
            'id': str(song['_id'])
        }
        elements.append(element)
        count += 1
    message = {
        'id': str(playlist['_id']),
        'name': playlist['name'],
        'description': playlist['description'],
        'count': count,
        'songs': elements
    }
    return message


@default_decorator('Get playlist songs error, open logs to more info')
def get_songs(essence: EssenceModel):
    playlist = playlists.find_one({'_id': ObjectId(essence.essence_id)})
    count = 0
    for i in playlist['songs']:
        song = client['songs'].find_one({'_id': i['song_id']})
        filename = f'{playlist["telegram_id"]}_{song["hash"]}'
        message = {
            'filename': filename,
            'url': song["url"],
            'songname': song["title"],
            'telegram_id': playlist["telegram_id"],
            'playlist_id': str(playlist["_id"]),
            'song_id': str(i['song_id']),
        }
        sender.send(message)
        count += 1
    message = {
        'id': str(playlist['_id']),
        'name': playlist['name'],
        'description': playlist['description'],
        'songs_count': count,
        'message': f'({count}) песен скоро будут выгружено'
    }
    return message


@default_decorator('Add music error, open logs to get more info')
def add(relation: RelationshipModel):
    playlist = playlists.find_one({'_id': ObjectId(relation.playlist_id)})
    song = client['songs'].find_one({'_id': ObjectId(relation.song_id)})
    element = {
        'song_id': ObjectId(relation.song_id)
    }
    songs = playlist['songs']
    message = {
        'playlist': relation.playlist_id,
        'song': relation.song_id,
        'message': 'песня не добавлена',
    }
    if element not in songs and song:
        playlist['songs'].append(element)
        playlists.update_one(
            {
                '_id': ObjectId(relation.playlist_id)
            },
            {"$set": {
                'songs': songs
            }}
        )
        message['message'] = f'песня {song["title"]} добавлена в {playlist["name"]}'
    return message


@default_decorator('Delete music error, open logs to get more info')
def delete_song(playlist_id, song_id):
    playlist = playlists.find_one({'_id': ObjectId(playlist_id)})
    songs = playlist['songs']
    songs.remove({
        'song_id': ObjectId(song_id)
    })
    playlists.update_one(
        {
            '_id': playlist['_id']
        },
        {"$set": {
            'songs': songs
        }}
    )
    message = {
        'playlist': playlist_id,
        'song': song_id,
        'message': 'песня была удалена',
    }
    return message
