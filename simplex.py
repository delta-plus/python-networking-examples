#!/usr/bin/python3

import socket
import sys

s = socket.socket()
host = '127.0.0.1'
port = 5000
s.bind((host, port))

s.listen(5)
while True:
   c, addr = s.accept()
   while True:
     data = input(">> ") + '\n'
     if data == 'exit\n':
       c.close()
       sys.exit()
     c.send(data.encode())
   c.close()
