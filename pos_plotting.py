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

import tkinter as tk
import tkinter
import numpy as np

import petalcomm
import petal

import tkinter.filedialog
import tkinter.messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import pandas as pd

# nominal hole location data


class PosPlottingApp(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master, bg = 'white')
        self.start_time = datetime.datetime.now()
        self.file_path = '/home/msdos/focalplane/pos_utility/'
        self.temp_log_path = os.getcwd()#'/home/msdos/test_util/temp_logs/'
        

        self.hole_coords = np.genfromtxt(self.file_path+'hole_coords.csv', delimiter = ',', usecols = (3,4), skip_header = 40)
        self.nons = [38, 331, 438, 460, 478, 479, 480, 481, 497, 498, 499, 500, 513, 514, 515, 516, 527, 528, 529, 530, 531, 535, 536, 537, 538, 539, 540]
        self.gifs = [541, 542]
        self.fifs = [11, 75, 150, 239, 321, 439, 482, 496, 517, 534]

        self.collect_data = False

        self.mean_temp = []
        self.pb_temps = {'PBOX_TEMP_SENSOR':[], 'FPP_TEMP_SENSOR_1': [], 'FPP_TEMP_SENSOR_2': [], 'FPP_TEMP_SENSOR_3': [], 'GXB_TEMP_SENSOR': []}
        self.adc_values = {'ADC2': [], 'ADC3': [], 'ADC1': [], 'ADC4': [], 'ADC0' = []}

        self.createWidgets()

    def createWidgets(self):
        window = tk.Frame(root, bg = 'white')
        window.pack(side='top', fill='both')
        plot_window = tk.Frame(root, bg = 'white')
        plot_window.pack(side='bottom', fill='both')

        #set PC
        self.PC_entry = tk.Entry(window, width = 8, justify = 'right')
        self.PC_entry.grid(column=0, row=0)
        self.PC_button = tk.Button(window, width = 10, text = 'CONNECT TO PC', command=lambda: self.set_PC())
        self.PC_button.grid(column=0,row=1)

        #wait time
        self.wait_time_entry = tk.Entry(window, width = 8, justify = 'right')
        self.wait_time_entry.grid(column=2, row=0)
        self.wait_time_entry.insert(0, 120)
        self.wait_time_button = tk.Button(window, width = 10, text = 'WAIT TIME', command=lambda: self.set_wait())
        self.wait_time_button.grid(column=2,row=1)

        #Start & Stop
        self.start_button = tk.Button(window, width = 10, text = 'START', command=lambda: self.start())
        self.start_button.grid(column=3, row=0)
        self.stop_button = tk.Button(window, width = 10, text = 'STOP', command=lambda: self.stop())
        self.stop_button.grid(column=3, row=1)

        self.run()

    def set_PC(self):
        Petal_to_PC = {0:4, 1:5, 2:6, 3:3, 4:8, 5:10, 6:11, 7:2, 8:7, 9:9}
        self.PC = int(self.PC_entry.get())
        self.petal = Petal_to_PC(self.PC)
        self.comm = petalcomm.PetalComm(self.PC)
        petal_label = tk.Text(root, text = "Connected to PC%s on Petal %s" % (str(self.PC), str(self.petal)))
        petal_label.grid(column=1, row=0)
        self.temp_log = open(self.temp_log_path+'/temp_log_PC_%d_%s.txt'%str(self.PC, self.start_time),'w')

    def set_wait(self)
        self.wait = int(self.wait_time_entry.get())
        wait_label = tk.Text(root, text = "Waiting %s seconds between calls" % str(self.wait))
        wait_label.grid(column=1, row=1)

    def start(self):
        self.collect_data = True
        data_collect_label = tk.Text(root, text = "Data is being collected")
        data_collect_label.grid(column=4, row=0)

        self.get_temps()
        #GO GET DATA

    def stop(self):
        self.collect_data = False
        data_collect_label = tk.Text(root, text = "Data not being collected")
        data_collect_label.grid(column=4, row=1)



    def get_temps(self):
        measure_time = datetime.datetime.now()
        current_pos_dict = self.comm.pbget('posfid_temps')
        pd_dict = self.comm.pbget('pd_temps')
        adc_dict = self.comm.pbget('adcs')

        pos_temps = []
        for can, val in current_pos_dict.items():
            pos_temps.append(list(t for t in val.values()))
        self.current_pos_temps = np.hstack(pos_temps)
        self.mean_temp.append(np.mean(self.current_pos_temps))

        for i in self.pb_temps.keys():
            try:
                self.pb_temps[i].append(pd_dict[i])
            except:
                pass

        for i in self.adc_values.keys():
            try:
                self.adc_values[i].append(adc_dict[i])
            except:
                pass

        D = {measure_time: [current_pos_dict, pd_dict, adc_dict]}
        self.temp_log.write(str(D))
        self.temp_log.write('\n')

        self.make_plot()

    def make_plot(self):
        gridsize = (4, 3)
        fig = plt.figure(figsize=(12, 8))
        ax1 = plt.subplot2grid(gridsize, (0, 0), colspan=3, rowspan=3)
        ax2 = plt.subplot2grid(gridsize, (3, 0))
        ax3 = plt.subplot2grid(gridsize, (3, 1))
        ax4 = plt.subplot2grid(gridsize, (3, 2))

        ax2.hist(self.current_pos_temps, bins = 25)
        ax3.plot(self.pb_temps['PBOX_TEMP_SENSOR'], '-x', label = 'PBOX')
        ax3.plot(self.pb_temps['FPP_TEMP_SENSOR_1'], '-x', label = 'FPP1')
        ax3.plot(self.pb_temps['FPP_TEMP_SENSOR_2'], '-x', label = 'FPP2')
        ax3.plot(self.pb_temps['FPP_TEMP_SENSOR_3'], '-x', label = 'FPP3')
        ax3.plot(self.pb_temps['GXB_TEMP_SENSOR'], '-x', label = 'GXB')
        ax3.legend()

        ax4.plot(self.adc_values['ADC2'], '-x', label = 'ADC2')
        ax4.plot(self.adc_values['ADC3'], '-x', label = 'ADC3')
        ax4.plot(self.adc_values['ADC1'], '-x', label = 'ADC1')
        ax4.plot(self.adc_values['ADC4'], '-x', label = 'ADC4')
        ax4.plot(self.adc_values['ADC0'], '-x', label = 'ADC0')
        ax4.legend()

    def plot_hole_info(self):
        for i in range(len(self.hole_coords)):
            x = self.hole_coords[i][0]
            y = self.hole_coords[i][1]

            if i not in self.nons:
                self.ax.plot(x, y, color = 'lightgrey', marker='o', zorder = -1)
                if i in self.fifs:
                    text = 'F' + str(i)
                    col = 'blue'
                elif i in self.gifs:
                    text = 'G' + str(i)
                    col = 'purple'
                else:
                    text = i
                    col = 'black'
                self.ax.text(x-.1, y + 0.3, text, color = col, fontsize=6)

    def initial_plot(self):

        self.fig=plt.figure(figsize = (10,5))
        self.ax=self.fig.add_axes(self.fig.add_axes([0,0,1,1]))
        self.plot_hole_info()
        self.hole=1
        self.ax.scatter(self.hole_coords[self.hole][0], self.hole_coords[self.hole][1], marker= '*', s=200, color = 'gold')

        # Google sheet
        url = 'https://docs.google.com/spreadsheets/d/1lJ9GjhUUsK2SIvXeerpGW7664OFKQWAlPqpgxgevvl8/edit#gid=0'
        credentials = self.file_path+'google_access_account.json'
        scope = ['https://spreadsheets.google.com/feeds', 'https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(url).sheet1
        df  = get_as_dataframe(sheet, parse_dates=True, usecols=[0,1,2,3,4,6,8,14], skiprows=20, header=0)
        pdf=df
        pdf=pdf.loc[pdf['PETAL_ID'] == int(self.petal)]

        self.dev_list=pdf['CAN_ID'].tolist()
        #self.dev_list = [str(i) for i in dev_list]
        self.hole_list=pdf['DEVICE_LOC'].tolist()
        self.dev_id_loc=dict(zip(self.dev_list,self.hole_list))

        holes = []
        idx = []
        for i,e in enumerate(self.ids):
            try:
                holes.append(self.dev_id_loc[e])
                idx.append(i)
            except:
                print('failed: ',e)
                self.nons.append(e)
                pass
        temps = np.array(self.temps)[np.array(idx)]
        new_ids = np.array(self.ids)[np.array(idx)]

        #print(holes[0:5]) 
        x = []
        y = []
        idx2 = []
        for i,e in enumerate(holes):
            try:
                x.append(self.hole_coords[int(e)][0])
                y.append(self.hole_coords[int(e)][1])
                idx2.append(i)
            except:
                print('failed: ',new_ids[i])
                self.nons.append(new_ids[i])
                pass
        temps = temps[np.array(idx2)]
        x = np.array(x)
        y = np.array(y)

        sc = self.ax.scatter(x,y,s=120,c=temps)
        self.cbar = plt.colorbar(sc)
        plt.show()


    def updated_plot(self):
        #Update data (with the new _and_ the old points)
        self.ax.scatter(self.hole_coords[self.hole][0], self.hole_coords[self.hole][1], marker= '*', s=200, color = 'gold')
        holes = []
        idx = []
        for i,e in enumerate(self.ids):
            try:
                holes.append(self.dev_id_loc[e])
                idx.append(i)
            except:
                print('failed: ',e)
                pass
        temps = np.array(self.temps)[np.array(idx)]
        new_ids = np.array(self.ids)[np.array(idx)]

        #print(holes[0:5]) 
        x = []
        y = []
        idx2 = []
        for i,e in enumerate(holes):
            try:
                x.append(self.hole_coords[int(e)][0])
                y.append(self.hole_coords[int(e)][1])
                idx2.append(i)
            except:
                print('failed: ',new_ids[i])
                pass
        temps = temps[np.array(idx2)]
        x = np.array(x)
        y = np.array(y)

        self.ax.scatter(x,y,s=120,c=temps)
        self.cbar.set_clim(vmin=min(temps),vmax=max(temps))
        self.cbar.draw_all()
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def run(self):
        while self.collect_data == True:
            self.get_temps()
            time.sleep(self.wait)

if __name__ == '__main__':
    P = PosPlottingApp()
    P()

    




        
