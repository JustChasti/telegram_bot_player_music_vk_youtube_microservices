from pymongo import MongoClient
from loguru import logger
from config import base_host, base_port, client_name
from time import sleep


while True:
    try:
        client = MongoClient(
            base_host, base_port
        )[client_name]
        break
    except Exception as e:
        logger.exception(e)
        sleep(5)
