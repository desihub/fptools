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


while True:
	PosTemps = []
	PetalTemps = []
	for i in [0,1,2,3,4,5,6,7,8,9]:
		PosTemp, PetalTemp = get_data(i)
		PosTemps.append(PosTemp)
		PetalTemps.append(PetalTemp)

	colors = iter(tab_colors.values())

	fig, (ax1, ax2, ax3) = plt.subplots(3,1, figsize=(12,20))
	for i, data in enumerate(PetalTemps):

		color = next(colors)
		ax1.plot(data['DATE'], data['MEAN_POS'], 'x', color = color, label = i)
		ax1.plot(data['DATE'], data['MEAN_FID'], '.', color = color)
		ax1.set_title("Mean Positioner and Fiducials Temp. %s" % date_today)
		ax1.set_ylim(0,40)
		ax1.legend()

		ax2.plot(data['DATE'], data['PBOX_TEMP_SENSOR'], color = color, label = i)
		ax2.set_title("PBOX Temp. %s" % date_today)
		ax2.legend()
		ax3.plot(data['DATE'], data['GXB_MONITOR'], color = color)
		ax3.set_title("GXB Temp. %s" % date_today)

	plt.draw()
	plt.pause(30)



