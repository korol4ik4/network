
from network_thread.network_threading import NetwokThread


class Client(NetwokThread):
    def __init__(self,port,address="127.0.0.1",timeout = 25,keys_path='keys', keys_name='client_rsa'):
        super(Client,self).__init__(timeout = timeout,keys_path=keys_path, keys_name=keys_name)
        self.port=port
        self.address = address
        self.create_session()

    def create_session(self):
        self.connect(self.address, self.port)
        #print('client connected',self.address)
        if self.sock.__session__(serv=False):
            self.recv_loop(self.sock)
            return True
        else:
            return False
        #print('client session created ',self.sock.session)


    def incoming(self, service_message, data, connect):
        print(service_message, data, connect)
        #connect.__send__('Hello'.encode(), data_type='text')

    def close(self):
        self.is_run = False
        self.sock.close()

    def send_data(self,data,**kwargs):
        self.sock.__send__(data, **kwargs)

