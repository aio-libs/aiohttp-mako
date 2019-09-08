.. aiohttp_mako documentation master file, created by
   sphinx-quickstart on Sun Mar 22 12:04:15 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

aiohttp_mako
============


mako_ template renderer for `aiohttp.web`__. `aiohttp_mako` based on
:term:`aiohttp_jinja2`. Library has almost same api and it is used in
aiohttp_debugtoolbar_.


.. _mako: http://www.makotemplates.org/
.. _aiohttp_debugtoolbar: https://github.com/aio-libs/aiohttp_debugtoolbar

.. _aiohttp_web: http://aiohttp.readthedocs.org/en/latest/web.html

__ aiohttp_web_


Usage
-----

Before template rendering you have to setup *mako* templates location first::

    app = web.Application(loop=loop)
    lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                output_encoding='utf-8',
                                default_filters=['decode.utf8'])


After that you may to use template engine in your *web-handlers*. The
most convinient way is to decorate *web-handler*::

    @aiohttp_mako.template('tmpl.html')
    async def handler(request):
        return {'head': 'aiohttp_mako', 'text': 'Hello World!'}

On handler call the ``aiohttp_mako.template`` decorator will pass
returned dictionary ``{'head': 'aiohttp_mako', 'text': 'Hello World!'}`` into
template named ``"tmpl.html"`` for getting resulting HTML text.

If you need more complex processing (set response headers for example)
you may call ``render_template`` function::

    async def handler(request):
        context = {'head': 'aiohttp_mako', 'text': 'Hello World!'}
        response = aiohttp_mako.render_template('tmpl.html',
                                                  request,
                                                  context)
        response.headers['Content-Language'] = 'ru'
        return response

.. _aiohttp_mako-reference:


Context processors
~~~~~~~~~~~~~~~~~~

Context processors is a way to add some variables to each
template context. It calculates variables on each request.

Context processors is following last-win strategy.
Therefore a context processor could rewrite variables delivered with
previous one.

In order to use context processors create required processors::

    async def foo_processor(request):
        return {'foo': 'bar'}

And pass them into :func:`setup`::

    aiohttp_mako.setup(
        app,
        context_processors=[foo_processor,
                            aiohttp_mako.request_processor],
        loader=loader)

As you can see, there is a built-in :func:`request_processor`, which
adds current :class:`aiohttp.web.Request` into context of templates
under ``'request'`` name.


Example
-------
::

    import asyncio
    import aiohttp_mako
    from aiohttp import web


    @aiohttp_mako.template('index.html')
    def func(request):
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


Reference
---------

.. highlight:: python

.. module:: aiohttp_mako

.. currentmodule:: aiohttp_mako


.. data:: APP_KEY

   The key name in :class:`aiohttp.web.Application` dictionary,
   ``'aiohttp_mako_environment'`` for storing :term:`mako`
   template lookup object (:class:`mako.lookup.TemplateLookup`).

   Usually you don't need to operate with *application* manually, left
   it to :mod:`aiohttp_mako` functions.


.. function:: get_lookup(app, app_key=APP_KEY)

   Get from `aiohttp` application instance :class:`mako.lookup.TemplateLookup`
   object

   :param app: (:class:`aiohttp.web.Application` instance).
   :param app_key: is an optional key for application dict, :const:`APP_KEY`
        by default.

   :returns: :class:`mako.lookup.TemplateLookup` object which has stored in the
        :class:`aiohttp.web.Application`

.. function:: render_template(template_name, request, context, *, \
                              app_key=APP_KEY)

    Return :class:`aiohttp.web.Response` which contains template
    *template_name* filled with *context*.

    :param template_name: name of template plus relative path.
    :param request: :class:`aiohttp.web.Request` object
    :param context: dictionary object required to render current template
    :param app_key: is an optional key for application dict, :const:`APP_KEY`
        by default.



.. function:: setup(app, *args, app_key=APP_KEY, **kwargs)

   Return :class:`mako.lookup.TemplateLookup` instance, which contains
   collections of templates.

   :param app: (:class:`aiohttp.web.Application` instance).
   :param app_key: is an optional key for application dict, :const:`APP_KEY`
   by default.

License
-------

``aiohttp_mako`` is offered under the Apache 2 license.

Glossary
--------

.. if you add new entries, keep the alphabetical sorting!

.. glossary::

   aiohttp_jinja2

       `jinja2` template renderer for `aiohttp.web`.

       See https://github.com/aio-libs/aiohttp_jinja2/

   jinja2

       A modern and designer-friendly templating language for Python.

       See http://jinja.pocoo.org/

   mako

       Mako is a template library written in Python. It provides a familiar,
       non-XML syntax which compiles into Python modules for maximum
       performance.

       See http://www.makotemplates.org/

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
