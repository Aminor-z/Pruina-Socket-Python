import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)


def general_handle(conn, hooks, handler, before=None, after=None, except_handle=None):
    import pruina.socket.handler.proto.PruinaSocketServer_pb2 as Pb
    data: bytes = bytes()
    c: bool = True
    while c:
        try:
            new_data: bytes = conn.recv(6)
            if new_data is None or new_data == b"":
                break
            data += new_data
            if len(data) < 6:
                continue
            while True:
                if data[0:2] != b'<W':
                    _pos = data.find(b'<W', 0)
                    if _pos == -1:
                        data = data[-2:]
                        break
                    else:
                        data = data[_pos + 2:]
                size: int = int().from_bytes(data[2:6], byteorder='big', signed=False)
                data: bytes = data[6:]
                while size > len(data):
                    data += conn.recv(1024)
                _data: bytes = data[:size]
                wrapper: Pb.Wrapper = Pb.Wrapper()
                wrapper.ParseFromString(_data)
                data = data[size:]
                if before is not None:
                    before(wrapper.type, wrapper.data, wrapper=wrapper, handler=handler)
                    hooks.call_hook(wrapper.type, wrapper.data, wrapper=wrapper, handler=handler)
                if after is not None:
                    after(wrapper.type, wrapper.data, wrapper=wrapper, handler=handler)
        except Exception as e:
            if except_handle is None:
                raise e
            else:
                c = except_handle(e, handler)
