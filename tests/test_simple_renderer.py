import asyncio
import pytest
from unittest import mock

import aiohttp
from aiohttp import web
from aiohttp.multidict import CIMultiDict
from mako.lookup import TemplateLookup

import aiohttp_mako


def make_request(app, method, path):
    headers = CIMultiDict()
    message = aiohttp.RawRequestMessage(method, path,
                                        aiohttp.HttpVersion(1, 1),
                                        headers, False, False)
    payload = mock.Mock()
    transport = mock.Mock()
    writer = mock.Mock()
    req = web.Request(app, message, payload, transport,
                      writer, 15)
    return req


def test_func(loop, create_server):

    @aiohttp_mako.template('tplt.html')
    @asyncio.coroutine
    def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    @asyncio.coroutine
    def go():
        app, url = yield from create_server()
        app.router.add_route('GET', '/', func)

        resp = yield from aiohttp.request('GET', url, loop=loop)
        assert 200 == resp.status
        txt = yield from resp.text()
        assert '<html><body><h1>HEAD</h1>text</body></html>' == txt
    loop.run_until_complete(go())


def test_meth(loop, create_server):

    class Handler:

        @aiohttp_mako.template('tplt.html')
        @asyncio.coroutine
        def meth(self, request):
            return {'head': 'HEAD', 'text': 'text'}

    @asyncio.coroutine
    def go():
        app, url = yield from create_server()
        handler = Handler()
        app.router.add_route('GET', '/', handler.meth)

        resp = yield from aiohttp.request('GET', url, loop=loop)
        txt = yield from resp.text()
        assert '<html><body><h1>HEAD</h1>text</body></html>' == txt
        assert 200 == resp.status

    loop.run_until_complete(go())


def test_render_template(loop, create_server):

    @asyncio.coroutine
    def func(request):
        return aiohttp_mako.render_template('tplt.html', request,
                                            {'head': 'HEAD',
                                             'text': 'text'})

    @asyncio.coroutine
    def go():
        app, url = yield from create_server()
        app.router.add_route('GET', '/', func)
        resp = yield from aiohttp.request('GET', url, loop=loop)
        assert 200 == resp.status
        txt = yield from resp.text()
        assert '<html><body><h1>HEAD</h1>text</body></html>' == txt

    loop.run_until_complete(go())


def test_convert_func_to_coroutine(loop, create_server):

    @aiohttp_mako.template('tplt.html')
    def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    @asyncio.coroutine
    def go():
        app, url = yield from create_server()
        app.router.add_route('GET', '/', func)
        resp = yield from aiohttp.request('GET', url, loop=loop)
        assert 200 == resp.status
        txt = yield from resp.text()
        assert '<html><body><h1>HEAD</h1>text</body></html>' == txt

    loop.run_until_complete(go())


def test_render_not_initialized(loop):

    @asyncio.coroutine
    def func(request):
        return aiohttp_mako.render_template('template', request, {})

    @asyncio.coroutine
    def go():
        app = web.Application(loop=loop)
        app.router.add_route('GET', '/', func)

        req = make_request(app, 'GET', '/')

        with pytest.raises(web.HTTPInternalServerError) as ctx:
            yield from func(req)

        assert "Template engine is not initialized, " \
               "call aiohttp_mako.setup(app_key={}) first" \
               "".format(aiohttp_mako.APP_KEY) == ctx.value.text

    loop.run_until_complete(go())


def test_template_not_found(loop):

    @asyncio.coroutine
    def func(request):
        return aiohttp_mako.render_template('template', request, {})

    @asyncio.coroutine
    def go():
        app = web.Application(loop=loop)
        aiohttp_mako.setup(app, input_encoding='utf-8',
                           output_encoding='utf-8',
                           default_filters=['decode.utf8'])

        app.router.add_route('GET', '/', func)

        req = make_request(app, 'GET', '/')

        with pytest.raises(web.HTTPInternalServerError) as ctx:
            yield from func(req)

        assert "Template 'template' not found" == ctx.value.text

    loop.run_until_complete(go())


def test_template_not_mapping(loop):

    @aiohttp_mako.template('tmpl.html')
    @asyncio.coroutine
    def func(request):
        return 'data'

    @asyncio.coroutine
    def go():
        app = web.Application(loop=loop)
        lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                    output_encoding='utf-8',
                                    default_filters=['decode.utf8'])

        tplt = "<html><body><h1>${head}</h1>${text}</body></html>"
        lookup.put_string('tmpl.html', tplt)

        app.router.add_route('GET', '/', func)

        req = make_request(app, 'GET', '/')

        with pytest.raises(web.HTTPInternalServerError) as ctx:
            yield from func(req)

        assert "context should be mapping, not" \
               " <class 'str'>" == ctx.value.text

    loop.run_until_complete(go())


def test_get_env(loop):

    @asyncio.coroutine
    def go():
        app = web.Application(loop=loop)
        lookup1 = aiohttp_mako.setup(app, input_encoding='utf-8',
                                     output_encoding='utf-8',
                                     default_filters=['decode.utf8'])

        lookup2 = aiohttp_mako.get_lookup(app)
        assert lookup1 is lookup2
        assert isinstance(lookup2, TemplateLookup)

    loop.run_until_complete(go())
