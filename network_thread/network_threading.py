from threading import Thread
from time import time
from crypto_util.crypto_socket import CryptoSocket
import socket
from utils.server_control import ServerControl



class NetwokThread:
    def __init__(self, timeout = 120,keys_path='keys', keys_name='rsa'):
        self.sock = CryptoSocket(socket.AF_INET, socket.SOCK_STREAM, rsa_keys_path=keys_path,rsa_keys_name=keys_name)
        self.is_run = True
        self.session_timeout = timeout  # sec.
        self.control = ServerControl()
        self.client_connected=False

    def accept_thread(self, address, port):
        self.sock.bind((address, port))
        self.sock.listen(10)
        lst_thr = Thread(target=self._accept, name=f'wait accept')
        lst_thr.start()
        return lst_thr

    def _accept(self):
        if not self.is_run:
            return  # Exit
        try:
            accept = self.sock.__accept__()
            connect, address = accept
            connect.sock.settimeout(self.session_timeout)
            if not connect.__session__(server_session= True):
                raise Exception("fail to access or create session")
            if connect.session:
                thr_recv = self.recv_loop_thread(connect)
                self.control.append_connect_thread(connect,thr_recv)
                self.control.update_keys(connect,connect.coder.get,connect.session)
            else:
                connect.sock.close()
        except BaseException as e:
            print('ошибка :D или выход сервера', e)
        finally:
            self._accept()

    def _connect(self,address,port):  # client
        self.sock.connect((address,port))
        self.sock.settimeout(self.session_timeout)
        self.client_connected = True
        self.is_run = True

    def connect_thread(self, address, port):
        cnct_thr = Thread(target=self._connect, args=(address,port))
        cnct_thr.start()
        tm = time()
        while time()-tm < 5 and not self.client_connected:
            pass
        if not self.client_connected:
            self.sock.close()
            raise ConnectionError('client is not connected')
        return cnct_thr

    def recv_loop_thread(self, connect, buffer_size=4096):
        if connect.session:
            thr_recv = Thread(target=self._recv_loop, args=(connect,buffer_size), name=f'receive loop {connect}')
            thr_recv.start()
            return thr_recv

    def _recv_loop(self, connect, buffer_size=4096):
        fail=0
        while self.is_run and fail < 10:
            try:
                service_message, data = connect.__recv_data__(buffer_size)
                #  тут проверка на stream
                # и начало stream
                self.incoming(service_message, data, connect)
                fail=0
            except ConnectionError as e:
                print(e, 'connect error')
                break
            except BaseException as e:
                #print(e, 'server BaseException')
                fail += 1
                continue
        if connect.sock:
            connect.sock.close()
        else:
            connect.close()


    def incoming(self,service_message,data, connect):
        print(service_message, data, connect)
        #connect.__send__('Hello'.encode(), data_type='text')
