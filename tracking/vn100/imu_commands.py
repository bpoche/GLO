# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 19:24:55 2018

@author: addiewan
"""
import pandas as pd
import numpy as np
#import matplotlib as mpl
from datetime import datetime
import os
import serial 
import time

#class IMU()

def open_imu(com_port='COM4',
                 baudrate=115200):
    # configure the serial connections (the parameters differs on the device you are connecting to)
    ser = serial.Serial(
        port=com_port,
        baudrate=baudrate)
    
    if ser.isOpen():
        print('Connected to VectorNav VN100')
        return ser
    else:
        print('Houston the comm port aint workin')
#    
#    #check to see if a shutter control file exists, if not, then create one
#
#    if os.path.isfile(data_loc + shutter_ctl) == False:
#        try:
#            open(data_loc + shutter_ctl, 'a')
#        except:
#            print('Could not create a data file :(')
#    
    return ser

def cmd(command,response=True,delay=0.1):
    ser.write(command.encode())
    if response == True:
        #line=[]  
        time.sleep(delay)
        bytesToRead = ser.inWaiting()
        ptu_out = ser.read(bytesToRead)
        #line.append(temp)
        return ptu_out
    return

def read_data(timeout=10):
    t0 = time.time()
    data=[]
    while (time.time() - t0) < timeout:
        #ser.readline()
        data.append(ser.readline())
    return data

def write_data(command):
    ser.write(command.encode())
    data = read_data(timeout=1)
    return data

def read_all(timeout=1):
    t0 = time.time()
    #data=[]
    data = pd.DataFrame(columns=['elasped',
                                 'yaw',
                                 'pitch',
                                 'roll',
                                 'mag_x',
                                 'mag_y',
                                 'mag_z',
                                 'accel_x',
                                 'accel_y',
                                 'accel_z',
                                 'ang_x',
                                 'ang_y',
                                 'ang_z'])
    while (time.time() - t0) < timeout:
        t1=time.time()-t0
        line=ser.readline().decode().split(',')
        try:
            yaw = float(line[1])
            pitch = float(line[2])
            roll = float(line[3])
            mag_x = float(line[4])
            mag_y = float(line[5])
            mag_z = float(line[6])
            accel_x = float(line[4])
            accel_y = float(line[5])
            accel_z = float(line[6])
            ang_x = float(line[4])
            ang_y = float(line[5])
            ang_z = float(line[6])
        except:
            yaw = np.nan
            pitch = np.nan
            roll = np.nan
            mag_x = np.nan
            mag_y = np.nan
            mag_z = np.nan
            accel_x = np.nan
            accel_y = np.nan
            accel_z = np.nan
            ang_x = np.nan
            ang_y = np.nan
            ang_z = np.nan
            
        data.loc[datetime.now()] = [1000*(t1-t0),
                                    yaw,
                                    pitch,
                                    roll,
                                    mag_x,
                                    mag_y,
                                    mag_z,
                                    accel_x,
                                    accel_y,
                                    accel_z,
                                    ang_x,
                                    ang_y,
                                    ang_z]
    return data

try:
    ser.open()
    print('Connected to IMU')
except:
    ser = open_imu()