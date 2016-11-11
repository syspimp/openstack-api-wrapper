import sys,os,time
import logging
import httplib
from pprint import pprint
import json
import re

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/../')
logging.getLogger('backup').addHandler(logging.NullHandler())
import config_openstack as config

class access():
  def __init__(self,device_type=None,hostname=None,username=None,password=None,sshkey=None,debug=config.debug):
    self.hostname=hostname
    self.username=username
    self.password=password
    self.debug=debug
    self.sshkey=sshkey
    self.timeout=5

  def debugit(self,msg,isobject=False):
    if self.debug is not False:
      if isobject:
        for attr in dir(msg):
          print "obj.%s = %s" % (attr, getattr(msg, attr)) 
      else:
        print msg

  def _soap_acccess(self,cmd):
    # soap request
    return

  def _ssh_access(self,cmds):
    import paramiko
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(
      paramiko.AutoAddPolicy())
    try:
      if self.sshkey is not None:
        client.connect(self.hostname,
          username=self.username,
          password=self.password,
          timeout=self.timeout,
          key_filename=self.sshkey,allow_agent=False)
      else:
        client.connect(self.hostname,
          username=self.username, 
          password=self.password,
          timeout=self.timeout,allow_agent=False)
      channel=client.invoke_shell()
    except Exception as e:
      for i in e:
        if i == "Bad authentication type":
          msg = "Username/Password wrong ..."
        else:
          msg = "Exception is: %s" % i
      return msg

    self.debugit("Connected!")
    alldata=""
    for cmd in  cmds:
      msg="Writing: "+cmd["write"]
      self.debugit(msg)
      #stdin, stdout, stderr = client.exec_command(cmd["write"].encode('ascii','ignore'))
      try:
        channel.send(cmd["write"].encode('ascii','ignore')+"\n")
        data=""
        time.sleep(1)
        while channel.recv_ready():
          data+=self.hostname+": "+channel.recv(1024)
          alldata+=data
        self.debugit("device returned after write: "+data)
        try:
          if cmd["read"]:
            msg="Reading: " +cmd["read"]
            self.debugit(msg)
            regex= r"(.*)%s(.*)" % cmd["read"]
            if re.search(regex, data):
              msg="matched "+cmd["read"]+",breaking"
              self.debugit(msg)
              self.debugit("Continuing...")
              alldata=alldata+ "\nContinuing..."
              continue
        except Exception,e:
          for i in e:
            self.debugit("ssh read exception: " + i)
          pass
        try:
          if cmd["wait"]:
            msg="Waiting for %d seconds..." % cmd["wait"]
            self.debugit(msg)
            stop=time.time() + cmd["wait"]
            while stop >= time.time():
              time.sleep(1)
              data=""
              while channel.recv_ready():
                data+=self.hostname+": "+channel.recv(1024)
                alldata+=data
                self.debugit(data)
              try:
                if 'read' in cmd:
                  regex= r"(.*)%s(.*)" % cmd["read"]
                  if re.search(regex, data):
                    msg="Matched "+cmd["read"]+ " in " +data
                    self.debugit(msg)
                    self.debugit("Continuing...")
                    alldata=alldata+ "\nContinuing..."
                    stop = 0
                    continue
              except Exception,e:
                for i in e:
                  self.debugit("ssh regex exception: " + i)
                pass
        except Exception,e:
          for i in e:
            self.debugit("ssh wait exception: " + i)
          pass
      except Exception,e:
        for i in e:
          self.debugit("ssh exception: " + i)
        pass
    try:
      #stdin.close()
      client.close()
      return data
    except Exception,e:
      pass

  def _telnet_access(self,cmds):
    import telnetlib
    telnet_timeout = self.timeout
    try:
      device = telnetlib.Telnet(self.hostname)
      self.debugit(device.read_until("User", telnet_timeout))
      self.debugit("read success")
      device.write(self.username + "\r")
      self.debugit(device.read_until("Pass", telnet_timeout))
      device.write(self.password + "\r")
      self.debugit(device.read_until(self.terminalprompt, telnet_timeout))
      for cmd in cmds:
        device.write(cmd["write"].encode('ascii','ignore') +"\r")
        try:
          if cmd["read"]:
            self.debugit(device.read_until(cmd["read"],telnet_timeout))
        except:
          self.debugit(device.read_until(self.terminalprompt,telnet_timeout))
          pass
      device.write(self.logout+"\r")
      self.debugit("Completed Sucessfully")
    except Exception as e:
      for i in e:
        self.debugit("Exception is: %s" % i)

  def _json_access(self,cmds):
    self.debugit("trying json access for")
    self.debugit(cmds)
    try:
      conn = httplib.HTTPConnection(cmds['host'])
      conn.request(cmds['method'], cmds['url'], cmds['params'], cmds['headers'])
      response = conn.getresponse()
      data = response.read()
      if data:
        self.debugit("dumping server response")
        self.debugit(response,isobject=True)
        dd = json.loads(data)
        self.debugit("dumping json data")
        self.debugit(dd)
        conn.close()
        return dd
      else:
        self.debugit("no data returned")
    except Exception, e:
      self.debugit("access: cant do json")
      for i in e:
        self.debugit(i)

