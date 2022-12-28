import socket
import ssl

import PySide6.QtCore

import Utils


class ChatClient(PySide6.QtCore.QObject):
    client_socket: socket.socket = None
    client_id: int = None

    server_ip: str = None
    server_port: int = None

    clients: list = None

    continue_running: bool = None
    connected: bool = None

    signal_new_client_list = PySide6.QtCore.Signal(dict)
    signal_update_client = PySide6.QtCore.Signal(dict)
    signal_incoming_message = PySide6.QtCore.Signal(dict)
    signal_connection = PySide6.QtCore.Signal(dict)

    def get_id(self):
        return self.client_id

    def send_data(self, data: dict) -> bool:
        return Utils.send_json_data(self.client_socket, data)

    def set_continue_running(self, value: bool):
        self.continue_running = value

    def shutdown(self):
        self.continue_running = False
        self.client_socket.close()

    def try_to_connect(self) -> bool:
        try:
            context = ssl.SSLContext()
            self.client_socket = context.wrap_socket(sock=socket.socket())
            self.client_socket.settimeout(1.0)
            self.client_socket.connect((self.server_ip, self.server_port))
            self.client_socket.settimeout(None)
        except (Exception, ):
            self.client_socket.close()
            return False
        return True

    def send_name(self, name: str):
        Utils.send_json_data(self.client_socket, {
            'name': name
        })

    def start_chat(self, ip: str, port: int):
        """
        Establishes connection to server, handles incoming and outgoing data, emits the appropriate signals
        :param ip: ip to connect to
        :param port: the port
        :return: None
        """
        def client_loop():
            data = Utils.receive_json_data(self.client_socket, 1024 * 1024)
            if data is None:
                return

            self.client_id = data['id']

            while True:
                data = Utils.receive_json_data(self.client_socket, 1024 * 1024)
                if data is None:
                    break

                tmp_clients = data.get('clients', None)
                status = data.get('info', None)
                text = data.get('text', None)
                who = data.get('from', None)

                if tmp_clients is not None and self.clients != tmp_clients:
                    self.clients = tmp_clients
                    self.signal_new_client_list.emit({'clients': self.clients})

                if status is not None:
                    self.signal_update_client.emit({'update': data})

                if text is not None:
                    self.signal_incoming_message.emit({'text': text, 'from': who})
            self.client_socket.close()

        self.server_ip = ip
        self.server_port = port
        self.continue_running = True
        self.connected = False
        count = 0

        self.signal_connection.emit({'text': 'Initializing...', 'connected': self.connected})

        while self.continue_running:
            if not self.connected:
                count += 1
                count %= 6
                self.signal_connection.emit({'text': f'Trying to connect{" ." * count}', 'connected': self.connected})
                self.connected = self.try_to_connect()
                if self.connected:
                    self.signal_connection.emit({'text': f'Connected!', 'connected': self.connected})
                    client_loop()
                    self.connected = False
                    count = 0
