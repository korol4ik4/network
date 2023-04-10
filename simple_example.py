
from server import Server
from client import Client


# start server
cs = Server(1111,timeout=50)
# connect client
cc = Client(address="127.0.0.1",port=1111,timeout=5)

# client send data
cc.send_data('priwet2'.encode(),datatype='text' )
# server send data to all connected
for serv_con in cs.control.connect:
    cs.send_data(serv_con, 'ok'.encode(), datatype='ok')
#client send data
cc.send_data("By-by".encode(), datatype="text", sub_type="exit")
# exit client (wait timeout, default = 120)
cc.close()
# exit server
cs.close()


