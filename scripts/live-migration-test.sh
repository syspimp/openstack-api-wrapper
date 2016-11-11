#!/bin/bash
echo "this script will start a new instance of a certain flavor, and migrate it through all the hypervisors to test functionality"
#set -x
TMP=$$
VMNAME="dt-livemigrationtest-${TMP}"
FLAVORS=( [1]="m1.tiny" [2]="m1.small" [3]='m1.medium', [4]='m1.large' [5]='m1.xlarge' )
## image is ET_EM_centos6_4_x86_64_2013Q4V2-0
#IMAGEID="cbc9442d-ad55-4156-80cc-c125bd472cea"
## image is ET_EM_centos6_4_x86_64_2013Q4V2-DT customized
IMAGEID="c2c20fdc-fe6e-4865-8196-ec60f0844038"
## cloud-init file
CLOUDCFG="$(pwd)/dit-64bit-rhel6-cloud.cfg"
##
ROOTPARTITION="vda3"

echo "changing to the .. directory"
pushd ..
function pingit()
{
  IP=$1
  COUNT=0
  while [[ 0 -ne `ping -W 1 -c 1 $IP > /dev/null 2>&1 ; echo $?` ]]
  do
    sleep 1
    echo -n ". "
    if [ $COUNT -gt 360 ]
    then
      echo -e "\nwaited 3 mins. giving up. please shut down instance."
      exit 1
    fi
  done
  return 0
}
function checkit()
{
  IP=$1
  FLAVOR=$2
  echo "Server booted, waiting for 2 mins, then checking if it is pingable"
  sleep 120
  echo "Waking up and ping it"
  if [ pingit $ip ]
  then
    echo "It's pingable! Running checks ..."
    WHATISIT=$(ssh $IP "hostname")
    if [ "$WHATISIT" == "localhost.localdomain" ]
    then
      ISITREADY=$(ssh $IP "grep HOSTNAME /etc/sysconfig/network"| cut -d= -f2)
      if [ "${ISITREADY}" != "${WHATISIT}" ]
      then
        echo "Instance (${FLAVOR}) did not reboot, hostname is ${WHATISIT}, should be ${ISITREADY}, maybe because growpart didn't have to grow. Rebooting."
        ssh $IP "shutdown -r +1"
        checkit $IP
      fi
    else
      echo "Instance is ready. Hostname is ${WHATISIT}"
    fi
  fi
}

function hdcheck()
{
  IP=$1
  echo "Checking hd performance, writing 84mb file ..."
  HDPERF=$(ssh $IP "dd if=/dev/zero of=/tmp/output bs=8k count=10k; rm -f /tmp/output")
  echo $HDPERF
}

# loop through the sizes
for flavr in "${!FLAVORS[@]}"
do
  ##########
  # HARD CODED TO TEST
  #flavr=2
  ##########
  eval "FLAVORNAME=${FLAVORS[$flavr]}"
  LASTHYPERV=
  NEWSERVER=$(./openstack-cli.py -b -n ${VMNAME} --image=${IMAGEID} --flavor=${flavr} --user-data-file=${CLOUDCFG} | grep ServerID | awk '{print $2}')
  echo -n "${NEWSERVER}, ${VMNAME}, ${FLAVORNAME} is the uuid, name, size of the new server. Waiting for it to be active "
  while [[ "active" != "$(./openstack-cli.py -u ${NEWSERVER} -s | grep "VM State"| awk '{print $3}')" ]]
  do
    sleep 1 
    echo -n ". "
  done
  ./openstack-cli.py -u ${NEWSERVER} -s 
  IP=$(./openstack-cli.py -u ${NEWSERVER} -s| grep Networks| awk '{print $4}')
  checkit $IP $FLAVORNAME
  echo "Retrieving list of hypervisors ..."
  HYPERVS=$(./openstack-cli.py --hypervisors|grep ditcld| sed -e 's/.example.com//g'| awk '{print $2}')
  echo ${HYPERVS}
  echo "look good? continue press enter or control c to end"
  read answer
  ## lets go!
  GOODHYPERVs=()
  BADHYPERVs=()
  for hyperv in $HYPERVS
  do
    if [ -z "$LASTHYPERV" ]
    then
      LASTHYPERV=$VMHOME
    fi
    VMHOME=$(./openstack-cli.py -u ${NEWSERVER} -s | grep "Host" |sed -e 's/.example.com//g'| awk '{print $3}')
    if [ "${hyperv}" == "${VMHOME}" ]
    then
      echo "${VMNAME} already lives on ${hyperv}, skipping"
      GOODHYPERVs+=("${hyperv}")
      continue
    else
      echo "Moving ${VMNAME} to ${hyperv}"
    fi
    ./openstack-cli.py -u ${NEWSERVER} -j --hypervisor=${hyperv} --robot > /dev/null 2>&1
    if [ $? -eq 0 ]
    then
      echo -n "Migration started.  Waiting for it to be active. This may take a while depending on disk size . "
      while [[ "None" != "$(./openstack-cli.py -u ${NEWSERVER} -s | grep "Current Task"| awk '{print $3}')" ]]
      do
        sleep 1 
        echo -n ". "
      done
      echo "Success! Testing hd performance"
      hdcheck $IP
      sleep 3
      LASTHYPERV=$hyperv
      GOODHYPERVs+=("${hyperv}:${FLAVORNAME}")
    else
      echo "Hypervisor ${hyperv} has failed on ${FLAVORNAME} sized instance! Check /var/log/nova/nova-compute.log on $LASTHYPERV"
      BADHYPERVs+=("${hyperv}:${FLAVORNAME}")
    fi
  done
done
echo "Good hypervisors = ${GOODHYPERVs[@]}"
echo "Bad hypervisors = ${BADHYPERVs[@]}"

popd
