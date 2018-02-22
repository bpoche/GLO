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
import csv

class PTU(object):
    
    def __init__(self,
                 com_port='/dev/ttyUSB0',
                 baudrate=9600,
                 sim_file=None,
                 save_loc=None):
        self.com_port=com_port
        self.baudrate=baudrate
        self.sim_file=sim_file
        self.save_loc=save_loc
    
    def open_ptu(self):
        ''' 
        Open serial connection with PTU
        '''
        
        ser = serial.Serial(
            port=self.com_port,
            baudrate=self.baudrate)
        
        if ser.isOpen():
            print('Connected to PTU D300 Ebay (or not)')
            return ser
        else:
            print('Houston the comm port aint workin')  
        return ser
    
    def parse_cmds(self,cmd_list):
        '''
        Parse ptu command list from provided .csv file
        '''
        with open(self.sim_file,'r') as f:
            reader = csv.reader(f)
            cmd_list = list(cmd_list)[0]
        return cmd_list
        

    def cmd_list(self,command_list):
        '''
        Enter a list of commands for ptu to execute sequentially
        
        Input:
            command_list: list of input commands (ie ['i ','pp200 ','pp-200 '])
        
        Example Usage:
            1) Command the pan axis to move to far left, then slowly move right,
                then on-the-fly speed up
            
                    commands=['i ',
                              'ps1900 ',
                              'pp2600 ',
                              'a ',
                              'ps600 ',
                              'pp-2600 ',
                              'ps1900 ']
                    cmd_list(commands)
            2) Set limits on pan axis to +-1000units
                pan_limit_hi=1000
                pan_limit_lo=-1000
                commands=['le ',
                          'l ',
                          'lu ',
                          'pxu'+str(pan_limit_hi)+' ',
                          'pnu'+str(pan_limit_lo)+' ']
                cmd_list(commands)
                cmd('pnu ')
                cmd('pxu ')
        
        '''
        for cmd in command_list:
            ser.write(cmd.encode())
            time.sleep(self.cmd_delay)

    def run(self):
        try:
            ser = self.open_ptu()
        except:
            print('Houston we aint connected to ptud300 ebay')
        date_str = datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
        commands = self.parse_cmds(self.sim_file)
        self.cmd_list(commands)
        print('Simulation Complete, goodbye')
        
#        data = self.read_all(ser)
#        data.to_csv(self.save_loc+'vn100_'+date_str+'.csv')
        
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
    parser.add_argument('-f','--sim_file',
                        default='home/pi/Desktop/git_repos/GLO/tracking/ptu_d300_ebay/simulations/test.csv'
                        type=float,
                        help='.csv file with ptu commands')
    parser.add_argument('-d','--cmd_delay',
                    default=0.1,
                    type=float,
                    help='delay between each ptu comman (seconds)')
    parser.add_argument('-s','--save_loc',
                        default='/home/pi/Desktop/git_repos/GLO/tracking/ptu_d300_ebay/data/',
                        type=str,
                        help='location to store .csv file of data')
        
    params=parser.parse_args()
    
    ptu = PTU(
        com_port=params.com_port,
        baudrate=params.baudrate,
        sim_file=params.sim_file,
        save_loc='/home/pi/Desktop/git_repos/GLO/tracking/vn100/data/')
    
    ptu.run()
                                    