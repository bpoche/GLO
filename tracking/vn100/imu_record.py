# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 19:24:55 2018

@author: addiewan
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os
import serial 
import time
import argparse

class VN100(object):
    
    def __init__(self,
                 com_port='/dev/ttyUSB1',
                 baudrate=115200,
                 rec_time=10,
                 save_loc=None):
        self.com_port=com_port
        self.baudrate=baudrate
        self.rec_time=rec_time
        self.save_loc=save_loc
        

    
    def open_imu(self):
        # configure the serial connections (the parameters differs on the device you are connecting to)
        
        ser = serial.Serial(
            port=self.com_port,
            baudrate=self.baudrate)
        
        if ser.isOpen():
            print('Connected to VectorNav VN100')
            return ser
        else:
            print('Houston the comm port aint workin')  
        return ser



    def read_all(self,ser):
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
        while (time.time() - t0) < self.rec_time:
            t1=time.time()
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
                
            data.loc[datetime.now()] = [round(1000*(t1-t0),4),
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

    def record_imu(self):
        try:
            ser.open()
            print('Connected to IMU')
        except:
            ser = self.open_imu()
        date_str = datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
        data = self.read_all(ser)
        data.to_csv(self.save_loc+'vn100_'+date_str+'.csv')
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Record VN100 IMU Data')
    parser.add_argument('-c','--com_port',
                        default='/dev/ttyUSB1',
                        type=str,
                        help='com port name')
    parser.add_argument('-b','--baudrate',
                        default=115200,
                        type=int,
                        help='baud rate')
    parser.add_argument('-t','--rec_time',
                        default=1.0,
                        type=float,
                        help='total time to record data (seconds)')
    parser.add_argument('-s','--save_loc',
                        default='/home/pi/Desktop/git_repos/GLO/tracking/vn100/data/',
                        type=str,
                        help='location to store .csv file of data')
        
    params=parser.parse_args()
    
    vn100 = VN100(
        com_port=params.com_port,
        baudrate=params.baudrate,
        rec_time=params.rec_time,
        save_loc='/home/pi/Desktop/git_repos/GLO/tracking/vn100/data/')
    
    data = vn100.record_imu()
                                    