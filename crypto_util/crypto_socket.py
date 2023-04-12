from socket import socket
from crypto_util.coder import Coder
from utils.message import Message
import rsa
import os
from time import sleep

class CryptoSocket(socket):

    def __init__(self, *args, **kwargs):
        self.coder = Coder()
        rsa_keys_path = kwargs.get("rsa_keys_path")
        if rsa_keys_path:
            kwargs.pop("rsa_keys_path")
        else:
            rsa_keys_path=''

        rsa_keys_name = kwargs.get("rsa_keys_name")
        if rsa_keys_path:
            kwargs.pop("rsa_keys_name")
        else:
            rsa_keys_name = 'rsa'

        self.rsa_keys_path = rsa_keys_path
        self.rsa_keys_name = rsa_keys_name
        self.public_key, self.private_key = self.get_keys(path=rsa_keys_path, name=rsa_keys_name)

        # __init__ clone from socket
        if args and isinstance(args[0], socket):
            self.sock = args[0]
        # or __init__ new socket
        else:
            self.sock=None
            super(CryptoSocket, self).__init__(*args, **kwargs)

        self.session = False
        self._on_send = False

    def __accept__(self):
        connected_socket, address = self.accept()
        connect = CryptoSocket(connected_socket,rsa_keys_name=self.rsa_keys_name, rsa_keys_path=self.rsa_keys_path)
        return connect, address

    def set_key(self,enc_key, dec_key):
        try:
            self.coder.set(enc_key, dec_key)
        except:
            pass

    def __recv_data__(self,buffer_size=4096):
        connect = self if not self.sock else self.sock
        enc_service_msg = connect.recv(buffer_size)
        if not enc_service_msg:
            raise Exception('empty service message')
        # decoding service message
        service_message = self.coder.decrypt(enc_service_msg).decode()
        message = Message(service_message)
        size = message.size
        if not size:
            size = 0
        # receive data
        received_size = 0
        blocks = b''
        while received_size < size:
            enc_data = connect.recv(buffer_size)
            if not enc_data:
                raise Exception('empty data block')
            blocks += enc_data
            received_size += len(enc_data)
        # decrypt data
        if blocks:
            data = self.coder.decrypt(blocks)
        else:
            data = b''
        return service_message, data

    def __send__(self, data, buffer_size = 4096, **kwargs):
        connect = self if not self.sock else self.sock
        try:
            enc_data = self.coder.encrypt(data)
            if not enc_data:
                raise Exception('NOT DATA')
            service_message = Message(**kwargs)
            # size from kwargs will rewrite
            service_message(size=len(enc_data))
            service_message = service_message.json()
            enc_serv_msg = self.coder.encrypt(service_message.encode())
            #--- socket send from threads block
            while self._on_send:
                sleep(0.01) # wait for end blocking
            self._on_send = True # block send for other
            ## send
            connect.sendall(enc_serv_msg,buffer_size)
            sleep(0.01)# иначе сольются данные, пока так
            connect.sendall(enc_data,buffer_size)
            self._on_send = False # end blocking
            return True
        except BaseException as e:
            print("can't __send__", e)
            return False

            #raise Exception("fail to send")


    @staticmethod
    def get_keys(path='', name="rsa", size=512):
        public_key_file_name = name + '_public.pem'
        private_key_file_name = name + '_private.pem'
        if path and not os.path.isdir(path):
            try:
                os.mkdir(path)
            except Exception as e:
                print('cannot create directory ', path)
                print(e)
                path = ''
        if os.path.isdir(path):
            path += os.path.sep
            public_key_file_name = path + public_key_file_name
            private_key_file_name = path + private_key_file_name

        try:
            # load
            with open(public_key_file_name, 'rb') as f:
                public_key = rsa.key.PublicKey.load_pkcs1(f.read())
            with open(private_key_file_name, 'rb') as f:
                private_key = rsa.key.PrivateKey.load_pkcs1(f.read())

        except FileNotFoundError:
            # create
            public_key, private_key = rsa.newkeys(size)
            public_pem = public_key.save_pkcs1()
            private_pem = private_key.save_pkcs1()
            # save
            try:
                with open(public_key_file_name, 'wb') as f:
                    f.write(public_pem)
                with open(private_key_file_name, 'wb') as f:
                    f.write(private_pem)
            except BaseException as e:
                print(e, ' don\'t save keys to files')
                return public_key, private_key
        except BaseException as e:
            print(e, 'don\'t create/load rsa keys')
            return None, None
        return public_key, private_key

    def __session__(self,serv = True):
        connect = self if not self.sock else self.sock
        try:
            data_key = self.public_key.save_pkcs1()

            if serv:
                repubkey = connect.recv(1024)  # recive remote pub key

            connect.sendall(data_key, 1024) # send self pub key

            if not serv:
                repubkey = connect.recv(1024)  # recive remote pub key

            if not repubkey:
                raise Exception('empty receiv by session begin')
            remote_pubkey = rsa.key.PublicKey.load_pkcs1(repubkey) # загрузка удаленного публичного ключа из байтовой строки
            key_encryptor = self.coder.generate_key()  # генерация ключа aes128
            enc_key_enc = rsa.encrypt(key_encryptor, remote_pubkey)  # шифруем аес ключ принятым публичным ключом

            if not serv:
                connect.sendall(enc_key_enc, 1024)  # send my key for encryptor

            enc_key_dec = connect.recv(1024)  # принимаем aes ключ для дешифровки входящих сообщений
            key_decryptor = rsa.decrypt(enc_key_dec, self.private_key)  # расшифровываем его

            if serv:
                connect.sendall(enc_key_enc, 1024)  # send my key for encryptor

            self.set_key(enc_key=key_encryptor, dec_key=key_decryptor)  # и загругаем оба аес ключа в наш кодер
            self.session = remote_pubkey
            return True
        except BaseException as e:
            self.session = False
            #print(e)
            #print("Don't create SESSION ", e, self, serv)
            return False
