# -*- coding: utf-8 -*-
"""
    tests.helpers
    -------------

    Tests helpers
"""

from contextlib import contextmanager

from emmett.asgi.handlers import RequestContext, WSContext
from emmett.ctx import current
from emmett.serializers import Serializers
from emmett.testing.env import ScopeBuilder
from emmett.wrappers.request import Request
from emmett.wrappers.response import Response
from emmett.wrappers.websocket import Websocket

json_dump = Serializers.get_for('json')


class FakeRequestContext(RequestContext):
    def __init__(self, app, scope, *args):
        self.app = app
        self.request = Request(scope, None, None)
        self.response = Response()
        self.session = None


class FakeWSContext(WSContext):
    def __init__(self, app, scope, *args):
        self.app = app
        self.websocket = Websocket(
            scope,
            self.receive,
            self.send
        )
        self._receive_storage = []
        self._send_storage = []

    async def receive(self):
        return json_dump({'foo': 'bar'})

    async def send(self, data):
        self._send_storage.append(data)


@contextmanager
def current_ctx(path, app=None):
    builder = ScopeBuilder(path)
    token = current._init_(
        FakeRequestContext, app, builder.get_data()[0], None, None
    )
    yield current
    current._close_(token)


@contextmanager
def ws_ctx(path, app=None):
    builder = ScopeBuilder(path)
    scope_data = builder.get_data()[0]
    scope_data.update(type='websocket', scheme='wss')
    token = current._init_(FakeWSContext, app, scope_data, None, None)
    yield current
    current._close_(token)
