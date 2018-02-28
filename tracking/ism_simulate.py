# -*- coding: utf-8 -*-
from goprohero import GoProHero
from goprocam import GoProCamera
from goprocam import constants
from  ptu_d300_ebay.ptu_simulation import PTU
from vn100.imu_record import VN100
import argparse
import multiprocessing
from multiprocessing import Queue,Value
import time
from glob import glob
import serial
import pandas as pd
import numpy as np
import os
from datetime import datetime
from vnpy import *
from queue import Empty
import threading

def rec_video(quick=True):
    with open('/home/pi/Desktop/git_repos/GLO/tracking/gopro/wifi.txt', 'r') as myfile:
        p=myfile.read().replace('\n', '')
    delay=2.0
    #name = multiprocessing.current_process().name
    cam = GoProHero(password=p)
    time.sleep(delay)
    #stop gopro video if already recording
    cam.command('record','00')
    time.sleep(delay)
    if quick != True:
        cam.command('power','01')
        time.sleep(10)
        cam.command('mode', '00') #set to video mode
        time.sleep(delay)
        cam.command('vidres', '01') #set resolution to 720p
        time.sleep(delay)
        cam.command('fps','120') #set to 120fps
        time.sleep(delay)    
        cam.command('fov','02')  #set to narrow field of view (90deg?)
        time.sleep(delay)
    status = cam.command('record','01')
    time.sleep(delay)  
    if status == True:
        print('Dude, the red Light is on, send it!!!')
    
def stop_video(save_loc):
    delay=2.0
    with open('/home/pi/Desktop/git_repos/GLO/tracking/gopro/wifi.txt', 'r') as myfile:
        p=myfile.read().replace('\n', '')
    cam = GoProHero(password=p)
    time.sleep(delay)
    #print(cam.getMediaInfo("file")) #Latest media taken filename
    #print(cam.getMediaInfo("size")) #Latest media taken size
    cam.command('record','00')
    time.sleep(delay)
    gpCam = GoProCamera.GoPro(constants.auth)
    time.sleep(delay)
    file_name=gpCam.getMedia()
    #file_name=gpCam.getMedia().split('videos')[1]
    print('filename = ',file_name)
    return


def rec_imu(imu_com_port,imu_baudrate,save_loc,file_prefix,loop_trigger):
    
    try:
        ser = serial.Serial(
            port=imu_com_port,
            baudrate=imu_baudrate)
    except:
        print('could not open imu com port')
    
    if ser.isOpen():
        print('Connected to VectorNav VN100')
    else:
        print('Houston the VectorNAv com port aint workin')
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
    #test=True
    #while ~run2.empty():
    while loop_trigger.value==1:
        #print('run=',run2)
        #print('testloop=',test.value)
        t1=time.time()
        #print(t1)
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
            print('is this where we exit?')
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
    data.to_csv(save_loc+'vn100_'+file_prefix+'.csv',
                index_label='time')
    return
    #return data
    
def ptu_parse_sim(sim_file):
    '''
    Parse simulation file into a list with the following format:
    
    Input:
        sim_file: (csv file) in the following format
        
                1.0,po100,po-100
                2.0,po-100,po100
                3.0,po1000,po-1000
                    
                where first column = time elapsed for command to execute
                second column = ptu_ebay command
                third column = ptu_d48 command
                
    Output:
        ptu_cmds: (list) of the commands in the following format
        
            [['elapsed time_1','ptu_ebay_cmd_1 ','ptu_d48_cmd_1 '],
             ['elapsed time_2','ptu_ebay_cmd_2 ','ptu_d48_cmd_2 ']]
             
    Example Usage:
    
        sim_file = '/home/pi/Desktop/git_repos/GLO/tracking/ptu_simulations/dual_test.csv'
        ptu_cmds = ptu_parse_file(sim_file)
        print(ptu_cmds)
        [out]: [['1.0', 'po100 ', 'po-100 '],
                ['2.0', 'po-100 ', 'po100 '],
                ['3.0', 'po1000 ', 'po-1000 ']]
                  
    '''
    with open(sim_file,'r') as f:
        ptu_cmds = f.readlines()
    ptu_cmds = [[x.strip().split(',')[0],
                 x.strip().split(',')[1]+' ',
                 x.strip().split(',')[2]+' '] for x in cmd_list]
                        
    return ptu_cmds

def cmd_list(ptu_ser,commands,cmd_delay=0.1,echo=True):
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
    for cmd in commands:
        if echo:
            print(cmd[0])
            ptu_ser.write(cmd[0].encode())
            time.sleep(cmd[1])
        else:
            ptu_ser.write(cmd.encode())
            time.sleep(cmd_delay)
            
def ptu_ebay_cmd(ser,cmd):
    try:
        ser.write(cmd.encode())
    except:
        print('ptu_ebay command failed',time.time())
        
def ptu_d48_cmd(ser,cmd):
    try:
        ser.write(cmd.encode())
    except:
        print('ptu_ebay command failed',time.time())
        
def ptu_timer(cmd_list):
    t0=time.time()
    print('t0=',t0)
    ti=np.zeros(len(cmd_list))
    #This loop for loop will schedule the print_time function to
    #be executed every second for 10 seconds
    for i in range(len(cmd_list):
        ti[i]=time.time()
        dt=ti[i]-t0
        Timer(cmd_list[i][0]-dt, ptu_ebay, args=[t0,cmd_list[i][1]).start()
        Timer(cmd_list[i][0]-dt, ptu_ebay, args=[t0,cmd_list[i][2]).start()

def ptu_simulate(ptu_com_port,
                 ptu_baudrate,
                 ptu_cmd_list,
                 ptu_save_loc,
                 file_prefix):
    try:
        ptu = PTU(ptu_com_port,ptu_baudrate,ptu_sim_file,ptu_save_loc)
        ptu.run()
    except:
        print('PTU not available, try again later')
    return
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='1. Start Video 2. Record IMU 3. Simulate PTU 4. Shutter Down')
    ########### GoPro parameters ################
    parser.add_argument('-gp_p','--gp_passw',
                        default='',
                        type=str,
                        help='gopro pass')
    parser.add_argument('-gp_m','--gp_mode',
                        default='video',
                        type=str,
                        help='mode: video, still, burst, timelapse, timer')
    parser.add_argument('-gp_v','--gp_vid_res',
                        default='720p',

                        type=str,
                        help='video resolution: 720p, 1080p')
    parser.add_argument('-gp_f','--gp_fov',
                    default='90',
                    type=str,
                    help='camera field of view: 90, 127, or 170')
    parser.add_argument('-gp_r','--gp_record',
                        default='off',
                        type=str,
                        help='record mode: on or off')
    parser.add_argument('-gp_s','--gp_sleep',
                        default='off',
                        type=str,
                        help='sleep mode: on or off')

########### IMU parameters ################ 
    
    parser.add_argument('-imu_c','--imu_com_port',
                        default='/dev/ttyUSB1',
                        type=str,
                        help='com port name')
    parser.add_argument('-imu_b','--imu_baudrate',
                        default=115200,   
                        type=int,
                        help='imu baud rate')
    parser.add_argument('-imu_t','--imu_rec_time',
                        default=1.0,
                        type=float,
                        help='total time to record imu data (seconds)')
    parser.add_argument('-imu_s','--imu_save_loc',
                        default='/home/pi/Desktop/git_repos/GLO/tracking/vn100/data/',
                        type=str,
                        help='location to store .csv file of imu data')

########### PTU_Ebay parameters ################    
    parser.add_argument('-ptu_c','--ptu_com_port',
                        default='/dev/ttyUSB1',
                        type=str,
                        help='ptu com port name')
    parser.add_argument('-ptu_b','--ptu_baudrate',
                        default=9600,
                        type=int,
                        help='ptu baud rate')
    parser.add_argument('-ptu_f','--ptu_sim_dir',
                        default='home/pi/Desktop/git_repos/GLO/tracking/ptu_d300_ebay/simulations/',
                        type=str,
                        help='.csv file with ptu commands')
    parser.add_argument('-ptu_d','--ptu_cmd_delay',
                    default=0.1,
                    type=float,
                    help='delay between each ptu comman (seconds)')
    parser.add_argument('-ptu_s','--ptu_save_loc',
                        default='/home/pi/Desktop/git_repos/GLO/tracking/ptu_d300_ebay/data/',
                        type=str,
                        help='location to store .csv file of ptu data')
    
########### PTU_Ebay parameters ################
    parser.add_argument('-ptu48_c','--ptu48_com_port',
                        default='/dev/ttyUSB2',
                        type=str,
                        help='ptu com port name')
    parser.add_argument('-ptu48_b','--ptu48_baudrate',
                        default=9600,
                        type=int,
                        help='ptu baud rate')


########### General parameters ################

    parser.add_argument('-s','--save_loc',
                        default='/home/pi/Desktop/git_repos/GLO/tracking/ISM_testing/data/',
                        type=str,
                        help='directory to store all data')

    params=parser.parse_args()

    
    ptu_sim_files= glob(params.ptu_sim_dir +'*.csv')
    video_filenames=[]
    #define a multiprocessing.Value object to share between processes
    loop_trigger=Value('i',1) 
    #check for existing run directories and continue existing number scheme
    if len(glob(params.save_loc+'run*')) > 0:
        run_num = len(glob(params.save_loc+'run*'))
    else:
        run_num=0
    #Start loop to execute every simulation file in the params.ptu_sim_dir provided
    for i in range(len(sim_files)):
        loop_trigger.value=1       #reset loop_trigger to 1 to enable imu_recording
        run_num=run_num+i    
        os.makedirs(params.save_loc+'run_'+str(run_num))  #create new folder for each simulation run
        cmd_list_ptu_d48,cmd_list_ptu_ebay = ptu_parse(sim_files[i])
        #define file_prefix 
        file_prefix = datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')+'_'+sim_files[i].split('/')[-1]
        gopro_start = multiprocessing.Process(name='gopro_start', target=rec_video,args=(True,))
        gopro_stop = multiprocessing.Process(name='gopro_stop', target=stop_video,args=(params.save_loc+'run_'+str(i),))
        imu_record = multiprocessing.Process(name='imu_record', target=rec_imu,args=(params.imu_com_port,
                                                                                    params.imu_baudrate,
                                                                                    params.save_loc+'run_'+str(i),
                                                                                    file_prefix,
                                                                                    loop_trigger
                                                                                    ))
        ptu_ebay = multiprocessing.Process(name='ptu_simulate',target=ptu_simulate,args=(params.ptu_com_port,
                                                                                        params.ptu_baudrate,
                                                                                        cmd_list_ptu_ebay,
                                                                                        params.ptu_cmd_delay,
                                                                                        params.save_loc+'run_'+str(i)))#,
##                                                                                        file_prefix))
        ptu_d48 = multiprocessing.Process(name='ptu_d48_simulate',target=ptu_d48_simulate,args=(params.ptu48_com_port,
                                                                                        params.ptu48_baudrate,
                                                                                        cmd_list_ptu_d48,
                                                                                        params.ptu_cmd_delay,
                                                                                        params.save_loc+'run_'+str(i)))#,
##                                                                                        file_prefix)) 
    
        gopro_start.start()
        while gopro_start.is_alive():
            pass
        #run2.put(1)
        imu_record.start()
        time.sleep(1)
        ptu_ebay.start()
        while ptu_ebay.is_alive():
            pass
        test.value=0
        time.sleep(1)
        imu_record.terminate()
        ptu_ebay.terminate()
        gopro_stop.start()
        time.sleep(4)
        
        #video_filenames.append(file_name)
##        while gopro_stop.is_alive():
##            time.sleep(2)
        #time.sleep(5)
        #run=False
        #time.sleep(1)
    gopro_stop.terminate()
    gopro_stop.join()
    imu_record.join()
    ptu_ebay.join()
    exit()
    print('are we at the end?')
##    print('path to save',params.save_loc+file_prefix.split('.csv')[0]+'_vid_filenames.txt')
##    with open(params.save_loc+file_prefix.split('.csv')[0]+'_vid_filenames.txt','w') as f:
##        print('list: ',video_filenames)
##        if len(video_filenames) > 0:
##            for filename in video_filenames:
##                print('for loop filename:',filename)
##                f.write("%s\n" %file_name)
##            f.close()
##        else:
##            f.close()
#    cam = GoProHero(password=params.passw)
#    
#    if params.mode == 'video':
#        cam.command('mode', '00') #set to video mode
#    else: 
#        cam.command('mode', '01') #set to still capture mode
#        
#    if params.vid_res == '720p':
#        cam.command('vidres', '01') #set resolution to 720p
#    else:
#        cam.command('vidres',params.vid_res) #set resolution to 720p
#        
#    if params.fov == '90':
#        cam.command('fov','02')
#    else:
#        cam.command('fov',params.fov)
#        
#    if params.record == 'on':
#        cam.command('record','01')
#    else: 
#        cam.command('record','00')
#        
#    if params.sleep == 'on':
#        cam.command('power','00')
#    else:
#        cam.command('power','01')
        