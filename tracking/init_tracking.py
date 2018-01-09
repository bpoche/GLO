 # -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 13:27:10 2017

@author: addiewan
"""
import pandas as pd
import os
import pyautogui
import time
from datetime import datetime
import serial
import minimalmodbus
from coarse_tracking_R2 import coarse_tracking

user=os.getenv('username')

#set length of pause between pyautogui function calls
pyautogui.PAUSE = .5
delay = .2

#moving the mouse to upper left of screen will cause a pyautogui.FailSafeException exception 
pyautogui.FAILSAFE = True

#Origin is at upper-left corner of screen
#screen resolution of machine determines number of x/y pixels
x_min = 0
y_min = 0
x_max = pyautogui.size()[0]
y_max = pyautogui.size()[1]

#get current position of cursor
x, y = pyautogui.position()

def open_tracking_gui(icon_dir='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/image_capture/icons/',
                      button_dir='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/image_capture/buttons/'):
    
    print('Opening EQASCOM tracking GUI')
    
    x, y = pyautogui.locateCenterOnScreen(icon_dir+'eqascom_unselected.PNG',region=(0,728,1022,767))
    pyautogui.click(x, y)
    
    time.sleep(.1)
    x, y = pyautogui.locateCenterOnScreen(button_dir+'EQASCOM/eq_connect.PNG')
    pyautogui.click(x, y)
    time.sleep(.1)
    
def loc_tracking_buttons(icon_dir='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/image_capture/icons/',
                      button_dir='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/image_capture/buttons/'):
    
    print('Saving location of all tracking buttons')
    
    x, y = pyautogui.locateCenterOnScreen(button_dir+'EQASCOM/eqascom_ref.PNG')
    time.sleep(.1)
    
    
    slew_PX = (x-38,y+240)
    slew_MX = (x-38,y+303)
    slew_PY = (x-7,y+272)
    slew_MY = (x-72,y+272)
    solar_track = (x+40,y+415)
    no_tracking= (x-25,y+364)
    e_stop = (x+12,y+221)
    time.sleep(.1)
    
#    x, y = pyautogui.locateCenterOnScreen(button_dir+'EQASCOM/slew_PX.PNG')
#    slew_PX = (x,y)
#    time.sleep(.1)
#    
#    x, y = pyautogui.locateCenterOnScreen(button_dir+'EQASCOM/slew_MY.PNG')
#    slew_MY = (x,y)
#    time.sleep(.1)
#    
#    x, y = pyautogui.locateCenterOnScreen(button_dir+'EQASCOM/slew_PY.PNG')
#    slew_PY = (x,y)
#    time.sleep(.1)
#    
#    x, y = pyautogui.locateCenterOnScreen(button_dir+'EQASCOM/track_solar.PNG')
#    solar_track = (x,y)
#    time.sleep(.1)
#    
#    x, y = pyautogui.locateCenterOnScreen(button_dir+'EQASCOM/stop_track_rate.PNG')
#    no_tracking= (x,y)
#    time.sleep(.1)
    
#    x, y = pyautogui.locateCenterOnScreen(button_dir+'EQASCOM/e-stop.PNG')
#    e_stop = (x,y)
#    time.sleep(.1)
    
    return {'slew_MX':slew_MX,
            'slew_PX':slew_PX,
            'slew_MY':slew_MY,
            'slew_PY':slew_PY,
            'solar_track':solar_track,
            'no_tracking':no_tracking,
            'e_stop':e_stop}

def init_dataframe():
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
                                 'temp_M',
                                'angle_x_ref',
                                'angle_y_ref',
                                'angle_x_off_R',
                                'angle_y_off_R',
                                'angle_x_off_M',
                                'angle_y_off_M',
                                'angle_x_off_L',
                                'angle_y_off_L'])
    return data

def init_shutter(com_port='COM10',
                 baudrate=115200,
                 data_loc = 'C:/Balloon/sensor_testing/20171109/',
                 shutter_ctl = '20171109_shutter_ctl.txt'):
    
    
    # configure the serial connections (the parameters differs on the device you are connecting to)
    ser = serial.Serial(
        port=com_port,
        baudrate=baudrate,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_TWO,
        bytesize=serial.SEVENBITS)

    ser.isOpen()
    
    #check to see if a shutter control file exists, if not, then create one
    if os.path.isfile(data_loc + shutter_ctl) == False:
        try:
            open(data_loc + shutter_ctl, 'a')
        except:
            print('Could not create a data file :(')
    
    return ser

def open_shutter(ser):
    ser.write('1'.encode())
    print('opening shutter',datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

def close_shutter(ser):
    ser.write('2'.encode())
    print('closing shutter',datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    
def init_ccd_com_port(icon_dir='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/image_capture/icons/',
                      button_dir='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/image_capture/buttons/'):
    
    print('Creating com port 2 for CCD')
    
    x, y = pyautogui.locateCenterOnScreen(icon_dir+'vcecomex_unselected.PNG',region=(0,728,1022,767))
    pyautogui.click(x, y)
    
    #need to add click on dropdown menu
    
    #need to add click on com port 2
    
    #need to add click minimize
    
def init_ccd_driver(icon_dir='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/image_capture/icons/',
                      button_dir='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/image_capture/buttons/'):

    print('Setting up driver for CCD')
    
    x, y = pyautogui.locateCenterOnScreen(icon_dir+'genpr_unselected.PNG',region=(0,728,1022,767))
    pyautogui.click(x, y)
    time.sleep(delay)
    x, y = pyautogui.locateCenterOnScreen(button_dir+'genpr/timing.PNG')
    pyautogui.click(x, y) 
    time.sleep(delay)
    x, y = pyautogui.locateCenterOnScreen(button_dir+'genpr/dm_and_proxy.PNG')
    pyautogui.click(x, y)   
    time.sleep(delay)
    x, y = pyautogui.locateCenterOnScreen(button_dir+'genpr/execute_dm_proxy.PNG')
    pyautogui.click(x, y)  
    time.sleep(delay)
    x, y = pyautogui.locateCenterOnScreen(button_dir+'genpr/execute_dm_proxy_2.PNG')
    pyautogui.click(x, y)  
    time.sleep(delay)
    x, y = pyautogui.locateCenterOnScreen(button_dir+'genpr/ok_dm_proxy.PNG')
    pyautogui.click(x, y)  
    
    time.sleep(delay)
    x, y = pyautogui.locateCenterOnScreen(button_dir+'genpr/timing.PNG')
    pyautogui.click(x, y) 
    
    time.sleep(delay)
    x, y = pyautogui.locateCenterOnScreen(button_dir+'genpr/system_mode.PNG')
    pyautogui.click(x, y)
    
    time.sleep(delay)
    x, y = pyautogui.locateCenterOnScreen(button_dir+'genpr/system_mode_exec1.PNG')
    pyautogui.click(x, y)
    
    time.sleep(delay)
    x, y = pyautogui.locateCenterOnScreen(button_dir+'genpr/system_mode_exec2.PNG')
    pyautogui.click(x, y)
    
    time.sleep(delay)
    x, y = pyautogui.locateCenterOnScreen(button_dir+'genpr/system_mode_ok.PNG')
    pyautogui.click(x, y)
    
    
    

def open_framelink(icon_dir='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/image_capture/icons/',
                      button_dir='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/image_capture/buttons/'):
    
    print('Opening Framelink Express')
    
    x, y = pyautogui.locateCenterOnScreen(icon_dir+'framelink_unselected.PNG',region=(0,728,1022,767))
    pyautogui.click(x, y)

def capture_image(frames=5,
                  icon_dir='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/image_capture/icons/',
                  button_dir='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/image_capture/buttons/'):
    
    x, y = pyautogui.locateCenterOnScreen(icon_dir+'framelink_selected.PNG',region=(0,728,1022,767))
    pyautogui.click(x, y)
    
    x, y = pyautogui.locateCenterOnScreen(button_dir+'framelink/view.PNG')
    pyautogui.click(x, y)
    
    time.sleep(delay)
    
    x, y = pyautogui.locateCenterOnScreen(button_dir+'framelink/capture_settings.PNG')
    pyautogui.click(x, y)
    
    time.sleep(delay)
    
    x, y = pyautogui.locateCenterOnScreen(button_dir+'framelink/start_capture.PNG')
    pyautogui.click(x, y)
    
    print('a cleeeeeeeeek',datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

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
    
def save_data(data,
              track,
              loc='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/PID/',
              rev=''):
    data.to_csv(loc+'_PID_testing_'+rev+'_instr_'+track+'.txt')

#in the future, can have this load a parameter file that can be changed in real-time
def gen_params():
    
    date=datetime.fromtimestamp(time.time()).strftime('%Y%m%d')
    
    #camera params
    interval=60
    im_exps=5
    
    #reference locations for the estimated 'center' pixel coordinates of each 
    #channel. This would ideally represent an incidence angle of 0 degrees.
    ch1_refx=204.5
    ch2_refx=636.5
    ch3_refx=1065.5
    ch4_refx=209.5
    ch5_refx=652.5
    ch6_refx=1056.5
    
    ch1_refy=219.5
    ch2_refy=205.5
    ch3_refy=244.5
    ch4_refy=711.5
    ch5_refy=662.5
    ch6_refy=713.5

    
    #PyautoGUI params
    icon_dir='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/image_capture/icons/'
    button_dir='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/image_capture/buttons/'
    
    #shutter params
    shut_com = 'COM9'
    shut_baud = 115200
    shut_data_loc = 'Q:/Users/GLOtastic/Desktop/Python/solar_tracking/testing/'+date+'/'
    shut_ctl = date+'/'+'_shutter_ctl.txt'
    
    #Sun sensor params
    sun_com = 'COM10'
    track='M'
    instr='all'
    instr_R_x_ref = 0.39
    instr_R_y_ref = 0.65
    instr_R_x_ref = 0.0
    instr_R_y_ref = 1.1
    instr_M_x_ref = 2.2
    instr_M_y_ref = 0.43
    instr_L_x_ref = 0.685
    instr_L_y_ref = 1.882
    
    #PID params
    kp=1.0
    ki=0.0
    kd=0.1
    min_thresh_x = 0.005
    min_thresh_y = 0.005
    if track == 'R':
        sp_x = instr_R_x_ref
        sp_y = instr_R_y_ref
    if track == 'M':
        sp_x = instr_M_x_ref
        sp_y = instr_M_y_ref
    if track == 'L':
        sp_x = instr_L_x_ref
        sp_y = instr_L_y_ref
        
    #save data params
    #data_loc='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/testing/'+date+'/'+date
    data_loc='C:/'+date+'/'
    data_rev='R0'
        
    return {'interval':interval,
            'im_exps':im_exps,
            'ch1_refx':ch1_refx,
            'ch2_refx':ch2_refx,
            'ch3_refx':ch3_refx,
            'ch4_refx':ch4_refx,
            'ch5_refx':ch5_refx,
            'ch6_refx':ch6_refx,
            'ch1_refy':ch1_refy,
            'ch2_refy':ch2_refy,
            'ch3_refy':ch3_refy,
            'ch4_refy':ch4_refy,
            'ch5_refy':ch5_refy,
            'ch6_refy':ch6_refy,
            'track':track,
            'sun_com':sun_com,
            'instr':instr,
            'instr_R_x_ref':instr_R_x_ref,
            'instr_R_y_ref':instr_R_y_ref,
            'instr_M_x_ref':instr_M_x_ref,
            'instr_M_y_ref':instr_M_y_ref,
            'instr_L_x_ref':instr_L_x_ref,
            'instr_L_y_ref':instr_L_y_ref,
            'kp':kp,
            'ki':ki,
            'kd':kd,
            'min_thresh_x':min_thresh_x,
            'min_thresh_y':min_thresh_y,
            'sp_x':sp_x,
            'sp_y':sp_y,
            'shut_com':shut_com,
            'shut_baud':shut_baud,
            'shut_data_loc':shut_data_loc,
            'shut_ctl':shut_ctl,
            'data_loc':data_loc,
            'data_rev':data_rev,
            'icon_dir':icon_dir,
            'button_dir':button_dir}

def load_params(param_dtype_loc='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/params_dtype.txt',
                param_loc='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/params.txt'):
    #params_dtype = dict(pd.Series.from_csv(param_dtype_loc))
    params = pd.Series.from_csv(param_loc)
    return params

def save_params(params,
                save_param_loc='Q:/Users/GLOtastic/Desktop/Python/solar_tracking/'):
    pd.Series(params).to_csv(save_param_loc+'params.txt')
    return

params = gen_params()
#save_params(params)
#params = load_params()

#init_ccd_com_port(icon_dir=params['icon_dir'],
#                  button_dir=params['button_dir'])
#init_ccd_driver(icon_dir=params['icon_dir'],
#                button_dir=params['button_dir'])
#open_framelink(icon_dir=params['icon_dir'],
#               button_dir=params['button_dir'])
#open_tracking_gui(icon_dir=params['icon_dir'],
#                  button_dir=params['button_dir'])
data = init_dataframe()
#
ser = init_shutter(com_port=params['shut_com'],
                   baudrate=params['shut_baud'],
                   data_loc = params['shut_data_loc'],
                   shutter_ctl = params['shut_ctl'])
#
track_buttons = loc_tracking_buttons(icon_dir=params['icon_dir'],
                                    button_dir=params['button_dir'])

instruments = init_sun_sensor(com_port=params['sun_com'],
                              instr=params['instr'],
                              track=params['track'])

##continually run a loop that tracks, then captures an image
##the current dataframe is submitted to the coarse tracking function, the coarse tracking
##function appends data and returns the dataframe. 
##initially, the command will be set to 'justdoit', but this command functionality
##can be improved to allow greater control to interupt the coarse tracking function
##manually (ie, have coarse tracking continually check for a command file update).
##This way, you can have another python console running, or just a text editor, where 
##you just enter the command and save the text file.
while 1:
    data,command = coarse_tracking(
                        instruments,
                        data,
                        params['sp_x'],
                        params['sp_y'],
                        track=params['track'],
                        interval=params['interval'],
                        kp=params['kp'],
                        ki=params['ki'],
                        kd=params['kd'],
                        min_thresh_x = params['min_thresh_x'],
                        min_thresh_y = params['min_thresh_y'],
                        slew_MX = track_buttons['slew_MX'],
                        slew_PX = track_buttons['slew_PX'],
                        slew_PY = track_buttons['slew_PY'],
                        slew_MY = track_buttons['slew_MY'],
                        solar_track = track_buttons['solar_track'],
                        no_tracking = track_buttons['no_tracking'],
                        e_stop = track_buttons['e_stop'],
                        instr_R_x_ref = params['instr_R_x_ref'],
                        instr_R_y_ref = params['instr_R_y_ref'],
                        instr_M_x_ref = params['instr_M_x_ref'],
                        instr_M_y_ref = params['instr_M_y_ref'],
                        instr_L_x_ref = params['instr_L_x_ref'],
                        instr_L_y_ref = params['instr_L_y_ref'],
                        track_img_dir = 'C:/20171130/')
    
#    if command == 'justdoit':
#        open_shutter(ser)
#        capture_image(frames=params['im_exps'])
#        close_shutter(ser)
#        save_data(data,
#                  params['track'],
#                  params['data_loc'],
#                  params['data_rev'])
    