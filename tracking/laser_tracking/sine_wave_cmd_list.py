#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 15:05:07 2018

@author: carstens
"""

import time
import numpy as np
import pandas as pd

def calibrate_angles(ptu='ism',
                     file_loc='/tesla/data/carstens/GLO_git/GLO/'+
                     'tracking/ptu_simulations'):

    cmd_time=[]
    cmd_ebay=[]
    cmd_ismu=[]
    
    #immediate execution
    cmd_time.append(0)
    cmd_ebay.append('i')
    cmd_ismu.append('i')

    #indipendent control mode
    cmd_time.append(0.1)
    cmd_ebay.append('ci')
    cmd_ismu.append('ci')
    
    #initial time for checker board pattern
    t0=5.0
    
    #PTU 1/8th microstep size in arc seconds converted to degrees
    ptu_mstep=23.14285/(60.0*60.0)
    
    for it in range(1,100):
        
        this_time=it+t0-1
        #move ism PTU to each position
        if (it % 10) == 0:
            #carraige return
            cmd_time.append(this_time)
            cmd_ebay.append('')
            cmd_ismu.append('po-80')
            
            cmd_time.append(this_time+0.1)
            cmd_ebay.append('')
            cmd_ismu.append('to-8')
        else:
            #"space"
            cmd_time.append(this_time)
            cmd_ebay.append('')
            cmd_ismu.append('po8')
    
    if ptu == 'ism':
        df = pd.DataFrame(data={'delay':cmd_time,
                                'ptu_ebay_cmd':cmd_ebay,
                                'ptu_d48_cmd':cmd_ismu})
        csv_file=(file_loc+'/calibrate_angles_ism.csv')
    else:
        df = pd.DataFrame(data={'delay':cmd_time,
                                'ptu_ebay_cmd':cmd_ismu,
                                'ptu_d48_cmd':cmd_ebay})
        csv_file=(file_loc+'/calibrate_angles_ebay.csv')
  
    df=df[['delay','ptu_ebay_cmd','ptu_d48_cmd']]   

        
    df.to_csv(csv_file,index=False)
    
    
    

def sine_wave_input_ism(period=30,   
                        amp=100.0,
                        duration=120, 
                        cmd_freq=10.0,
                        file_loc='/tesla/data/carstens/GLO_git/GLO/tracking/ptu_simulations'):

    cmd_time=[]
    cmd_ebay=[]
    cmd_ismu=[]
    
    #immediate execution
    cmd_time.append(0)
    cmd_ebay.append('i')
    cmd_ismu.append('i')
    
    #velocity mode
    cmd_time.append(0.1)
    cmd_ebay.append('cv')
    cmd_ismu.append('se')
        
    #initial time for sine sweep
    t0=5.0
    num_i=duration*cmd_freq
    for i in range(int(round(num_i))):
        t=i/cmd_freq
        cmd_time.append(t+t0)
        x=amp*np.sin(2*np.pi/period*t)
        cmd_temp='ps'+str(int(round(x)))
        cmd_ebay.append(cmd_temp)
        cmd_ismu.append('')
            
    #ensure everything is stopped
    cmd_time.append(t0+duration+1.0)
    cmd_ebay.append('ps0')
    cmd_ismu.append('sd')
    
    df = pd.DataFrame(data={'delay':cmd_time,
                            'ptu_ebay_cmd':cmd_ebay,
                            'ptu_d48_cmd':cmd_ismu})
        
    df=df[['delay','ptu_ebay_cmd','ptu_d48_cmd']]
        
    csv_file=(file_loc+'/sine_wave_sweep_ism_period_'+str(int(period))+
              '_amp_'+str(int(amp))+'_freq_'+str(int(cmd_freq))+
              '_duration_'+str(int(duration))+'.csv')
        
    df.to_csv(csv_file,index=False)
        
    #end of function
    
    
def sine_wave_input_manual(period=30,   
                           amp=100.0,
                           duration=120, 
                           cmd_freq=10.0,
                           file_loc='/tesla/data/carstens/GLO_git/GLO/tracking/ptu_simulations'):

    cmd_time=[]
    cmd_ebay=[]
    cmd_ismu=[]
    
    #immediate execution
    cmd_time.append(0)
    cmd_ebay.append('i')
    cmd_ismu.append('i')
    
    #velocity mode
    cmd_time.append(0.1)
    cmd_ebay.append('cv')
    cmd_ismu.append('cv')
        
    #initial time for sine sweep
    t0=5.0
    num_i=duration*cmd_freq
    for i in range(int(round(num_i))):
        t=i/cmd_freq
        cmd_time.append(t+t0)
        x=amp*np.sin(2*np.pi/period*t)
        cmd_temp1='ps'+str(int(round(x)))
        cmd_ebay.append(cmd_temp1)
        cmd_temp2='ps'+str(int(-round(x)))
        cmd_ismu.append(cmd_temp2)
            
    #ensure everything is stopped
    cmd_time.append(t0+duration+1.0)
    cmd_ebay.append('ps0')
    cmd_ismu.append('ps0')
        
    df = pd.DataFrame(data={'delay':cmd_time,
                            'ptu_ebay_cmd':cmd_ebay,
                            'ptu_d48_cmd':cmd_ismu})
        
    df=df[['delay','ptu_ebay_cmd','ptu_d48_cmd']]
        
    csv_file=(file_loc+'/sine_wave_sweep_maual_period_'+str(int(period))+
              '_amp_'+str(int(amp))+'_freq_'+str(int(cmd_freq))+
              '_duration_'+str(int(duration))+'.csv')
        
    df.to_csv(csv_file,index=False)
        
    #end of function