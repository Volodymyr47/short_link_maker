from aiohttp import web
import aiohttp_jinja2
import jinja2
import random
import json
import os


class HomeView(web.View):

    @aiohttp_jinja2.template('home.html')
    async def get(self):
        title = 'Welcome to awesome short-link maker'
        return {'title':title}

    @aiohttp_jinja2.template('link-result.html')
    async def post(self):
        if not os.path.isfile('links.json'):
            with open('links.json', 'w') as file:
                file.write("{}")

        post_data = await self.request.post()
        old_link = post_data['old_link']
        if not old_link:
            err_message = 'Field of old link is not populated'
            return {'err_message': err_message}
        new_link = ''.join(random.choice('abcdef0123456789abcdef') for _ in range(6))

        with open('links.json', 'r') as rf:
            line = json.load(rf)
            line.update({new_link: old_link})
        with open('links.json', 'w') as wf:
            json.dump(line, wf, indent=2)
        return {'title': 'Your new link',
                'old_link': old_link,
                'new_link': 'http://127.0.0.1:8080/'+new_link}


class RedirectToNewLink(web.View):
    async def get(self):
        new_link = self.request.match_info['new_link']
        with open('links.json') as f:
            file_data = json.loads(f.read())
        long_url = file_data.get(new_link)

        if long_url is None:
            raise web.HTTPNotFound(text=f'The link of {new_link} not found')
        raise web.HTTPFound(long_url)


app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates/'))
app.add_routes([web.get('/', HomeView),
                web.post('/', HomeView),
                web.get('/{new_link}', RedirectToNewLink)])
web.run_app(app)
