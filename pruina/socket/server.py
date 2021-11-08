import logging
import socket
from socketserver import ThreadingTCPServer

from pruina.socket.handler.util.General import Properties, Resources, CachedHooks

from pruina.socket.handler.MessageHookRequestHandler import MessageHookRequestHandler

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)


class PruinaSocketServer:
    def __init__(self, host: str = socket.gethostbyname(socket.gethostname()), port: int = 50003,
                 name: str = 'server',
                 daemon_threads: bool = True):
        super().__init__()
        self.name: str = name
        self.server: ThreadingTCPServer = ThreadingTCPServer((host, port), MessageHookRequestHandler)
        self.properties: Properties = Properties()
        self.local_properties: Properties = Properties()
        self.resources: Resources = Resources()
        self.local_resources: Resources = Resources()
        self.hooks: CachedHooks = CachedHooks()
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
        self.__is_init = True

    def serve_forever(self,new_thread=False):
        if self.__is_init is False:
            self.init()
        del self.__is_init
        logging.info(f'{self.name} serve at {self.server.server_address[0]}:{self.server.server_address[1]}.')
        if new_thread:
            import _thread
            _thread.start_new_thread(self.server.serve_forever,())
        else:
            self.server.serve_forever()
