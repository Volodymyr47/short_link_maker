import asyncio
import logging
from aiogram import Bot, Dispatcher, executor, types
import random
import sys

import config
import database as db


API_TOKEN = config.TG_BOT_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command to return info about service
    """
    await message.reply('Hello, my friend! Welcome to short_link_maker service.\n '
                        'If you need to get a short website link, '
                        'please, enter the your long-link that starts with "http" or "https"')


@dp.message_handler(commands=['my_links'])
async def send_user_links(message: types.Message):
    """
    This handler will be called when user sends `/my_links` command to return user links
    """
    try:
        user_links = await db.select_many(db.tbl_link, message.from_id)
        await message.reply('\n'.join(user_links))
    except Exception as err:
        print(f'Send_user_link error:\n{err}')


@dp.message_handler()
async def generate_new_link(message: types.Message):
    """
    This handler generates and returns a new link
    """
    if not (message.text.startswith('http://') or message.text.startswith('https://')):
        await message.reply('You have wrong link entered: Your link does not begin from "http://" or "https://"')
    else:
        is_inserted = False
        old_link = message.text
        new_link = ''.join(random.choice('abcdef0123456789abcdef') for _ in range(6))
        try:
            is_inserted = await db.insert_one(db.tbl_link,
                                              old_link=old_link,
                                              new_link=new_link,
                                              user_id=message.from_id)
        except Exception as err:
            print(f'Bot link insertion error:\n{err}')

        if is_inserted:
            message.text = f'Your new link:\n{config.SLM_HOST}:80/{new_link}'
            await message.answer(message.text)


if __name__ == '__main__':
    if sys.version_info >= (3, 8) and sys.platform.lower().startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    executor.start_polling(dp, skip_updates=True)
