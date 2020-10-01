#!/usr/local/bin/python3.7

from socket import *
import tqdm
import sys
import os

def main():
  client = socket(AF_INET, SOCK_STREAM)
  host = sys.argv[1]
  port = int(sys.argv[2])

  try:
    runClient(client, host, port)
  except KeyboardInterrupt:
    client.shutdown(SHUT_RDWR)
    client.close()
    sys.exit()

def runClient(client, host, port):  
  client.connect((host, port))
  infoStr = client.recv(1024).decode()
  filename, filesize = infoStr.split(',')
  filesize = int(filesize)
  progress = tqdm.tqdm(range(filesize), f'Receiving {filename}: ', unit='B', unit_scale=True, unit_divisor=1024)
  with open(filename, 'wb') as file:
    for _ in progress:
      bytesRead = client.recv(3000)
      if not bytesRead:    
        break
      file.write(bytesRead)
      progress.update(len(bytesRead))

if __name__ == '__main__':
  main()
