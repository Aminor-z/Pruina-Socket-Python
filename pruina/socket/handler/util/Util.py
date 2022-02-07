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
    conn.send(b"<W" + len(byte_data).to_bytes(4, byteorder='big', signed=False) + byte_data)


def hashcode(s):
    # the same as java default hashcode
    h: int = 0
    if len(s) > 0:
        for item in s:
            h: int = 31 * h + ord(item)
        return h & 0x7FFFFFFF
    else:
        return 0
