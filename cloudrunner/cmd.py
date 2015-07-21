__author__ = 'tdurakov'
import argparse
import ConfigParser
from BaseHTTPServer import HTTPServer
import os

import objects
import cloudrunner.hypervisor.manager as hyp_man
import cloudrunner.ansible.manager as ans_man
import cloudrunner.callback.server as srv


def main():
    parser = argparse.ArgumentParser(prog='cloudrunner')
    parser.add_argument('-c', dest='conf', metavar='cloud.conf', required=True,
                        help="configuration file")
    parser.add_argument('command',
                        choices=['deploy', 'destroy', 'vms', 'devstack',
                                 'rabbitmq', 'rabbitmq-clusterer'],
                        help="command to execute")
    args = parser.parse_args()
    if not (os.path.exists(args.conf)):
        print 'cloud.conf file %s not found. exiting...' % args.conf
        return 1
    config = ConfigParser.ConfigParser()
    config.read(args.conf)
    sections = config._sections

    net_obj = objects.Network(**sections.pop('network'))

    nodes_set = set()
    controller_address = None
    app_obj = objects.App(network=net_obj, nodes=nodes_set,
                      controller_address=controller_address,
                      **sections.pop('app'))
    for name, params in config._sections.iteritems():
        node = objects.Node(**params)
        nodes_set.add(node)
        if (node.controller):
            controller_address = node.address
    app_obj.controller_address = controller_address
    hypervisor_manager = hyp_man.CloudManager(app_obj)

    command = args.command
    if command == 'deploy':
        hypervisor_manager.deploy()
        wait_for_call_home(hypervisor_manager)
        ansible_manager = ans_man.DevstackManager(app_obj)
        ansible_manager.run_ansible()
    elif command == 'vms':
        hypervisor_manager.deploy()
        wait_for_call_home(hypervisor_manager)
    elif command == 'destroy':
        hypervisor_manager.destroy()
    elif command == 'devstack':
        ansible_manager = ans_man.DevstackManager(app_obj)
        ansible_manager.run_ansible()
    elif command == 'rabbitmq':
        ansible_manager = ans_man.RabbitManager(app_obj)
        ansible_manager.run_ansible()
    elif command == 'rabbitmq-clusterer':
        ansible_manager = ans_man.RabbitClustererManager(app_obj)
        ansible_manager.run_ansible()


def wait_for_call_home(manager):
    handler = srv.handleRequestsUsing(manager)
    serv = HTTPServer((manager.app.network.gateway,
                      int(manager.app.callback_port)),
                      handler)
    while len(manager.deployed_nodes) < len(manager.app.nodes):
        serv.handle_request()

if __name__ == "__main__":
    main()

