aiohttp_mako
============
.. image:: https://travis-ci.com/aio-libs/aiohttp-mako.svg?branch=master
    :target: https://travis-ci.com/aio-libs/aiohttp-mako
.. image:: https://codecov.io/gh/aio-libs/aiohttp-mako/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/aio-libs/aiohttp-mako
.. image:: https://img.shields.io/pypi/v/aiohttp-mako.svg
    :target: https://pypi.python.org/pypi/aiohttp-mako
.. image:: https://badges.gitter.im/Join%20Chat.svg
    :target: https://gitter.im/aio-libs/Lobby
    :alt: Chat on Gitter


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
        return app

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop))
    web.run_app(app, host='127.0.0.1', port=9000)


License
-------

``aiohttp_mako`` is offered under the Apache 2 license.


.. _mako: http://www.makotemplates.org/
.. _aiohttp_jinja2: https://github.com/aio-libs/aiohttp_jinja2
.. _aiohttp_web: http://aiohttp.readthedocs.org/en/latest/web.html
.. _html_error_template: http://docs.makotemplates.org/en/latest/usage.html#mako.exceptions.html_error_template
.. _aiohttp_debugtoolbar: https://github.com/aio-libs/aiohttp_debugtoolbar
.. _PEP492: https://www.python.org/dev/peps/pep-0492/

