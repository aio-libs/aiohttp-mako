import aiohttp_mako


async def test_func(app, test_client):

    @aiohttp_mako.template('tplt.html')
    async def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    app.router.add_route('GET', '/', func)

    client = await test_client(app)

    resp = await client.get('/')
    assert 200 == resp.status
    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt
