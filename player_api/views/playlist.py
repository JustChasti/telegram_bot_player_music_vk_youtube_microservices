from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models import PlayListModel, LinkModel, EssenceModel, RelationshipModel
from db.db import client
import services


playlists_router = APIRouter()
playlists = client['playlists']


@playlists_router.post('/playlist/create', response_class=JSONResponse)
async def playlist_create(playlist: PlayListModel):
    return services.playlists.creation(playlist)


@playlists_router.patch('/playlist/insert', response_class=JSONResponse)
async def playlist_insert(link: LinkModel):
    return services.playlists.insertion(link)


@playlists_router.get('/info/{telegram_id}/{item_id}', response_class=JSONResponse)
async def playlist_info(telegram_id:str, item_id:str):
    playlist = EssenceModel(**{
        'telegram_id': telegram_id,
        'essence_id': item_id
    })
    return services.playlists.get_info(playlist)


@playlists_router.get('/get/{telegram_id}/{item_id}', response_class=JSONResponse)
async def playlist_get(telegram_id:str, item_id:str):
    playlist = EssenceModel(**{
        'telegram_id': telegram_id,
        'essence_id': item_id
    })
    return services.playlists.get_songs(playlist)


@playlists_router.patch('/playlist/add/', response_class=JSONResponse)
async def playlist_add(relation: RelationshipModel):
    return services.playlists.add(relation)


@playlists_router.delete('/delete/{playlist_id}/{song_id}', response_class=JSONResponse)
async def delete_song(playlist_id:str, song_id:str):
    return services.playlists.delete_song(playlist_id, song_id)


@playlists_router.delete('/delete_playlist/{playlist_id}', response_class=JSONResponse)
async def delete_playlist(playlist_id:str):
    return services.playlists.deletion(playlist_id)
