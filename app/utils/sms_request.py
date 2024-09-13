from base64 import b64encode

from aiohttp import ClientSession

from config import settings


def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'


async def sms_request(phone_number: str, message: str):
    async with ClientSession() as session:
        try:
            response = await session.get(
                url=settings.sms_request_url,
                params={
                    'phone': phone_number,
                    'text': message,
                    'sender': settings.sms_request_sender,
                },
                headers={
                    "Authorization": basic_auth(settings.sms_request_login, settings.sms_request_password)
                }
            )
        except Exception as e:
            print(e)
    return response
