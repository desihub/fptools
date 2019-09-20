
import sys
sys.path.append('/home/msdos/focalplane/plate_control/trunk/petal')
import datetime
import numpy as np
import petalcomm
import petal
import time


Petal_to_PC = {0:4, 1:5, 2:6, 3:3, 4:8, 5:10, 6:11, 7:2, 8:7, 9:9, 18:0}
start_time = datetime.datetime.now()
print(start_time)
Comms = []
for pc in [0,1,2,3,4,5,6,7,8,9]:
    petal = Petal_to_PC[pc]
    try:
        Comms.append(petalcomm.PetalComm(pc))
    except:
        print("Can't connect to PC%d" % i)
for i, comm in enumerate(Comms):
    try:
        comm.pbset('PS1_EN', 'on')
        comm.pbset('PS2_EN', 'on')
        print("The Petal in location %d is turned ON" % i)
    except:
        print("Some issue with PC%d" % i)

print("All Petals should be turned on now: ", datetime.datetime.now())

time.sleep(2)
print("Now double checking")

for i, comm in enumerate(Comms):
    print("Petal Location %d" % i)
    print(comm.pbget('pospwr_fbk'))

