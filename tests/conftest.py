import asyncio
import socket
import sys

import pytest

import aiohttp_mako
from aiohttp import web


def pytest_ignore_collect(path, config):
    if 'pep492' in str(path):
        if sys.version_info < (3, 5, 0):
            return True


@pytest.fixture
def unused_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture
def loop(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    def fin():
        loop.close()

    request.addfinalizer(fin)
    return loop


@pytest.yield_fixture
def create_server(loop, unused_port):
    app = app_handler = srv = None

    @asyncio.coroutine
    def create(*, debug=False, **kw):
        nonlocal app, app_handler, srv
        app = web.Application(loop=loop)
        lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                    output_encoding='utf-8',
                                    default_filters=['decode.utf8'])

        tplt = "<html><body><h1>${head}</h1>${text}</body></html>"
        lookup.put_string('tplt.html', tplt)

        app_handler = app.make_handler(debug=debug, keep_alive_on=False)
        port = unused_port
        srv = yield from loop.create_server(app_handler, '127.0.0.1', port)
        url = "http://127.0.0.1:{}/".format(port)
        return app, url

    yield create

    @asyncio.coroutine
    def finish():
        yield from app_handler.finish_connections()
        yield from app.finish()
        srv.close()
        yield from srv.wait_closed()

    loop.run_until_complete(finish())
