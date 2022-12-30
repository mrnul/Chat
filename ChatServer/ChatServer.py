import socket
import ssl
import threading
import uuid

import Utils

MAX_DATA_SIZE = 1024 * 1024


class ChatServer:
    client_lock: threading.Lock = None
    print_lock: threading.Lock = None
    server: socket.socket = None
    clients: dict = {}

    def send_whole_client_list(self, client_socket: socket.socket):
        with self.client_lock:
            client_list = {
                'clients': [{
                    'id': client_id,
                    'name': self.clients[client_id].get('name')
                } for client_id in self.clients]
            }
        Utils.send_json_data(client_socket, client_list)

    def send_client_update(self, client_id: int, info: str):
        update_data = {
            'id': client_id,
            'name': self.clients[client_id].get('name'),
            'info': info
        }
        with self.client_lock:
            for client in self.clients:
                Utils.send_json_data(self.clients[client]['socket'], update_data)

    def send_client_id(self, client_id: int):
        update_data = {
            'id': client_id
        }
        Utils.send_json_data(self.clients[client_id]['socket'], update_data)

    def send_message_to_recipients(self, json_data, client_id: int):
        text = json_data.get('text')
        msg_id = json_data.get('msg_id')
        recipients = json_data.get('recipients', [])
        if not isinstance(recipients, list):
            return

        for recipient in recipients:
            if recipient in self.clients:
                Utils.send_json_data(self.clients[recipient]['socket'], {
                    'from': client_id,
                    'text': text if text is not None else '<No text>',
                    'msg_id': msg_id
                })
            else:
                Utils.send_json_data(self.clients[client_id]['socket'], {
                    'info': 'Could not send message',
                    'msg_id': msg_id
                })

    def cleanup(self, client_id: int):
        try:
            self.clients[client_id]['socket'].close()
            self.send_client_update(client_id, 'delete')
            self.clients.pop(client_id)
            with self.print_lock:
                print(f'- {client_id} ({len(self.clients)})')
        except Exception as e:
            with self.print_lock:
                print(f'cleanup: {e}')

    def start_serving(self, ip: str, port: int):
        def client_thread(cid: int, client_socket: socket.socket):
            self.send_client_id(cid)
            self.send_whole_client_list(client_socket)
            self.send_client_update(cid, 'add')
            while True:
                data = Utils.receive_json_data(client_socket, MAX_DATA_SIZE)
                if data is None:
                    break
                name = data.get('name')
                if name is not None and isinstance(name, str) and name != self.clients[cid].get('name'):
                    self.clients[cid]['name'] = name
                    self.send_client_update(cid, 'update')
                self.send_message_to_recipients(data, cid)
            self.cleanup(cid)

        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="C:\\openssl\\cert.pem", keyfile="C:\\openssl\\key.pem", password="password")

        self.server = socket.socket()
        self.server.bind((ip, port))
        self.server.listen()
        self.client_lock = threading.Lock()
        self.print_lock = threading.Lock()
        while True:
            try:
                sock, _ = self.server.accept()
                sock = context.wrap_socket(sock=sock, server_side=True)
                client_id = uuid.uuid1().int
                self.clients[client_id] = {'socket': sock}

                with self.print_lock:
                    print(f'+ {client_id} ({len(self.clients)})')

                threading.Thread(target=client_thread, args=(client_id, sock)).start()
            except Exception as e:
                with self.print_lock:
                    print(f'start_serving: {e}')
