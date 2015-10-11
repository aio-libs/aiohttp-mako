aiohttp_mako
============
.. image:: https://travis-ci.org/aio-libs/aiohttp_mako.svg?branch=master
    :target: https://travis-ci.org/aio-libs/aiohttp_mako
.. image:: https://coveralls.io/repos/aio-libs/aiohttp_mako/badge.svg
    :target: https://coveralls.io/r/aio-libs/aiohttp_mako

mako_ template renderer for `aiohttp.web`__ based on aiohttp_jinja2_. Library
has almost same api and support python 3.5 (PEP492_) syntax. It is used in aiohttp_debugtoolbar_.

__ aiohttp_web_


Example 
-------

.. code:: python

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

        handler = app.make_handler()
        srv = await loop.create_server(handler, '127.0.0.1', 8080)
        print("Server started at http://127.0.0.1:8080")
        return srv, handler

    loop = asyncio.get_event_loop()
    srv, handler = loop.run_until_complete(init(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(handler.finish_connections())


License
-------

``aiohttp_mako`` is offered under the Apache 2 license.


.. _mako: http://www.makotemplates.org/
.. _aiohttp_jinja2: https://github.com/aio-libs/aiohttp_jinja2
.. _aiohttp_web: http://aiohttp.readthedocs.org/en/latest/web.html
.. _html_error_template: http://docs.makotemplates.org/en/latest/usage.html#mako.exceptions.html_error_template
.. _aiohttp_debugtoolbar: https://github.com/aio-libs/aiohttp_debugtoolbar
.. _PEP492: https://www.python.org/dev/peps/pep-0492/

