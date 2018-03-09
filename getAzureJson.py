import json
import os
from elasticsearch import Elasticsearch
from datetime import date


# Return {} or the first json object of a certain key/value
# j is an array of json
# key is the key you want filter
# value is the value
def retFirstVal(j, key, value):
    r = [x for x in j if x[key] == value]
    r = r[0] if len(r) else {}
    return r


# busca data atual
d = date.today()
d = "2018-03-09"

# json com os Accounts
#a = os.popen('az account list --query "[?name==\'17-0134-B-GM-ASCOM-PORTAL-PLANEJAMENTO-MP-PRD\'].{id:id, name:name, state:state, tenantid:tenantid}"').read()
a = os.popen('az account list --query "[].{id:id, name:name, state:state, tenantid:tenantid}"').read()
subscriptions = json.loads(a)

# json com os hardwareProfiles (flavours)
a = os.popen('az vm list-sizes -l BRAZILSOUTH').read()
listsizes = json.loads(a)

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

for s in subscriptions:
    s['date'] = d
    a = os.popen('az account set -s ' + s['id']).read()

    # disks
    a = os.popen('az disk list').read()
    disks = json.loads(a)

    for disk in disks:
    	print "Buscando disco " + disk['name'] + " da subsc: " + s['name']
        # disk['subscription'] = s
        disk['date'] = d

        # es.index(index='disk', doc_type='disks', body=disk)

    # storage
    
    a = os.popen('az storage account list').read()
    storageaccounts = json.loads(a)

    for sa in storageaccounts:
        # sa['subscription'] = s
        sa['date'] = d

        # container
        a = os.popen('az storage container list --account-name="' + sa['name'] + '"').read()
        containers = json.loads(a)

        for container in containers:
            print "Buscando blobs do container: " + container['name']

            a = os.popen('az storage blob list --container-name="' + container['name'] + '" --account-name="' + sa['name'] + '"').read()
            blobs = json.loads(a)
            # associate blobs to containers
            container['blobs'] = blobs

            # todo files

        sa['containers'] = containers
        
        # storage files
        a = os.popen('az storage share list --account-name="' + sa['name'] + '"').read()
        try:
            shares = json.loads(a)
        except ValueError, e:
        	shares = []
        

        s['diskshares'] = shares

        # es.index(index='storageaccount', doc_type='sas', body=sa)
    
    
    # vms
    # a = os.popen('az vm list --query "[].{RG:resourceGroup,Name:name,HardProfile:hardwareProfile.vmSize,storageProfile:storageProfile}"').read()
    a = os.popen('az vm list').read()
    vms = json.loads(a)

    # adiciona subscription ao json de vms
    for vm in vms:
    	print "buscando vm " + vm['name']
        # vm['subscription'] = s
        vm['date'] = d
        print vm
        vm['flavour'] = retFirstVal(listsizes, 'name', vm['hardwareProfile']['vmSize'])

        es.index(index='vm', doc_type='vms', body=vm)

    # associate disks in subscription
    s['disks'] = disks
    # associate storageaccounts in subscription
    s['storageaccounts'] = storageaccounts
    # associate vms in subscription
    s['vms'] = vms

    # es.index(index='subscription', doc_type='subscri', body=s)
    with open('subs.json', 'w') as outfile:
        json.dump(subscriptions, outfile)

    print s


print "Json Novo:", vms
print "Jesus Cristo"
# /subscriptions/274f6e6b-ae08-4c4a-a521-406b1d2dde79/resourceGroups/16-0042-B-DTI-RANCHER-PRD/providers/Microsoft.Compute/virtualMachines/17-0042-B-DTI-RANCHER-PRD-VM-01
# https://160042bdtirancherprd284.blob.core.windows.net/vhds/17-0042-B-DTI-RANCHER-PRD-VM-0120170622200313.vhd
