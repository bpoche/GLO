# -*- coding: utf-8 -*-
"""
Created on Wed Feb 07 21:24:19 2018

@author: GLOtastic
"""
import serial
import time
import numpy as np

def close(ser):
    ser.close()

def open_serial(port='COM15',
                baudrate=9600,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=None):
    ser = serial.Serial(port=port,
                        baudrate=baudrate,
                        stopbits=stopbits,
                        bytesize=bytesize,
                        timeout=timeout
                        )
    return ser

def cmd(command,response=True,delay=0.5):
    ser.write(command.encode())
    if response == True:
        #line=[]  
        time.sleep(delay)
        bytesToRead = ser.inWaiting()
        ptu_out = ser.read(bytesToRead)
        #line.append(temp)
        return ptu_out
    return



def cmd_list(command_list):
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
        time.sleep(0.2)


def pan(position):
    command ='pp'+str(position)+' '
    ser.write(command.encode())
    
def tilt(position):
    command ='tp'+str(position)+' '
    ser.write(command.encode())
    line=ser.readline()
    print(line)
    
def pan_off(position):
    command ='po'+str(position)+' '
    ser.write(command.encode())
    
def tilt_off(position):
    command ='to'+str(position)+' '
    ser.write(command.encode())

def set_micro_step():
    command = 'wpe '
    ser.write(command.encode())
    
def lab_lamp():
    cmd('tp400 ')
    cmd('pp00 ')
    
def left_right():
    pan(200)
    cmd('a ')
    pan(-200)

def cmd_fast(command,response=True):
    ser.write(command.encode())
    if response == True:
        #line=[]  
        #time.sleep(delay)
        bytesToRead = ser.inWaiting()
        ptu_out = ser.read(bytesToRead)
        #line.append(temp)
        return ptu_out
    
def sine_wave_input(period=60,
                    amp=100.0,
                    duration=60,
                    cmd_freq=10.0):

    commands=[]

    cmd('cv ',delay=5)
    cmd_out=[]
    pan_pos=[]
    #plt.plot(x)
    num_i=duration*cmd_freq
    for i in range(int(round(num_i))):
        t0=time.time()
        time.sleep(1/cmd_freq)
        print(time.time()-t0)
        t1=time.time()
        t=i/cmd_freq
        x=amp*np.sin(2*np.pi/period*t)
        print('x=',x)
        cmd_temp='ps'+str(int(round(x)))+' '
        print('cmd_temp=',cmd_temp)
        commands.append(cmd_temp)
        pan_pos_temp = cmd('pp ',delay=0.01)
        pan_pos.append(pan_pos_temp)
        #out = cmd_fast(cmd_temp,response=True,delay=1/cmd_freq)
        out = cmd_fast(cmd_temp,response=True)
        #out='blah'
        print(out)
        cmd_out.append(out)
        print(time.time()-t1)
    cmd('ps0 ')
        
    return cmd_list,cmd_out,pan_pos
    
ser=open_serial()