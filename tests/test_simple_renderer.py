import pytest

from aiohttp import web
from aiohttp.test_utils import make_mocked_request
from mako.lookup import TemplateLookup

import aiohttp_mako


async def test_func(app, aiohttp_client):

    @aiohttp_mako.template('tplt.html')
    async def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    app.router.add_route('GET', '/', func)

    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert 200 == resp.status
    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


async def test_meth(app, aiohttp_client):

    class Handler:

        @aiohttp_mako.template('tplt.html')
        async def meth(self, request):
            return {'head': 'HEAD', 'text': 'text'}

    handler = Handler()
    app.router.add_route('GET', '/', handler.meth)

    client = await aiohttp_client(app)

    resp = await client.get('/')
    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt
    assert 200 == resp.status


async def test_render_template(app, aiohttp_client):

    async def func(request):
        return aiohttp_mako.render_template('tplt.html', request,
                                            {'head': 'HEAD',
                                             'text': 'text'})

    app.router.add_route('GET', '/', func)
    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert 200 == resp.status
    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


async def test_render_not_initialized():

    async def func(request):
        return aiohttp_mako.render_template('template', request, {})

    app = web.Application()
    app.router.add_route('GET', '/', func)

    req = make_mocked_request('GET', '/', app=app)

    with pytest.raises(web.HTTPInternalServerError) as ctx:
        await func(req)

    assert "Template engine is not initialized, " \
        "call aiohttp_mako.setup(app_key={}) first" \
        "".format(aiohttp_mako.APP_KEY) == ctx.value.text


async def test_template_not_found():

    app = web.Application()
    aiohttp_mako.setup(app, input_encoding='utf-8',
                       output_encoding='utf-8',
                       default_filters=['decode.utf8'])

    req = make_mocked_request('GET', '/', app=app)

    with pytest.raises(web.HTTPInternalServerError) as ctx:
        aiohttp_mako.render_template('template', req, {})

    assert "Template 'template' not found" == ctx.value.text


async def test_template_not_mapping():

    @aiohttp_mako.template('tmpl.html')
    async def func(request):
        return 'data'

    app = web.Application()
    lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                output_encoding='utf-8',
                                default_filters=['decode.utf8'])

    tplt = "<html><body><h1>${head}</h1>${text}</body></html>"
    lookup.put_string('tmpl.html', tplt)

    app.router.add_route('GET', '/', func)

    req = make_mocked_request('GET', '/', app=app)

    with pytest.raises(web.HTTPInternalServerError) as ctx:
        await func(req)

    assert "context should be mapping, not" \
           " <class 'str'>" == ctx.value.text


async def test_get_env():

    app = web.Application()
    lookup1 = aiohttp_mako.setup(app, input_encoding='utf-8',
                                 output_encoding='utf-8',
                                 default_filters=['decode.utf8'])

    lookup2 = aiohttp_mako.get_lookup(app)
    assert lookup1 is lookup2
    assert isinstance(lookup2, TemplateLookup)
