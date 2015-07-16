__author__ = 'tdurakov'

import ConfigParser
import os
import subprocess

from jinja2 import Environment, PackageLoader


class Base(object):
    def __init__(self, app):
        self.env = Environment(loader=PackageLoader('cloudrunner', 'template'))
        self.app = app

    def _generate_ansible_templates(self):
        raise NotImplementedError()

    def _generate_ansible_playbook(self):
        raise NotImplementedError()

    def _run_playbooks(self):
        raise NotImplementedError()

    def _build_inventory(self):
        controllers = []
        computes = []
        for node in self.app.nodes:
            if node.controller:
                controllers.append(node)
            else:
                computes.append(node)
        config = ConfigParser.RawConfigParser(allow_no_value=True)
        config.add_section('controllers')
        for node in controllers:
            config.set('controllers', node.address)
        config.add_section('computes')
        for node in computes:
            config.set('computes', node.address)
        inventory_path = os.path.join(self.app.env_home, 'hosts')
        with open(inventory_path, 'wb') as configfile:
            config.write(configfile)

    def run_ansible(self):
        self._build_inventory()
        self._generate_ansible_templates()
        self._generate_ansible_playbook()
        self._run_playbooks()


class DevstackManager(Base):

    def __init__(self, app):
        super(DevstackManager, self).__init__(app)

    def _generate_ansible_templates(self):
        compute = os.path.join(self.app.env_home, 'compute.local.conf')
        compute_template = self.env.get_template('ansible/compute.local.conf')
        compute_template.stream(app=self.app).dump(compute)
        controller = os.path.join(self.app.env_home, 'controller.local.conf')
        controller_template = self.env.get_template(
            'ansible/controller.local.conf')
        controller_template.stream(app=self.app).dump(controller)

    def _generate_ansible_playbook(self):
        controller_playbook = os.path.join(self.app.env_home,
                                           'devstack_controllers.yml')
        controller_playbook_template = self.env.get_template(
            'ansible/devstack_controllers.yml')
        controller_local_conf = os.path.join(self.app.env_home,
                                             'controller.local.conf')
        controller_playbook_template.stream(
            temlpate_path=controller_local_conf).dump(controller_playbook)

        compute_playbook = os.path.join(self.app.env_home,
                                        'devstack_computes.yml')
        compute_playbook_template = self.env.get_template(
            'ansible/devstack_computes.yml')
        compute_local_conf = os.path.join(self.app.env_home,
                                          'compute.local.conf')
        compute_playbook_template.stream(
            temlpate_path=compute_local_conf).dump(compute_playbook)

    def _run_playbooks(self):
        hosts = os.path.join(self.app.env_home, 'hosts')
        # run controllers
        controllers = os.path.join(self.app.env_home,
                                   'devstack_controllers.yml')
        subprocess.call('ansible-playbook -i %s %s' % (hosts, controllers),
                        shell=True)
        # run computes
        computes = os.path.join(self.app.env_home, 'devstack_computes.yml')
        subprocess.call('ansible-playbook -i %s %s' % (hosts, computes),
                        shell=True)


class RabbitManager(Base):

    def __init__(self, app):
        super(RabbitManager, self).__init__(app)

    def _generate_ansible_templates(self):
        cluster_nodes = []
        for node in self.app.nodes:
            cluster_nodes.append('rabbit@%s' % node.name)
        cluster_nodes = repr(cluster_nodes)

        rabbit = os.path.join(self.app.env_home, 'rabbitmq.config')
        rabbit_template = self.env.get_template(
            'ansible/rabbitmq.config')
        rabbit_template.stream(cluster_nodes=cluster_nodes).dump(rabbit)

    def _generate_ansible_playbook(self):
        rabbit_playbook = os.path.join(self.app.env_home,
                                        'rabbit.yml')
        rabbit_template = self.env.get_template(
            'ansible/rabbit.yml')
        rabbit_conf = os.path.join(self.app.env_home,
                                          'rabbitmq.config')
        rabbit_template.stream(
            temlpate_path=rabbit_conf).dump(rabbit_playbook)

    def _run_playbooks(self):
        hosts = os.path.join(self.app.env_home, 'hosts')

        rabbits = os.path.join(self.app.env_home,
                                   'rabbit.yml')
        subprocess.call('ansible-playbook -i %s %s' % (hosts, rabbits),
                        shell=True)



