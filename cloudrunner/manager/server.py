__author__ = 'tdurakov'

from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse


class ServerHandler(BaseHTTPRequestHandler):

    def __init__(self, manager, *args):
        self.manager = manager
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_POST(self):
        print('in post')
        for name, value in sorted(self.headers.items()):
            print('%s=%s' % (name, value))
        ctype = self.headers['content-type']
        if ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = urlparse.parse_qs(
                    self.rfile.read(length),
                    keep_blank_values=1)
            print(postvars)
        self.send_response(200)
        self.manager.deployed_nodes.add(self.client_address)
        return

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        self.send_response(200)
        return

def handleRequestsUsing(manager):
    return lambda *args: ServerHandler(manager, *args)
