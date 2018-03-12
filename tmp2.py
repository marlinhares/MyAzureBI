from multiprocessing import Pool
import threading
import os
import json
import time

'''
def f(x):
    return x*x

if __name__ == '__main__':
    p = Pool(5)
    print(p.map(f, [1, 2, 3]))
'''


def listdisk(subsc):
    print("disco")
    a = os.popen('az account list --query "[].{id:id, name:name, state:state, tenantid:tenantid}"').read()
    subscriptions = json.loads(a)
    
    for s in subscriptions:
        a = os.popen('az account set -s ' + s['id']).read()
        a = os.popen('az disk list').read()
        disks = json.loads(a)
        print ("Buscando disco da subsc: " + s["name"])
        for disk in disks:
            
            time.sleep(3)

        print("Terminei discos subs:" + s["name"])
        a = os.popen('az account get-access-token --query "[subscription]"').read()
        print(a + " --- " +  s["id"] + "\n\n")
    return


def listvm(subsc):
    print("vm")
    a = os.popen('az account list --query "[].{id:id, name:name, state:state, tenantid:tenantid}"').read()
    subscriptions = json.loads(a)
    
    for s in subscriptions:
        print("Buscando vms da subs:" + s["name"] )
        a = os.popen('az account set -s ' + s['id']).read()
        a = os.popen('az vm list').read()
        vms = json.loads(a)

        # adiciona subscription ao json de vms
        for vm in vms:
            print("Buscando vm " + vm["name"] + " da subsc: " + s["name"])
            
        print("Terminei vms subs:" + s["name"] + "\n\n")
        a = os.popen('az account get-access-token --query "[subscription]"').read()
        print(a + " --- " +  s["id"] + "\n\n")
    return


threads = []
t = threading.Thread(target=listdisk, args=("",))
threads.append(t)
t.start()

t = threading.Thread(target=listvm, args=("",))
threads.append(t)
t.start()
