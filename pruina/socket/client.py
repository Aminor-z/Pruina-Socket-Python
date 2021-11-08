import logging
import socket
from pruina.socket.handler.util.General import Properties, Resources, CachedHooks

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
        self.max_retry = max_retry
        self.client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.properties: Properties = Properties()
        self.resources: Resources = Resources()
        self.hooks: CachedHooks = CachedHooks()
        self.__is_init: bool = False

    def set_address(self, host: str, port: int):
        self.host: str = host
        self.port: int = port

    def init(self):
        self.resources.load_resources()
        self.__is_init = True

    def connect(self):
        if self.__is_init is False:
            self.init()
        del self.__is_init
        logging.info(f'{self.name} is connecting to {self.host}:{self.port}.')
        fail = 0
        while True:
            try:
                self.client.connect((self.host, self.port))
                break
            except socket.error:
                fail += 1
                logging.info(f'{self.name}({self.host}:{self.port}): Connection failed, retrying. [fail={fail}]')
                if fail > self.max_retry:
                    logging.error(
                        f'{self.name}({self.host}:{self.port}): Connection failed, reaching max_retry. [fail={fail}]')
                    return False
        self._handle()

    def _handle(self):
        from pruina.socket.handler.GeneralHandler import general_handle
        import _thread
        _thread.start_new_thread(general_handle,(self.client, self.hooks, self))


    def send(self, _type, data: bytes, _id=0):
        from pruina.socket.handler.util.Util import send as __send
        __send(self.client, _type, data, _id=_id)
