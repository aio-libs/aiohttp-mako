import asyncio
import aiohttp_mako
from aiohttp import web


@aiohttp_mako.template('index.html')
def func(request):
    return {'head': 'aiohttp_mako', 'text': 'Hello World!'}


@aiohttp_mako.template('index.html')
def bug_in_template(request):
    # text key missing intentionally to show rich traceback from mako
    return {'head': 'aiohttp_mako'}


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                output_encoding='utf-8',
                                default_filters=['decode.utf8'])
    template = """<html><body><h1>${head}</h1>${text}</body></html>"""
    template_bug = """<html><body><h1>${head}</h1>${text}</body></html>"""

    lookup.put_string('index.html', template)
    lookup.put_string('bug.html', template_bug)

    app.router.add_route('GET', '/', func)
    app.router.add_route('GET', '/bug', bug_in_template)
    app['DEBUG_TEMPLATE'] = True

    handler = app.make_handler()
    srv = yield from loop.create_server(handler, '127.0.0.1', 8080)
    print("Server started at http://127.0.0.1:8080")
    return srv, handler

loop = asyncio.get_event_loop()
srv, handler = loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(handler.finish_connections())
