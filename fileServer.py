#!/usr/local/bin/python3.7

from socket import *
import tqdm
import sys
import os

def main():
  server = socket(AF_INET, SOCK_STREAM)

  try:
    runServer(server)
  except KeyboardInterrupt:
    server.shutdown(SHUT_RDWR)
    server.close()
    sys.exit()

def runServer(server):
  server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  server.bind(('', 5000))
  server.listen(5)

  filename = 'Classical-guitar-music.mp3'
  filesize = os.path.getsize(filename)

  while(True):
    client, address = server.accept()
    print(f'{client.getpeername()[0]} connected.')
    sendToClient(client, filename, filesize)

def sendToClient(client, filename, filesize):
  progress = tqdm.tqdm(range(filesize), f'Sending {filename}', unit='B', unit_scale=True, unit_divisor=1024)

  client.send(f'{filename},{filesize}'.encode()); # Send file name and size as CSV string

  with open(filename, 'rb') as file:
    for _ in progress:
      bytesRead = file.read(4096)
      if not bytesRead:
        break
      client.sendall(bytesRead)
      progress.update(len(bytesRead))

  client.shutdown(SHUT_WR)
  client.close()

if __name__ == '__main__':
  main()
