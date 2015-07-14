import shutil
import subprocess
import os
from jinja2 import Environment, PackageLoader


class CloudManager(object):
    def __init__(self, app):
        self.app = app
        self.env = Environment(loader=PackageLoader('cloudrunner', 'template'))
        self.deployed_nodes = set()

    def deploy(self):
        if not os.path.exists(self.app.env_home):
            os.makedirs(self.app.env_home)
        self._create_network()
        for node in self.app.nodes:
            self._deploy_node(node)

    def destroy(self):
        for node in self.app.nodes:
            self._destroy_node(node)
        if os.path.exists(self.app.env_home):
            shutil.rmtree(path=self.app.env_home)
        self._destroy_network()

    def _generate_network(self, xml):
        template = self.env.get_template('net.xml')
        template.stream(app=self.app).dump(xml)

    def _create_network(self):
        net_xml = os.path.join(self.app.env_home, 'net.xml')
        self._generate_network(net_xml)
        subprocess.call('virsh net-define %s' % net_xml, shell=True)
        subprocess.call('virsh net-start %s' % self.app.network.name,
                        shell=True)
        subprocess.call('virsh net-autostart %s' % self.app.network.name,
                        shell=True)

    def _destroy_network(self):
        network_name = self.app.network.name
        subprocess.call('virsh net-destroy %s' % network_name,
                        shell=True)
        subprocess.call('virsh net-undefine %s' % network_name,
                        shell=True)

    def _destroy_node(self, node):
        subprocess.call('virsh destroy %s' % node.name, shell=True)
        subprocess.call('virsh undefine %s' % node.name, shell=True)

    def _deploy_node(self, node):
        node_path = os.path.join(self.app.env_home, node.name)
        if not os.path.exists(node_path):
            os.makedirs(node_path)
        node.home = node_path
        self._generate_cloud_config(node)
        image = os.path.join(self.app.image_path, self.app.image_name)
        subprocess.call('cp %s %s' % (image, node.home), shell=True)
        image_path = os.path.join(node.home, self.app.image_name)
        subprocess.call(
            'qemu-img resize %s +%s' % (image_path, node.disk_size),
            shell=True)
        config_path = os.path.join(node.home, 'config.iso')
        subprocess.call(
            'virt-install --connect=qemu:///system  --name %s --ram %s '
            '--disk path=%s,device=disk,format=qcow2 '
            '--disk path=%s,device=cdrom --vcpus=1 '
            '--vnc --noautoconsole --import  --network network:%s'
            % (node.name, node.memory, image_path, config_path,
               self.app.network.name), shell=True)

    def _generate_cloud_config(self, node):
        metadata = os.path.join(node.home, 'meta-data')
        userdata = os.path.join(node.home, 'user-data')
        metadata_template = self.env.get_template('cloud-config/meta-data')
        metadata_template.stream(app=self.app, node=node) \
            .dump(metadata)

        userdata_template = self.env.get_template('cloud-config/user-data')
        userdata_template.stream(app=self.app, node=node) \
            .dump(userdata)
        subprocess.Popen(
            'genisoimage -o config.iso -V cidata -r -J meta-data user-data',
            cwd=node.home, shell=True)