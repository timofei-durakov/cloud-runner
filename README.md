# Cloud-runner
cloud-runner is a tool for vm provision and devstack deployment

# Requirements:
 - `cloud-runner` uses `Ansible` to deliver configuration to devstack nodes
 - valid cloud image - `ubuntu`-based

#Usage:
cloudrunner [-h] -c cloud.conf {deploy,destroy,vms,devstack-only,rabbit-only}

where:

cloud.conf - configuration file 

possible goals:

 - `deploy` - vm provision for destack node and devstack setup
 - `destroy` - full environment cleanup
 - `vms` - only vm provision, no devstack installed
 - `devstack-only` - only devstack install
 - `rabbit-only` - only rabbitmq install

#cloud.conf
 Configuration file consists of 3 section types:
 
 - `app` - section for application level setting. One per file:
     * home - path on host system to store all environment related data
     * env - env directory in home
     * image_path - path to cloud-image
     * image_name - image file name
     * callback_port - port to serve ass callback for cloud-init
     * server_key - public rsa key for remote access to booted vms, also used by Ansible
 - `network` - description of network, that should be created for vms. One per file:
     * name - network name for libvirt
     * bridge - bridge name in host system
     * netmask - network mask
     * broadcast - broadcast address
     * gateway - gateway address
     * floating_range - floating range CIDR
 - `node` - node specific settings. One for node, that should be booted:
     * name - name used in hypervisor during and hostname of vm
     * address - ip address
     * disk_size - amount of  memory for hdd in GB. Example: 20G
     * memory - amount of RAM Example: 3500


Example: 
[cloud.conf][1]

[1]:https://github.com/timofei-durakov/cloud-runner/blob/master/cloud.conf
