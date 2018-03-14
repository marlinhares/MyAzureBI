import utils
import json
import os
from datetime import date


def getFlavour(region):
    a = os.popen('az vm list-sizes -l ' + region).read()
    return json.loads(a)


def getListSizes():
    r = getFlavour('BRAZILSOUTH') + getFlavour('EASTUS') + getFlavour('WESTUS')

    return r


def getDisks(subscription, fdate):
    a = os.popen('az disk list').read()
    disks = json.loads(a)

    for disk in disks:
        disk['subscription'] = subscription
        disk['date'] = fdate

    return disks


def getStorageAccs(subscription, fdate):
    a = os.popen('az storage account list').read()
    storageaccounts = json.loads(a)

    for sa in storageaccounts:
        sa['subscription'] = subscription
        sa['date'] = fdate

        containers = getContainers(sa['name'])
        sa['containers'] = containers

        shares = getFileShares(sa['name'])
        sa['diskshares'] = shares

    return storageaccounts


def getContainers(sa):
    a = os.popen('az storage container list --account-name="' + sa + '"').read()
    containers = json.loads(a)

    for container in containers:
        blobs = getBlobs(sa, container['name'])
        container['blobs'] = blobs

    return containers


def getBlobs(sa, container):
    a = os.popen('az storage blob list --container-name="' + container + '" --account-name="' + sa + '"').read()
    blobs = json.loads(a)

    return blobs


def getFileShares(sa):
    a = os.popen('az storage share list --account-name="' + sa + '"').read()
    try:
        shares = json.loads(a)
    except ValueError, e:
        shares = []

    return shares



def getVms(subscription, fdate):
    a = os.popen('az vm list').read()
    vms = json.loads(a)

    for vm in vms:
        vm['date'] = fdate
        vm['flavour'] = utils.retFirstVal(listsizes, 'name', vm['hardwareProfile']['vmSize'])
        vm['subscription'] = subscription

    return vms



# busca data atual
fdate = date.today()
fdate = "2018-03-12"

# get accounts json
#a = os.popen('az account list --query "[?name==\'17-0134-B-GM-ASCOM-PORTAL-PLANEJAMENTO-MP-PRD\'].{id:id, name:name, state:state, tenantid:tenantid}"').read()
a = os.popen('az account list --query "[].{id:id, name:name, state:state, tenantid:tenantid}"').read()
subscriptions = json.loads(a)


# list with all flavours
listsizes = getListSizes()

colDisks = []
colSas = []
colVms = []

for s in subscriptions:

    a = os.popen('az account set -s ' + s['id']).read()

    print "Subscricao: " + s['name']

    print "Discos"
    disks = getDisks(s['name'], fdate)
    print "Storage Accounts"
    storageaccounts = getStorageAccs(s['name'], fdate)
    print "Vms"
    vms = getVms(s['name'], fdate)

    s['vms'] = vms
    s['date'] = fdate

    colDisks.extend(disks)
    colSas.extend(storageaccounts)
    colVms.extend(vms)

    with open('subs.json', 'w') as outfile:
        json.dump(subscriptions, outfile)

    with open('disks.json', 'w') as outfile:
        json.dump(colDisks, outfile)

    with open('sas.json', 'w') as outfile:
        json.dump(colSas, outfile)

    with open('vms.json', 'w') as outfile:
        json.dump(colVms, outfile)
