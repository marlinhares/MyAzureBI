import threading, time


def worker(num, num2, num3):
    """thread worker function"""
    print 'Worker: %s' % num2
    time.sleep(num)
    return


threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(i, i+1, i+2,))
    threads.append(t)
    t.start()

print "esperando..."
t.join()

t.join()
print "terminei"
