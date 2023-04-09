import aiofiles
import argparse
import asyncio
import logging
import json

logger = logging.getLogger(__name__)


async def create_chat_connection(host, port):
    return await asyncio.open_connection(host, port)


async def authorize_user(reader, writer, hash_path):
    async with aiofiles.open(hash_path, mode='r') as f:
        contents = await f.read()
        user_payload = json.loads(contents)

    writer.write(f'{user_payload["account_hash"]}\n'.encode())
    await writer.drain()



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
    parser.add_argument('--hash', type=str, default='user_hash.txt', help='user history path')
    parser.add_argument('--host', type=str, default='minechat.dvmn.org', help='chat host')
    parser.add_argument('--port', type=int, default=5050, help='chat port')
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=getattr(logging, args.logLevel),
    )

    chat_host = args.host
    chat_port = args.port
    hash_path = args.hash
    reader, writer = await create_chat_connection(chat_host, chat_port)
    await authorize_user(reader, writer, hash_path)


if __name__ == '__main__':
    asyncio.run(main())
