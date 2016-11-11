#!/bin/bash
set -x
echo "this script starts up an instance and pauses it so you can inspect the harddrive"
TMP=$$
# Standard ET
#IMAGEID=cbc9442d-ad55-4156-80cc-c125bd472cea
# Customized DT ET
#IMAGEID=c2c20fdc-fe6e-4865-8196-ec60f0844038
VMNAME="dt-puppettest-${TMP}"
IMAGEID=47bab1c7-28a4-4657-90c7-5d16f4855d95
echo "changing to the .. directory"
pushd ..

NEWSERVER=$(./openstack-cli.py -b -n ${VMNAME} --image=${IMAGEID} --flavor=2 --user-data-file=$(pwd)/dit-64bit-rhel6-cloud.cfg | grep ServerID | awk '{print $2}')
echo -n "$NEWSERVER is the uuid of the new server. Waiting for it to be active "
while [[ "active" != "$(./openstack-cli.py -u ${NEWSERVER} -s | grep "VM State"| awk '{print $3}')" ]]
do
  sleep 1 
  echo -n ". "
done
./openstack-cli.py -u ${NEWSERVER} -p
echo "now modify the hard drive"
popd
