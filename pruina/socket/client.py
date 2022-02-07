import logging
import socket

from pruina.socket.exception.exception import ConnectionReachMaxRetryTimesException
from pruina.socket.util.general import Properties, Resources, CachedHooks

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)


class PruinaSocketClient:
    def __init__(self, host: str = socket.gethostbyname(socket.gethostname()), port: int = 50003, name: str = 'client',
                 max_retry: int = 3):
        super().__init__()
        self.name: str = name
        self.host: str = host
        self.port: int = port
        self.max_retry: int = max_retry
        self.client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.properties: Properties = Properties()
        self.resources: Resources = Resources()
        self.hooks: CachedHooks = CachedHooks()
        self.__is_init: bool = False
        self.threads = []

    def set_address(self, host: str, port: int):
        self.host: str = host
        self.port: int = port

    def init(self):
        self.resources.load_resources()
        self.__is_init: bool = True

    def connect(self):
        if self.__is_init is False:
            self.init()
        del self.__is_init
        fail: int = 0
        while True:
            try:
                self.client.connect((self.host, self.port))
                break
            except socket.error:
                fail += 1
                if fail > self.max_retry:
                    raise ConnectionReachMaxRetryTimesException(self.max_retry)
        self._handle()

    def _handle(self):
        from pruina.socket.handler.GeneralHandler import general_handle
        import threading
        t = threading.Thread(target=general_handle, args=(self.client, self.hooks, self),
                             kwargs={"before": self.before, "after": self.after, "except_handle": self.except_handle})
        self.threads.append(t)
        t.start()

    def wait_until_finish(self):
        for t in self.threads:
            t.join()

    def send(self, _type, data: bytes, _id=0):
        from pruina.socket.handler.util.util import send as __send
        __send(self.client, _type, data, _id=_id)

    def before(self, _type, _data, **kwargs):
        pass

    def after(self, _type, _data, **kwargs):
        pass

    def except_handle(self, e, handler):
        raise e
