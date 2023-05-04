import asyncio
import sys

from aiohttp import web
import aiohttp_jinja2
import jinja2
import random

import database as db
import config


class HomeView(web.View):

    @aiohttp_jinja2.template('home.html')
    async def get(self):
        title = 'Welcome to awesome short-link maker'
        return {'title': title}

    @aiohttp_jinja2.template('link-result.html')
    async def post(self):
        post_data = await self.request.post()
        actual_port = self.request.url.port
        old_link = post_data['old_link']

        if not old_link:
            err_message = 'Field of old link is not populated'
            return {'err_message': err_message}

        if not (old_link.startswith('http://') or old_link.startswith('https://')):
            err_message = 'You have entered the wrong URL. URL must starts with "http://"' \
                          'or "https://"'
            return {'err_message': err_message}

        new_link = ''.join(random.choice('abcdef0123456789abcdef') for _ in range(6))

        await db.insert_one(db.tbl_link,
                            old_link=old_link,
                            new_link=new_link)

        return {'title': 'Your new link',
                'old_link': old_link,
                'new_link': f'{config.SLM_HOST}:{actual_port}/' + new_link}


class RedirectToNewLink(web.View):
    async def get(self):
        new_link = self.request.match_info['new_link']
        long_url = await db.select_one(db.tbl_link, link=new_link)

        if long_url is None:
            raise web.HTTPNotFound(text=f'The link of {new_link} not found')
        raise web.HTTPFound(long_url)


if __name__ == '__main__':
    if sys.version_info >= (3, 8) and sys.platform.lower().startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates/'))
    app.add_routes([web.get('/', HomeView),
                    web.post('/', HomeView),
                    web.get('/{new_link}', RedirectToNewLink)])
    web.run_app(app)
