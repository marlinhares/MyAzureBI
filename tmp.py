import threading
import json
import os
from datetime import date
import time



def listdisk(subsc):
    a = os.popen('az disk list').read()
    disks = json.loads(a)

    for disk in disks:
        print ("Buscando disco " + disk['name'] + " da subsc: " + subsc)
        time.sleep(20)

    print("Terminei disco subs:" + subsc + "\n\n\n\n")
    return


def listvm(subsc):
    a = os.popen('az vm list').read()
    vms = json.loads(a)

    # adiciona subscription ao json de vms
    for vm in vms:
        print("Buscando vm " + vm["name"] + " da subsc: " + subsc)

    return


'''
threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()
''' 

a = os.popen('az account list --query "[].{id:id, name:name, state:state, tenantid:tenantid}"').read()
subscriptions = json.loads(a)

for s in subscriptions:
    
    a = os.popen('az account set -s ' + s['id']).read()
    
    threads = []
    
    # thread1
    t = threading.Thread(target=listdisk, args=(s['name'],))
    threads.append(t)
    t.start()
    
    # thread2
    t = threading.Thread(target=listvm, args=(s['name'],))
    threads.append(t)
    t.start()