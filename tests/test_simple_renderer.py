import asyncio
import pytest

from aiohttp import web
from aiohttp.test_utils import make_mocked_request
from mako.lookup import TemplateLookup

import aiohttp_mako


@asyncio.coroutine
def test_func(app, test_client):

    @aiohttp_mako.template('tplt.html')
    @asyncio.coroutine
    def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    app.router.add_route('GET', '/', func)

    client = yield from test_client(app)
    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


@asyncio.coroutine
def test_meth(app, test_client):

    class Handler:

        @aiohttp_mako.template('tplt.html')
        @asyncio.coroutine
        def meth(self, request):
            return {'head': 'HEAD', 'text': 'text'}

    handler = Handler()
    app.router.add_route('GET', '/', handler.meth)

    client = yield from test_client(app)

    resp = yield from client.get('/')
    txt = yield from resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt
    assert 200 == resp.status


@asyncio.coroutine
def test_render_template(app, test_client):

    @asyncio.coroutine
    def func(request):
        return aiohttp_mako.render_template('tplt.html', request,
                                            {'head': 'HEAD',
                                             'text': 'text'})

    app.router.add_route('GET', '/', func)
    client = yield from test_client(app)
    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


@asyncio.coroutine
def test_convert_func_to_coroutine(app, test_client):

    @aiohttp_mako.template('tplt.html')
    def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    app.router.add_route('GET', '/', func)
    client = yield from test_client(app)
    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


@asyncio.coroutine
def test_render_not_initialized(loop):

    @asyncio.coroutine
    def func(request):
        return aiohttp_mako.render_template('template', request, {})

    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', func)

    req = make_mocked_request('GET', '/', app=app)

    with pytest.raises(web.HTTPInternalServerError) as ctx:
        yield from func(req)

    assert "Template engine is not initialized, " \
        "call aiohttp_mako.setup(app_key={}) first" \
        "".format(aiohttp_mako.APP_KEY) == ctx.value.text


@asyncio.coroutine
def test_template_not_found(loop):

    app = web.Application(loop=loop)
    aiohttp_mako.setup(app, input_encoding='utf-8',
                       output_encoding='utf-8',
                       default_filters=['decode.utf8'])

    req = make_mocked_request('GET', '/', app=app)

    with pytest.raises(web.HTTPInternalServerError) as ctx:
        aiohttp_mako.render_template('template', req, {})

    assert "Template 'template' not found" == ctx.value.text


@asyncio.coroutine
def test_template_not_mapping(loop):

    @aiohttp_mako.template('tmpl.html')
    @asyncio.coroutine
    def func(request):
        return 'data'

    app = web.Application(loop=loop)
    lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                output_encoding='utf-8',
                                default_filters=['decode.utf8'])

    tplt = "<html><body><h1>${head}</h1>${text}</body></html>"
    lookup.put_string('tmpl.html', tplt)

    app.router.add_route('GET', '/', func)

    req = make_mocked_request('GET', '/', app=app)

    with pytest.raises(web.HTTPInternalServerError) as ctx:
        yield from func(req)

    assert "context should be mapping, not" \
           " <class 'str'>" == ctx.value.text


@asyncio.coroutine
def test_get_env(loop):

    app = web.Application(loop=loop)
    lookup1 = aiohttp_mako.setup(app, input_encoding='utf-8',
                                 output_encoding='utf-8',
                                 default_filters=['decode.utf8'])

    lookup2 = aiohttp_mako.get_lookup(app)
    assert lookup1 is lookup2
    assert isinstance(lookup2, TemplateLookup)
