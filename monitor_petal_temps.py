import pandas as pd 
import numpy as np 
import datetime
import glob
import matplotlib.pyplot as plt 
from numpy import nan

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 12

date_today = input("What date information do you want? (YYYYMMDD): ")

files = glob.glob('/home/msdos/fp_tools/fptools/%s_temp_log_PC_*.txt' % date_today)

cc = ['PBOX_TEMP_SENSOR', 'FPP_TEMP_SENSOR_1', 'FPP_TEMP_SENSOR_2', 'FPP_TEMP_SENSOR_3', 'GXB_MONITOR', 'ADC0', 'ADC1', 'ADC2', 'ADC3', 'ADC4', 'ADC5','MEAN_POS', 'MEAN_FID', 'DATE']

Petal_to_PC = {0:4, 1:5, 2:6, 3:3, 4:8, 5:10, 6:11, 7:2, 8:7, 9:9}

