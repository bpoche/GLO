import serial
import time
import numpy as np
import pandas as pd
from threading import Timer

def ptu_ebay_cmd(ser,t0,cmd):
    try:
        ser.write(cmd.encode())
    except:
        print('ptu_ebay command failed',time.time())
        
def ptu_d48_cmd(ser,t0,cmd):
    try:
        ser.write(cmd.encode())
    except:
        print('ptu_ebay command failed',time.time())

def open_ptu(com_port,baudrate):
    ''' 
    Open serial connection with PTU
    '''
    
    ser = serial.Serial(
        port=com_port,
        baudrate=baudrate)
    
    if ser.isOpen():
        print('Connected to PTU ')
        return ser
    else:
        print('Houston the comm port aint workin')  
    return ser
##
##def ptu_parse_sim(sim_file):
##    with open(sim_file,'r') as f:
##        ptu_cmds = f.readlines()
##    ptu_cmds = [[float(x.strip().split(',')[0]),
##                 x.strip().split(',')[1],
##                 x.strip().split(',')[2]] for x in ptu_cmds]
##                        
##    return ptu_cmds


def ptu_parse_sim(sim_file):
    df = pd.read_csv(sim_file)
    ptu_cmds=[]
    for i in range(len(df)):
        ptu_cmds.append([df.delay[i],
                         df.ptu_ebay_cmd[i][1:-1]+' ',
                         df.ptu_d48_cmd[i][1:-1]+' '])                    
    return ptu_cmds

def ptu_timer(ser_ptu_ebay,ser_ptu_d48,cmd_list):
    t0=time.time()
    print('t0=',t0)
    ti=np.zeros(len(cmd_list))
    #This loop for loop will schedule the print_time function to
    #be executed every second for 10 seconds
    try:
        for i in range(len(cmd_list)):
            ti[i]=time.time()
            dt=ti[i]-t0
            try:
                Timer(cmd_list[i][0]-dt+1, ptu_ebay_cmd, args=(ser_ptu_ebay,t0,cmd_list[i][1])).start()
            except:
                print('ebay command','##'+cmd_list[i][1]+'##')
                print('timer creation failed')
            Timer(cmd_list[i][0]-dt+1, ptu_d48_cmd, args=(ser_ptu_d48,t0,cmd_list[i][2])).start()
    except:
        print('timer function failed')

def ptu_simulate(ptu_ebay_com_port,
                 ptu_d48_com_port,
                 ptu_ebay_baudrate,
                 ptu_d48_baudrate,
                 ptu_cmd_list,
                 ptu_save_loc,
                 file_prefix):
    try:
        ser_ptu_ebay = open_ptu(ptu_ebay_com_port,ptu_ebay_baudrate)
        ser_ptu_d48 = open_ptu(ptu_d48_com_port,ptu_d48_baudrate)
        print('made it')
        ptu_timer(ser_ptu_ebay,ser_ptu_d48,ptu_cmd_list)
    except:
        print('PTU not available, try again later')
    return

sim_file = "/home/pi/Desktop/git_repos/GLO/tracking/ptu_simulations/fast2.csv"
cmd_list = ptu_parse_sim(sim_file)
ptu_ebay_com_port='/dev/ttyUSB0'
ptu_d48_com_port='/dev/ttyUSB2'
ptu_ebay_baudrate=9600
ptu_d48_baudrate=9600
ptu_cmd_list=cmd_list
ptu_save_loc=''
file_prefix=''

ptu_simulate(ptu_ebay_com_port,
             ptu_d48_com_port,
             ptu_ebay_baudrate,
             ptu_d48_baudrate,
             ptu_cmd_list,
             ptu_save_loc,
             file_prefix)
             
             