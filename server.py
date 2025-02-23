# Copyright (C) 2013  Lukas Rist <glaslos@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import sys
import logging
import argparse
from pkipplib import pkipplib

from gevent.server import StreamServer

logger = logging.getLogger(__name__)


class PrintServer(object):

    def __init__(self):
        pass

    def handle(self, sock, address):
        print(address)
        data = sock.recv(8192)
        print(repr(data))
        try:
            body = data.split('\r\n\r\n', 1)[1]
        except IndexError:
            body = data
        request = pkipplib.IPPRequest(body)
        request.parse()
        print(request)
        request = pkipplib.IPPRequest(operation_id=pkipplib.CUPS_GET_DEFAULT)
        request.operation["attributes-charset"] = ("charset", "utf-8")
        request.operation["attributes-natural-language"] = ("naturalLanguage", "en-us")
        sock.send(request.dump())

    def get_server(self, host, port):
        connection = (host, port)
        server = StreamServer(connection, self.handle)
        logger.info('LPR server started on: {0}'.format(connection))
        return server


if __name__ == "__main__":
    print_address="127.0.0.1"
    print_port=9100

    # Parse input parameters
    parser = argparse.ArgumentParser(description='Honeyprint Honeypot')
    parser.add_argument('-i','--serveraddress', help='Select deploy server address (default localhost)', nargs='?', const='127.0.0.1', required=False)
    parser.add_argument('-p','--port', help='Select port number (default 9100)', nargs='?', const=9100, required=False)
    args = vars(parser.parse_args())
    if args['serveraddress']:
            print_address=args['serveraddress']
    if args['port']:
            print_port=int(args['port'])

    # Start print server
    ps = PrintServer()
    print_server = ps.get_server(print_address, print_port)
    print(f'Started honeyprint on {print_address}:{print_port}')
    try:
        print_server.serve_forever()
    except KeyboardInterrupt as e:
        print('Stopped honeyprint')
        sys.exit(0)
