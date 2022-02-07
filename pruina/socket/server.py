import logging
import socket
from socketserver import ThreadingTCPServer

from pruina.socket.handler.PruinaHandler import PruinaHandler
from pruina.socket.util.general import Properties, Resources, CachedHooks

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)


class PruinaSocketServer:
    def __init__(self, host: str = socket.gethostbyname(socket.gethostname()), port: int = 50003,
                 name: str = 'server',
                 hooks_thread_pool_size=2,
                 daemon_threads: bool = True):
        super().__init__()
        self.name: str = name
        self.server: ThreadingTCPServer = ThreadingTCPServer((host, port), PruinaHandler)
        self.properties: Properties = Properties()
        self.local_properties: Properties = Properties()
        self.resources: Resources = Resources()
        self.local_resources: Resources = Resources()
        self.hooks: CachedHooks = CachedHooks(thread_pool_size=hooks_thread_pool_size)
        self.server.daemon_threads = daemon_threads
        self.__is_init: bool = False
        self.__transfer_data_list: list = list()

    def add_transfer(self, name: str, data):
        self.__transfer_data_list.append((name, data))

    def transfer_to_handler(self):
        self.server.name = self.name
        self.server.properties = self.properties
        self.server.local_properties = self.local_properties
        self.server.resources = self.resources
        self.server.local_resources = self.local_resources
        self.server.hooks = self.hooks
        for td in self.__transfer_data_list:
            setattr(self.server, td[0], td[1])

    def init(self):
        self.resources.load_resources()
        self.transfer_to_handler()
        self.__is_init: bool = True

    def serve_forever(self, new_thread=False):
        if self.__is_init is False:
            self.init()
        del self.__is_init
        if new_thread:
            import _thread
            _thread.start_new_thread(self.server.serve_forever, ())
        else:
            self.server.serve_forever()

    def set_before_handle(self, func):
        setattr(self.server, "before_handle", func)

    def set_after_handle(self, func):
        setattr(self.server, "after_handle", func)

    def set_except_handle(self, func):
        setattr(self.server, "except_handle", func)
