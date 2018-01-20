# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 14:44:11 2017

@author: GLOtastic

R2: add the ability to track at specific sun sensor angles
    -upon startup, ask user to press enter when glo is pointed to the desired
    tracking location
        -grab x_angle and y_angle from sun sensor and use this as reference for
        PID loop
"""

import numpy as np
import time
from datetime import datetime
import pyautogui
import pandas as pd

def coarse_tracking(instruments,
                    data,
                    sp_x,
                    sp_y,
                    track='M',
                    interval=60,
                    kp=1.0,
                    ki=0.0,
                    kd=0.1,
                    min_thresh_x = 0.005,
                    min_thresh_y = 0.005,
                    slew_MX = (71,300),
                    slew_PX = (71,362),
                    slew_PY = (105,329),
                    slew_MY = (42,329),
                    solar_track = (150,471),
                    no_tracking = (33, 472),
                    e_stop = (71, 333),
                    instr_R_x_ref = 0.39,
                    instr_R_y_ref = 0.65,
                    instr_M_x_ref = 2.2,
                    instr_M_y_ref = 0.43,
                    instr_L_x_ref = 0.24,
                    instr_L_y_ref = 0.72,
                    track_img_dir = 'C:/20171130/'):

    '''
    inputs:
        instruments: list of initialized minimalmodbus instrument objects
            list should either be all three instruments [instrR,instrM,instrL]
            or a list of one instrument, ie [instrM]
        data: pandas dataframe to store sun sensor data in
        sp_x: PID setpoint for x-axis control
        sp_y: PID setpoint for y-axis control
        track: pick which instrument to use to track 'R' 'M' or 'L'
        interval: set number of seconds between image captures
        kp: PID proportional gain setting
        ki: PID integral gain setting
        kd: PID derivative gain setting
        min_thresh_x: minimum x-axis error to care about (hysteresis)
        min_thresh_y: minimum y-axis error to care about (hysteresis)
        slew_MX: location of slew_PX or slew_N button on tracking GUI
        slew_MX: location of slew_MX or slew_S button on tracking GUI
        slew_MX: location of slew_PY or slew_E button on tracking GUI
        slew_MX: location of slew_MY or slew_W button on tracking GUI
        solar_track: location of solar_tracking_rate button on tracking GUI
        no_tracking: location of stop_tracking_rate button on tracking GUI
        e_stop: location of e-stop button on tracking GUI
        instr_R_x_ref = x-axis reading from instr_R when glo is 'centered'
        instr_R_y_ref = y-axis reading from instr_R when glo is 'centered'
        instr_M_x_ref = x-axis reading from instr_M when glo is 'centered'
        instr_M_y_ref = y-axis reading from instr_M when glo is 'centered'
        instr_L_x_ref = x-axis reading from instr_L when glo is 'centered'
        instr_L_y_ref = y-axis reading from instr_L when glo is 'centered'
    '''
    
    if len(instruments) > 1:
        turn_on_R = 'yes'
        turn_on_M = 'yes'
        turn_on_L = 'yes'
        instrumentR = instruments[0]
        instrumentM = instruments[1]
        instrumentL = instruments[2]
        if track == 'R':
            tracker_instr = instrumentR
        if track == 'M':
            tracker_instr = instrumentM
        if track == 'L':
            tracker_instr = instrumentL
    
    if len(instruments) == 1:
        if track == 'R':
            instrumentR = instruments[0]
            turn_on_R = 'yes'
            turn_on_M = 'no'
            turn_on_L = 'no'
            tracker_instr = instrumentR
        if track == 'M':
            instrumentM = instruments[0]
            turn_on_R = 'no'
            turn_on_M = 'yes'
            turn_on_L = 'no'
            tracker_instr = instrumentM
        if track == 'L':
            instrumentL = instruments[0]
            turn_on_R = 'no'
            turn_on_M = 'no'
            turn_on_L = 'yes'
            tracker_instr = instrumentL
    
    #slew (move) the tracker in a chosen direction for specified duration
    def slew(direction,distance):
        if direction == 'MX':
            slew_dir = slew_MX
            print('slewing -x dir for ' + str(distance) + ' units')
        elif direction == 'PX':
            slew_dir = slew_PX
            print('slewing +x dir for ' + str(distance) + ' units')
        elif direction == 'PY':
            slew_dir = slew_PY
            print('slewing +y dir for ' + str(distance) + ' units')
        elif direction == 'MY':
            slew_dir = slew_MY
            print('slewing -y dir for ' + str(distance) + ' units')
        else:
            print('Invalid direction silly head')
            
        pyautogui.click(slew_dir[0],slew_dir[1],clicks=1)
        pyautogui.dragTo(slew_dir[0],slew_dir[1], duration=distance, button='left')
            
#    def open_shutter(ser):
#        ser.write('1'.encode())
#        print('opening shutter',datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
#
#    def close_shutter(ser):
#        ser.write('2'.encode())
#        print('closing shutter',datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
#    
    def save_data(data,
                  loc='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/PID/',
                  rev=''):
        date=datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')
        data.to_csv(loc+date+'_PID_testing'+rev+'instr_'+track+'.txt')
        
    
    class PID:
        """ Simple PID control.
    
            This class implements a simplistic PID control algorithm. When
            first instantiated all the gain variables are set to zero, so
            calling the method GenOut will just return zero.
        """
        def __init__(self):
            # initialize gains
            self.Kp = 0
            self.Kd = 0
            self.Ki = 0
    
            self.Initialize()
    
        def SetKp(self, invar):
            """ Set proportional gain. """
            self.Kp = invar
    
        def SetKi(self, invar):
            """ Set integral gain. """
            self.Ki = invar
    
        def SetKd(self, invar):
            """ Set derivative gain. """
            self.Kd = invar
    
        def SetPrevErr(self, preverr):
            """ Set previous error value. """
            self.prev_err = preverr
    
        def Initialize(self):
            # initialize delta t variables
            self.currtm = time.time()
            self.prevtm = self.currtm
    
            self.prev_err = 0
    
            # term result variables
            self.Cp = 0
            self.Ci = 0
            self.Cd = 0
    
    
        def GenOut(self, error):
            """ Performs a PID computation and returns a control value based
                on the elapsed time (dt) and the error signal from a summing
                junction (the error parameter).
            """
            self.currtm = time.time()               # get t
            dt = self.currtm - self.prevtm          # get delta t
            de = error - self.prev_err              # get delta error
    
            self.Cp = self.Kp * error               # proportional term
            self.Ci += error * dt                   # integral term
    
            self.Cd = 0
            if dt > 0:                              # no div by zero
                self.Cd = de/dt                     # derivative term
    
            self.prevtm = self.currtm               # save t for next pass
            self.prev_err = error                   # save t-1 error
    
            # sum the terms and return the result
            return self.Cp + (self.Ki * self.Ci) + (self.Kd * self.Cd)
        
    #Initiate PID controller
    pid_x= PID()
    pid_y= PID()
    pid_x.SetKp(kp)
    pid_x.SetKi(ki)
    pid_x.SetKd(kd)
    pid_y.SetKp(kp)
    pid_y.SetKi(ki)
    pid_y.SetKd(kd)
    
    track_set = input(">> enter the following option:\n"+
                   "1: set tracking to current GLO position\n"+
                   "2: set tracking to predefined ref location\n"+
                    "    preset x_angle_ref = "+str(sp_x)+"\n"+
                    "    preset y_angle_ref = "+str(sp_y)+"\n"+
                    "    instr_R_x_ref = "+str(instr_R_x_ref)+"\n"+
                    "    instr_R_y_ref = "+str(instr_R_y_ref)+"\n"+
                    "    instr_M_x_ref = "+str(instr_M_x_ref)+"\n"+
                    "    instr_M_y_ref = "+str(instr_M_y_ref)+"\n"+
                    "    instr_L_x_ref = "+str(instr_L_x_ref)+"\n"+
                    "    instr_L_y_ref = "+str(instr_L_y_ref)+"\n"+
                    "0: no tracking\n"+
                    ">>")
    
    rt_display_on = input("Show real time display?\n"+
                          "1: yes\n"+
                          "0: no\n"+
                          ">>")
                
    if track_set == '1':
        print('GLO tracking set to current position')
    
    #Grab initial values from tracking registers       
    regs_tracker = tracker_instr.read_registers(8,7)
    if regs_tracker[3] > 50000:
        fb_x = -float(65536 - regs_tracker[3])/1000.0
    else:    
        fb_x = float(regs_tracker[3])/1000.0
        
    if regs_tracker[4] > 50000:
        fb_y = -float(65536 - regs_tracker[4])/1000.0
    else:    
        fb_y = float(regs_tracker[4])/1000.0
        
    if track_set == '1':
        sp_x = fb_x
        sp_y = fb_y
    params_rt = {'sp_x':sp_x,
              'sp_y':sp_y,
              'fb_x':fb_x,
              'fb_y':fb_y}
    save_param_loc='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/'
    pd.Series(params_rt).to_csv(save_param_loc+'params_rt.txt')
    
    outv_x = 0
    outv_y = 0
    scale_x = 3.0
    scale_y = 3.0
    
    PID_loop = True

    t_start = time.time()
    while PID_loop:
        # summing node
        err_x = sp_x - fb_x    
        
        #looks like instrument_M needs opposite sign compared to instr_R
        outv_x = pid_x.GenOut(err_x)
        
        #send the output error signal to the slew_motor North/South function
        if track_set != '0':
            if outv_x*scale_x > min_thresh_x:
                slew('MX',outv_x*scale_x)
            if outv_x*scale_x < min_thresh_x:
                slew('PX',outv_x*scale_x)
        
        print('outv_x = ',outv_x*scale_x)
    
        time.sleep(.5)
    
        err_y = sp_y - fb_y    # assume sp is set elsewhere
        
        outv_y = -pid_y.GenOut(err_y)
        
        #send the output error signal to the slew_motor North/South function
        if track_set != '0':
            if outv_y*scale_y > min_thresh_y:
                slew('MY',outv_y*scale_y)
            if outv_y*scale_y < min_thresh_y:
                slew('PY',outv_y*scale_y)
        
        print('outv_y = ',outv_y*scale_y)   
        time.sleep(.5)
        
        regs_tracker = tracker_instr.read_registers(8,7)
        if regs_tracker[3] > 50000:
            fb_x = -float(65536 - regs_tracker[3])/1000.0
        else:    
            fb_x = float(regs_tracker[3])/1000.0
            
        if regs_tracker[4] > 50000:
            fb_y = -float(65536 - regs_tracker[4])/1000.0
        else:    
            fb_y = float(regs_tracker[4])/1000.0
        
        if rt_display_on == '1':
            params_rt = {'sp_x':sp_x,
                         'sp_y':sp_y,
                         'fb_x':fb_x,
                         'fb_y':fb_y}
            save_param_loc='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/'
            pd.Series(params_rt).to_csv(save_param_loc+'params_rt.txt')
            
        
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
        
        angle_x_ref = sp_x
        angle_y_ref = sp_y
        
        angle_x_off_R = angle_x_ref - angle_x_filter_R
        angle_y_off_R = angle_y_ref - angle_y_filter_R
        
        angle_x_off_M = angle_x_ref - angle_x_filter_M
        angle_y_off_M = angle_y_ref - angle_y_filter_M
        
        angle_x_off_L = angle_x_ref - angle_x_filter_L
        angle_y_off_L = angle_y_ref - angle_y_filter_L
        
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
                    temp_M,
                    angle_x_ref,
                    angle_y_ref,
                    angle_x_off_R,
                    angle_y_off_R,
                    angle_x_off_M,
                    angle_y_off_M,
                    angle_x_off_L,
                    angle_y_off_L]
        
        data.loc[datetime.now()] = data_add
        print('')
        print(data.index[-1])
        print('sp_x = ',sp_x)
        print('sp_y = ',sp_y)
        print('ang_x_offset = ',sp_x-fb_x)
        print('ang_y_offset = ',sp_y-fb_y)
        print('ang_x_R = ',data.angle_x_filter_R[-1],' deg')
        print('ang_y_R = ',data.angle_y_filter_R[-1],' deg')
        print('ang_x_M = ',data.angle_x_filter_M[-1],' deg')
        print('ang_y_M = ',data.angle_y_filter_M[-1],' deg')
        print('ang_x_L = ',data.angle_x_filter_L[-1],' deg')
        print('ang_y_L = ',data.angle_y_filter_L[-1],' deg')
        
        
#        t_now = time.time()
#        if t_now - t_start > interval:
#            command = 'justdoit'
#            return data,command