aiohttp_mako
============
.. image:: https://travis-ci.org/jettify/aiohttp_mako.svg?branch=master
    :target: https://travis-ci.org/jettify/aiohttp_mako


mako_ template renderer for `aiohttp.web`_ based on aiohttp_jinja2_. Library
supports almost same api and some my experiments with functions annotations.


Usage
-----

Before template rendering you have to setup *mako* template loader first:

.. code:: python

    app = web.Application(loop=loop)
    lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                output_encoding='utf-8',
                                default_filters=['decode.utf8'])

There are several possible ways of usage:

.. code:: python

    @aiohttp_mako.template('index.html')
    def handler(request):
        return {'greeting': 'Hello world!', 'title': 'mako example'}

or using python 3 annotations and decorator:

.. code:: python

    @aiohttp_mako.render_mako
    def handler(request) -> T('index.html'):
        return {'greeting': 'Hello world!', 'title': 'mako example'}

It is possible to get rid off ``@aiohttp_mako.render_mako`` decorator, but you
have to add middleware and this middleware must be first in processing
chain:

.. code:: python

    middlewares = [aiohttp_mako.mako_middleware_factory]
    app = web.Application(loop=self.loop, middlewares=middlewares)

    def handler(request) -> T('index.html'):
        return {'greeting': 'Hello world!', 'title': 'mako example'}

Example
-------

.. code:: python

    import asyncio
    import aiohttp

    import aiohttp_mako

    from aiohttp import web
    from aiohttp_mako import render_mako, T

    @render_mako
    @asyncio.coroutine
    def func(request) -> T('index.html'):
        return {'head': 'HEAD', 'text': 'text'}

    @asyncio.coroutine
    def go():
        app = web.Application(loop=loop)
        lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                    output_encoding='utf-8',
                                    default_filters=['decode.utf8'])

        template = "<html><body><h1>${head}</h1>${text}</body></html>"
        lookup.put_string('index.html', template)
        app.router.add_route('GET', '/', func)


        port = 8080
        srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', port)
        url = "http://127.0.0.1:{}/".format(port)

        resp = yield from aiohttp.request('GET', url, loop=loop)
        assert 200, resp.status
        txt = yield from resp.text()
        print(txt)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(go())


License
-------

``aiohttp_mako`` is offered under the Apache 2 license.


.. _mako: http://www.makotemplates.org/
.. _aiohttp_jinja2: https://github.com/aio-libs/aiohttp_jinja2
.. _aiohttp_web: http://aiohttp.readthedocs.org/en/latest/web.html
