# Cloud-runner
cloud-runner is a tool for vm provision and devstack deployment

# Requirements:
 - `cloud-runner` uses `Ansible` to deliver configuration to devstack nodes
 - valid cloud image - `ubuntu`-based

#Usage:
cloudrunner [-h] -c cloud.conf {deploy,destroy,vms,ansible-only}

where:

cloud.conf - configuration file 

possible goals:

 - `deploy` - vm provision for destack node and devstack setup
 - `destroy` - full environment cleanup
 - `vms` - only vm provision, no devstack installed
 - `ansible` - only devstack install

#cloud.conf
TBD
