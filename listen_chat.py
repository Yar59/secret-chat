import argparse
import asyncio
import logging
from datetime import datetime
from time import sleep

import aiofiles
from environs import Env

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
    parser.add_argument('--history', type=str, default='chat_history.txt', help='chat history directory')
    parser.add_argument('--host', type=str, default='minechat.dvmn.org', help='chat host')
    parser.add_argument('--port', type=int, default=5000, help='chat port')
    return parser.parse_args()

async def create_chat_connection(host, port):
    return await asyncio.open_connection(host, port)


async def read_messages(reader, writer, history_path):
    while True:
        try:
            message = await reader.readline()
            decoded_message = f'[{datetime.now().strftime("%d.%m.%y %H:%M")}] {message.decode()}'
            print(decoded_message)
            async with aiofiles.open(history_path, mode='a') as file:
                await file.write(decoded_message)
        except asyncio.CancelledError:
            logger.debug('Closing connection')
            writer.close()
            raise
        except:
            logger.exception('Проблемы с подключением к серверу сообщений:\n')
            sleep(3)


async def main():
    args = get_arguments()

    env = Env()
    env.read_env()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=getattr(logging, env('LOG_LEVEL') or args.logLevel),
    )

    chat_host = env('CHAT_HOST') or args.host
    chat_port = env('CHAT_READER_PORT') or args.port
    history_path = env('HISTORY_PATH') or args.history

    reader, writer = await create_chat_connection(chat_host, chat_port)
    await read_messages(reader, writer, history_path)


if __name__ == '__main__':
    asyncio.run(main())
