import sys

import pytest

import aiohttp_mako
from aiohttp import web


@pytest.fixture
def app():
    app = web.Application()
    lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                output_encoding='utf-8',
                                default_filters=['decode.utf8'])

    tplt = "<html><body><h1>${head}</h1>${text}</body></html>"
    lookup.put_string('tplt.html', tplt)
    return app
