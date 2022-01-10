import time


def ndarray_img_to_bytes(data, _format: str = 'jpeg'):
    from PIL.Image import Image
    from io import BytesIO
    bytes_io = BytesIO()
    _data = Image.fromarray(data)
    _data.save(bytes_io, _format)
    return bytes_io.getvalue()


def bytes_img_to_ndarray(data: bytes):
    from PIL.Image import Image
    from io import BytesIO
    import numpy as np
    img = Image.open(BytesIO(data))
    return np.asarray(img, dtype=np.uint8)


def send(conn, _type, data: bytes, _id=-1, is_stream=False, stream_end=False):
    import pruina.socket.handler.proto.PruinaSocketServer_pb2 as Pb
    __type = _type
    if type(__type) == str:
        __type = hashcode(__type)
    wrapper = Pb.Wrapper()
    wrapper.id = _id
    wrapper.type = __type
    wrapper.data = data
    wrapper.stream_property = (is_stream << 1) + stream_end
    byte_data = wrapper.SerializeToString()
    try:
        conn.send(b"<W" + len(byte_data).to_bytes(4, byteorder='big', signed=False) + byte_data)
    except:
        pass


def hashcode(s):
    # the same as java default hashcode
    h = 0
    if len(s) > 0:
        for item in s:
            h = 31 * h + ord(item)
        return h & 0x7FFFFFFF
    else:
        return 0
