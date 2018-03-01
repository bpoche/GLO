# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 07:30:37 2018

@author: addiewan
"""
import pandas as pd
import numpy as np
import matplotlib as mpl
from threading import Timer
import serial
import time

def ptu_parse_sim(sim_file):
    with open(sim_file,'r') as f:
        ptu_cmds = f.readlines()
    ptu_cmds = [[float(x.strip().split(',')[0]),
                 x.strip().split(',')[1]+' ',
                 x.strip().split(',')[2]+' '] for x in ptu_cmds]
                        
    return ptu_cmds

def ptu_ebay_cmd(t0,cmd,cnt):
    try:
        print('cnt=',cnt,'ref time t0=',t0,'cmd=',cmd)
    except:
        print('cnt=',cnt,'ptu_ebay command failed',time.time())
        
def ptu_d48_cmd(t0,cmd):
    try:
        print('ref time t0=',t0,'cmd=',cmd)
    except:
        print('ptu_ebay command failed',time.time())
        
def ptu_timer(cmd_list):
    t0=time.time()
    print('t0=',t0)
    ti=np.zeros(len(cmd_list))
    cnt=0
    #This loop for loop will schedule the print_time function to
    #be executed every second for 10 seconds
    for i in range(len(cmd_list)):
        ti[i]=time.time()
        dt=ti[i]-t0
        Timer(cmd_list[i][0]-dt, ptu_ebay_cmd, args=(cmd_list[i][0]-dt,cmd_list[i][1],cnt)).start()
        cnt+=1
        #Timer(cmd_list[i][0]-dt, ptu_d48_cmd, args=(dt,cmd_list[i][2])).start()

sim_file = "C:/git_repos/GLO/tracking/ptu_simulations/fast.csv"
cmd_list = ptu_parse_sim(sim_file)
ptu_timer(cmd_list)
