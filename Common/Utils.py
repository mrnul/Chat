import json
import socket


def receive_n_bytes(s: socket.socket, n: int) -> bytes:
    """
    Receives exactly n bytes from socket
    :param s: the socket
    :param n: number of bytes
    :return: bytes received. If zero bytes are returned then connection should be closed
    """
    result = b''
    remaining = n
    try:
        while remaining > 0:
            data = s.recv(remaining)
            if data is None or len(data) == 0:
                return b''
            remaining -= len(data)
            result += data
    except (Exception,):
        return b''
    return result


def bytes_to_uint32(data: bytes) -> int:
    return int.from_bytes(data, byteorder='little', signed=False)


def send_json_data(s: socket.socket, data: dict) -> bool:
    data_bytes = bytes(json.dumps(data), encoding='utf-8', errors='ignore')
    length = len(data_bytes)
    length_bytes = length.to_bytes(4, byteorder='little', signed=False)
    try:
        if s.send(length_bytes) != 4:
            return False
        if s.send(data_bytes) != length:
            return False
    except (Exception, ):
        return False
    return True


def receive_json_data(s: socket.socket, max_size: int):
    data_length = bytes_to_uint32(receive_n_bytes(s, 4))
    if data_length == 0 or data_length > max_size:
        return None
    raw_data = receive_n_bytes(s, data_length)
    if len(raw_data) == 0:
        return None

    return json.loads(raw_data)
