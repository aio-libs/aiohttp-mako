aiohttp_mako
============
.. image:: https://travis-ci.org/jettify/aiohttp_mako.svg?branch=master
    :target: https://travis-ci.org/jettify/aiohttp_mako


mako_ template renderer for `aiohttp.web`__ based on aiohttp_jinja2_. Library
supports almost same api and some my experiments with functions annotations.

__ aiohttp_web_

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

or using python 3 annotations and decorator. This is experimental feature
I just wanted to play with annotations, and will be removed I guess:

.. code:: python

    @aiohttp_mako.render_mako
    def handler(request) -> T('index.html'):
        return {'greeting': 'Hello world!', 'title': 'mako example'}

It is possible to pretty print python and template exceptions using
mako's html_error_template_ function. You have to set ``DEBUG_TEMPLATE`` key
in application:

.. code:: python
    app = web.Application(loop=loop)
    app['DEBUG_TEMPLATE'] = True

Example
-------

.. code:: python

    import asyncio
    import aiohttp_mako
    from aiohttp import web


    @aiohttp_mako.template('index.html')
    def func(request):
        return {'head': 'aiohttp_mako', 'text': 'Hello World!'}


    @aiohttp_mako.template('index.html')
    def bug_in_template(request):
        # text key missing intentionally
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


License
-------

``aiohttp_mako`` is offered under the Apache 2 license.


.. _mako: http://www.makotemplates.org/
.. _aiohttp_jinja2: https://github.com/aio-libs/aiohttp_jinja2
.. _aiohttp_web: http://aiohttp.readthedocs.org/en/latest/web.html
.. _html_error_template: http://docs.makotemplates.org/en/latest/usage.html#mako.exceptions.html_error_template
