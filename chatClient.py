#!/usr/local/bin/python3.7

from socket import *
import threading
import _thread
import sys
import os
import re
import urwid

text_str = ''
cols, rows = urwid.raw_display.Screen().get_cols_rows()

def main():
  client = socket(AF_INET, SOCK_STREAM)
  host = sys.argv[1]
  port = int(sys.argv[2])

  try:
    client.connect((host, port));

    my_term = MyTerminal()
    my_term.set_client(client)
    my_term.set_host(host)
    mainloop = urwid.MainLoop(my_term)

    new_thread = threading.Thread(target=read_client, args=[client, my_term, mainloop])
    new_thread.daemon = True
    new_thread.start()

    mainloop.run()
  except KeyboardInterrupt:
    client.shutdown(SHUT_RDWR)
    client.close()
    urwid.ExitMainLoop()
    os._exit(0)

def read_client(client, my_term, mainloop):
  while True:
    try:
      read = client.recv(4096).decode()
      if read:
        if my_term.count >= rows - 12:
          my_term.screen_text.set_text(re.sub(r'^.*\n', '', my_term.screen_text.text))
        my_term.screen_text.set_text(my_term.screen_text.text + '\n' + read)
        my_term.count = my_term.count + 1
        mainloop.draw_screen()
    except:
      _thread.interrupt_main()

def serve_file(server, filename):
  server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  server.bind(('', 6000))
  server.listen(1)

  client, address = server.accept()
  with open(filename, 'rb') as file:
    while True:
      bytes_read = file.read(4096)
      if not bytes_read:
        break
      client.sendall(bytes_read)

  client.shutdown(SHUT_WR)
  client.close()
  server.shutdown(SHUT_WR)
  server.close()

def receive_file(receiver, host):
  connected = False
  while not connected:
    try:
      if receiver.connect((host, 6001)) == None:
        connected = True
    except:
      pass
  data = receiver.recv(1024).split('\n'.encode())
  filename = data[0]
  filename = filename.decode()
  read_bytes = data[1]
  # Just in case extra bytes are sent with the filename
  if read_bytes:
    file = open(filename, 'ab')
    file.write(read_bytes)
    file.close()

  while True:
    file = open(filename, 'ab')
    read_bytes = receiver.recv(4096)
    if not read_bytes:
      file.close()
      receiver.shutdown(SHUT_RDWR)
      receiver.close()
      break
    file.write(read_bytes)
    file.close()

class MyTerminal(urwid.WidgetWrap):
  def __init__(self):
    self.screen_text = urwid.Text(text_str)
    self.prompt_text = urwid.Edit('─' * cols + '\n>> ', '')
    self._w = urwid.Frame(header=urwid.Pile([
                            urwid.Text(' ──────────────── '),
                            urwid.Text('│Chat Client v1.0│'),
                            urwid.Text('─' * cols)]),
                          body=urwid.ListBox([self.screen_text]),
                          footer=self.prompt_text,
                          focus_part='footer')
    self.count = 0
    self.client = None
    self.host = None
    self.char_limit = 80

  def set_client(self, client):
    self.client = client

  def set_host(self, host):
    self.host = host

  def keypress(self, size, key):
    filesize = False

    if key is 'esc':
      self.client.send('\\x'.encode())
      _thread.interrupt_main()
    if len(self.prompt_text.edit_text) >= self.char_limit:
      self.prompt_text.edit_text = self.prompt_text.edit_text[:self.char_limit]
    if key == 'enter':
      # User exits
      if self.prompt_text.edit_text == '\\x':
        self.client.send(self.prompt_text.edit_text.encode())
        _thread.interrupt_main()

      # User requests file transfer
      if self.prompt_text.edit_text[:3] == '\\f ':
        if len(self.prompt_text.edit_text.split(' ')) == 3:
          filename = self.prompt_text.edit_text.split(' ')[2].rstrip()
          if os.path.isfile(filename):
            filesize = os.path.getsize(filename)
            self.client.send(self.prompt_text.edit_text.encode())
            self.prompt_text.edit_text = ''
            server = socket(AF_INET, SOCK_STREAM)
            serve_thread = threading.Thread(target=serve_file, args=[server, filename])
            serve_thread.daemon = True
            serve_thread.start()         
            msg = 'file_size ' + str(filesize)
            self.client.send(msg.encode())
        elif len(self.prompt_text.edit_text.split(' ')) == 2:
          if self.prompt_text.edit_text.split(' ')[1].upper() == 'Y':
            receiver = socket(AF_INET, SOCK_STREAM)
            receive_thread = threading.Thread(target=receive_file, args=[receiver, self.host])
            receive_thread.daemon = True
            receive_thread.start()

      self.client.send(self.prompt_text.edit_text.encode())
      self.prompt_text.edit_text = ''
      return
    if len(self.prompt_text.edit_text) < self.char_limit:
      super(MyTerminal, self).keypress(size, key)
    elif key is 'backspace':
      super(MyTerminal, self).keypress(size, key)

if __name__ == '__main__':
  main()
