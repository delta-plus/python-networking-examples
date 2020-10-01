#!/usr/bin/python3

from socket import *
import threading
import sys

def main():
  server = socket(AF_INET, SOCK_STREAM)

  try:
    run_server(server)
  except KeyboardInterrupt:
    server.shutdown(SHUT_RDWR)
    server.close()
    sys.exit()

def run_server(server):
  server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  server.bind(('', 5000))
  server.listen(5)
  clients = {}

  while True:
    client, address = server.accept()
    new_thread = threading.Thread(target=read_client, args=[client, clients])
    new_thread.daemon = True
    new_thread.start()
    
def read_client(client, clients):
  has_nick = False
  nick = ''
  client.send('Welcome to the Chat! To join, please enter a nickname using "/nick (nickname)".'.encode())

  while not has_nick:
    data = client.recv(4096).decode()
    if data[:6] == '/nick ':
      if len(data) > 6:
        has_nick = True
        nick = data[6:]
        clients[nick] = client
        for nicks in clients:
          str = nick + ' has joined the chat.'
          clients[nicks].send(str.encode())

  while True:
    data = client.recv(4096).decode()
    if data:
      if data == '/exit':
        print(nick + ' has left the chat.')
        clients.pop(nick)
      else:
        print(nick + ': ' + data)

      for nicks in clients:
        if data == '/exit':
          str = nick + ' has left the chat.'
          clients[nicks].send(str.encode())
        else:
          str = nick + ': ' + data
          clients[nicks].send(str.encode())

    if data == '/exit':
      client.shutdown(SHUT_WR)
      client.close()
      exit()

if __name__ == '__main__':
  main()
