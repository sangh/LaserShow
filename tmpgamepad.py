import sys
import threading
import subprocess
import Queue
import re

def jp(q):
    while True:
        try:
            p = subprocess.Popen( [
                "/usr/bin/jstest",
                "--event",
                "/dev/input/by-id/usb-Logitech_Logitech_RumblePad_2_USB-joystick",
                ], shell=False, stdout=subprocess.PIPE )
            while True:
                q.put(p.stdout.readline(),False)
        except:
            print sys.exc_info()
            try:
                try:
                    while True:
                        q.get(False)
                except Queue.Empty:
                    pass
                p.terminate()
                p.kill()
            except:
                pass
jq = Queue.Queue(maxsize=100)
jt = threading.Thread(target=jp,args=(jq,))
kt = threading.Thread(target=lambda: raw_input())
jt.daemon = True
kt.daemon = True
jt.start()
kt.start()

try: # Clear the queue.
    while True: jq.get(True,.1)
except Queue.Empty:
    pass
# Lines from gamepad.
# Event: type 2, time 17339776, number 1, value 19255
r=re.compile("^Event: type ([0-9]), time ([0-9]+), number ([0-9]?[0-9]), value (-?[0-9]+)$")
# Until Enter is pressed.
while kt.isAlive():
    try:
        l = jq.get(True, .2)
        rm = r.match(l)
        if rm:
            t = int(rm.group(1))
            ti = int(rm.group(2))
            n = int(rm.group(3))
            v = int(rm.group(4))
            print l.strip()
            print "t=%d  time=%d  num=%d  val=%d"%(t,ti,n,v)
        else:
            print "No.::%s::"%(l)
            break
    except Queue.Empty:
        pass
