import asyncio

from aiohttp import web

import aiohttp_mako


def create_app(context_processors):
    app = web.Application()
    lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                output_encoding='utf-8',
                                default_filters=['decode.utf8'],
                                context_processors=context_processors)

    tplt = "<html><body><h1>${head}</h1>${text}</body></html>"
    lookup.put_string('tplt.html', tplt)
    return app


async def test_simple(aiohttp_client):

    async def context_processor(request):
        return {'text': request.path}

    app = create_app([context_processor])

    @aiohttp_mako.template('tplt.html')
    async def func(request):
        return {'head': 'HEAD'}

    app.router.add_route('GET', '/', func)

    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert 200 == resp.status
    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>/</body></html>' == txt


async def test_overwrite(aiohttp_client):

    async def context_processor1(request):
        return {'head': 'HEAD', 'text': 'foo'}

    async def context_processor2(request):
        return {'text': 'bar'}

    app = create_app([context_processor1, context_processor2])

    @aiohttp_mako.template('tplt.html')
    async def func(request):
        return {}

    app.router.add_route('GET', '/', func)

    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert 200 == resp.status
    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>bar</body></html>' == txt


async def test_overwrite_primary_context(aiohttp_client):

    async def context_processor(request):
        return {'text': 'foo'}

    app = create_app([context_processor])

    @aiohttp_mako.template('tplt.html')
    async def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    app.router.add_route('GET', '/', func)

    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert 200 == resp.status
    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


async def test_request_processor(aiohttp_client):

    app = web.Application()
    lookup = aiohttp_mako.setup(
        app,
        input_encoding='utf-8',
        output_encoding='utf-8',
        default_filters=['decode.utf8'],
        context_processors=[aiohttp_mako.request_processor]
    )

    tplt = "<html><body><h1>${head}</h1>path=${request.path}</body></html>"
    lookup.put_string('tplt.html', tplt)

    @aiohttp_mako.template('tplt.html')
    async def func(request):
        return {'head': 'HEAD'}

    app.router.add_route('GET', '/', func)

    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert 200 == resp.status
    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>path=/</body></html>' == txt
