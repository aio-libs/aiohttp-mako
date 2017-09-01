import asyncio
import aiohttp_mako
from aiohttp import web


@aiohttp_mako.template('index.html')
async def func(request):
    return {'head': 'aiohttp_mako', 'text': 'Hello World!'}


async def init(loop):
    app = web.Application(loop=loop)
    lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                output_encoding='utf-8',
                                default_filters=['decode.utf8'])
    template = """<html><body><h1>${head}</h1>${text}</body></html>"""
    lookup.put_string('index.html', template)
    app.router.add_route('GET', '/', func)
    return app

loop = asyncio.get_event_loop()
app = loop.run_until_complete(init(loop))
web.run_app(app, host='127.0.0.1', port=9000)
