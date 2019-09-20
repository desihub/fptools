import pandas as pd 
import numpy as np 
import datetime
import glob
import matplotlib.pyplot as plt 
from numpy import nan
import matplotlib.colors as mcolors

tab_colors = mcolors.TABLEAU_COLORS

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 12

date_today = '20190920' #input("What date information do you want? (YYYYMMDD): ")


cc = ['PBOX_TEMP_SENSOR', 'FPP_TEMP_SENSOR_1', 'FPP_TEMP_SENSOR_2', 'FPP_TEMP_SENSOR_3', 'GXB_MONITOR', 'ADC0', 'ADC1', 'ADC2', 'ADC3', 'ADC4', 'MEAN_POS', 'MEAN_FID', 'DATE']

Petal_to_PC = {0:4, 1:5, 2:6, 3:3, 4:8, 5:10, 6:11, 7:2, 8:7, 9:9}

bad_temp_sensors = [1636, 5856, 5658, 660, 5115]

def get_data(PC):
	PosTemp = {}
	D = pd.DataFrame(columns=cc)

	filen = '/home/msdos/fp_tools/fptools/%s_temp_log_PC_%d.txt' % (date_today, PC)

	file = open(filen, 'r')
	for line in file:

		a = eval(line)[0]
		new_d = []
		for date, v in a.items():
			pos_temps, petal_temps, adcs, mean_vals = v
			PosTemp[date] = pos_temps
			for c in cc:
				if c in petal_temps.keys():
					new_d.append(petal_temps[c])
				elif c in adcs.keys():
					new_d.append(adcs[c])
				elif c in mean_vals.keys():
					new_d.append(mean_vals[c])
				elif c == 'DATE':
					new_d.append(date)
				else:
					new_d.append(np.nan)
					print("Couldn't find this key %s" % c)
		df = pd.DataFrame([new_d], columns=cc)
		D = D.append(df)

	return PosTemp, D


def get_latest_data(posdata):
	dates = [d for d in posdata.keys()]
	my_dates_ix = np.flipud(np.argsort(dates))
	my_data = None
	for date_ix in my_dates_ix:
		date = dates[date_ix]
		data = posdata[date]

		for can, temp_dict in data.items():
			if len(temp_dict) == 0:
				pass
			else:
				my_date = date
				my_data = data 
		if my_data == None:
			pass
		else:
			break
	print(my_data)

	return my_date, my_data

def PosHist(PosTemps):
	plt.figure()
	ALL = []
	for i, posdata in enumerate(PosTemps):
		this_date, this_data = get_latest_data(posdata)

		ids = []
		all_temps = []
		x = []
		y = []
		for can, data in this_data.items():
			for ix, temp in data.items():
				if ix in bad_temp_sensors:
					pass
				elif ix >10000:
					pass
				else:
					try:
						ids.append(ix)
						hole = dev_id_loc[float(i)]
						x.append(hole_coords[int(hole)][0])
						y.append(hole_coords[int(hole)][1])
						all_temps.append(temp)
						if temp > 40:
							print(ix, temp)
					except:
						print("Didn't find hole info: ", ix)
		print(all_temps)
		x = np.array(x)
		y = np.array(y)
		ALL.append(all_temps)

	plt.hist(np.hstack(ALL), bins = 100)
	plt.title("Pos Temp Histogram (no fiducials)")




#PosHist(PosTemps)

PosTemps = []
PetalTemps = []
for i in [0,1,2,3,4,5,6,7,8,9]:
	PosTemp, PetalTemp = get_data(i)
	PosTemps.append(PosTemp)
	PetalTemps.append(PetalTemp)
colors = iter(tab_colors.values())

plt.figure(figsize=(12,8))
for i, data in enumerate(PetalTemps):

	color = next(colors)
	plt.plot(data['DATE'], data['MEAN_POS'], 'x', color = color, label = i)
	plt.plot(data['DATE'], data['MEAN_FID'], '.', color = color)
	plt.title("Mean Positioner and Fiducials Temp. %s" % date_today)
	plt.ylim(0,40)
	plt.legend()

fig, (ax1, ax2, ax3) = plt.subplots(3, 1,figsize=(12,20))
colors = iter(tab_colors.values())
for i, data in enumerate(PetalTemps):
	color = next(colors)
	ax1.plot(data['DATE'], data['PBOX_TEMP_SENSOR'], color = color, label = i)
	ax1.set_title("PBOX Temp. %s" % date_today)
	ax1.legend()
	ax2.plot(data['DATE'], data['FPP_TEMP_SENSOR_1'], color = color)
	ax2.set_title("FPP Sensor 1 Temp. %s" % date_today)
	ax3.plot(data['DATE'], data['GXB_MONITOR'], color = color)
	ax3.set_title("GXB Temp. %s" % date_today)

PosHist(PosTemps)
plt.show()


