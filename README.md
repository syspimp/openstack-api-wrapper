# openstack-api-wrapper
This is a python based wrapper I made for the Juno Openstack API.

Use this if you have openstack and want to control it via the commandline, but don't want to install the binaries or use the dashboard.

[projectsdir]$ git clone https://github.com/syspimp/openstack-api-wrapper
Cloning into 'openstack-api-wrapper'...
remote: Counting objects: 3, done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (3/3), done.
Checking connectivity... done.
[openstack-api-wrapper]$ cd openstack-api-wrapper/
[openstack-api-wrapper]$ chmod +x ./openstack-cli.py 
[openstack-api-wrapper]$ ./openstack-cli.py -h

Usage: openstack-cli.py [options]

Options:
  -h, --help            show this help message and exit
  -a, --float-add       Add a floating ip to a VM
  -r, --float-remove    Remove a floating ip from a VM
  -b, --vm-boot         Boot a VM
  -q, --vm-reboot-soft  Reboot a VM, softly
  -e, --vm-reboot-hard  Reboot a VM, hard
  --vm-resetstate       Reset VM state back to active
  -c, --vm-suspend      Suspendt a VM
  -o, --vm-resume       Resume a suspended VM
  -p, --vm-pause        Pause a VM
  -z, --vm-backup       Schedule backups for a VM
  -t, --vm-unpause      Unpause a VM
  --vm-migrate          Migrate a VM, reboots
  -j, --vm-livemigrate  Live Migration of a VM, no reboot
  -x, --vm-term         Terminate a VM
  -s, --vm-show         Show a VM
  -l, --vm-list         List all VMs.
  -f, --flavors-list    List all flavors.
  -v FLAVOR, --flavor=FLAVOR
                        Flavor ID (not the uuid) to use for a VM.
  -i, --images-list     List all images.
  -m IMAGE, --image=IMAGE
                        Image uuid to use for a VM
  --project=PROJECT     set the project, should be one of ['Your_Openstack_Project',
                        'admin']
  --oshost=OSHOST       Use this hypervisor/oshost for migration, etc tasks.
                        Needs to be NAME of hypervisor found in --hypervisors.
  --oshosts             List all oshosts.
  --oshost-listvms      List all vms within project running on a
                        hypervisor/oshost.
  --hypervisor=HYPERV   Use this hypervisor/oshost for migration, etc tasks.
                        Needs to be ID of hypervisor found in --hypervisors.
  --hypervisors         List all hypervisors.
  --hyperv-listvms      List all vms within project running on a
                        hypervisor/oshost.
  --hyperv-livemigrate-off
                        Live migrates all VMs off a hypervisor.
  --hyperv-migrate-target
                        Target hypervisor for live migrating all VMs off a
                        hypervisor. Needs to be NAME of hyperv found in
                        --hypervisors
  --snapshots           List all snapshots.
  --robot               Robot mode. No confirmation.
  -g SECGROUP, --secgroup=SECGROUP
                        Security group to use.
  -k SSHKEY, --sshkey=SSHKEY
                        Name of SSH key to use.
  -y USERDATA, --user-data=USERDATA
                        String of  user data.
  -w USERDATAFILE, --user-data-file=USERDATAFILE
                        Path of a file containing user data.
  -d, --debug           Debugging
  --env=ENVIRONMENT     Environment to configure instance for. Default is dev
  --os=OS               Cloud-init setting, Operating System to configure
                        instance for. Default is rhel6
  --arch=ARCH           Cloud-init setting. Arch should be i686 or x86_64.
                        Default is x86_64
  -u UUID, --uuid=UUID  uuid to use
  -n NAME, --name=NAME  Server name to use

