#!/usr/bin/python3

from socket import *
import threading
import sys

def main():
  server = socket(AF_INET, SOCK_STREAM)

  message = 'HTTP/1.1 200 OK\n\n'
  with open('./index.html', 'r') as file:
    for line in file:
      message += line

  try:
    runServer(server, message)
  except KeyboardInterrupt:
    server.shutdown(SHUT_RDWR)
    server.close()
    sys.exit()

def runServer(server, message):
  server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  server.bind(('', 8080))
  server.listen(5)
  while(True):
    client, address = server.accept()
    newThread = threading.Thread(target=sendToClient, args=(client, message))
    newThread.start()

def sendToClient(client, message):
  client.send(message.encode())
  client.shutdown(SHUT_WR)
  client.close()

if __name__ == '__main__':
  main()
