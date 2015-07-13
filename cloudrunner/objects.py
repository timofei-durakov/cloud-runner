__author__ = 'tdurakov'


class Base(object):
    def __init__(self, fields, **kwargs):
        for key in kwargs.keys():
            if key in fields:
                setattr(self, key, kwargs[key])


class Network(Base):
    fields = {
        'name',
        'bridge',
        'network',
        'netmask',
        'broadcast',
        'gateway',
        'dhcp_start',
        'dhcp_end'
    }

    def __init__(self, **kwargs):
        super(Network, self).__init__(fields=Network.fields, **kwargs)


class App(Base):
    fields = {
        'home',
        'env',
        'image_name',
        'image_path',
        'callback_port'

    }

    def __init__(self, **kwargs):
        super(App, self).__init__(fields=App.fields, **kwargs)


class Node(Base):
    fields = {
        'name',
        'address',
        'controller',
        'home',
        'size'
    }

    def __init__(self, **kwargs):
        self.controller = False
        super(Node, self).__init__(fields=Node.fields, **kwargs)

