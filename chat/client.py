#-*- coding: utf-8 -*-

import socket
from threading import Thread

MSG_LEN_CHUNK_LENGTH = 5


def config(msg_len_chunk_length):
    global MSG_LEN_CHUNK_LENGTH
    MSG_LEN_CHUNK_LENGTH = msg_len_chunk_length


class Client(Thread):

    def __init__(self, host, port):
        super(Client, self).__init__()
        self.daemon = True

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(1)
        self.sock.connect((host, port))

    def __recv_fixed_length(self, LENGTH):
        try:
            msg = ''
            while len(msg) < LENGTH:
                chunk = self.sock.recv(LENGTH - len(msg))
                if len(chunk) < 1 or chunk == '':
                    raise RuntimeError()
                msg += chunk
            msg.decode(u'utf8')

        except socket.error:
            msg = None

        return msg

    def recv(self):
        msg_len = self.__recv_fixed_length(MSG_LEN_CHUNK_LENGTH)
        if msg_len is None:
            msg = None
        else:
            if msg_len.isdigit():
                msg_len = int(msg_len)
            else:
                raise RuntimeError()

            msg = self.__recv_fixed_length(msg_len)
            if msg is None:
                raise RuntimeError()

        return msg

    def send(self, msg):
        fmt = u'%%0%dd%%s' % (MSG_LEN_CHUNK_LENGTH, )
        msg = msg.encode(u'utf8')
        self.sock.sendall(fmt % (len(msg), msg))
