# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 07:30:37 2018

@author: addiewan
"""
import numpy as np
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

def ptu_ebay_cmd(time0,cmd,cnt):
    cmd_ebay_out[cnt]=time.time()-t0
    pass
    
##    try:
##        print('cnt=',cnt,'ref time t0=',t0,'cmd=',cmd)
##    except:
##        print('cnt=',cnt,'ptu_ebay command failed',time.time())
        
def ptu_d48_cmd(time0,cmd,cnt):
    cmd_d48_out[cnt]=time.time()-t0
    pass
##    try:
##        print('cnt=',cnt,'ref time t0=',t0,'cmd=',cmd)
##    except:
##        print('ptu_ebay command failed',time.time())
        
def ptu_timer(cmd_list):
    global cmd_ebay_out
    global cmd_d48_out
    global t0
    t0=time.time()
    print('t0=',t0)
    ti=np.zeros(len(cmd_list))
    ti2=np.zeros(len(cmd_list))
    cmd_ebay_out=np.zeros(len(cmd_list))
    cmd_d48_out=np.zeros(len(cmd_list))
    cnt=0
    #This loop for loop will schedule the print_time function to
    #be executed every second for 10 seconds
    for i in range(len(cmd_list)):
        
        ti[i]=time.time()
        dt=ti[i]-t0
        Timer(cmd_list[i][0]-dt+1, ptu_ebay_cmd, args=(cmd_list[i][0]-dt,cmd_list[i][1],cnt)).start()
        #cmd_ebay_out[i]=1-dt
        ti2[i]=time.time()
        dt2=ti2[i]-t0
        Timer(cmd_list[i][0]-dt2+1, ptu_d48_cmd, args=(cmd_list[i][0]-dt2,cmd_list[i][2],cnt)).start()
        #cmd_d48_out[i]=1-dt2
        cnt+=1
        
    return cmd_ebay_out,cmd_d48_out

sim_file = "/home/pi/Desktop/git_repos/GLO/tracking/ptu_simulations/fast.csv"
cmd_list = ptu_parse_sim(sim_file)
cmd_ebay_out,cmd_d48_out=ptu_timer(cmd_list)
