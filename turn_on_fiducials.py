import sys
sys.path.append('/home/msdos/focalplane/plate_control/trunk/petal')
import datetime
import numpy as np
import petalcomm
import petal
import time
import pandas as pd 

df = pd.read_csv('fiducial_levels.csv')

pcs = np.unique(df['PC'])
dd = []
for pc in pcs:
	dd.append(len(df[df['PC']==pc]))
print(np.sum(dd))

#Make dictionary
Levels = {}
for pc in pcs:
	data = df[df['PC'] == pc]
	Levels[pc] = {'can17': {}, 'can15': {}, 'can11': {}, 'can12': {}, 'can23': {}, 'can10': {}, 'can16': {}, 'can13': {}, 'can22': {}, 'can14': {}}

	for can in np.unique(data['BUS']):
		can_bus = 'can%s' % str(can)
		can_data = data[data['BUS']==can].to_records()

		a = {}
		for line in can_data:
			a[line['CAN']] = 0#line['DUTY']
		Levels[pc][can_bus] = a

start_time = datetime.datetime.now()
print(start_time)
Comms = []
pcs = [0,1,2,3,4,5,6,7,8,9]
for pc in pcs: #:
    try:
        Comms.append(petalcomm.PetalComm(pc))
    except:
        print("Can't connect to PC%d" % pc)

for i, comm in enumerate(Comms):
	pc = pcs[i]
	print(pc)
	fid_dict = Levels[pc]
	comm.pbset('fiducials',fid_dict)

print("All Fiducials should be turned ON now: ", datetime.datetime.now())

time.sleep(2)
print("Now double checking")

for i, comm in enumerate(Comms):
    print("Petal Location %d" % i)
    print(comm.pbget('fiducials'))


