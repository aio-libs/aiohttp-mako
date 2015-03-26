import asyncio
import functools
from mako.exceptions import html_error_template
from aiohttp import web
from mako.lookup import TemplateLookup
from functools import partial


__version__ = '0.0.1'

__all__ = ('setup', 'get_lookup', 'render_template', 'template')


APP_KEY = 'aiohttp_mako_lookup'


def setup(app, *args, app_key=APP_KEY, **kwargs):
    app[app_key] = TemplateLookup(*args, **kwargs)
    return app[app_key]


def get_lookup(app, *, app_key=APP_KEY):
    return app.get(app_key)


def _render_template(template_name, request, response, context, *,
                     app_key, encoding):
    lookup = request.app.get(app_key)
    if lookup is None:
        raise web.HTTPInternalServerError(
            text=("Template engine is not initialized, "
                  "call aiohttp_mako.setup(app_key={}) first"
                  "".format(app_key)))
    try:
        template = lookup.get_template(template_name)
        body = template.render(**context)
    except:
        if request.app.get('DEBUG_TEMPLATE'):
            error_body = html_error_template().render()
            raise web.HTTPInternalServerError(body=error_body)
        raise
    response.content_type = 'text/html'
    response.charset = encoding
    response.body = body


def render_template(template_name, request, context, *,
                    app_key=APP_KEY, encoding='utf-8'):
    response = web.Response()
    _render_template(template_name, request, response, context,
                     app_key=app_key, encoding=encoding)
    return response


def template(template_name, *, app_key=APP_KEY, encoding='utf-8', status=200):

    def wrapper(func):
        @asyncio.coroutine
        @functools.wraps(func)
        def wrapped(*args):
            if asyncio.iscoroutinefunction(func):
                coro = func
            else:
                coro = asyncio.coroutine(func)
            response = web.Response()
            context = yield from coro(*args)
            request = args[-1]
            _render_template(template_name, request, response, context,
                             app_key=app_key, encoding=encoding)
            response.set_status(status)
            return response
        return wrapped
    return wrapper


def render_mako(func):

    @asyncio.coroutine
    @functools.wraps(func)
    def wrapped(*args):
        if asyncio.iscoroutinefunction(func):
            coro = func
        else:
            coro = asyncio.coroutine(func)
        annotations = func.__annotations__
        if not annotations.get('return'):
            return (yield from coro)

        render = annotations.get('return')

        context = yield from coro(*args)
        request = args[-1]

        response = render(request, context)
        return response
    return wrapped


def T(template_name):
    return partial(render_template, template_name)
