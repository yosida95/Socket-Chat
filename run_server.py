#-*- coding: utf-8 -*-

import sys
import logging
import argparse
from chat.server import (
        Server,
        config,
    )

logging.basicConfig(level=logging.INFO,
                    format=u'%(asctime)s:%(levelname)s:%(message)s')


def getargs():
    parser = argparse.ArgumentParser(u'Socket Chat Server')
    parser.add_argument(u'--log', type=argparse.FileType(u'a'),
                        default=sys.stdout, help=u'Name of log file.')
    parser.add_argument(u'--host', type=str, required=True,
                        help=u'Host that srever listen.')
    parser.add_argument(u'--port', type=int, required=True,
                        help=u'Port that srever listen.')
    parser.add_argument(u'--msg_len_chunk_length',
                        type=int, default=5,
                        help=u'Number of length of length of message chunk')
    return parser.parse_args()

if __name__ == u'__main__':
    args = getargs()

    config(msg_len_chunk_length=args.msg_len_chunk_length)
    server = Server(host=args.host, port=args.port)
    server.start()

    logging(u'Server started.')
