__author__ = 'tdurakov'

from http.server import BaseHTTPRequestHandler

class ServerHandler(BaseHTTPRequestHandler):

    def __init__(self, manager, *args):
        self.manager = manager
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_POST(self):
        print('finished cloud-config on %s' % repr(self.client_address))
        self.send_response(200)
        self.manager.deployed_nodes.add(self.client_address)
        return

    def do_GET(self):
        self.send_response(200)
        return


def handleRequestsUsing(manager):
    return lambda *args: ServerHandler(manager, *args)
