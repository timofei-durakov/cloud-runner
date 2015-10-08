__author__ = 'tdurakov'

import ConfigParser
import os
import subprocess

from jinja2 import Environment, PackageLoader


class Base(object):
    def __init__(self, app, template_params, templates):
        self.env = Environment(loader=PackageLoader('cloudrunner', 'template'))
        self.app = app
        self.template_params = template_params
        self.templates = templates

    def _generate_ansible_templates(self):
        for template in self.templates:
            self._generate_template(template)

    def _generate_template(self, name):
        out_file = os.path.join(self.app.env_home, name)
        template = self.env.get_template('ansible/%s' % name)
        template.stream(**self.template_params).dump(out_file)

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
        config.add_section('controllers:vars')
        private_key_path = os.path.join(self.app.env_home, 'keys', 'private')
        config.add_section('controllers:vars', 'ansible_ssh_private_key_file',
                           private_key_path)
        config.add_section('computes:vars')
        config.add_section('computes:vars', 'ansible_ssh_private_key_file',
                           private_key_path)
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
        template_params = {'app': app}
        templates = ['compute.local.conf', 'controller.local.conf']
        super(DevstackManager, self).__init__(app, template_params, templates)


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

    def __init__(self, app, template_params=None, templates=None):
        self.app = app
        if not template_params and not templates:
            template_params = {'cluster_nodes': self._cluster_nodes()}
            templates = ['rabbitmq.config']
        super(RabbitManager, self).__init__(app, template_params, templates)

    def _cluster_nodes(self):
        cluster_nodes = []
        for node in self.app.nodes:
            cluster_nodes.append('rabbit@%s' % node.name)
        return repr(cluster_nodes)

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


class RabbitClustererManager(RabbitManager):

    def __init__(self, app):
        self.app = app
        template_params = {'cluster_nodes': self._cluster_nodes()}
        super(RabbitClustererManager, self).__init__(
            app, template_params, ['rabbitmq-clusterer.config'])

    def _cluster_nodes(self):
        cluster_nodes = '['
        counter = 0
        for node in self.app.nodes:
            if counter > 0:
                cluster_nodes += ', '
            else:
                counter = 1
            cluster_nodes += '{rabbit@%s, disc}' % node.name
        cluster_nodes += ']'
        return cluster_nodes

    def _generate_ansible_playbook(self):
        rabbit_playbook = os.path.join(self.app.env_home,
                                        'rabbit-clusterer.yml')
        rabbit_template = self.env.get_template(
            'ansible/rabbit-clusterer.yml')
        rabbit_conf = os.path.join(self.app.env_home,
                                          'rabbitmq-clusterer.config')
        rabbit_template.stream(
            temlpate_path=rabbit_conf).dump(rabbit_playbook)

    def _run_playbooks(self):
        hosts = os.path.join(self.app.env_home, 'hosts')

        rabbits = os.path.join(self.app.env_home,
                                   'rabbit-clusterer.yml')
        subprocess.call('ansible-playbook -i %s %s' % (hosts, rabbits),
                        shell=True)
