from server import Server
from client import Client

from time import sleep
from utils.message import Message

class myServer(Server):
    def __init__(self,*args,**kwargs):
        super(myServer,self).__init__(*args,**kwargs)

    def incoming(self, service_message, data, connect):
        msg = Message(service_message)

        if msg.datatype == 'text':
            txt = data.decode()
            print("Server receive ",txt)
            # example function resend with upper
            self.send_data(connect=connect, data=txt.upper().encode(), **msg())

        elif msg.datatype == 'file':
            filename = msg.filename
            with open(filename,"wb") as fn:
                fn.write(data)
            print("Server receive and save file: ", filename)
        else:
            print('unknown data type ', print(msg))


class myClient(Client):
    def __init__(self, *args, **kwargs):
        super(myClient, self).__init__(*args, **kwargs)

    def incoming(self, service_message, data, connect):
        msg = Message(service_message)
        if msg.datatype == 'text':
            txt = data.decode()
            print('Client received ', txt)

        elif msg.datatype == 'file':
            filename = msg.filename
            with open(filename, "wb") as fn:
                fn.write(data)
        else:
            print('unknown data type ', print(msg))


# create and connect server and client
server = myServer(address="127.0.0.1", port=5555,keys_path='keys', keys_name='server_rsa' )
client = myClient(address="127.0.0.1",port=5555,timeout=5, keys_path='keys', keys_name='client_rsa')

# send text message
client.send_data('Привет Сервер'.encode(), datatype="text", sub_type="hello")
# wait
sleep(0.05)
# send file
data = b''
with open('readme.md', "rb") as fn:
    data = fn.read()
if data:
    client.send_data(data, datatype="file",filename="README.MD")

#wait for sending data
sleep(2)
# close and exit
client.close()
server.close()
