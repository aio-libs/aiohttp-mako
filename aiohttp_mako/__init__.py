import asyncio
import functools
import sys
from collections import Mapping

from aiohttp import web
from mako.lookup import TemplateLookup
from mako.exceptions import TemplateLookupException, text_error_template

__version__ = '0.3.0'

__all__ = ('setup', 'get_lookup', 'render_template', 'template',
           'render_string')


APP_KEY = 'aiohttp_mako_lookup'
APP_CONTEXT_PROCESSORS_KEY = 'aiohttp_mako_context_processors'
REQUEST_CONTEXT_KEY = 'aiohttp_mako_context'


def setup(app, *args, app_key=APP_KEY, context_processors=(), **kwargs):
    app[app_key] = TemplateLookup(*args, **kwargs)
    if context_processors:
        app[APP_CONTEXT_PROCESSORS_KEY] = context_processors
        app.middlewares.append(context_processors_middleware)
    return app[app_key]


def get_lookup(app, *, app_key=APP_KEY):
    return app.get(app_key)


def render_string(template_name, request, context, *, app_key):
    lookup = request.app.get(app_key)

    if lookup is None:
        raise web.HTTPInternalServerError(
            text=("Template engine is not initialized, "
                  "call aiohttp_mako.setup(app_key={}) first"
                  "".format(app_key)))
    try:
        template = lookup.get_template(template_name)
    except TemplateLookupException as e:
        raise web.HTTPInternalServerError(
            text="Template '{}' not found".format(template_name)) from e
    if not isinstance(context, Mapping):
        raise web.HTTPInternalServerError(
            text="context should be mapping, not {}".format(type(context)))
    if request.get(REQUEST_CONTEXT_KEY):
        context = dict(request[REQUEST_CONTEXT_KEY], **context)
    try:
        text = template.render_unicode(**context)
    except Exception:  # pragma: no cover
        exc_info = sys.exc_info()
        errtext = text_error_template().render(
            error=exc_info[1],
            traceback=exc_info[2])
        exc = MakoRenderingException(errtext).with_traceback(exc_info[2])
        raise exc

    return text


def render_template(template_name, request, context, *,
                    app_key=APP_KEY, encoding='utf-8'):
    response = web.Response()
    text = render_string(template_name, request, context, app_key=app_key)
    response.content_type = 'text/html'
    response.charset = encoding
    response.text = text
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
            context = yield from coro(*args)
            request = args[-1]
            response = render_template(template_name, request, context,
                                       app_key=app_key, encoding=encoding)
            response.set_status(status)
            return response
        return wrapped
    return wrapper


class MakoRenderingException(Exception):
    """Mako rendering exceptions with error """


@asyncio.coroutine
def context_processors_middleware(app, handler):
    @asyncio.coroutine
    def middleware(request):
        request[REQUEST_CONTEXT_KEY] = {}
        for processor in app[APP_CONTEXT_PROCESSORS_KEY]:
            request[REQUEST_CONTEXT_KEY].update(
                (yield from processor(request)))
        return (yield from handler(request))
    return middleware


@asyncio.coroutine
def request_processor(request):
    return {'request': request}
