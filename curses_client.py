#-*- coding: utf-8 -*-

import curses
from chat.client import Client
from threading import Thread

import locale
locale.setlocale(locale.LC_ALL, "")


class CursesClient:

    def __init__(self, client, name):
        self.client = client
        self.name = name

        self.client.send(u'system: %s has joined' % (self.name, ))

        self.screen = curses.initscr()
        curses.noecho()
        self.screen.keypad(1)
        curses.cbreak()

    def render_windows(self):
        height, width = self.screen.getmaxyx()

        self.conv_window = curses.newwin(height - 1, width, 0, 0)
        self.input_window = curses.newwin(1, width, height - 1, 0)

        self.screen.refresh()

    def get_message(self):
        lines = []

        def callback(msg):
            lines.append(msg)

            self.conv_window.erase()
            height, width = self.conv_window.getmaxyx()
            for y, msg in enumerate(lines[len(lines) - height:len(lines)]):
                self.conv_window.addstr(y, 0, msg)
            self.conv_window.refresh()

            self.input_window.move(0, 0)
            self.input_window.refresh()

        return callback

    def start(self):
        self.render_windows()
        client_thread = Thread(target=self.client.start,
                               args=(self.get_message(), ))
        client_thread.daemon = True
        client_thread.start()

        while True:
            self.input_window.erase()
            curses.echo()
            msg = self.input_window.getstr()
            curses.noecho()
            if len(msg) > 0:
                self.client.send(u'%s: %s' % (self.name, msg))

    def stop(self):
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

    def __del__(self):
        self.stop()


def getargs():
    try:
        import argparse
        parser = argparse.ArgumentParser(u'Socket Chat Client')
        parser.add_argument(u'--host', type=str, required=True,
                            help=u'Host of server')
        parser.add_argument(u'--port', type=int, required=True,
                            help=u'Host of server')
        parser.add_argument(u'--name', type=str, required=True,
                            help=u'Your name.')

    except ImportError:
        import optparse
        parser = optparse.OptionParser(u'Socket Chat Client')
        parser.add_option('--host', type='string',
                          help=u'Host of server')
        parser.add_option('--port', type=u'int',
                          help=u'Host of server')
        parser.add_option('--name', type=u'string',
                          help=u'Your name.')

        args = parser.parse_args()[0]
    else:
        args = parser.parse_args()
    finally:
        return args


def main():
    args = getargs()

    client = Client(host=args.host, port=args.port)
    curses_client = CursesClient(client, name=args.name)

    try:
        curses_client.start()
    except:
        curses_client.stop()

if __name__ == '__main__':
    main()
