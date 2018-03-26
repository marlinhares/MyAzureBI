import utils
import json
import os
from datetime import date
import threading


def getCmdResultJson(cmd):
    a = os.popen(cmd).read()
    try:
        r = json.loads(a)
    except ValueError:
        print "\n\n\n\n\nErro: ", cmd
        r = []
    except UnicodeEncodeError:
        r = []
        print "\n\n\n\nErro: ", cmd
    return r


def getFlavour(region):
    return getCmdResultJson('az vm list-sizes -l ' + region)


def getListSizes():
    r = getFlavour('BRAZILSOUTH') + getFlavour('EASTUS') + getFlavour('WESTUS')

    return r


def getDisks(subscription, fdate):
    disks = getCmdResultJson('az disk list')

    for disk in disks:
        disk['subscription'] = subscription
        disk['date'] = fdate

    return disks


def getStorageAccs(subscription, fdate):

    storageaccounts = getCmdResultJson('az storage account list')

    for sa in storageaccounts:
        sa['subscription'] = subscription
        sa['date'] = fdate

        containers = getContainers(sa['name'])
        sa['containers'] = containers

        shares = getFileShares(sa['name'])
        sa['diskshares'] = shares

    return storageaccounts


def getContainers(sa):

    containers = getCmdResultJson('az storage container list --account-name="' + sa + '"')

    for container in containers:
        if(container['name'].find('crashdump')>-1 or container['name'].find('.xml')>-1 or container['name'].find('.gz')>-1 or container['name'].find('heartbeat')>-1 or container['name'].find('RomeAsm')>-1 or container['name'].find('romedetect')>-1 or container['name'].find('romeasm')>-1 or container['name'].find('mam')==0 or container['name'].find('bootdiagnostic')>-1): continue
        print "SA / Cont", sa, container['name']
        blobs = getBlobs(sa, container['name'])
        container['blobs'] = blobs

    return containers


def getBlobs(sa, container):

    lblobs = getCmdResultJson('az storage blob list --query "[].{name:name,size:properties.contentLength}" --container-name="' + container + '" --account-name="' + sa + '"')

    blobs = []
    threads = []
    
    i = 0
    j = 0
    for blob in lblobs:
        j = j + 1

        if(int(blob['size']) < 1073741824): continue
        print "calculando blob", blob['name']
        #rblob = [getCmdResultJson('az storage blob show --container-name="' + container + '" --account-name="' + sa + '" ' + ' --name="' + blob['name'] + '"')]
        t = threading.Thread(target=getBlobShow, args=(sa, container, blob['name'], blobs, ))
        threads.append(t)
        t.start()

        i = i + 1

        if(i > 10):
            t.join()
            threads = []
            i = 0
        
        if(j == len(lblobs)):
            t.join()

        #blobs.extend(rblob)
        #print sa + ' - ' + container
        #print blob['name']

    return blobs


def getBlobShow(sa, container, bname, blobs):

    #print "chamando blob show " + bname
    r = [getCmdResultJson('az storage blob show --container-name="' + container + '" --account-name="' + sa + '" ' + ' --name="' + bname + '"')]
    blobs.extend(r)
    
    return


def getFileShares(sa):

    shares = getCmdResultJson('az storage share list --account-name="' + sa + '"')

    return shares



def getVms(subscription, fdate):

    vms = getCmdResultJson('az vm list')

    for vm in vms:
        vm['date'] = fdate
        vm['flavour'] = utils.retFirstVal(listsizes, 'name', vm['hardwareProfile']['vmSize'])
        vm['subscription'] = subscription

    return vms



# busca data atual
fdate = date.today()
fdate = "2018-03-22"

# get accounts json
#getCmdResultJson('az account list --query "[?name==\'16-0028-A-SERVICOS_SUSTENTACAO-PRD\'].{id:id, name:name, state:state, tenantid:tenantid}"')
subscriptions = getCmdResultJson('az account list --query "[].{id:id, name:name, state:state, tenantid:tenantid}"')


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
