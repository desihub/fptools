import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
import sys,os
sys.path.append('/home/msdos/focalplane/plate_control/trunk/petal')
import petalcomm
import petal
import pandas as pd
import datetime
import time, datetime
import pickle
import csv
from scipy import interpolate
import json
import argparse
from matplotlib.figure import Figure
import tkinter as tk
import numpy as np

import petalcomm
import petal

import tkinter.filedialog
import tkinter.messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import pandas as pd
from threading import Thread

# nominal hole location data

class PetalTempApp():
    def __init__(self, pc, postemp_wait, fidtemp_wait):
        self.PC = pc
        self.postemp_wait = postemp_wait
        self.fidtemp_wait = fidtemp_wait
        self.start_time = datetime.datetime.now()
        self.file_path = '/home/msdos/focalplane/pos_utility/'
        self.temp_log_path = os.getcwd()#'/home/msdos/test_util/temp_logs/'
        self.pos_index_file = 'desi_positioner_indexes.csv'
        self.date_today = str(self.start_time.year)+str(self.start_time.month).zfill(2)+str(self.start_time.day)

        #Start PC
        Petal_to_PC = {0:4, 1:5, 2:6, 3:3, 4:8, 5:10, 6:11, 7:2, 8:7, 9:9, 18:0}
        self.temp_log_name = self.temp_log_path+'/%s_temp_log_PC_%s.txt' % (self.date_today, str(self.PC))
        self.petal = Petal_to_PC[self.PC]
        self.comm = petalcomm.PetalComm(self.PC)
        petal_label = print("Connected to PC%s on Petal %s" % (str(self.PC), str(self.petal)))

        df = pd.read_csv(self.pos_index_file)
        self.pdf=df.loc[df['PETAL_ID'] == int(self.petal)]


        self.hole_coords = np.genfromtxt(self.file_path+'hole_coords.csv', delimiter = ',', usecols = (3,4), skip_header = 40)
        self.nons = [38, 331, 438, 460, 478, 479, 480, 481, 497, 498, 499, 500, 513, 514, 515, 516, 527, 528, 529, 530, 531, 535, 536, 537, 538, 539, 540]
        self.gifs = [541, 542]
        self.fifs = [11, 75, 150, 239, 321, 439, 482, 496, 517, 534]


        self.mt = []
        self.mean_temps = []
        self.mean_fids = []
        self.can_buses= {'can10','can11','can12','can13','can14','can15','can16','can17','can22','can23'}
        self.pb_temps = {'PBOX_TEMP_SENSOR':[], 'FPP_TEMP_SENSOR_1': [], 'FPP_TEMP_SENSOR_2': [], 'FPP_TEMP_SENSOR_3': [], 'GXB_TEMP_SENSOR': []}
        self.adc_values = {'ADC2': [], 'ADC3': [], 'ADC1': [], 'ADC4': [], 'ADC0': []}


    def get_temps(self, temp_mode):
        self.current_time = datetime.datetime.now()
        print("Taking Temp Data: ", self.current_time)
        self.mt.append(self.current_time)
        
        if temp_mode == 'pos':
            print("Measuring positioner and fiducials temperatures")
            current_pos_dict = self.comm.pbget('posfid_temps')
        elif temp_mode == 'fid':
            print("Measuring ONLY fiducials temperatures")
            current_pos_dict = self.comm.pbget('fid_temps')
        else: 
            current_pos_dict = self.comm.pbget('fid_temps')

        #Check if power is on
        total = 0 
        for can in self.can_buses:
            num = len(current_pos_dict[can])
            total += num
        if total == 0:
            print("Power not on")
            self.power_off = True
        else:
            self.power_off = False

        pb_dict = self.comm.pbget('pb_temps')
        adc_dict = self.comm.pbget('adcs')
        if self.power_off == True:
            self.mean_temp = np.nan
            self.mean_fid = np.nan
        else:
            self.all_temps = []
            self.all_fids = []
            self.ids = []
            for can, val in current_pos_dict.items():
                for i, t in val.items():
                    if t > 1000:
                        pass
                    else:
                        if i > 10000:
                            self.all_fids.append(t)
                        else:
                            self.all_temps.append(t)
                        self.ids.append(i)
            self.mean_temp = np.mean(self.all_temps)
            self.mean_fid = np.mean(self.all_fids)
        self.mean_temps.append(self.mean_temp)
        self.mean_fids.append(self.mean_fid)


        for i in self.pb_temps.keys():
            try:
                self.pb_temps[i].append(pb_dict[i])
            except:
                self.pb_temps[i].append(np.nan)

        for i in self.adc_values.keys():
            try:
                self.adc_values[i].append(adc_dict[i])
            except:
                self.adc_values[i].append(np.nan)

        D = {self.current_time: [current_pos_dict, pb_dict, adc_dict, {'MEAN_POS': self.mean_temp, 'MEAN_FID': self.mean_fid}]}
        print(D)
        #Start Temperature log
        self.temp_log = open(self.temp_log_name,'a+')

        self.temp_log.write(str(D))
        self.temp_log.write(', \n')
        self.temp_log.close()

    def run(self):
        if self.postemp_wait < self.fidtemp_wait:
            print("You want to take positioner temperatures more often than fiducials?")
            sys.exit()
        num_fid_pulls = int(self.postemp_wait/self.fidtemp_wait) - 1
        print("We will measure the fiducial temperatures every %d seconds and the positioner temperatures after %d fiducial only measurements"%(int(self.fidtemp_wait), num_fid_pulls))

        while True:
            for i in range(num_fid_pulls):
                self.get_temps('fid')
                time.sleep(self.fidtemp_wait)
            self.get_temps('pos')
            time.sleep(self.fidtemp_wait)

if __name__ == '__main__':
    postemp_wait = 300 #int(input("How long should you wait between taking measurements of the positioner temps? (sec): "))
    fidtemp_wait = 30 #int(input("How long should you wait between taking measurements of the fiducial temps? (sec): "))
    pc = int(input("Which PC? "))
    P = PetalTempApp(pc, postemp_wait, fidtemp_wait)
    P.run()

    """
    P0=PetalTempApp(0, postemp_wait, fidtemp_wait)
    #P1=PetalTempApp(1, postemp_wait, fidtemp_wait)
    P2=PetalTempApp(2, postemp_wait, fidtemp_wait)
    P3=PetalTempApp(3, postemp_wait, fidtemp_wait)
    P4=PetalTempApp(4, postemp_wait, fidtemp_wait)
    P5=PetalTempApp(5, postemp_wait, fidtemp_wait)
    P6=PetalTempApp(6, postemp_wait, fidtemp_wait)
    P7=PetalTempApp(7, postemp_wait, fidtemp_wait)
    P8=PetalTempApp(8, postemp_wait, fidtemp_wait)
    #P9=PetalTempApp(9, postemp_wait, fidtemp_wait)

    PETALS = [P0, P1, P2, P3, P4, P5, P6, P7, P8, P9]

    Thread(P0.run()).start()
    #Thread(P1.run()).start()
    Thread(P2.run()).start()
    Thread(P3.run()).start()
    Thread(P4.run()).start()
    Thread(P5.run()).start()
    Thread(P6.run()).start()
    Thread(P7.run()).start()
    Thread(P8.run()).start()
    #Thread(P9.run()).start()
    """

