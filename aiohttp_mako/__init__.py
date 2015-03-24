import asyncio
import functools
from mako.exceptions import TemplateLookupException
from aiohttp import web
from mako.lookup import TemplateLookup

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
    except TemplateLookupException:
        raise web.HTTPInternalServerError(
            text="Template {} not found".format(template_name))
    body = template.render(**context)
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
