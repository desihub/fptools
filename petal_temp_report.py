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

date_today = input("What date information do you want? (YYYYMMDD): ")



cc = ['FPP_TEMP_SENSOR_3', 'FPP_TEMP_SENSOR_2', 'PBOX_TEMP_SENSOR', 'GXB_MONITOR', 'FPP_TEMP_SENSOR_1', 'ADC0', 'ADC2','ADC4', 'ADC3', 'ADC1','MEAN_POS','MEAN_FID','DATE']

Petal_to_PC = {0:4, 1:5, 2:6, 3:3, 4:8, 5:10, 6:11, 7:2, 8:7, 9:9}
petal_degs = {3:0,2:36,1:36*2,0:36*3,9:36*4,8:36*5,7:36*6,6:36*7,5:36*8,4:36*9}

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



PosTemps0, df0 = get_data(0)
PosTemps1, df1 = get_data(1)
PosTemps2, df2 = get_data(2)
PosTemps3, df3 = get_data(3)
PosTemps4, df4 = get_data(4)
PosTemps5, df5 = get_data(5)
PosTemps6, df6 = get_data(6)
PosTemps7, df7 = get_data(7)
PosTemps8, df8 = get_data(8)
PosTemps9, df9 = get_data(9)

data_list = [ df0,df1, df2, df3, df4, df5, df6, df7, df8, df9]


#PLOT 1
colors = iter(tab_colors.values())
plt.figure(figsize=(10,6))
for i, data in enumerate(data_list):
    plt.plot(data['DATE'], data['MEAN_POS'], 'o',label = i)
    plt.plot(data['DATE'], data['MEAN_FID'], 'x')
plt.legend(bbox_to_anchor=(1.1,1), loc='upper right', ncol=1)
plt.ylabel('Temp. (C)')
plt.title("Mean Positioner (o) and Fiducial (x) Temperatures for each Petal")
plt.ylim(0,40)

#PLOT 2
comps = ['PBOX_TEMP_SENSOR', 'FPP_TEMP_SENSOR_1','FPP_TEMP_SENSOR_2', 'FPP_TEMP_SENSOR_3', 'GXB_MONITOR']
fig, axarr = plt.subplots(len(comps),1, figsize = (12, 24))
for x, comp in enumerate(comps):
    colors = iter(tab_colors.values())
    for i, data in enumerate(data_list):
        axarr[x].plot(data['DATE'], data[comp], label = i)
    axarr[x].legend(bbox_to_anchor=(1.3,1), loc='upper right', ncol=1)
    axarr[x].set_ylabel('Temp (C)')
    axarr[x].set_title(comp+': %s' % date_today)

pos_temp_list = [PosTemps0, PosTemps1, PosTemps2, PosTemps3, PosTemps4, PosTemps5, PosTemps6, PosTemps7, PosTemps8] #, PosTemps9
#PLOT 3

plt.figure(figsize=(12,10))
all_all = []
for pc, petal_data in enumerate(pos_temp_list):
    petal = Petal_to_PC[pc]
    hole_coords = np.genfromtxt('hole_coords.csv', delimiter = ',', usecols = (3,4), skip_header = 40)
    df = pd.read_csv('desi_positioner_indexes.csv')
    pdf=df.loc[df['PETAL_ID'] == int(petal)]
    dev_list=pdf['CAN_ID'].tolist()
    hole_list=pdf['DEVICE_LOC'].tolist()
    dev_id_loc=dict(zip(dev_list,hole_list))
    
    #Get rid of data with no temps

    dates = [d for d in petal_data.keys()]
    my_dates_ix = np.flipud(np.argsort(dates))
    
    my_data = None
    for date_ix in my_dates_ix:
        date = dates[date_ix]
        data = petal_data[date]
        
        for can, temp_dict in data.items():
            if len(temp_dict) < 10:
                pass
            else:
                my_date = date
                my_data = data

        if my_data == None:
            pass
        else:
            break
    ids = []
    all_temps = []
    x = []
    y = []
    for can, data in my_data.items():
        for i, temp in data.items():
            if i in bad_temp_sensors:
                pass
            elif i > 10000:
                pass
            elif temp > 1000:
                pass
            else:
                try:
                    ids.append(i)
                    hole = dev_id_loc[float(i)]
                    x.append(hole_coords[int(hole)][0])
                    y.append(hole_coords[int(hole)][1])
                    all_temps.append(temp)
                    if temp > 40:
                        print(i, temp)
                except:
                    print(i)
    x = np.array(x)
    y = np.array(y)
    all_all.append(all_temps)
    new_x = []
    new_y = []
    deg = petal_degs[pc]
    radians = np.deg2rad(deg)
    c, s = np.cos(radians), np.sin(radians)
    j = np.matrix([[c, s], [-s, c]])
    for i, xx in enumerate(x):
        yy = y[i]
 
        m = np.dot(j, [xx, yy])
        new_x.append(float(m.T[0]))
        new_y.append(float(m.T[1]))
    #print(new_x)

    df = pd.DataFrame(list(zip(ids, all_temps, new_x, new_y)), columns = ['ID', 'Temp','X','Y'])

    plt.scatter(df['X'], df['Y'], c=df['Temp'],s=100)
    l_xy = np.dot(j, [410, 125])
    plt.text(l_xy.T[0], l_xy.T[1], pc, fontsize=20, color = 'red')
plt.colorbar()
plt.title("POS Temp Map: %s" % (my_date))

all_all = np.hstack(all_all)

#PLOT 5
plt.figure(figsize=(8,6))
ret = plt.hist(all_all, bins = 100)
plt.title('All Pos temps %s' % date_today)

plt.show()

