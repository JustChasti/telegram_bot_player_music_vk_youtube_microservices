from loguru import logger


def default_decorator(errormessage: str):
    def internal_decorator(function):
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                logger.exception(e)
                return {'message': errormessage}
        return wrapper
    return internal_decorator
