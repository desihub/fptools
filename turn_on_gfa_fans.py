import sys
sys.path.append('/home/msdos/focalplane/plate_control/trunk/petal')
import datetime
import numpy as np
import petalcomm
import petal


start_time = datetime.datetime.now()
print(start_time)
Comms = []
for pc in [0,1,2,3,4,5,6,7,8,9]:
    try:
        Comms.append(petalcomm.PetalComm(pc))
    except:
    	print("Can't connect with PC%d" % pc)

for i, comm in enumerate(Comms):
    comm.pbset('GFA_FAN', {'inlet':['on', 15],'outlet':['on',15]})
    print("GFA Fans turned on for PC%d"%i)


print("All GFA Fans should be turned ON now: ", datetime.datetime.now())

print("Now double checking the GFA Fans are turned ON at 15%")

for i, comm in enumerate(Comms):
    print("Petal Location %d" % i)
    print(comm.pbget('GFA_FAN'))

