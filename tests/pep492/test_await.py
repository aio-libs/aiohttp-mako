import aiohttp
import aiohttp_mako


def test_func(loop, create_server):

    @aiohttp_mako.template('tplt.html')
    async def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    async def go():
        app, url = await create_server()
        app.router.add_route('GET', '/', func)

        resp = await aiohttp.request('GET', url, loop=loop)
        assert 200 == resp.status
        txt = await resp.text()
        assert '<html><body><h1>HEAD</h1>text</body></html>' == txt
    loop.run_until_complete(go())
