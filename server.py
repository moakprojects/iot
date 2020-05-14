import socket
import json
import struct
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import time

# these are necessary for the database connection
cred = credentials.Certificate('service.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

# initialize the socket to get the values from the pycom
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# server config, the port number should be the same as at pycom device
server = socket.gethostbyname(socket.gethostname())
port = 1236

# we connect to the port
try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

# and we keep the socket listen on the port, it is neccessary if we not send the data continuously
s.listen(5)

while True:
    # here we get the data in the clientsocket, the address is the IP of the sender
    clientsocket, address = s.accept()
    b = b''
    #in the data variable we store the json we got
    data = clientsocket.recv(1024).decode()
    # json have to be decode
    d = json.loads(data)
    print(d)
    # this is need to get a date object from the string, time.strftime looking for a tuple, but we didn't get a tuple with the pycom device, therefore we make a hack here
    d["t"].append(0)
    # here we make a datetime object from the date string, and count the temperature value from the voltage
    date_str = time.strftime("%Y-%m-%d %H:%M:%S", tuple(d["t"]))
    temp=0.0685*d['v']-27.2
    # we save the data to the database
    doc_ref = db.collection(u'fromPycom').document()
    doc_ref.set({
        u'time': date_str,
        u'temp': temp,
        u'light_b': d['b'],
        u'light_r': d['r'],
        u'hum': d['h'],
    })
    # print(d["temp"])
    # print(f"Connection from {address} has been established!")
    # clientsocket.send(bytes("Welcome", "utf-8"))
