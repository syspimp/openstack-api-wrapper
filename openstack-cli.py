#!/usr/bin/env python
import os,sys
import base64
from lib import openstack
from optparse import OptionParser
import config_openstack as config


flavors=None
images=None


parser = OptionParser()
## actions
parser.add_option("-a", "--float-add", action="store_true", dest="VMADDFLOAT", help="Add a floating ip to a VM", default=False)
parser.add_option("-r", "--float-remove", action="store_true", dest="VMRMFLOAT", help="Remove a floating ip from a VM", default=False)
parser.add_option("-b", "--vm-boot", action="store_true", dest="VMBOOT", help="Boot a VM", default=False)
parser.add_option("-q", "--vm-reboot-soft", action="store_true", dest="VMREBOOTS", help="Reboot a VM, softly", default=False)
parser.add_option("-e", "--vm-reboot-hard", action="store_true", dest="VMREBOOTR", help="Reboot a VM, hard", default=False)
parser.add_option("--vm-resetstate", action="store_true", dest="VMRESET", help="Reset VM state back to active", default=False)
parser.add_option("-c", "--vm-suspend", action="store_true", dest="VMSUSPEND", help="Suspendt a VM", default=False)
parser.add_option("-o", "--vm-resume", action="store_true", dest="VMRESUME", help="Resume a suspended VM", default=False)
parser.add_option("-p", "--vm-pause", action="store_true", dest="VMPAUSE", help="Pause a VM", default=False)
parser.add_option("-z", "--vm-backup", action="store_true", dest="VMBACKUP", help="Schedule backups for a VM", default=False)
parser.add_option("-t", "--vm-unpause", action="store_true", dest="VMUNPAUSE", help="Unpause a VM", default=False)
parser.add_option("--vm-migrate", action="store_true", dest="VMMIG", help="Migrate a VM, reboots", default=False)
parser.add_option("-j", "--vm-livemigrate", action="store_true", dest="VMLIVEMIG", help="Live Migration of a VM, no reboot", default=False)
parser.add_option("-x", "--vm-term", action="store_true", dest="VMTERM", help="Terminate a VM", default=False)
parser.add_option("-s", "--vm-show", action="store_true", dest="VMSHOW", help="Show a VM", default=False)
parser.add_option("-l", "--vm-list", action="store_true", dest="VMLIST", help="List all VMs.", default=False)
parser.add_option("-f", "--flavors-list", action="store_true", dest="FLAVORS", help="List all flavors.", default=False)
parser.add_option("-v", "--flavor", type="string", dest="FLAVOR", help="Flavor ID (not the uuid) to use for a VM.", default=config.defaultFlavor)
parser.add_option("-i", "--images-list", action="store_true", dest="IMAGES", help="List all images.", default=False)
parser.add_option("-m", "--image", type="string", dest="IMAGE", help="Image uuid to use for a VM", default=config.defaultImage)
parser.add_option("--project", type="string", dest="PROJECT", help="set the project, should be one of %s" % config.os_projects, default=False)
parser.add_option("--oshost", type="string", dest="OSHOST", help="Use this hypervisor/oshost for migration, etc tasks. Needs to be NAME of hypervisor found in --hypervisors.", default=False)
parser.add_option("--oshosts", action="store_true", dest="OSHOSTS", help="List all oshosts.", default=False)
parser.add_option("--oshost-listvms", action="store_true", dest="OSHOSTLIST", help="List all vms within project running on a hypervisor/oshost.", default=False)
parser.add_option("--hypervisor", type="string", dest="HYPERV", help="Use this hypervisor/oshost for migration, etc tasks. Needs to be ID of hypervisor found in --hypervisors.", default=False)
parser.add_option("--hypervisors", action="store_true", dest="HYPERVS", help="List all hypervisors.", default=False)
parser.add_option("--hyperv-listvms", action="store_true", dest="HYPERVLIST", help="List all vms within project running on a hypervisor/oshost.", default=False)
parser.add_option("--hyperv-livemigrate-off", action="store_true", dest="HYPERVMIG", help="Live migrates all VMs off a hypervisor.", default=False)
parser.add_option("--hyperv-migrate-target", action="store_true", dest="HYPERVTARGET", help="Target hypervisor for live migrating all VMs off a hypervisor. Needs to be NAME of hyperv found in --hypervisors", default=False)
parser.add_option("--snapshots", action="store_true", dest="SNAPS", help="List all snapshots.", default=False)
parser.add_option("--robot", action="store_true", dest="ROBOT", help="Robot mode. No confirmation.", default=False)
parser.add_option("-g", "--secgroup", type="string", dest="SECGROUP", help="Security group to use.", default=config.defaultSecGroup)
parser.add_option("-k", "--sshkey", type="string", dest="SSHKEY", help="Name of SSH key to use.", default=config.defaultSSHKey)
parser.add_option("-y", "--user-data", type="string", dest="USERDATA", help="String of  user data.", default=False)
parser.add_option("-w", "--user-data-file", type="string", dest="USERDATAFILE", help="Path of a file containing user data.", default=False)
parser.add_option("-d", "--debug", action="store_true", dest="DEBUG", help="Debugging", default=False)
parser.add_option("--env", type="string", dest="ENVIRONMENT", help="Environment to configure instance for. Default is dev", default='dev')
parser.add_option("--os", type="string", dest="OS", help="Cloud-init setting, Operating System to configure instance for. Default is rhel6", default='rhel6')
parser.add_option("--arch", type="string", dest="ARCH", help="Cloud-init setting. Arch should be i686 or x86_64. Default is x86_64", default='x86_64')
## required info for some actions
parser.add_option("-u", "--uuid", type="string", dest="UUID", help="uuid to use", default=False)
parser.add_option("-n", "--name", type="string", dest="NAME", help="Server name to use", default=False)

## get the options
(options, args) = parser.parse_args()
config.debug = options.DEBUG
_openstack=openstack(debug=config.debug)

def oshost_listvms(oshost=options.OSHOST,ask=True,tenantname='infra_eng',doall=False):
  """ we need to make a new api entry point with /v2/{tenant_id}/os-hypervisors/{hypervisor_hostname}/servers
  at http://developer.openstack.org/api-ref-compute-v2-ext.html
  """
  try:
    if options.ROBOT == False and config.confirmation == True:
      if ask == True:
        print "You need to have access rights to a project"
        tenantname = raw_input("Enter project name or accept default (default %s): " % tenantname)
        if not tenantname:
          tenantname = 'admin'
      if tenantname == 'all':
        doall = True
        tenantname = 'admin'
    else:
      tenantname = config.default_tenantname
    try:
      exec("config.tenantid = config.%s_tenantid" % tenantname)
      _openstack=openstack(osuser=config.osuser,ospass=config.ospass,tenantid=config.tenantid,debug=config.debug)
    except Exception as e:
      raise Exception('oshost_listvms: Could not switch tenants: %s Try adding the credentials to the config_openstack.py file' % e)
    print "Please wait ..."
    targethost=oshost
    if doall == True:
      total = 0
      for _tenantname in config.os_projects:
        try:
          exec("config.tenantid = config.%s_tenantid" % _tenantname)
          _openstack=openstack(osuser=config.osuser,ospass=config.ospass,tenantid=config.tenantid,debug=config.debug)
        except:
          print "User %s has no access to project %s" % (config.osuser,_tenantname)
          continue
        data=_openstack.list_servers()
        arraylength = range(len(data['servers']))
        reply = "List of vms in project %s running on hypervisor %s:\n" % (_tenantname,oshost)
        count = 0
        servers = ""
        for n in arraylength:
          name = data['servers'][n]['name']
          _server=_openstack.show_server(str(data['servers'][n]['id']))
          try:
            if targethost == str(_server['server']['OS-EXT-SRV-ATTR:hypervisor_hostname']):
              count = count + 1
              total = total + 1
              servers += str(count) + ':' + name + "\n"
          except Exception as e:
            print "Old instance %s only has hostId, can't parse hostId %s" % (name,str(_server['server']['hostId']))
            _openstack.logit("Dumping _server array:")
            _openstack.logit(_server,True)
            for i in e:
              _openstack.logit("Exception is:  %s" % i)
            continue
        reply += servers + "\nTotal: " + total
        print reply
    else:
      total = 0
      data=_openstack.list_servers()
      arraylength = range(len(data['servers']))
      reply = "List of vms in project %s running on hypervisor %s:\n" % (tenantname,oshost)
      count = 0
      servers = ""
      for n in arraylength:
        name = data['servers'][n]['name']
        _server=_openstack.show_server(str(data['servers'][n]['id']))
        try:
          if targethost == str(_server['server']['OS-EXT-SRV-ATTR:hypervisor_hostname']):
            count = count + 1
            total = total + 1
            servers += str(count) + ':' + name + "\n"
        except Exception as e:
          print "Old instance %s only has hostId, can't parse hostId %s" % (name,str(_server['server']['hostId']))
          _openstack.logit("Dumping _server array:")
          _openstack.logit(_server,True)
          continue
      reply += servers
      print reply
  except Exception as e:
    raise Exception("Exception in oshost_listvms: %s" % e)

def server_livemigration(target,hyperv=options.HYPERV,doit='n'):
  try:
    if not target:
      print "You need to give a server uuid."
    else:
      _openstack.logit("Live migrating uuid %s to host %s" % (target,hyperv))
      if options.ROBOT:
        doit = 'y'
      if doit == 'n':
        if not hyperv:
          list_hypervisors()
          hyperv = raw_input("Type the hostname of the hypervisor to live migrate to: ")
          if not hyperv:
            raise Exception('You need to pick a hypervisor to migrate to. Try again.')
        server_show(target)
        doit = raw_input("Are you SURE you want to live migrate this instance to %s? [Ny]: " % hyperv)
      if doit == 'y':
        data=_openstack.server_livemigration(target,targethost=hyperv)
        if data:
          _openstack.logit(data)
          if 'badRequest' in data:
            reply = "\n================\n"
            reply += "*Server live migration to %s failed ..." % hyperv
            reply += "\nCheck the /var/log/nova/nova-compute.log on the node above"
            reply += "\nthe vm CURRENTLY lives on for the reason why\n"
            reply += "\n\n I marked the server back to active\n\nPick another hypervisor and try again\n\n"
            reply += "\n"
            reply += "\nERROR: " +data['badRequest']['message']+"\n\n"
            _openstack.server_resetstate(target)
            if options.ROBOT:
              raise Exception(reply)
            else:
              server_show(target)
        else:
          reply = "\n================\n"
          reply += "*Server live migration to %s started ..." % hyperv
          reply += "\n================\n"
      else:
        reply = "Server still lives. Done nothing."
      if not options.ROBOT:
        print reply
  except Exception as e:
    raise Exception("Exception in server_livemigrate: %s" % e)

def server_migrate(target):
  try:
    if not target:
      print "You need to give a server uuid."
    else:
      _openstack.logit("Migrating uuid "+target)
      server_show(target)
      doit = 'n'
      doit = raw_input("Are you SURE you want to migrate this instance (scheduler decides whereto, reboots instance)? [Ny]: ")
      if doit == 'y':
        data=_openstack.server_migrate(target)
        _openstack.logit(data)
        reply = "\n================\n"
        reply += "*Server migration started ..."
        reply += "\n================\n"
      else:
        reply = "Server still lives"
      print reply
  except Exception as e:
    raise Exception("Exception in server_migrate: %s" % e)

def server_terminate(target):
  try:
    if not target:
      print "You need to give a server uuid."
    else:
      _openstack.logit("Terminating uuid "+target)
      server_show(target)
      doit = 'n'
      doit = raw_input("Are you SURE you want to shutdown this instance? [Ny]: ")
      if doit == 'y':
        data=_openstack.server_terminate(target)
        _openstack.logit(data)
        reply = "\n================\n"
        reply += "*Server KILLED*"
        reply += "\n================\n"
      else:
        reply = "Server still lives"
      print reply
  except Exception as e:
    raise Exception("Exception in server_terminate: %s" % e)

def server_floatip(target,action='ADD'):
    try:
      if not target:
        print "You need to give a server uuid."
      else:
        if action == 'ADD':
          _openstack.logit("Adding Floating IP to "+target)
          data=_openstack.server_floatip('ADD',target)
          reply += "\n================================\n"
          reply += "*Added Floating IP "+data+"*"
          reply += "\n=================================\n"
          print reply
        elif action == 'DEL':
          _openstack.logit("Adding Floating IP to "+target)
          data=_openstack.server_floatip('DEL',target)
          reply += "\n================================\n"
          reply += "*Deleted Floating IP "+data+"*"
          reply += "\n=================================\n"
          print reply
        else:
          print 'Doing nothing in floatip, action is not ADD or DEL floatip'
    except Exception as e:
      raise Exception("Exception in server_floatip: %s" % e)

def server_pause(target):
    try:
      if not target:
        print "You need to give a server uuid."
      else:
        import re
        checkif_uuid = re.compile('[0-9a-f\-]{36}\Z', re.I)
        if checkif_uuid.match(target):
          data=_openstack.server_pause(target)
        else:
          _openstack.logit("NOT a uuid, perhaps using the name?")
          ndata=_openstack.list_servers()                                                                                                                  
          arraylength = range(len(ndata['servers']))
          for n in arraylength:
            _openstack.logit(ndata['servers'][n]['name'])
            if target == ndata['servers'][n]['name']:
              data=_openstack.server_pause(ndata['servers'][n]['id'])
        _openstack.logit("results of pause server:")
        _openstack.logit(data)
        reply = "\n===============\n"
        reply += "Server PAUSED\n"
        print reply
        server_show(target)
    except Exception as e:
      raise Exception("Exception in server_pause: %s" % e)

def server_unpause(target):
    try:
      if not target:
        print "You need to give a server uuid."
      else:
        import re
        checkif_uuid = re.compile('[0-9a-f\-]{36}\Z', re.I)
        if checkif_uuid.match(target):
          data=_openstack.server_unpause(target)
        else:
          _openstack.logit("NOT a uuid, perhaps using the name?")
          ndata=_openstack.list_servers()                                                                                                                  
          arraylength = range(len(ndata['servers']))
          for n in arraylength:
            _openstack.logit(ndata['servers'][n]['name'])
            if target == ndata['servers'][n]['name']:
              data=_openstack.server_unpause(ndata['servers'][n]['id'])
        _openstack.logit("results of unpause server:")
        _openstack.logit(data)
        reply = "\n===============\n"
        reply += "Server UNPAUSED\n"
        print reply
        server_show(target)
    except Exception as e:
      raise Exception("Exception in server_unpause: %s" % e)

def server_suspend(target):
    try:
      if not target:
        print "You need to give a server uuid."
      else:
        data=_openstack.server_suspend(target)
        _openstack.logit("results of suspend server:")
        _openstack.logit(data)
        reply = "\n===============\n"
        reply += "Server SUSPENDED\n"
        print reply
        server_show(target)
    except Exception as e:
      raise Exception("Exception in server_suspend: %s" % e)

def server_resume(target):
    try:
      if not target:
        print "You need to give a server uuid."
      else:
        data=_openstack.server_resume(target)
        _openstack.logit("results of resume server:")
        _openstack.logit(data)
        reply = "\n===============\n"
        reply += "Server RESUMED\n"
        print reply
        server_show(target)
    except Exception as e:
      raise Exception("Exception in server_resume: %s" % e)

def server_reboot(target,action='SOFT'):
    try:
      if not target:
        print "You need to give a server uuid."
      else:
        data=_openstack.server_reboot(target,rebootType=action)
        _openstack.logit("results of reboot server:")
        _openstack.logit(data)
        reply = "\n===============\n"
        reply += "Server REBOOTED\n"
        print reply
        server_show(target)
    except Exception as e:
      raise Exception("Exception in server_reboot: %s" % e)

def server_resetstate(target):
    try:
      if not target:
        print "You need to give a server uuid."
      else:
        data=_openstack.server_resetstate(target)
        _openstack.logit("results of reset state of server:")
        _openstack.logit(data)
        reply = "\n===============\n"
        reply += "Server marked Active\n"
        print reply
        server_show(target)
    except Exception as e:
      raise Exception("Exception in server_resetstate: %s" % e)

def server_show(target):
    try:
      _openstack=login()
      if not target:
        print "You need to give a server uuid."
      else:
        import re
        checkif_uuid = re.compile('[0-9a-f\-]{36}\Z', re.I)
        if checkif_uuid.match(target):
          data=_openstack.show_server(target)
        else:
          _openstack.logit("NOT a uuid, perhaps using the name?")
          ndata=_openstack.list_servers()                                                                                                                  
          arraylength = range(len(ndata['servers']))
          for n in arraylength:
            _openstack.logit(ndata['servers'][n]['name'])
            if target == ndata['servers'][n]['name']:
              data=_openstack.show_server(ndata['servers'][n]['id'])
        _openstack.logit("results of show server:")
        _openstack.logit(data)
        arraylength = range(len(data['server']))
        current_task = 'None'
        reply = "\n==============="
        reply += "\nServer Name: "
        reply += "\t"+str(data['server']['name'])
        reply += "\nCreated: "
        reply += "\t"+str(data['server']['created'])
        reply += "\nNetworks: "
        for net in data['server']['addresses']:
          _openstack.logit("net is %s" % net)
          _openstack.logit(data['server']['addresses'][net])
          for i in  data['server']['addresses'][net]:
            reply += "\t"+net+": "+i['addr']
        reply += "\nServer Security Groups: "
        for sec in data['server']['security_groups']:
          _openstack.logit(data['server']['security_groups'])
          _openstack.logit(sec)
          reply +=  "\t"+sec['name']
        if data['server']['OS-EXT-STS:task_state']:
          current_task = data['server']['OS-EXT-STS:task_state']
        reply += "\nKey Name: "
        reply += "\t"+str(data['server']['key_name'])
        reply += "\nMetadata:\n"
        for k in data['server']['metadata']:
          reply +=  "\t%s = %s\n" % (k,data['server']['metadata'][k])
        reply += "\nVM State: "
        reply += "\t"+str(data['server']['OS-EXT-STS:vm_state'])
        reply += "\nCurrent Task: "
        reply += "\t"+str(current_task)
        reply += "\nFlavor: "
        flavors=_openstack.show_flavor(data['server']['flavor']['id'])
        for flavor in flavors:
          reply += "\t"+str(flavors[flavor]['name'])
        try:
          reply += "\nOn Host: "
          reply += "\t"+str(data['server']['OS-EXT-SRV-ATTR:hypervisor_hostname'])
          reply += "\n===============\n"
        except Exception:
          pass
        print reply
    except Exception as e:
      raise Exception("Exception in server_show: %s" % e)

def server_boot(target,image=options.IMAGE,flavor=options.FLAVOR,secgroup=options.SECGROUP,key_name=options.SSHKEY,user_data=options.USERDATA,user_data_file=options.USERDATAFILE):
    try:
      if not target:
        print "You need to give a server uuid."
      else:
        userdata=base64.b64encode(b'echo this is a test')
        if user_data or user_data_file:
          if user_data:
            userdata = base64.b64encode(b'%s' % user_data)
            _openstack.logit("userdata is:")
            _openstack.logit(userdata)
          else:
            _openstack.logit("userdata file is %s:" % user_data_file)
            with open(user_data_file) as f:
              contents=f.read()
              _openstack.logit("TESTING VARIABLE SUBSTITION. ONLY ENVIRONMENT,OS,ARCH IMPLEMENTED. old userdata file contents is:")
              _openstack.logit(contents)
              #print type(contents)
              contents=contents.replace('${ET_ENVIRONMENT}',options.ENVIRONMENT)
              contents=contents.replace('${ET_OS}',options.OS)
              contents=contents.replace('${ET_ARCH}',options.ARCH)
              _openstack.logit("new userdata file contents is:")
              _openstack.logit(contents)
              userdata = base64.b64encode(contents)
              #sys.exit(1)
            #_openstack.logit("base64 userdata file is:")
            #_openstack.logit(userdata)
        _openstack.logit("Starting flavor %s, image %x, name "+target)
        data=_openstack.server_boot(target,imageRef=image,flavorRef=flavor,secgroup=secgroup,key_name=key_name,user_data=userdata)
        _openstack.logit("results of server start:")
        _openstack.logit(data)
        reply = "\n==============="
        reply += "\nServerID: "
        reply += "\t"+str(data['server']['id'])
        reply += "\nServer Security Groups: "
        for sec in data['server']['security_groups']:
          _openstack.logit(data['server']['security_groups'])
          _openstack.logit(sec)
          reply +=  "\t"+sec['name']
        reply += "\nAdmin Pass: "
        reply += "\t"+str(data['server']['adminPass'])
        #print ips
        reply += "\n===============\n"
        print reply
    except Exception as e:
      raise Exception("Exception in server_boot: %s" % e)

def hypervisor_show(target=options.HYPERV):
  try:
    if not target:
      _openstack.logit('no target given for hypervisor_show. it return all the hyperv info anyway.')
      data=_openstack.show_hypervisor('1')
      arraylength = range(len(data['hypervisors']))
      reply = ""
      for n in arraylength:
        _openstack.logit(data['hypervisors'][n], True)
        reply += "\n===============\n"
        reply += "Hypervisor Name:\t"+str(data['hypervisors'][n]['hypervisor_hostname']) + "\n"
        reply += "Id:\t"+str(data['hypervisors'][n]['id']) + "\n"
        reply += "\nVM's running on this hypervisor:\n"
        try:
          sarraylength = range(len(data['hypervisors'][n]['servers']))
          for s in sarraylength:
            reply += "UUID:\t" + str(data['hypervisors'][n]['servers'][s]['uuid']) + "\tName:\t" + str(data['hypervisors'][n]['servers'][s]['name']) + "\n"
        except Exception as e:
          for i in e:
            _openstack.logit("Exception is : %s" % i)
          if 'servers' in e:
            reply += "this hypervisor doesnt have any servers\n"
          continue
    else:
      _openstack.logit("target is " +target)
      data=_openstack.show_hypervisor('1')
      arraylength = range(len(data['hypervisors']))
      reply = None
      for n in arraylength:
        if target in data['hypervisors'][n]['hypervisor_hostname']:
          reply = "\n===============\n"
          reply += "Hypervisor Name:\t"+str(data['hypervisors'][n]['hypervisor_hostname']) + "\n"
          reply += "Id:\t"+str(data['hypervisors'][n]['id']) + "\n"
          reply += "\nVM's running on this hypervisor:\n"
          try:
            sarraylength = range(len(data['hypervisors'][n]['servers']))
            for s in sarraylength:
              reply += "UUID:\t" + str(data['hypervisors'][n]['servers'][s]['uuid']) + "\tName:\t" + str(data['hypervisors'][n]['servers'][s]['name']) + "\n"
          except Exception as e:
            for i in e:
              _openstack.logit("Exception is : %s" % i)
            if 'servers' in e:
              reply += "this hypervisor doesnt have any servers\n"
        else:
          continue
    if not reply:
      print "I could not find that hypervisor. Try --hypervisors to get a usable ID"
    else:
      print reply+"\n"
  except Exception as e:
    _openstack.logit(data['hypervisors'],True)
    _openstack.logit('n is '+str(n))
    raise Exception("Exception in hypervisor_show: %s" % e)

def hypervisor_livemigrateoff(source=options.HYPERV,target=options.HYPERVTARGET):
  """source should be the ID from show_hypervisors
     target is the hostname to move the vms to
  """
  try:
    if not source:
      print "You need to give an id."
    else:
      data=_openstack.show_hypervisor(source)
      _openstack.logit("results of show hypervisors:")
      _openstack.logit(data)
      arraylength = range(len(data['hypervisors']))
      allvms = []
      for n in arraylength:
        reply += "Hypervisor Name:\t"+str(data['hypervisors'][n]['hypervisor_hostname']) + "\n"
        reply += "Id:\t"+str(data['hypervisors'][n]['id']) + "\n"
        reply += "\nVM's running on this hypervisor:\n"
        sarraylength = range(len(data['hypervisors'][n]['servers']))
        for s in sarraylength:
          allvms.append(str(data['hypervisors'][n]['servers'][s]['uuid']))
      print reply+"\n"
      
      doit = raw_input("Are you SURE you want to migrate all vms off hypervisor %s to hypervisor %s? [Ny]: " % (source, target))
      if doit == 'y':
        for vm in allvms:
          server_livemigrate(vm,doit=True)

  except Exception as e:
    raise Exception("Exception in hypervisor_show: %s" % e)

def list_flavors():
  try:
    data=_openstack.list_flavors()
    arraylength = range(len(data['flavors']))
    reply="Flavor ID,Name\n"
    for n in arraylength:
      reply += "\t"+str(data['flavors'][n]['id'])
      reply += "\t"+data['flavors'][n]['name'] + "\n"
    print reply
  except Exception as e:
    raise Exception("Exception in list_flavors: %s" % e)

def list_snapshots():
  try:
    _openstack=login()
    data=_openstack.list_snapshots()
    arraylength = range(len(data['snapshots']))
    reply = "Snap ID, Name, description, volume id, status, size, created:\n"
    for n in arraylength:
      reply += "\t"+str(data['snapshots'][n]['id'])
      reply += "\t"+data['snapshots'][n]['display_name']
      reply += "\t"+data['snapshots'][n]['display_description']
      reply += "\t"+data['snapshots'][n]['volume_id']
      reply += "\t"+data['snapshots'][n]['status']
      reply += "\t"+str(data['snapshots'][n]['size'])
      reply += "\t"+data['snapshots'][n]['created_at']
    print reply
  except Exception as e:
    raise Exception("Exception in list_snapshots: %s" % e)

def list_servers():
  try:
    _openstack=login()
    data=_openstack.list_servers()
    arraylength = range(len(data['servers']))
    reply = "Server ID, Name, IP:\n"
    for n in arraylength:
      reply += "\t"+str(data['servers'][n]['id'])
      reply += "\t"+data['servers'][n]['name']
      ips=_openstack.show_server_ips(str(data['servers'][n]['id']))
      for net in ips['addresses']:
        #print "net is %s" % net
        #print ips['addresses'][net]
        for i in  ips['addresses'][net]:
          reply += "\t"+net+": "+i['addr']+"\n"
      #print ips
    print reply
  except Exception as e:
    raise Exception("Exception in list_servers: %s" % e)

def list_hypervisors():
  try:
    data=_openstack.list_hypervisors()
    arraylength = range(len(data['hypervisors']))
    reply = "Server ID, Name:\n"
    for n in arraylength:
      reply += "\t"+str(data['hypervisors'][n]['id'])
      reply += "\t"+data['hypervisors'][n]['hypervisor_hostname'] + "\n"
    print reply
  except Exception as e:
    #_openstack.logit("Dumping list_hypervisor retrieved data")
    #_openstack.logit(data)
    raise Exception("Exception in list_hypervisors: %s" % e)

def list_oshosts():
  try:
    data=_openstack.list_oshosts()
    arraylength = range(len(data['hosts']))
    reply="Hostname,Service,Zone\n"
    for n in arraylength:
      reply += "\t"+data['hosts'][n]['host_name']
      reply += "\t"+data['hosts'][n]['service']
      reply += "\t"+data['hosts'][n]['zone'] + "\n"
    print reply
  except Exception as e:
    raise Exception("Exception in list_oshosts: %s" % e)


def list_images():
  try:
    data=_openstack.list_images()
    arraylength = range(len(data['images']))
    reply="Name ID,Name\n"
    for n in arraylength:
      reply += "\t"+str(data['images'][n]['id'])
      reply += "\t"+data['images'][n]['name'] + "\n"
    print reply
  except Exception as e:
    raise Exception("Exception in list_images: %s" % e)

def login():
  try:
    if options.ROBOT == False and config.confirmation == True:
      import getpass
      user = raw_input("Hit enter to use config settings.\nUsername [%s]: " % config.osuser)
      passwd = getpass.getpass()
      tenantname = raw_input("Enter project name or accept default (default %s): " % config.default_tenantname)
      if user:
        config.osuser = user
      if passwd:
        config.ospass = passwd
      if not tenantname:
        tenantname = config.tenantname
      if tenantname in config.os_projects:
        try:
          exec("config.tenantid = config.%s_tenantid" % tenantname)
        except Exception as e:
          raise Exception("Could not configure tenantname %s add credentials to the config_openstack.py file, exception: %s" % (tenantname,e))
      else:
        raise Exception("Unknown tenantname '%s' add credentials to the config_openstack.py file" % tenantname)
      return openstack(osuser=config.osuser,ospass=config.ospass,tenantid=config.tenantid,debug=config.debug)
    else:
      return openstack(osuser=config.osuser,ospass=config.ospass,tenantid=config.tenantid,debug=config.debug)
  except Exception as e:
    raise Exception("Exception in login: %s" % e)

def mainloop():
  if options.PROJECT:
    exec("config.tenantid = config.%s_tenantid" % options.PROJECT)
    _openstack=openstack(osuser=config.osuser,ospass=config.ospass,tenantid=config.tenantid,debug=config.debug)
  if options.VMRESET or options.VMMIG or options.VMLIVEMIG or options.VMADDFLOAT or options.VMRMFLOAT or options.VMTERM or options.VMSHOW or options.VMREBOOTR or options.VMREBOOTS or options.VMSUSPEND or options.VMRESUME or options.VMPAUSE or options.VMUNPAUSE:
    if not options.UUID:
      print 'You need to give me the uuid to work on. Perform -l to see all vm info'
      sys.exit(1)
    if options.VMTERM:
      login()
      _openstack=openstack(debug=config.debug)
      server_terminate(options.UUID)
    elif options.VMMIG or options.VMLIVEMIG:
      if options.VMLIVEMIG:
        #if not options.OSHOST:
        #  print 'You need to give me the host to work on. Perform -l to see all vm info'
        #  sys.exit(1)
        #login()
        server_livemigration(options.UUID)
      else:
        server_migrate(options.UUID)
    elif options.VMRESET:
      server_resetstate(options.UUID)
    elif options.VMADDFLOAT or options.VMRMFLOAT:
      action='ADD'
      if options.VMRMFLOAT:
        action='DEL'
      server_floatip(options.UUID,action=action)
    elif options.VMREBOOTR or options.VMREBOOTS:
      action='HARD'
      if options.VMREBOOTS:
        action='SOFT'
      server_reboot(options.UUID,action=action)
    elif options.VMSUSPEND:
      server_suspend(options.UUID)
    elif options.VMRESUME:
      server_resume(options.UUID)
    elif options.VMUNPAUSE:
      server_unpause(options.UUID)
    elif options.VMPAUSE:
      server_pause(options.UUID)
    else:
      server_show(options.UUID)
  elif options.VMLIST or options.FLAVORS or options.IMAGES:
    if options.FLAVORS:
      list_flavors()
    elif options.IMAGES:
      list_images()
    elif options.VMLIST:
      list_servers()
  elif options.VMBOOT:
    if not options.NAME:
      print "I need a server name to boot a VM"
      sys.exit(1)
    server_boot(options.NAME)
  elif options.OSHOSTLIST or options.OSHOSTS:
    if options.OSHOSTS:
      list_oshosts()
    elif options.OSHOSTLIST:
      if not options.OSHOST:
        print "I need an oshost. Use --oshosts to show all oshosts, then use --oshost=myhost"
        sys.exit(1)
      else:
        oshost_listvms()
  elif options.HYPERVLIST or options.HYPERVS or options.HYPERVMIG:
    if options.HYPERVS:
      list_hypervisors()
    elif options.HYPERVLIST:
        hypervisor_show()
    elif options.HYPERVMIG:
      if not options.HYPERV:
        print "I need an hypervisor. Use --hypervisors to show all hypervisors, then use --hypervisor=ID"
        sys.exit(1)
      else:
        hypervisor_livemigrateoff()
  elif options.SNAPS:
    list_snapshots()
  else:
    print "I need something to do, use -h for help."
    sys.exit(1)

if __name__=='__main__':
  try:
    mainloop()
  except KeyboardInterrupt:
    print("\nbye bye")
  except Exception as e:
    print "Exception occurred. Use -d for more information."
    for i in e:
      _openstack.logit(i)
    sys.exit(1)
