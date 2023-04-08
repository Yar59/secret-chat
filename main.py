import argparse
import asyncio
import logging

logger = logging.getLogger(__name__)


async def create_chat_connection(host, port):
    return await asyncio.open_connection(host, port)


async def read_messages(reader, writer):
    while True:
        try:
            message = await reader.readline()
            print(message.decode())
        except asyncio.CancelledError:
            logger.debug('Closing connection')
            writer.close()
            raise
        except:
            logger.exception('Проблемы с подключением к серверу сообщений:\n')


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
    parser.add_argument('--history', type=str, default='test_photos', help='chat history directory')
    parser.add_argument('--host', type=str, default='minechat.dvmn.org', help='chat host')
    parser.add_argument('--port', type=int, default=5000, help='chat port')
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=getattr(logging, args.logLevel),
    )

    chat_host = args.host
    chat_port = args.port
    reader, writer = await create_chat_connection(chat_host, chat_port)
    await read_messages(reader, writer)


if __name__ == '__main__':
    asyncio.run(main())
