import asyncio
import logging
from socketserver import BaseRequestHandler, BaseServer
from typing import Any

from pruina.socket.handler.util.General import CachedHooks, Resource, Properties, Resources
from copy import copy

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)


class MessageHookRequestHandler(BaseRequestHandler):
    def __init__(self, request: Any, client_address: Any, server: BaseServer):
        super().__init__(request, client_address, server)
        self.resources: Resources = None
        self.local_resources: Resources = None
        self.properties: Properties = None
        self.local_properties: Properties = None
        self.server_hooks: CachedHooks = None
        self.hooks: CachedHooks = None
        self.server_name: str = None

    def setup(self):
        super().setup()
        self.server_name: str = getattr(self.server, "name")
        self.resources: Resources = getattr(self.server, "resources")
        self.local_resources: Resources = copy(getattr(self.server, "local_resources"))
        self.properties: Properties = getattr(self.server, "properties")
        self.local_properties: Properties = copy(getattr(self.server, "local_properties"))
        self.server_hooks: CachedHooks = getattr(self.server, "hooks")
        self.hooks: CachedHooks = CachedHooks(parent=self.server_hooks)

    def handle(self):
        logging.info(f'{self.client_address[0]}:{self.client_address[1]} connected.')
        self._handle()

    def finish(self):
        logging.info(f'{self.client_address[0]}:{self.client_address[1]} disconnected.')

    def _handle(self):
        from pruina.socket.handler.GeneralHandler import general_handle
        general_handle(self.request, self.hooks, self)

    def send(self, _type, data: bytes, _id=0):
        from pruina.socket.handler.util.Util import send as __send
        __send(self.request, _type, data, _id=_id)
