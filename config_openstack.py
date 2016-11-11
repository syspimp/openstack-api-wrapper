## config file for openstack cli
import os, base64

## Set this to turn debugging on
## If openstack-cli.py isn't working, start here
debug=False

## ask for credentials on each use
## the --robot option always turns this off
confirmation=False

## Set to a Openstack controller and your password base64 encoded
## run at a shell to get the base64 of your password
## bash -c 'echo $PASSWORD | base64'
oshost = "10.2.3.456"
## we will try to pull these from the environment further down
username = 'my-horizon-username'
password = 'b3BlbnN0YWNrCg=='

## Set these to the tenantid's you want to give this cli access to
## Notice the naming convention, the tenant name is a prefix. No spaces for the name,  use underscores.
## I havent tested using spaces in the name
## admin tenant REQUIRED
admin_tenantid = "a0c308140ed6xxx"

## others
Masked_Admins_tenantid = "b771d19b71bf4a8ab767xxx"

## set this to the default tenant id and name
default_tenantid = Masked_Admins_tenantid
default_tenantname = 'Masked_Admins'

## this should match the names above
os_projects = ['Masked_Admins','admin']

## try to pull from the environment
## will work if you source the openrc or keystone file
osuser = os.getenv('OS_USERNAME', username)
ospass = os.getenv('OS_PASSWORD', base64.b64decode(password).strip())
tenantid = os.getenv('OS_TENANT_ID', default_tenantid)
tenantname = os.getenv('OS_TENANT_NAME', default_tenantname)

## m1.tiny
defaultFlavor = '1'

## ubuntu 12
defaultImage = '57cb666d-8507-4bef-ba2e-e0663d7fe73a'
defaultSecGroup = 'default'
defaultSSHKey = 'my-openstack-key'

## migration related
os_shared_storage="False"
os_disk_over_commit="False"
os_block_migration="True"
