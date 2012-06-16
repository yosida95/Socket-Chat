#-*- coding: utf-8 -*-

import socket
import uuid
import logging
from threading import Thread

MSG_LEN_CHUNK_LENGTH = 5


def config(msg_len_chunk_length):
    global MSG_LEN_CHUNK_LENGTH
    MSG_LEN_CHUNK_LENGTH = msg_len_chunk_length


class MessageQueue(object):

    class Empty(Exception):
        pass

    def __init__(self):
        self.__queues = {}

    def connect(self):
        id = uuid.uuid4().hex
        self.__queues[id] = []
        return id

    def empty(self, id):
        if id not in self.__queues:
            Exception()

        return len(self.__queues[id]) is 0

    def put(self, id, value):
        if id not in self.__queues:
            Exception()

        ids = self.__queues.keys()
        while len(ids) > 0:
            id = ids.pop(0)
            if id in self.__queues:
                self.__queues[id].append(value)

    def get(self, id):
        if id not in self.__queues:
            Exception()

        if len(self.__queues[id]) is 0:
            raise self.Empty()

        return self.__queues[id].pop(0)

    def leave(self, id):
        if id in self.__queues:
            del self.__queues[id]


class ClientThread(Thread):

    class ClientLeft(Exception):
        pass

    def __init__(self, sock, msg_q):
        super(ClientThread, self).__init__()
        self.daemon = True

        self.sock = sock
        self.sock.setblocking(0)
        self.host, self.port = self.sock.getpeername()
        self.msg_q = msg_q
        self.msg_q_id = msg_q.connect()

    def run(self):
        while True:
            try:
                recv_msg = self.recv()
            except self.ClientLeft:
                self.msg_q.leave(self.msg_q_id)
                logging.info(u'Client left: %s:%d' % (self.host, self.port))
                break
            else:
                if recv_msg is not None:
                    self.msg_q.put(self.msg_q_id, recv_msg)

                    logging.info(u'Leceived Message \'%s\' from %s:%d' % (
                            recv_msg, self.host, self.port))

            while not self.msg_q.empty(self.msg_q_id):
                msg = self.msg_q.get(self.msg_q_id)
                self.send(msg)

                logging.info(u'Sended Message \'%s\' to %s:%d' % (
                        msg, self.host, self.port))

    def __recv_fixed_length(self, LENGTH):
        try:
            msg = u''
            while len(msg) < LENGTH:
                chunk = self.sock.recv(LENGTH - len(msg))
                if len(chunk) < 1 or chunk == '':
                    raise self.ClientLeft()
                msg += chunk.decode(u'utf8')

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
        if len(msg) < 1:
            raise Exception()

        fmt = u'%%0%dd%%s' % (MSG_LEN_CHUNK_LENGTH, )
        self.sock.sendall((fmt % (len(msg), msg)).encode(u'utf8'))


class Server(object):

    def __init__(self, host, port):
        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))

        logging.info(u'Bind %s:%d' % (host, port))

    def start(self):
        self.sock.listen(5)

        msg_q = MessageQueue()
        while True:
            logging.info(u'Waiting Connection')
            (client, address) = self.sock.accept()
            client_thread = ClientThread(client, msg_q)
            client_thread.start()
            logging.info('%s:%d has joined' % address)
