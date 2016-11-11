import sys,os
import base64
from pprint import pprint
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/../')
import config_openstack as config
from access_abstract import access

class openstack:
  def __init__(self,osuser=config.osuser,ospass=config.ospass,tenantid=config.tenantid,oshost=config.oshost,debug=config.debug,tenantname=None):
    self._access=access(debug=debug)
    self.debug=debug
    if tenantname:
      try:
        exec("self.tenantid = config.%s_tenantid" % tenantname)
      except Exception as e:
        raise Exception("Could not configure tenantname %s, please check the config_openstack.py file. exception: %s" % (tenantname,e))
    else:
      self.tenantid=tenantid
    self.osuser=osuser
    self.ospass=ospass
    self.novahost=config.oshost+':8774'
    self.keystonehost=config.oshost+':5000'
    self.defaultFlavor=config.defaultFlavor,
    self.defaultImage=config.defaultImage
    self.defaultSecgroup=config.defaultSecGroup
    self.defaultSSHKey=config.defaultSSHKey
    cmds = {  'host': self.keystonehost,
              'url':  '/v2.0/tokens',
              'method': 'POST',
              'params': '{"auth":{"passwordCredentials":{"username": "'+self.osuser+'", "password":"'+self.ospass+'"}, "tenantId":"'+self.tenantid+'"}}',
              'headers':  {"Content-Type": "application/json"}
    }
    try:
      dd = self._access._json_access(cmds)
      self.apitoken = dd['access']['token']['id']
      self.logit("succesfully inited openstack lib")
      #self.apiurl = dd['access']['serviceCatalog']['nova'][0]['publicURL']
      #self.apiurlt = urlparse(dd['access']['serviceCatalog']['nova'][0]['publicURL'])
      #print 'openstack init complete'
    except Exception as e:
      raise Exception('openstack init exception: %s' % e)

  def logit(self,msg,isobject=False):
    try:
      if self.debug:
        if isobject:
          pprint(msg)
        else:
          print msg
    except Exception as e:
      raise Exception('openstack logit exception: %s' % e)

  def _poll(self,url,method='GET',version='v2'):
    cmds = {  'host': self.novahost,
              'url':  '/' + version + '/' + self.tenantid + url,
              'method': method,
              'params': '{"X-Auth-Token": %s}' % self.apitoken,
              'headers':  {"X-Auth-Token": self.apitoken}
    }
    try:
      self.logit('polling using cmds: %s' % cmds)
      return self._access._json_access(cmds)
    except Exception as e:
      self.logit('openstack _poll  exception:')
      for i in e:
        self.logit(i)

  def _post(self,url,params,method='POST'):
    try:
      if method != 'DELETE':
        cmds = {  'host': self.novahost,
                  'url':  '/v2/' + self.tenantid + url,
                  'method': method,
                  'params': params,
                  'headers':  {
                    "X-Auth-Token": self.apitoken,
                    "Content-type": "application/json"
                  }
        }
      else:
        cmds = {  'host': self.novahost,
                  'url':  '/v2/' + self.tenantid + url,
                  'method': method,
                  'params': None,
                  'headers':  {
                    "X-Auth-Token": self.apitoken,
                    "Content-type": "application/json"
                  }
        }

      self.logit('posting using cmds: %s' % cmds)
      return self._access._json_access(cmds)
    except Exception as e:
      self.logit('openstack _post exception:')
      for i in e:
        self.logit(i)

  def list_servers(self):
    return self._poll('/servers')

  def list_snapshots(self):
    return self._poll('/snapshots',version='v2')

  def list_flavors(self):
    return self._poll('/flavors')

  def list_images(self):
    return self._poll('/images')

  def list_oshosts(self):
    return self._poll('/os-hosts')

  def list_hypervisors(self):
    return self._poll('/os-hypervisors')

  def show_server(self,id):
    return self._poll('/servers/'+id)

  def show_server_ips(self,id):
    return self._poll('/servers/'+id+'/ips')

  def show_flavor(self,id):
    return self._poll('/flavors/'+id)

  def show_hypervisor(self,target):
    return self._poll('/os-hypervisors/'+target+'/servers')

  def server_reboot(self,serverid=None,rebootType = "HARD"):
    try:
      cmds = {'url':  '/servers/'+serverid+'/action',
              'params': '{"reboot": {"type": "'+rebootType+'"}}',
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack reboot exception:')
      for i in e:
        self.logit(i)

  def server_suspend(self,serverid):
    try:
      cmds = {'url':  '/servers/'+serverid+'/action',
              'params': '{"suspend": null}',
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack suspend exception:')
      for i in e:
        self.logit(i)

  def server_resume(self,serverid):
    try:
      cmds = {'url':  '/servers/'+serverid+'/action',
              'params': '{"resume": null}',
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack resume exception:')
      for i in e:
        self.logit(i)

  def server_pause(self,serverid):
    try:
      cmds = {'url':  '/servers/'+serverid+'/action',
              'params': '{"pause": null}',
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack pause exception:')
      for i in e:
        self.logit(i)

  def server_unpause(self,serverid):
    try:
      cmds = {'url':  '/servers/'+serverid+'/action',
              'params': '{"unpause": null}',
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack unpause exception:')
      for i in e:
        self.logit(i)

  def server_migrate(self,serverid):
    try:
      cmds = {'url':  '/servers/'+serverid+'/action',
              'params': '{"migrate": null}',
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack migrate exception:')
      for i in e:
        self.logit(i)

  def server_lock(self,serverid):
    try:
      cmds = {'url':  '/servers/'+serverid+'/action',
              'params': '{"lock": null}',
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack lock exception:')
      for i in e:
        self.logit(i)

  def server_unlock(self,serverid):
    try:
      cmds = {'url':  '/servers/'+serverid+'/action',
              'params': '{"unlock": null}',
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack unlock exception:')
      for i in e:
        self.logit(i)

  def server_backup(self,serverid):
    try:
      cmds = {'url':  '/servers/'+serverid+'/action',
              'params': '"createBackup": {"name": "Backup 1","backup_type": "daily","rotation": 1}',
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack backup exception:')
      for i in e:
        self.logit(i)

  def server_livemigration(self,serverid,targethost=None,block_migration=config.os_block_migration,disk_over_commit=config.os_disk_over_commit):
    try:
      cmds = {'url':  '/servers/'+serverid+'/action',
              'params': '{"os-migrateLive": {"host": "'+targethost
              +'","block_migration": "'+block_migration
              +'","disk_over_commit": "'+disk_over_commit+'"}}',
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack livemigration exception:')
      for i in e:
        self.logit(i)

  def server_resetstate(self,serverid):
    try:
      cmds = {'url':  '/servers/'+serverid+'/action',
              'params': '{"os-resetState": {"state": "active"}}',
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack resetstate exception:')
      for i in e:
        self.logit(i)

  def server_evacuate(self,serverid,targethostuuid=None,adminPass=config.ospass,shared_storage=config.os_shared_storage):
    """
    Evacuates a server from failed host.
    """
    try:
      cmds = {'url':  '/servers/'+serverid+'/action',
              'params': '{"evacuate": {"host": "'+targethostuuid
              +'","adminPass": "'+adminPass
              +'","onSharedStorage": "'+shared_storage+'"}}',
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack resume exception:')
      for i in e:
        self.logit(i)

  def server_stop(self,serverid):
    try:
      cmds = {'url':  '/servers/'+serverid+'/action',
              'params': '{"os-stop": null}',
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack stop exception:')
      for i in e:
        self.logit(i)

  def server_start(self,serverid):
    try:
      cmds = {'url':  '/servers/'+serverid+'/action',
              'params': '{"os-start": null}',
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack stop exception:')
      for i in e:
        self.logit(i)

  def server_boot(self,
                  servername,
                  flavorRef=config.defaultFlavor,
                  imageRef=config.defaultImage,
                  secgroup=config.defaultSecGroup,
                  user_data=base64.b64encode(b'echo this is a test'),
                  key_name=config.defaultSSHKey):
    try:
      flavor=self.novahost+"/v2/"+self.tenantid+"/flavors/"+ flavorRef
      image=self.novahost+"/v2/"+self.tenantid+"/images/"+ imageRef
      cmds = {'url':  '/servers',
              'params': '{\
                "server": {\
                  "flavorRef": "'+flavor+'",\
                  "personality": [{\
                    "path": "",\
                    "contents": ""\
                  }],\
                  "name": "'+servername+'",\
                  "imageRef": "'+image+'",\
                  "metadata": {\
                    "Server Name": "'+servername+'"\
                  },\
                  "security_group": "'+secgroup+'",\
                  "key_name": "'+key_name+'",\
                  "user_data": "'+user_data+'"\
                }\
              }'
      }
      return self._post(cmds['url'],cmds['params'])
    except Exception as e:
      self.logit('openstack server_boot exception:')
      for i in e:
        self.logit(i)

  def server_terminate(self,serverid):
    try:
      cmds = {
        'url':  '/servers/'+serverid,
        'method': 'DELETE',
        'params': 'null'
      }
      return self._post(cmds['url'],cmds['params'],method=cmds['method'])
    except Exception as e:
      self.logit('openstack esrver_terminate exception:')
      for i in e:
        self.logit(i)

  def server_floatip(self,action,serverid):
    if action == "ADD":
      try:
        cmds = {
                  'url':  '/os-floating-ips',
                  'params': '{"pool": "nova"}',
        }
        # get an floating ip from the pool
        ips = self._post(cmds['url'],cmds['parms'])
        floatip=ips['floating_ip']['ip']
        cmds = {
                'url':  '/servers/'+serverid+'/action',
                'params': '{"addFloatingIp": {"address": "'+floatip+'"}}',
        }
        # assign the floating ip to the vm
        self._post(cmds['url'],cmds['params'])
        return floatip
      except Exception as e:
        self.logit('openstack floatip exception:')
        for i in e:
          self.logit(i)
    elif action == "DEL":
      try:
        cmds = {
                  'url':  '/servers/'+serverid+'/action',
                  'params': '{"removeFloatingIp": {"address": "'+floatip+'"}}',
        }
        return self._post(cmds['url'],cmds['params'])
      except Exception as e:
        self.logit('openstack floatip exception:')
        for i in e:
          self.logit(i)
