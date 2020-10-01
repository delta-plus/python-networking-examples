#!/usr/bin/python3

import os
import sys
import socket
import _thread
import time

def main():
  usage = '''
  Duplex Client/Server
  --------------------

  Usage: ./duplex.py [remote host] [port]
  '''

  if (len(sys.argv) < 3):
    print(usage)
    exit()

  host = sys.argv[1]
  port = int(sys.argv[2])

  _thread.start_new_thread(server, ('0.0.0.0', port))

  # Wait for other server to start before running client
  time.sleep(5)
  client(host, port)

def server(host, port):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
  s.bind((host, port))
  s.listen(5)

  while True:
    con, address = s.accept()
    while True:
      data = con.recv(4096).decode()
      if data == 'exit':
        con.close()
        _thread.interrupt_main()
        exit()
      print(data)
      if not data: break

def client(host, port):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
  s.connect((host, port))

  while True:
    data = input(">> ")
    if (data == 'exit'):
      s.send(data.encode())
      s.close()
      exit()
    s.send(data.encode())

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    os._exit(0)
