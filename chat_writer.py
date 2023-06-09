import argparse
import asyncio
import json
import logging

import aiofiles
from environs import Env

from socket_manager import create_chat_connection

logger = logging.getLogger(__name__)


def get_arguments():

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
    parser.add_argument('message', type=str, help='message to be sent')
    parser.add_argument('--hash', type=str, default='user_hash.txt', help='user hash path')
    parser.add_argument('--host', type=str, default='minechat.dvmn.org', help='chat host')
    parser.add_argument('--port', type=int, default=5050, help='chat port')
    parser.add_argument('--token', type=str, default=None, help='user auth token')
    parser.add_argument('--user_name', type=str, default=None,
                        help='user name (uses only when token not provided or invalid)')

    return parser.parse_args()


async def send_message(writer, message):
    sanitized_message = message.replace(r"\n", " ")
    logger.debug(f'Sending message: {sanitized_message}')
    writer.write(f'{sanitized_message}\n'.encode())
    await writer.drain()


async def get_token(hash_path):
    try:
        async with aiofiles.open(hash_path, mode='r') as f:
            contents = await f.read()
            user_payload = json.loads(contents)
        return user_payload['account_hash']
    except FileNotFoundError:
        return


async def authorize_user(reader, writer, user_token):
    await send_message(writer, user_token)

    submit_hash_message = await reader.readline()
    logger.debug(submit_hash_message.decode())

    submit_hash_message_payload = json.loads(submit_hash_message)
    return submit_hash_message_payload


async def register_user(reader, writer, hash_path, user_name):
    empty_message = await reader.readline()
    logger.debug(f'why? {empty_message}')
    user_name = user_name or input('Введите имя пользователя: ')
    await send_message(writer, user_name)
    message = await reader.readline()
    decoded_message = message.decode()
    logger.info(f'Вы успешно зарегистрированы: {decoded_message}')
    async with aiofiles.open(hash_path, mode='w') as file:
        await file.write(decoded_message)


async def handle_message_sending(message, chat_host, chat_port, user_token, user_name, hash_path):
    async with create_chat_connection(chat_host, chat_port) as connection:
        reader, writer = connection

        connection_message = await reader.readline()
        logger.debug(connection_message.decode())

        if user_token is not None:
            submit_hash_message_payload = await authorize_user(reader, writer, user_token)
            if submit_hash_message_payload is None:
                logger.info('Токен недействителен, пройдите регистрацию заново или проверьте его и перезапустите программу')
                await register_user(reader, writer, hash_path, user_name)
            else:
                logger.info(f'Вы авторизованы как {submit_hash_message_payload["nickname"]}')
        else:
            logger.info('Токен не обнаружен, пройдите регистрацию')
            await send_message(writer, '')
            await register_user(reader, writer, hash_path, user_name)

        await send_message(writer, message)
        logger.info(f'Ваше сообщение {message} отправлено')

        logger.debug('Close the connection')
        writer.close()
        await writer.wait_closed()


async def main():
    env = Env()
    env.read_env()

    args = get_arguments()
    message = args.message
    chat_host = env('CHAT_HOST') or args.host
    chat_port = env('CHAT_WRITE_PORT') or args.port
    hash_path = env('HASH_PATH') or args.hash
    user_token = env('USER_TOKEN') or args.token or await get_token(hash_path)
    user_name = env('USER_NAME') or args.user_name
    log_level = env('LOG_LEVEL') or args.logLevel

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=getattr(logging, log_level),
    )

    await handle_message_sending(message, chat_host, chat_port, user_token, user_name, hash_path)


if __name__ == '__main__':
    asyncio.run(main())
