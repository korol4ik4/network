
from network_thread.network_threading import NetwokThread
import socket

class Server(NetwokThread):
    def __init__(self, port, address ='',timeout = 120,keys_path='keys', keys_name='server_rsa'):
        super(Server,self).__init__(timeout = timeout,keys_path=keys_path, keys_name=keys_name)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((address, port))
        self.sock.listen(1000)
        self.listen()

    def close(self):
        self.is_run = False
        #close accept thread

        try:
            address, port = self.sock.getsockname()
            if address == '0.0.0.0':
                address = '127.0.0.1'
            exit_sock = socket.socket()
            exit_sock.settimeout(2)
            exit_sock.connect((address, port))
            exit_sock.send(b'')

            for conn in self.control.connect:
                conn.close()
        except:
            pass
        ########################
        self.sock.close()

    def incoming(self, service_message, data, connect):
        print(service_message, data, connect)
        #connect.__send__('Hello'.encode(), data_type='text')

    #  @staticmethod
    def send_data(self,connect, data, **kwargs):

        connect.__send__(data, **kwargs)

