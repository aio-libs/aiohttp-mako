import sys

import pytest

import aiohttp_mako
from aiohttp import web


def pytest_ignore_collect(path, config):
    if 'pep492' in str(path):
        if sys.version_info < (3, 5, 0):
            return True


@pytest.fixture
def app(loop):
    app = web.Application(loop=loop)
    lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                output_encoding='utf-8',
                                default_filters=['decode.utf8'])

    tplt = "<html><body><h1>${head}</h1>${text}</body></html>"
    lookup.put_string('tplt.html', tplt)
    return app
