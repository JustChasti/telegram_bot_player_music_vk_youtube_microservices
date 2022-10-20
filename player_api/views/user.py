from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services import users
from models import UserModel, AllMailModel


user_router = APIRouter()


@user_router.post('/user/create', response_class=JSONResponse)
async def create_user(user: UserModel):
    return users.creation(user)


@user_router.post('/user/send', response_class=JSONResponse)
async def send_to_all(mail: AllMailModel):
    return users.send_all(mail)


@user_router.get('/user/get_playlists/{telegram_id}', response_class=JSONResponse)
async def get_playlist(telegram_id: str):
    return users.get_user_playlists(telegram_id)
