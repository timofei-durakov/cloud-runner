
import subprocess
import argparse
import ConfigParser
import os

from jinja2 import Environment, PackageLoader
from cloudrunner import objects


class CloudManager(object):
    def __init__(self, network, nodes, app):
        self.network = network
        self.nodes = nodes
        self.app = app
        self.env = Environment(loader=PackageLoader('cloudrunner', 'template'))

    def deploy(self):
        path = os.path.join(self.app.home, self.app.env)
        if not os.path.exists(path):
            os.makedirs(path)
        self._create_network(path)
        for node in self.nodes:
            self._deploy_node(node, path)

    def _generate_network(self, xml):
        template = self.env.get_template('net.xml')
        template.stream(network=self.network).dump(xml)

    def _create_network(self, home):
        net_xml = os.path.join(home, 'net.xml')
        self._generate_network(net_xml)
        subprocess.call(['virsh net-define ' + net_xml], shell=True)
        subprocess.call(['virsh net-start ' + self.network.name], shell=True)
        subprocess.call(['virsh net-autostart ' + self.network.name],
                        shell=True)

    def _deploy_node(self, node, home):
        node_path = os.path.join(home, node.name)
        if not os.path.exists(node_path):
            os.makedirs(node_path)
        node.home = node_path
        self._generate_cloud_config(node)
        image = os.path.join(self.app.image_path, self.app.image_name)
        # subprocess.call('qemu-img create -f qcow2 ' +
        #                 os.path.join(node.home, 'root.qcow2') +
        #                 ' ' + node.size, shell=True)

        # subprocess.call('virt-resize --expand /dev/sda1 ' + image +' ' +os.path.join(node.home, 'root.qcow2'), shell=True)
        subprocess.call('cp ' + image + ' ' + node.home, shell=True)
        subprocess.call(' qemu-img resize ' + os.path.join(node.home, self.app.image_name)+' +' + node.size, shell=True)
        subprocess.call('virt-install --connect=qemu:///system  --name ' + node.name +
                         ' --ram 512 --disk path=' + os.path.join(node.home, self.app.image_name) +
                         ',device=disk,format=qcow2 --disk path='+os.path.join(node.home, 'config.iso')+',device=cdrom '
                         '--vcpus=1 --vnc --noautoconsole --import  --network network:' + self.network.name, shell=True)

    def _generate_cloud_config(self, node):
        metadata = os.path.join(node.home, 'meta-data')
        userdata = os.path.join(node.home, 'user-data')
        metadata_template = self.env.get_template('cloud-config/meta-data')
        metadata_template.stream(network=self.network, node=node)\
            .dump(metadata)

        userdata_template = self.env.get_template('cloud-config/user-data')
        userdata_template.stream(network=self.network, node=node)\
            .dump(userdata)
        subprocess.Popen('genisoimage -o config.iso -V cidata -r -J meta-data user-data', cwd=node.home, shell=True)










def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', help="config file")
    args = parser.parse_args()
    config = ConfigParser.ConfigParser()
    config.read(args.conf)
    sections = config._sections

    net_obj = objects.Network(**sections.pop('network'))
    app_obj = objects.App(**sections.pop('app'))
    nodes_set = set()
    for name, params in config._sections.iteritems():
        nodes_set.add(objects.Node(**params))
    manager = CloudManager(net_obj, nodes_set, app_obj)
    manager.deploy()
    # template = env.get_template('net.xml')
    # print template.render(network=net_obj)
