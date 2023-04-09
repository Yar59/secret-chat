import aiofiles
import argparse
import asyncio
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


async def get_token(hash_path):
    async with aiofiles.open(hash_path, mode='r') as f:
        contents = await f.read()
        user_payload = json.loads(contents)
    return user_payload['account_hash']


async def create_chat_connection(host, port):
    return await asyncio.open_connection(host, port)


async def authorize_user(reader, writer, user_token):
    connection_message = await reader.readline()
    logger.debug(f'[{datetime.now().strftime("%d.%m.%y %H:%M")}] {connection_message.decode()}')

    writer.write(f'{user_token}\n'.encode())
    await writer.drain()

    submit_hash_message = await reader.readline()
    logger.debug(f'[{datetime.now().strftime("%d.%m.%y %H:%M")}] {submit_hash_message.decode()}')

    submit_hash_message_payload = json.loads(submit_hash_message)
    return submit_hash_message_payload


async def main():
    parser = argparse.ArgumentParser(
        prog='ProgramName',
        description='What the program does',
        epilog='Text at the bottom of help',
    )
    parser.add_argument(
        '-l', '--log',
        dest='logLevel',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level',
        default='INFO',
    )
    parser.add_argument('--hash', type=str, default='user_hash.txt', help='user hash path')
    parser.add_argument('--host', type=str, default='minechat.dvmn.org', help='chat host')
    parser.add_argument('--port', type=int, default=5050, help='chat port')
    parser.add_argument('--token', type=str, default=None, help='user auth token')
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=getattr(logging, args.logLevel),
    )

    chat_host = args.host
    chat_port = args.port
    hash_path = args.hash
    user_token = args.token or await get_token(hash_path)

    reader, writer = await create_chat_connection(chat_host, chat_port)

    if user_token is not None:
        submit_hash_message_payload = await authorize_user(reader, writer, user_token)
        if submit_hash_message_payload is None:
            logger.info('Токен недействителен, пройдите регистрацию заново или проверьте его и перезапустите программу')
    else:
        logger.info('Токен не обнаружен, пройдите регистрацию')
        


if __name__ == '__main__':
    asyncio.run(main())
