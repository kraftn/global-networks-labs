import socket

BUFFER_SIZE = 32768


class FTPClient:
    def __init__(self, active_mode, verbose):
        self.active_mode = active_mode
        self.verbose = verbose

        self.ctrl_socket = None
        self.server_ip = None

        # Канал для передачи данных
        self.data_socket = None
        # Для активного режима
        self.listener = None

    def connect(self, server_ip, username='anonymous', password=''):
        self.server_ip = server_ip

        self.ctrl_socket = socket.socket()
        self.ctrl_socket.connect((server_ip, 21))
        banner = self.ctrl_socket.recv(BUFFER_SIZE).decode()
        if self.verbose > 1:
            print(banner)

        self._send_command(f'USER {username}')
        code, _ = self._send_command(f'PASS {password}')
        if code == 530:
            self._send_command('QUIT')
            self.server_ip = None
            self.ctrl_socket.close()
            self.ctrl_socket = None
        elif self.verbose > 0:
            address = self.ctrl_socket.getsockname()
            print(f'Установлено управляющее соединение: {address[0]}:{address[1]} (клиент) - {server_ip}:21 (сервер)')
        return code

    def disconnect(self):
        self._send_command('QUIT')
        self.server_ip = None
        self.ctrl_socket.close()
        self.ctrl_socket = None

    def pwd(self):
        _, response = self._send_command('PWD')
        return response.split(' ')[1].strip('\"')

    def list(self):
        self._prepare_data_transfer()
        self._send_command('LIST')
        data = self._receive_data()
        response = self.ctrl_socket.recv(BUFFER_SIZE).decode()
        if self.verbose > 1:
            print(response)
        return data.decode()

    def cwd(self, folder_name):
        code, _, = self._send_command(f'CWD {folder_name}')
        return code

    def download_file(self, server_file, client_path):
        self._prepare_data_transfer()
        code, _, = self._send_command(f'RETR {server_file}')

        if code == 550:
            return code

        data = self._receive_data()
        response = self.ctrl_socket.recv(BUFFER_SIZE).decode()
        if self.verbose > 1:
            print(response)
        self._save_file(data, client_path)
        return int(response[:3])

    def upload_file(self, client_path, server_file):
        data = self._read_file(client_path)
        self._prepare_data_transfer()
        code, _ = self._send_command(f'STOR {server_file}')

        if code == 550:
            return code

        self._send_data(data)
        response = self.ctrl_socket.recv(BUFFER_SIZE).decode()
        if self.verbose > 1:
            print(response)
        return int(response[:3])

    def delete_file(self, file_name):
        code, _ = self._send_command(f'DELE {file_name}')
        return code

    def create_folder(self, folder_name):
        code, _, = self._send_command(f'MKD {folder_name}')
        return code

    def remove_folder(self, folder_name):
        code, _, = self._send_command(f'RMD {folder_name}')
        return code

    def _send_command(self, command):
        self.ctrl_socket.sendall(f'{command}\r\n'.encode())
        response = self.ctrl_socket.recv(BUFFER_SIZE).decode()
        code = int(response[:3])
        if self.verbose > 1:
            print(response)
        return code, response

    def _prepare_data_transfer(self):
        if self.active_mode:
            client_ip = socket.gethostbyname(socket.gethostname())

            self.listener = socket.socket()
            self.listener.bind((client_ip, 0))
            self.listener.listen(1)

            listener_port = self.listener.getsockname()[1]
            first_byte = str(listener_port // 256)
            second_byte = str(listener_port % 256)
            str_port = first_byte + ',' + second_byte
            comma_ip = client_ip.replace('.', ',')
            self._send_command(f'PORT {comma_ip},{str_port}')
        else:
            _, response = self._send_command('PASV')
            response = response.strip()
            response = response.split(' ')[-1]
            response = response.split(',')
            first_byte = int(response[-2])
            second_byte = int(response[-1][:-1])
            server_data_port = 256 * first_byte + second_byte
            self.data_socket = socket.socket()
            self.data_socket.connect((self.server_ip, server_data_port))

    def _receive_data(self):
        if self.active_mode:
            self.data_socket, _ = self.listener.accept()
        if self.verbose > 0:
            addr = self.data_socket.getsockname()
            remote_addr = self.data_socket.getpeername()
            print(f'Установлено соединение для передачи данных: {addr[0]}:{addr[1]} (клиент) - {remote_addr[0]}:{remote_addr[1]} (сервер)')

        data = bytes()
        data_portion = True
        while data_portion:
            data_portion = self.data_socket.recv(BUFFER_SIZE)
            data += data_portion
        self.data_socket.close()
        self.data_socket = None

        if self.active_mode:
            self.listener.close()
            self.listener = None
        return data

    def _send_data(self, data):
        if self.active_mode:
            self.data_socket, _ = self.listener.accept()
        if self.verbose > 0:
            addr = self.data_socket.getsockname()
            remote_addr = self.data_socket.getpeername()
            print(f'Установлено соединение для передачи данных: {addr[0]}:{addr[1]} (клиент) - {remote_addr[0]}:{remote_addr[1]} (сервер)')

        self.data_socket.sendall(data)
        self.data_socket.close()
        self.data_socket = None

        if self.active_mode:
            self.listener.close()
            self.listener = None

    @staticmethod
    def _save_file(data, path):
        with open(path, 'wb') as f:
            f.write(data)

    @staticmethod
    def _read_file(path):
        with open(path, 'rb') as f:
            res = f.read()
        return res
