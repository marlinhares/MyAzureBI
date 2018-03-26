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
        print "Erro: ", cmd
        r = []
    except UnicodeEncodeError:
        r = []
        print "Erro: ", cmd
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

    threads2 = []
    i = 0
    j = 0

    blobs_l = []

    for container in containers:

        j = j + 1

        if(container['name'].find('crashdump')>-1 or container['name'].find('.xml')>-1 or container['name'].find('.gz')>-1 or container['name'].find('RomeAsm')>-1 or container['name'].find('mam')==0 or container['name'].find('bootdiagnostic')>-1): continue

        print "SA / Cont", sa, container['name']

        t2 = threading.Thread(target=getBlobs, args=(sa, container['name'], blobs_l, ))
        threads2.append(t2)
        t2.start()

        i = i + 1

        if(i > 5):
            t2.join()
            threads2 = []
            i = 0

        if(j == len(containers)):
            t2.join()

        #blobs = getBlobs(sa, container['name'])
        container['blobs'] = blobs_l

    return containers


def getBlobs(sa, container, blobs_l):

    lblobs = getCmdResultJson('az storage blob list --query "[].{name:name,size:properties.contentLength}" --container-name="' + container + '" --account-name="' + sa + '"')
    
    ##threads = []
    
    i = 0
    j = 0
    for blob in lblobs:
        j = j + 1

        #if(blob['name'].find('d=201') > -1): continue
        if(int(blob['size']) < 1073741824): continue
        print "calculando blob", blob['name']
        #rblob = [getCmdResultJson('az storage blob show --container-name="' + container + '" --account-name="' + sa + '" ' + ' --name="' + blob['name'] + '"')]
        ##t = threading.Thread(target=getBlobShow, args=(sa, container, blob['name'], blobs, ))
        getBlobShow(sa, container, blob['name'], blobs_l)
        ##threads.append(t)
        ##t.start()

        i = i + 1

        if(i > 10):
            ##t.join()
            ##threads = []
            i = 0
        
        ##if(j == len(lblobs)):
            ##t.join()

        #blobs.extend(rblob)
        #print sa + ' - ' + container
        #print blob['name']

    return blobs_l


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
fdate = "2018-03-19"

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
