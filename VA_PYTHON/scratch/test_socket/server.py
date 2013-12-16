from socket import *

myHost = ''
myPort = 50007

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.bind((myHost,myPort))
sockobj.listen(5)

while True:
    connection, address = sockobj.accept()
    print 'server connected by' +str(address)
    while True:
        data = connection.recv(1024)
        if not data:
            break
        connection.send(b'Echo=>' + data)
    connection.close()
