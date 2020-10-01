#!/usr/bin/python3

import sys
import socket

usage = '''
Simple Web Client
-----------------

Usage: ./webclient.py [URL] [port]
If no port is specified, default is 80.
'''

if (len(sys.argv) == 1):
  print(usage)
  exit()

if (len(sys.argv) == 2):
  host = sys.argv[1]
  port = 80
else:
  host = sys.argv[1]
  port = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.sendall(b'GET / HTTP/1.1\r\nHost: ' + host.encode() + b'\r\n\r\n')
print(s.recv(1024).decode())
