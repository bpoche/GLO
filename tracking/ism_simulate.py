# -*- coding: utf-8 -*-
from goprohero import GoProHero
from  ptu_d300_ebay.ptu_simulation import PTU
from vn100.imu_record import VN100
import argparse
import multiprocessing
import time
from glob import glob
import serial
import pandas as pd
import numpy as np
from datetime import datetime

def rec_video():
    #name = multiprocessing.current_process().name
    cam = GoProHero(password='@d@lie4444')
    time.sleep(0.5)
    cam.command('power','01')
    time.sleep(0.5)
    cam.command('mode', '00') #set to video mode
    time.sleep(0.5)
    cam.command('vidres', '01') #set resolution to 720p
    time.sleep(0.5)
    cam.command('fov','02')
    time.sleep(0.5)
    status = cam.command('record','01')
    time.sleep(0.5)  
    if status == True:
        print('Dude, the red Light is on, send it!!!')
    
def stop_video():
    cam = GoProHero(password='@d@lie4444')
    print(cam.getMediaInfo("file")) #Latest media taken filename
    print(cam.getMediaInfo("size")) #Latest media taken size
    cam.command('record','00')
    time.sleep(0.5)  
    cam.command('power','00')
    time.sleep(0.5)

def rec_imu(imu_com_port,imu_baudrate,imu_save_loc,file_prefix):
    global run
    
    try:
        ser = serial.Serial(
            port=imu_com_port,
            baudrate=imu_baudrate)
    except:
        print('could not open imu com port')
    
    if ser.isOpen():
        print('Connected to VectorNav VN100')
    else:
        print('Houston the comm port aint workin')
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
    while run:
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
        
    data.to_csv(imu_save_loc+'vn100_'+file_prefix+'.csv')
    #return data
    

def ptu_simulate(ptu_com_port,
                 ptu_baudrate,
                 ptu_sim_file,
                 ptu_save_loc,
                 file_prefix):
    ptu = PTU(com_port,baudrate,sim_file,save_loc)
    ptu.run()
 
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='1. Start Video 2. Record IMU 3. Simulate PTU 4. Shutter Down')
    ########### GoPro parameters ################
    parser.add_argument('-gp_p','--gp_passw',
                        default='@d@lie4444',
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

########### PTU parameters ################    
    parser.add_argument('-ptu_c','--ptu_com_port',
                        default='/dev/ttyUSB0',
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
    
########### General parameters ################
    
    params=parser.parse_args()

    global run
    run = True
    sim_files = glob(params.ptu_sim_dir +'*.csv')
    for i in range(len(sim_files)):
        file_prefix = datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')+'_'+sim_files[i].split('/')[-1]
        gopro_start = multiprocessing.Process(name='gopro_start', target=rec_video)
        gopro_stop = multiprocessing.Process(name='gopro_stop', target=stop_video)
        imu_record = multiprocessing.Process(name='imu_record', target=rec_imu,args=(params.imu_com_port,
                                                                                    params.imu_baudrate,
                                                                                    params.imu_save_loc,
                                                                                    file_prefix))
        ptu_ebay = multiprocessing.Process(name='ptu_simulate',target=ptu_simulate,args=(params.ptu_com_port,
                                                                                        params.ptu_baudrate,
                                                                                        params.ptu_sim_file,
                                                                                        params.ptu_save_loc,
                                                                                        file_prefix)) 
    
        gopro_start.start()
        imu_record.start()
        time.sleep(5)
        ptu_ebay.start()
        while ptu_ebay.is_alive():
            time.sleep(1)
        gopro_stop.start()
        run=False
   
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
        