import logging
from copy import copy
from socketserver import BaseRequestHandler, BaseServer
from typing import Any

from pruina.socket.handler.GeneralHandler import general_handle
from pruina.socket.util.general import CachedHooks, Properties, Resources

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)


class PruinaHandler(BaseRequestHandler):
    def __init__(self, request: Any, client_address: Any, server: BaseServer):
        super().__init__(request, client_address, server)
        self.resources: Resources = None
        self.local_resources: Resources = None
        self.properties: Properties = None
        self.local_properties: Properties = None
        self.server_hooks: CachedHooks = None
        self.hooks: CachedHooks = None
        self.server_name: str = None
        self.event_loop = None

    def setup(self):
        super().setup()
        self.server_name: str = getattr(self.server, "name")
        self.resources: Resources = getattr(self.server, "resources")
        self.local_resources: Resources = copy(getattr(self.server, "local_resources"))
        self.properties: Properties = getattr(self.server, "properties")
        self.local_properties: Properties = copy(getattr(self.server, "local_properties"))
        self.server_hooks: CachedHooks = getattr(self.server, "hooks")
        try:
            self.before_handle = getattr(self.server, "before_handle")
        except:
            pass
        try:
            self.after_handle = getattr(self.server, "after_handle")
        except:
            pass
        try:
            self.except_handle = getattr(self.server, "except_handle")
        except:
            pass
        self.hooks: CachedHooks = CachedHooks(parent=self.server_hooks)

    def before_handle(self, _type, _data, **kwargs):
        pass

    def after_handle(self, _type, _data, **kwargs):
        pass

    def finish(self):
        pass

    def close(self):
        self.request.close()

    def handle(self):
        general_handle(self.request, self.hooks, self, before=self.before_handle, after=self.after_handle,
                       except_handle=self.except_handle)

    def send(self, _type, data: bytes, _id=0):
        from pruina.socket.handler.util.util import send as __send
        __send(self.request, _type, data, _id=_id)

    def except_handle(self, e: Exception, handler):
        import traceback
        logging.error(traceback.format_exc() + "\n" + str(e))
