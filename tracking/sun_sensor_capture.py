# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 14:30:47 2018

@author: GLOtastic

R1: attempting to add synchronized polling...before it was somewhat random when
the data was fetched
"""
#from init_tracking import init_sun_sensor
from datetime import datetime
import pandas as pd
import numpy as np
import minimalmodbus
import time
import threading
import os
import natsort
from glob import glob

user=os.getenv('username')
base_dir = 'Q:/git_repos/GLO/tracking/'
date=datetime.fromtimestamp(time.time()).strftime('%Y%m%d')

#check to see if any runs are already stored in todays directory
runs = glob(base_dir+'data/'+date+'/run_*')
if len(runs) == 0:
    os.makedirs(base_dir+'data/'+date+'/run_0/')
if len(runs) >= 1:
    run_num=int(runs[-1].split('run_')[-1])+1
    os.makedirs(base_dir+'data/'+date+'/run_'+str(run_num)+'/')
    
    

#check to see if directory for today exists, if not then create one
if not os.path.exists(base_dir+'data/'+date+'/'):
    os.makedirs(base_dir+'data/'+date+'/')


def init_sun_sensor(com_port='COM10',
                      instr='all',
                      track='M'):
    '''
    input: 
        com_port: set com port...usually 10 or 11
        instr: set instruments to initialize- 'all' for all instruments
                or 'R', 'L', or 'M' for right, left, or middle (labeled on sensor)
        track: designate which sun sensor to use for tracking
    '''
    if instr == 'all':
        turn_on_R = 'yes'
        turn_on_M = 'yes'
        turn_on_L = 'yes'   
    if instr == 'R':
        turn_on_R = 'yes'
        turn_on_M = 'no'
        turn_on_L = 'no'
    if instr == 'M':
        turn_on_R = 'no'
        turn_on_M = 'yes'
        turn_on_L = 'no'
    if instr == 'L':
        turn_on_R = 'no'
        turn_on_M = 'no'
        turn_on_L = 'yes'
    
    #initialize sun sensor (change identifier if needed)
    if turn_on_R == 'yes':
        instrumentR = minimalmodbus.Instrument(com_port, 1)
    if turn_on_M == 'yes':
        instrumentM = minimalmodbus.Instrument(com_port, 2)
    if turn_on_L == 'yes':
        instrumentL = minimalmodbus.Instrument(com_port, 3)
  
    if instr == 'all':
        return [instrumentR,instrumentM,instrumentL]
    if instr == 'R':
        return [instrumentR]
    if instr == 'M':
        return [instrumentM]
    if instr == 'L':
        return [instrumentL]

instruments = init_sun_sensor()

turn_on_R = 'yes'
turn_on_M = 'yes'
turn_on_L = 'yes'
instrumentR = instruments[0]
instrumentM = instruments[1]
instrumentL = instruments[2]



data = pd.DataFrame(columns=['angle_x_filter_R',
                             'angle_x_filter_L',
                             'angle_x_filter_M',
                             'angle_y_filter_R',
                             'angle_y_filter_L',
                             'angle_y_filter_M',
                             'angle_x_raw_R',
                             'angle_x_raw_L',
                             'angle_x_raw_M',
                             'angle_y_raw_R',
                             'angle_y_raw_L',
                             'angle_y_raw_M',
                             'radiation_R',
                             'radiation_L',
                             'radiation_M',
                             'temp_R',
                             'temp_L',
                             'temp_M'])

cnt=0
t0 = int(time.time())
def read_data(cnt,t0,t_sleep=0.02):
    '''
    cnt: counter to label files
    t_sleep is a delay (in seconds) to wait before polling each successive sensor
    '''
    #time.sleep(.02)
    t1 = int(time.time())
    if (t1-t0) >= 10:
        data.to_csv(base_dir+'data/'+date+'/sun_sensor_'+str(cnt)+'.csv',
                    index_label='time')
        cnt+=1
        t0 = t1
    
    if turn_on_R == 'yes':
        regs_R = instrumentR.read_registers(8,7)
        watts_R = regs_R[1]
        temp_R = float(regs_R[2])/10.0
        if regs_R[3] > 50000:
            angle_x_filter_R = -float(65536 - regs_R[3])/1000.0
        else:    
            angle_x_filter_R = float(regs_R[3])/1000.0
        if regs_R[4] > 50000:
            angle_y_filter_R = -float(65536 - regs_R[4])/1000.0
        else:    
            angle_y_filter_R = float(regs_R[4])/1000.0
        if regs_R[5] > 50000:
            angle_x_raw_R = -float(65536 - regs_R[5])/1000.0
        else:    
            angle_x_raw_R = float(regs_R[5])/1000.0
        if regs_R[6] > 50000:
            angle_y_raw_R = -float(65536 - regs_R[6])/1000.0
        else:    
            angle_y_raw_R = float(regs_R[6])/1000.0

    else:
        angle_x_filter_R = np.nan
        angle_y_filter_R = np.nan
        angle_x_raw_R = np.nan
        angle_y_raw_R = np.nan
        temp_R = np.nan  
        watts_R = np.nan
    
    time.sleep(t_sleep)
    if turn_on_M == 'yes':
        regs_M = instrumentM.read_registers(8,7)
        watts_M = regs_M[1]
        temp_M = float(regs_M[2])/10.0
        if regs_M[3] > 50000:
            angle_x_filter_M = -float(65536 - regs_M[3])/1000.0
        else:    
            angle_x_filter_M = float(regs_M[3])/1000.0
        if regs_M[4] > 50000:
            angle_y_filter_M = -float(65536 - regs_M[4])/1000.0
        else:    
            angle_y_filter_M = float(regs_M[4])/1000.0
        if regs_M[5] > 50000:
            angle_x_raw_M = -float(65536 - regs_M[5])/1000.0
        else:    
            angle_x_raw_M = float(regs_M[5])/1000.0
        if regs_M[6] > 50000:
            angle_y_raw_M = -float(65536 - regs_M[6])/1000.0
        else:    
            angle_y_raw_M = float(regs_M[6])/1000.0
    else:
        angle_x_filter_M = np.nan
        angle_y_filter_M = np.nan
        angle_x_raw_M = np.nan
        angle_y_raw_M = np.nan
        temp_M = np.nan  
        watts_M = np.nan        
    
    time.sleep(t_sleep)
    if turn_on_L == 'yes':
        regs_L = instrumentL.read_registers(8,7)
        watts_L = regs_L[1]
        temp_L = float(regs_L[2])/10.0
        if regs_L[3] > 50000:
            angle_x_filter_L = -float(65536 - regs_L[3])/1000.0
        else:    
            angle_x_filter_L = float(regs_L[3])/1000.0
        if regs_L[4] > 50000:
            angle_y_filter_L = -float(65536 - regs_L[4])/1000.0
        else:    
            angle_y_filter_L = float(regs_L[4])/1000.0
        if regs_L[5] > 50000:
            angle_x_raw_L = -float(65536 - regs_L[5])/1000.0
        else:    
            angle_x_raw_L = float(regs_L[5])/1000.0
        if regs_L[6] > 50000:
            angle_y_raw_L = -float(65536 - regs_L[6])/1000.0
        else:    
            angle_y_raw_L = float(regs_L[6])/1000.0

          
    else:
        angle_x_filter_L = np.nan
        angle_y_filter_L = np.nan
        angle_x_raw_L = np.nan
        angle_y_raw_L = np.nan
        temp_L = np.nan  
        watts_L = np.nan
    
    data_add = [angle_x_filter_R,
                angle_x_filter_L,
                angle_x_filter_M,
                angle_y_filter_R,
                angle_y_filter_L,
                angle_y_filter_M,
                angle_x_raw_R,
                angle_x_raw_L,
                angle_x_raw_M,
                angle_y_raw_R,
                angle_y_raw_L,
                angle_y_raw_M,
                watts_R,
                watts_L,
                watts_M,                         
                temp_R,
                temp_L,
                temp_M]
    
    data.loc[datetime.now()] = data_add
    print(data.index[-1],'ang_x_R = ',data.angle_x_filter_R[-1],' deg')
    threading.Timer(0.1,read_data(cnt,t0,t_sleep=0.02)).start()
    
    
read_data(cnt,t0,t_sleep=0.02)
#    print('')
#    print(data.index[-1])
#    print('sp_x = ',sp_x)
#    print('sp_y = ',sp_y)
#    print('ang_x_offset = ',sp_x-fb_x)
#    print('ang_y_offset = ',sp_y-fb_y)
print('ang_x_R = ',data.angle_x_filter_R[-1],' deg')
#    print('ang_y_R = ',data.angle_y_filter_R[-1],' deg')
#    print('ang_x_M = ',data.angle_x_filter_M[-1],' deg')
#    print('ang_y_M = ',data.angle_y_filter_M[-1],' deg')
#    print('ang_x_L = ',data.angle_x_filter_L[-1],' deg')
#    print('ang_y_L = ',data.angle_y_filter_L[-1],' deg')