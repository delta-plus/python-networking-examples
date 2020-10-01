#!/usr/bin/python3

from socket import *
import select
import queue
import sys

def main():
  server = socket(AF_INET, SOCK_STREAM)
  clients = {}

  try:
    run_server(server, clients)
  except KeyboardInterrupt:
    for connection in clients:
      connection.shutdown(SHUT_WR)
      connection.close()
    server.shutdown(SHUT_RDWR)
    server.close()
    sys.exit()

def run_server(server, clients):
  server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  server.setblocking(0)
  server.bind(('', 5000))
  server.listen(100)
  inputs = [server]
  outputs = []
  message_queues = {}

  while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    for connection in readable:
      if connection is server:
        client, address = server.accept()
        inputs.append(client)
        message_queues[client] = queue.Queue()
        clients[client] = {'nick': False, 
                           'room': False, 
                           'priv': False, 
                           'receive_client': False, 
                           'serve_client': False, 
                           'file_server': False,
                           'filename': False, 
                           'filesize': 0, 
                           'recipient': False,
                           'sending': False, 
                           'counter': 0}
        client.send('Welcome to the Chat! To sign in, please enter a nickname using "\\nick (nickname)".\nTo exit, use "\\x".\nTo list rooms, use "\\r".\nTo join a room, use "\\e (room name)".\nTo display the name of the current room, use "\\w".\nTo list connected users in the current room, use "\\l".'.encode())

      else:
        is_file_client = False
        is_file_server = False
        filename = False
        filesize = 0
        sending_client = False

        for client in clients:
          if connection == clients[client]['receive_client']:
            is_file_client = True
            filename = clients[client]['filename']
            filesize = clients[client]['filesize']
            sending_client = client
          elif connection == clients[client]['file_server']:
            is_file_server = True

        if is_file_client:
          data = connection.recv(4096)
          if data:
            file = open('./files/' + filename, 'ab')
            file.write(data)
          else:
            file.close()
            inputs.remove(connection)
            connection.shutdown(SHUT_WR)
            connection.close()
            clients[sending_client]['receive_client'] = False
            clients[sending_client]['sending'] = 'Done'
            sending_client.send('FILE TRANSFER - Done!'.encode())
            for recipient in clients:
              if clients[sending_client]['recipient'] == clients[recipient]['nick']:
                msg = 'FILE TRANSFER - ' + clients[client]['nick'] + ' wants to send you a file. Accept?'
                msg = msg.encode()
                recipient.send(msg)
                clients[recipient]['sending'] = 'Wait'

        elif is_file_server:
          receiver, rec_address = file_server.accept()
          outputs.append(receiver)
          for client in clients:
            if clients[client]['sending'] == 'Done':
              for recipient in clients:
                if clients[recipient]['nick'] == clients[client]['recipient']:
                  clients[client]['sending'] = False
                  clients[client]['serve_client'] = receiver

        else:
          if not clients[connection]['nick']:
            data = connection.recv(4096).decode()
            if data[:6] == '\\nick ':
              if len(data) > 6:
                print(data[6:] + ' has logged in.')
                if connection not in outputs:
                  outputs.append(connection)
                clients[connection]['nick'] = data[6:]

          elif not clients[connection]['room']:
            data = connection.recv(4096).decode()
            if data[:3] == '\\e ':
              if len(data) > 3:
                message_queues[connection].put(data)
                if data[3:] == 'hobby' or data[3:] == 'food' or data[3:] == 'travel':
                  print(clients[connection]['nick'] + ' has joined ' + data[3:] + '.')
            elif data == '\\r':
              message_queues[connection].put(data)
            elif data == '\\l':
              message_queues[connection].put(data)
            elif data == '\\w':
              message_queues[connection].put(data)

          else:
            # Receive message data from client
            data = connection.recv(4096).decode()
            if data:
              message_queues[connection].put(data)
              if data == '\\x':
                print(clients[connection]['nick'] + ' has left the chat.')
              else:
                print(clients[connection]['nick'] + ': ' + data)

              if data == '\\x':
                inputs.remove(connection)
                if connection in outputs:
                  outputs.remove(connection)
                connection.shutdown(SHUT_WR)
                connection.close()

            else:
              if connection in outputs:
                outputs.remove(connection)
              if connection in clients:
                clients.pop(connection)
              inputs.remove(connection)
              connection.shutdown(SHUT_WR)
              connection.close()
              del message_queues[connection]

    for connection in writable:
      for client in clients:
        if connection == clients[client]['serve_client']:
          if not clients[client]['sending'] == 'name_sent':
            msg = clients[client]['filename'] + '\n'
            connection.send(msg.encode())
            clients[client]['sending'] = 'name_sent'
          file = open('./files/' + clients[client]['filename'], 'rb')
          if (clients[client]['counter'] * 4096) <= (clients[client]['filesize'] - 4096):
            file.seek(clients[client]['counter'] * 4096)
            bytes_read = file.read(4096)
            connection.sendall(bytes_read)
            clients[client]['counter'] = clients[client]['counter'] + 1
          else:
            file.seek(clients[client]['counter'] * 4096)
            diff = clients[client]['filesize'] % 4096
            bytes_read = file.read(diff)
            connection.sendall(bytes_read)
            bytes_read = False
            clients[client]['serve_client'].shutdown(SHUT_WR)
            clients[client]['serve_client'].close()
            outputs.remove(clients[client]['serve_client'])
            clients[client]['file_server'].shutdown(SHUT_WR)
            clients[client]['file_server'].close()
            inputs.remove(clients[client]['file_server'])
          if not bytes_read:
            for other_client in clients:
              if clients[other_client]['nick'] == clients[client]['recipient']:
                msg = 'FILE TRANSFER - ' + clients[client]['filename'] + ' has been received.'
                msg = msg.encode()
                other_client.send(msg)
                msg = 'FILE TRANSFER - ' + str(clients[client]['recipient'])
                msg = msg + ' has received ' + clients[client]['filename'] + '.'
                msg = msg.encode()
                client.send(msg)
                clients[client]['serve_client'] = False
                clients[client]['receive_client'] = False
                clients[client]['file_server'] = False
                clients[client]['filesize'] = 0
                clients[client]['recipient'] = False
                clients[client]['sending'] = False
                clients[client]['counter'] = 0

      try:
        next_msg = message_queues[connection].get_nowait()
      except queue.Empty:
        pass
      except:
        for client in clients:
          if client.fileno() == -1:
            clients.pop(client)
      else:
        if len(next_msg) > 80:
          next_msg = next_msg[:80]

        # User enters a room
        if next_msg[:3] == '\\e ':
          if len(next_msg) > 3:
            if next_msg[3:] == 'hobby' or next_msg[3:] == 'food' or next_msg[3:] == 'travel':
              if clients[connection]['room']:
                for client in clients:
                  if clients[client]['nick']:
                    if clients[client]['room'] == clients[connection]['room']: 
                      if client != connection:
                        msg = clients[connection]['nick'] + ' has left ' + clients[connection]['room'] + '.'
                        client.send(msg.encode())
              clients[connection]['room'] = next_msg[3:]
              msg = clients[connection]['nick'] + ' has joined ' + next_msg[3:] + '.'
              msg = msg.encode()
              for client in clients:
                if clients[client]['nick']:
                  if clients[client]['room'] == clients[connection]['room']:
                    client.send(msg)
            else:
              connection.send('Invalid room. Please request an existing room.'.encode())

        # User exits the chat
        elif next_msg == '\\x':
          nick = clients[connection]['nick']
          room = clients[connection]['room']
          msg = nick + ' has left the chat.'
          msg = msg.encode()
          if connection in clients:
            clients.pop(connection) 
          for client in clients:
            if clients[client]['nick']:
              if clients[client]['room'] == room:
                client.send(msg)
          del message_queues[connection]

        # User requests a list of rooms
        elif next_msg == '\\r':
          msg = 'hobby,travel,food'
          connection.send(msg.encode());

        # User requests a list of users in the room
        elif next_msg == '\\l':
          if clients[connection]['room']:
            msg = ''
            for client in clients:
              if clients[client]['nick']:
                if clients[client]['room'] == clients[connection]['room']:
                  msg += clients[client]['nick'] + ','
            msg = msg[:-1]
            connection.send(msg.encode());
          else:
            connection.send('Unable to list users. You have not joined a room.'.encode())

        # User requests the name of the current room
        elif next_msg == '\\w':
          if clients[connection]['room']:
            connection.send(clients[connection]['room'].encode());
          else:
            connection.send('Unable to list current room. You have not joined one.'.encode())

        # User enters private message mode
        elif next_msg[:3] == '\\p ':
          if len(next_msg) > 3:
            found = False
            for client in clients:
              if clients[client]['nick'] == next_msg[3:]:
                if clients[client]['room'] == clients[connection]['room']:
                  clients[connection]['priv'] = next_msg[3:]
                  found = True
                  msg = 'Entered private message mode with ' + clients[client]['nick'] + '.'
                  msg = msg.encode()
                  connection.send(msg)
            if not found:
              connection.send('Can\'t enter private message mode. Client does not exist.'.encode())

        # User exits private message mode
        elif next_msg == '\\q':
          if clients[connection]['priv']:
            msg = 'Left private message mode with ' + clients[connection]['priv'] + '.'
            msg = msg.encode()
            connection.send(msg)
            clients[connection]['priv'] = False

        # User requests file transfer
        elif next_msg[:3] == '\\f ':
          if len(next_msg.split(' ')) == 3:
            if not clients[connection]['receive_client']:
              clients[connection]['recipient'] = next_msg.split(' ')[1].rstrip()
              clients[connection]['filename'] = next_msg.split(' ')[2].rstrip()
          elif len(next_msg.split(' ')) == 2:
            if clients[connection]['sending'] == 'Wait':
              if next_msg.split(' ')[1].rstrip().upper() == 'Y':
                file_server = socket(AF_INET, SOCK_STREAM)
                file_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                file_server.setblocking(0)
                file_server.bind(('', 6001))
                file_server.listen(1)
                inputs.append(file_server)
                for client in clients:
                  if clients[client]['recipient'] == clients[connection]['nick']:
                    clients[client]['file_server'] = file_server
                clients[connection]['sending'] = 'Sending'
              else:
                clients[connection]['sending'] = False
                for client in clients:
                  if clients[client]['sending'] == 'Done':
                    if clients[connection]['nick'] == clients[client]['recipient']:
                      clients[client]['sending'] = False

        # User begins file transfer to server
        elif next_msg[:10] == 'file_size ':
          if len(next_msg) > 10:
            if not clients[connection]['receive_client']:
              file_client = socket(AF_INET, SOCK_STREAM)
              file_client.connect((connection.getpeername()[0], 6000))
              inputs.append(file_client)
              clients[connection]['filesize'] = int(next_msg[10:].rstrip())
              clients[connection]['receive_client'] = file_client
              connection.send('FILE TRANSFER - Sending to server...'.encode())

        # User sends a message
        else:
          if clients[connection]['priv']:
            msg = '(Private) ' + clients[connection]['nick'] + ': ' + next_msg
            msg = msg.encode()
            for client in clients:
              if clients[client]['nick'] == clients[connection]['priv']:
                client.send(msg)
            connection.send(msg)
          else:
            msg = clients[connection]['nick'] + ': ' + next_msg
            msg = msg.encode()
            for client in clients:
              if clients[client]['nick']:
                if clients[client]['room'] == clients[connection]['room']:
                  client.send(msg)

    for connection in exceptional:
      if connection in outputs:
        outputs.remove(connection)
      if connection in clients:
        clients.pop(connection)
      inputs.remove(connection)
      connection.shutdown(SHUT_WR)
      connection.close()
      del message_queues[connection]     

if __name__ == '__main__':
  main()
