import threading
import os
import json
import time



def getCmdResultJson(cmd):
    a = os.popen(cmd).read()
    
    try:
        r = json.loads(a)
    except ValueError:
        r = []
    except UnicodeEncodeError:
        r = []
    return r


def getStorageAccs(subscription, fdate):

    storageaccounts = getCmdResultJson('az storage account list ')

    for sa in storageaccounts:
        sa['subscription'] = subscription
        sa['date'] = fdate

        containers = getContainers(sa['name'])
        sa['containers'] = containers


    return storageaccounts


def getContainers(sa):

    containers = getCmdResultJson('az storage container list --account-name="' + sa + '" ')


    for container in containers:
        blobs = getBlobs(sa, container['name'])
        container['blobs'] = blobs



    return containers


def getBlobs(sa, container):

    lblobs = getCmdResultJson('az storage blob list --query "[].{name:name}" --container-name="' + container + '" --account-name="' + sa + '"')

    print sa + ' - ' + container

    blobs = []
    threads = []
    for blob in lblobs:

        if(blob['name'].find('d=201') > -1): continue

        #rblob = [getCmdResultJson('az storage blob show --container-name="' + container + '" --account-name="' + sa + '" ' + ' --name="' + blob['name'] + '"')]
        #blobs.extend(rblob)        
        print "adicionando blob a thread " + blob['name']        
        t = threading.Thread(target=getBlobShow, args=(sa, container, blob['name'], blobs, ))

        threads.append(t)
        t.start()

    
    if(len(threads)):
        print 'Vou iniciar os blobs em thread'
        #t.start()
        print "esperando"

        t.join()

        print "retornando"
    
    print "Blobs ", len(blobs)
    print blobs
    return blobs


def getBlobShow(sa, container, bname, blobs):
    sema.acquire()
    print "chamando blob show " + bname
    r = [getCmdResultJson('az storage blob show --container-name="' + container + '" --account-name="' + sa + '" ' + ' --name="' + bname + '"')]
    time.sleep(1)
    blobs.extend(r)
    sema.release()


    return


sema = threading.Semaphore(value=50)

getStorageAccs('subs1', '2018-03-19')
