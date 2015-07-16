__author__ = 'tdurakov'

import os

import netaddr

class Base(object):
    def __init__(self, fields, **kwargs):
        for key in kwargs.keys():
            if key in fields:
                setattr(self, key, kwargs[key])


class Network(Base):
    fields = {
        'name',
        'bridge',
        'netmask',
        'broadcast',
        'gateway',
        'dhcp_start',
        'dhcp_end',
        'floating_range'

    }

    def __init__(self, **kwargs):
        super(Network, self).__init__(fields=Network.fields, **kwargs)
        if self.floating_range:
            net = netaddr.IPNetwork(self.floating_range)
            self.dhcp_start = netaddr.IPAddress(net.first)
            self.dhcp_end = netaddr.IPAddress(net.last)


class App(Base):
    fields = {
        'home',
        'env',
        'image_name',
        'image_path',
        'callback_port',
        'controller_address',
        'server_key',
        'network',
        'nodes'
    }

    def __init__(self, network, nodes, controller_address, **kwargs):
        super(App, self).__init__(fields=App.fields, **kwargs)
        self.env_home = os.path.join(self.home, self.env)
        self.network = network
        self.nodes = nodes
        self.controller_address = controller_address


class Node(Base):
    fields = {
        'name',
        'address',
        'controller',
        'home',
        'disk_size',
        'memory',
        'node_home'
    }

    def __init__(self, **kwargs):
        self.controller = False
        super(Node, self).__init__(fields=Node.fields, **kwargs)

