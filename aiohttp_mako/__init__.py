import asyncio
import functools
from collections import Mapping

from aiohttp import web
from mako.lookup import TemplateLookup
from mako.exceptions import TemplateLookupException, text_error_template
import sys

__version__ = '0.0.1'
__all__ = ('setup', 'get_lookup', 'render_template', 'template',
           'render_string')


APP_KEY = 'aiohttp_mako_lookup'


def setup(app, *args, app_key=APP_KEY, **kwargs):
    app[app_key] = TemplateLookup(*args, **kwargs)
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
    except TemplateLookupException:
        raise web.HTTPInternalServerError(
            text="Template '{}' not found".format(template_name))
    if not isinstance(context, Mapping):
        raise web.HTTPInternalServerError(
            text="context should be mapping, not {}".format(type(context)))
    try:
        text = template.render_unicode(**context)
    except Exception:  # pragma: no cover
        try:
            exc_info = sys.exc_info()
            errtext = text_error_template().render(
                error=exc_info[1],
                traceback=exc_info[2])
            exc = MakoRenderingException(errtext).with_traceback(exc_info[2])
            raise exc
        finally:
            del exc_info

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
