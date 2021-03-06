# -*- coding: utf-8 -*-
from goprohero import GoProHero
from goprocam import GoProCamera
from goprocam import constants
#from ptu_d300_ebay.ptu_simulation import PTU
#from vn100.imu_record import VN100
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
from threading import Timer

def rec_video(vid_data_loc,quick=False):
    '''
    1. Connect to GoPro using GoProHero library
    2. Stop GoPro (in case already recording)
    3. Record timestamp
    4. Start GoPro video recording
    5. Save start timestamp to sim_info.csv
    '''
    print('rec_video started')
    with open('/home/pi/Desktop/git_repos/GLO/tracking/gopro/wifi.txt', 'r') as myfile:
        p=myfile.read().replace('\n', '')
    delay=2.0
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
    video_start_time=datetime.now()
    status = cam.command('record','01')
    vid_data = pd.read_csv(vid_data_loc,index_col='run')
    vid_data.loc[vid_data.index[0],'t_start']=video_start_time
    vid_data.to_csv(vid_data_loc)
    time.sleep(delay)  
    if status == True:
        print('Dude, the red Light is on, send it!!!')
    print('rec_video done')
    
def stop_video(vid_data_loc):
    '''
    1. Connect to gopro using GoProHero Library
    2. Stop video recording
    3. Connect to gopro using GoProCamera Library
    4. Retrieve filename of latest video
    5. Save video filename and timestamp of when 'stop recording command' was sent to sim_info.csv
    '''
    delay=2.0
    with open('/home/pi/Desktop/git_repos/GLO/tracking/gopro/wifi.txt', 'r') as myfile:
        p=myfile.read().replace('\n', '')
    cam = GoProHero(password=p)
    time.sleep(delay)
    #print(cam.getMediaInfo("file")) #Latest media taken filename
    #print(cam.getMediaInfo("size")) #Latest media taken size
    cam.command('record','00')
    print('stopping video')
    time.sleep(delay)
    try:
        gpCam = GoProCamera.GoPro(constants.auth)
        time.sleep(delay+2)
        #print('obtaining filename (unobtanium?)',vid_data_loc)
        file_name=gpCam.getMedia().split('videos')[1]
        time.sleep(2)
        vid_data = pd.read_csv(vid_data_loc,index_col='run')
        vid_data.loc[vid_data.index[0],'t_stop']=datetime.now()
        vid_data.loc[vid_data.index[0],'filename']=file_name
        vid_data.to_csv(vid_data_loc,index_label='run')
        print('filename = ',file_name)
    except:
        print('')
        print('******FAILED to get gopro video filename, check wifi connection')
        print('')
    time.sleep(2)
    return

##def imu_read_async(ez):
##
##def imu_timer(ez):
##    t0=time.time()
##    print('scheduling ptu timers t=',t0)
##    ti=np.zeros(len(cmd_list))
##    #This loop for loop will schedule the print_time function to
##    #be executed every second for 10 seconds
##    try:
##        while loop_trigger.value==1:
##            ti[i]=time.time()
##            dt=ti[i]-t0
##            Timer(cmd_list[i][0]-dt+1, imu_read_async, args=(ser_ptu_ebay,cmd_list[i][1])).start()
##            
##    except:
##        print('timer function failed')

def rec_imu_async(imu_com_port,
                  imu_baudrate,
                  save_loc,
                  file_prefix,
                  loop_trigger,
                  imu_freq):
    '''
    1)Open IMU VN100 com port
    2)Start reading/storing imu data in pandas dataframe
    3)Once loop_trigger changes from 1->0, stop recording, save to file
    
    Inputs:
        imu_com_port,
        imu_baudrate,
        save_loc,
        file_prefix,
        loop_trigger,
        imu_freq
    
    '''
    print('rec_imu_async starting')
    
##    try:
    #Initally try given com port parameters, if that doesn't work, try default parameters
    #and then reconnect with desired settings
    s = VnSensor()
    s.connect(imu_com_port, imu_baudrate)
    s.change_baudrate(921600)
    s.write_async_data_output_frequency(imu_freq)
    # IMU cannot support > 40fps using 115200, set baudrate to 921600
##    if (imu_freq > 40) & (imu_baudrate < 921600):
##        print('Insufficient baud rate for desired imu_freq of ',imu_freq,' hz, setting baudrate to 921600')
##        ez.sensor.change_baudrate(921600)
    
    print('imu baudrate =',s.baudrate)
    print('imu frequency =',s.read_async_data_output_frequency())
##    except:
##        print('Houston, got an imu issue, please consult the oracle')
    ypr = []
    accel=[]
    ang_r=[]
    mag=[]
    timestamp=[]
    t0 = time.time()
    interval = 1/float(imu_freq)
    time.sleep(.5) 
    while loop_trigger.value==1:
        #print('rec_imu loop',loop_trigger.value)
        try:
            t1=time.time()
            ypr.append(s.read_yaw_pitch_roll())
            accel.append(s.read_acceleration_measurements())
            ang_r.append(s.read_angular_rate_measurements())
            timestamp.append(datetime.now())
            dt=time.time()-t1
            if dt <= .01:
                time.sleep(interval-dt)
        except:
            print('excepted')
            ypr.append(np.nan)
            accel.append(np.nan)
            ang_r.append(np.nan)
            timestamp.append(datetime.now())
    s.disconnect()       
    yaw=[]
    pitch=[]
    roll=[]
    accel_x=[]
    accel_y=[]
    accel_z=[]
    ang_x=[]
    ang_y=[]
    ang_z=[]
    for i in range(len(ypr)):
        try:
            yaw.append(ypr[i].x)
            pitch.append(ypr[i].y)
            roll.append(ypr[i].z)
            accel_x.append(accel[i].x)
            accel_y.append(accel[i].y)
            accel_z.append(accel[i].z)
            ang_x.append(ang_r[i].x)
            ang_y.append(ang_r[i].y)
            ang_z.append(ang_r[i].z)          
        except:
            yaw.append(np.nan)
            pitch.append(np.nan)
            roll.append(np.nan)
            accel_x.append(np.nan)
            accel_y.append(np.nan)
            accel_z.append(np.nan)
            ang_x.append(np.nan)
            ang_y.append(np.nan)
            ang_z.append(np.nan)
            
    data = pd.DataFrame({'time':timestamp,
                         'yaw':yaw,
                         'pitch':pitch,
                         'roll':roll,
                         'accel_x':accel_x,
                         'accel_y':accel_y,
                         'accel_z':accel_z,
                         'ang_x':ang_x,
                         'ang_y':ang_y,
                         'ang_z':ang_z})
    data = data.set_index('time')
    data.to_csv(save_loc+'/imu_'+file_prefix+'.csv',
                index_label='time')
    print('rec_imu async done')
    return

##def rec_imu(imu_com_port,imu_baudrate,save_loc,file_prefix,loop_trigger):
##    '''
##    1)Open IMU VN100 com port
##    2)Start reading/storing imu data in pandas dataframe
##    3)Once loop_trigger changes from 1->0, stop recording, save to file
##    '''
##    print('rec_imu starting')
##    try:
##        ser = serial.Serial(
##            port=imu_com_port,
##            baudrate=imu_baudrate)
##    except:
##        print('could not open imu com port')
##    
##    if ser.isOpen():
##        print('Connected to VectorNav VN100')
##    else:
##        print('Houston the VectorNav com port aint workin')
##         
##    t0 = time.time()
##    data = pd.DataFrame(columns=['elasped',
##                                 'yaw',
##                                 'pitch',
##                                 'roll',
##                                 'mag_x',
##                                 'mag_y',
##                                 'mag_z',
##                                 'accel_x',
##                                 'accel_y',
##                                 'accel_z',
##                                 'ang_x',
##                                 'ang_y',
##                                 'ang_z'])
##    while loop_trigger.value==1:
##        #print('rec_imu loop',loop_trigger.value)
##        t1=time.time()
##        try:
##            line=ser.readline().decode().split(',')        
##            try:
##                yaw = float(line[1])
##                pitch = float(line[2])
##                roll = float(line[3])
##                mag_x = float(line[4])
##                mag_y = float(line[5])
##                mag_z = float(line[6])
##                accel_x = float(line[4])
##                accel_y = float(line[5])
##                accel_z = float(line[6])
##                ang_x = float(line[4])
##                ang_y = float(line[5])
##                ang_z = float(line[6])
##            except:
##                yaw = np.nan
##                pitch = np.nan
##                roll = np.nan
##                mag_x = np.nan
##                mag_y = np.nan
##                mag_z = np.nan
##                accel_x = np.nan
##                accel_y = np.nan
##                accel_z = np.nan
##                ang_x = np.nan
##                ang_y = np.nan
##                ang_z = np.nan    
##            data.loc[datetime.now()] = [round(1000*(t1-t0),4),
##                                        yaw,
##                                        pitch,
##                                        roll,
##                                        mag_x,
##                                        mag_y,
##                                        mag_z,
##                                        accel_x,
##                                        accel_y,
##                                        accel_z,
##                                        ang_x,
##                                        ang_y,
##                                        ang_z]
##        except:
##            print('missed imu dataframe')
##    data.to_csv(save_loc+'/vn100_'+file_prefix+'.csv',
##                index_label='time')
##    print('rec_imu done')
##    return
   
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
        ptu_cmds = ptu_parse_sim(sim_file)
        print(ptu_cmds)
        [out]: [[1.0, 'po100 ', 'po-100 '],
                [2.0, 'po-100 ', 'po100 '],
                [3.0, 'po1000 ', 'po-1000 ']]
                  
    '''
    df = pd.read_csv(sim_file,keep_default_na=False)
    ptu_cmds=[]
    for i in range(len(df)):
        ptu_cmds.append([df.delay[i],
                         df.ptu_ebay_cmd[i]+' ',
                         df.ptu_d48_cmd[i]+' '])                    
    return ptu_cmds

            
def ptu_ebay_cmd(ser,cmd_list,t0,index):
    '''
    Inputs:
        ser: serial port object for ptu_ebay
        cmd: (str) ASCII command to sent to ptu (ie 'po100 ')
    '''
    try:
        print('ptu_ebay cmd=##',cmd_list[index][1],'##')
        #execute this command
        ser.write(cmd_list[index][1].encode())
        
        #schedual next command
        index+=1
        ti=time.time()
        dt=ti-t0
        Timer(cmd_list[index][0]-dt+1, ptu_ebay_cmd, args=(ser,cmd_list,t0,index)).start()
    except:
        print('ptu_ebay command failed',time.time())
        
def ptu_d48_cmd(ser,cmd_list,t0,index):
    '''
    Inputs:
        ser: serial port object for ptu_d48
        cmd: (str) ASCII command to sent to ptu (ie 'po100 ')
    '''
    try:
        print('ptu_d48 cmd=##',cmd_list[index][2],'##')
        ser.write(cmd_list[index][2].encode())
        
        #schedule nexty command
        index+=1
        ti=time.time()
        dt=ti-t0
        Timer(cmd_list[index][0]-dt+1, ptu_d48_cmd, args=(ser,cmd_list,t0,index)).start()
    except:
        print('ptu_d48 command failed',time.time())
    
        
def ptu_timer(ser_ptu_ebay,ser_ptu_d48,cmd_list):
    '''
    Schedule thread timers using delays provided in ptu command list
    Inputs:
        ser_ptu_ebay: serial object for ptu_ebay
        ser_ptu_ebay: serial object for ptu_d48
        cmd_list: command list in format (delay,ptu_cmd_ebay,ptu_cmd_d48), (ie [1.5,po100,po200]) 
    '''
    try:
        t0=time.time()
        print('scheduling ptu timers t=',t0)
        ti=np.zeros(len(cmd_list))
        print('number of commands=',len(cmd_list))
        print('last delay in list',ptu_cmd_list[-1][0])
        #This loop for loop will schedule the print_time function to
        #be executed every second for 10 seconds
        #try:
        #for i in range(len(cmd_list)):
        ti=time.time()
        dt=ti-t0
        Timer(cmd_list[0][0]-dt+1, ptu_ebay_cmd, args=(ser_ptu_ebay,cmd_list,t0,0)).start()
        #print('ebay timer ',i,' command= ',cmd_list[i][1
        ti=time.time()
        dt=ti-t0
        Timer(cmd_list[0][0]-dt+1, ptu_d48_cmd, args=(ser_ptu_d48,cmd_list,t0,0)).start()
        #print('d48 timer ',i,' command= ',cmd_list[i][2])
            
    except:
        print('timer function failed, good luck')
        
def open_ptu(com_port,baudrate):
    ''' 
    Open serial connection with PTU
    '''
    try:
        ser = serial.Serial(
            port=com_port,
            baudrate=baudrate)
        
        if ser.isOpen():
            print('Connected to PTU D300 Ebay (or not)')
            return ser
        else:
            print('Houston the comm port aint workin')  
        return ser
    except:
        print('Failed to open up ptu com port')

def ptu_cmd(ser,cmd,delay=0.2):
    ser.write(cmd.encode())
    time.sleep(delay)

def ptu_simulate(ptu_ebay_com_port,
                 ptu_d48_com_port,
                 ptu_ebay_baudrate,
                 ptu_d48_baudrate,
                 ptu_cmd_list,
                 ptu_save_loc,
                 file_prefix,
                 ptu48_kp,
                 ptu48_ks,
                 ptu48_ka,
                 ptu48_vd,
                 ptu48_pd):
    '''
    1. Open ptu_ebay serial port
    2. Open ptu_d48 serial port
    3. Start threading timer function ptu_timer()
    4. Sleep for longest delay in provided ptu_cmd_list
    
    Inputs:
        ptu_ebay_com_port: (str) default = '/dev/ttyUSB0'
        ptu_d48_com_port: (str) default = '/dev/ttyUSB1'
        ptu_ebay_baudrate: (int) default = 9600
        ptu_d48_baudrate: (int) default = 9600
        ptu_cmd_list: (list) ptu command list generated from ptu_parse_sim() 
        ptu_save_loc: unused
        file_prefix:
        ptu48_kp: proportional gain setting
        ptu48_ks: output filter setting (0.0 - 1.0) 
        ptu48_ka: acceleration feed-forward settting
        ptu48_vd: velocity deadband setting
        ptu48_pd: position deadband setting
    '''
    try:
        ser_ptu_ebay = open_ptu(ptu_ebay_com_port,ptu_ebay_baudrate)
        ser_ptu_d48 = open_ptu(ptu_d48_com_port,ptu_d48_baudrate)
        print('made it')
        
        #Set ptu_d48 feedback parameters     
        ptu_cmd(ser_ptu_d48,'scpkp'+str(ptu48_kp)+' ')  #pan proportional gain
        ptu_cmd(ser_ptu_d48,'sctkp'+str(ptu48_kp)+' ')  #tilt proportional gain
        ptu_cmd(ser_ptu_d48,'scpks'+str(ptu48_kp)+' ')  #pan output filter
        ptu_cmd(ser_ptu_d48,'sctks'+str(ptu48_kp)+' ')  #tilt output filter
        ptu_cmd(ser_ptu_d48,'scpka'+str(ptu48_kp)+' ')  #pan acceleration feed forward
        ptu_cmd(ser_ptu_d48,'sctka'+str(ptu48_kp)+' ')  #tilt acceleration feed forward
        ptu_cmd(ser_ptu_d48,'scpvd'+str(ptu48_kp)+' ')  #pan velocity deadband
        ptu_cmd(ser_ptu_d48,'sctvd'+str(ptu48_kp)+' ')  #tilt velocity deadband
        ptu_cmd(ser_ptu_d48,'scppd'+str(ptu48_kp)+' ')  #pan position deadband
        ptu_cmd(ser_ptu_d48,'sctpd'+str(ptu48_kp)+' ')  #tilt position deadband
        
        ptu_timer(ser_ptu_ebay,ser_ptu_d48,ptu_cmd_list)
        time.sleep(ptu_cmd_list[-1][0]+2)
        print('sleep timer expired')
    except:
        print('PTU not available, try again later')
    return
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='1. Start Video 2. Record IMU 3. Simulate PTU 4. Shutter Down\n'+
                                     'If imu not working, ensure ensure baudrate, com port and imu_freq are correct\n'+
                                     '>>>from vnpy import *\n'+
                                     ">>>ez = EzAsyncData.connect('/dev/ttyUSB0', 115200)   #test com port/baud rate with putty"+
                                     ">>>ez.sensor.change_baudrate(921600)\n"+
                                     ">>>ez.sensor.write_async_data_output_frequency(100)  #or whatever imu_freq you want")
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
    parser.add_argument('-gp_i','--gp_save_loc',
                        default='/home/pi/Desktop/git_repos/GLO/tracking/ptu_simulations/data/',
                        type=str,
                        help='location of video info')

########### IMU parameters ################ 
    
    parser.add_argument('-imu_c','--imu_com_port',
                        default='/dev/ttyUSB1',
                        type=str,
                        help='com port name')
    parser.add_argument('-imu_b','--imu_baudrate',
                        default=921600,   
                        type=int,
                        help='imu baud rate')
    parser.add_argument('-imu_f','--imu_freq',
                        default=100,   
                        type=int,
                        help='imu data frequency')
    parser.add_argument('-imu_t','--imu_rec_time',
                        default=1.0,
                        type=float,
                        help='total time to record imu data (seconds)')
    parser.add_argument('-imu_s','--imu_save_loc',
                        default='/home/pi/Desktop/git_repos/GLO/tracking/ptu_simulations/data/',
                        type=str,
                        help='location to store .csv file of imu data')

########### PTU_Ebay parameters ################    
    parser.add_argument('-ptue_c','--ptu_ebay_com_port',
                        default='/dev/ttyUSB0',
                        type=str,
                        help='ptu ebay com port name')
    parser.add_argument('-ptue_b','--ptu_ebay_baudrate',
                        default=9600,
                        type=int,
                        help='ptu ebay baud rate')
    parser.add_argument('-ptu_f','--ptu_sim_dir',
                        default='/home/pi/Desktop/git_repos/GLO/tracking/ptu_simulations/',
                        type=str,
                        help='.csv file with ptu commands')
    parser.add_argument('-ptu_d','--ptu_cmd_delay',
                    default=0.1,
                    type=float,
                    help='delay between each ptu comman (seconds)')
    parser.add_argument('-ptu_s','--ptu_save_loc',
                        default='/home/pi/Desktop/git_repos/GLO/tracking/ptu_simulations/data/',
                        type=str,
                        help='location to store .csv file of ptu data')
    
########### PTU_D48 parameters ################
    parser.add_argument('-ptu48_c','--ptu48_com_port',
                        default='/dev/ttyUSB2',
                        type=str,
                        help='ptu com port name')
    parser.add_argument('-ptu48_b','--ptu48_baudrate',
                        default=9600,
                        type=int,
                        help='ptu baud rate')
    parser.add_argument('-ptu48_kp','--ptu48_kp',
                        default=16.0,
                        type=float,
                        help='ptu d48 proportional gain setting')
    parser.add_argument('-ptu48_ks','--ptu48_ks',
                        default=0.5,
                        type=float,
                        help='ptu-d48 output filter value (0.0-1.0) where 1.0=max filtering')
    parser.add_argument('-ptu48_ka','--ptu48_ka',
                        default=12.0,
                        type=float,
                        help='ptu-d48 acceleration feed forward setting')
    parser.add_argument('-ptu48_vd','--ptu48_vd',
                        default=0.004,
                        type=float,
                        help='ptu-d48 velocity deadband')
    parser.add_argument('-ptu48_pd','--ptu48_pd',
                        default=0.004,
                        type=float,
                        help='ptu-d48 position deadband')


########### General parameters ################

    parser.add_argument('-s','--save_loc',
                        default='/home/pi/Desktop/git_repos/GLO/tracking/ptu_simulations/data/',
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
    for i in range(len(ptu_sim_files)):
        print('')
        print('############################################################################################')
        print('running sim_file',ptu_sim_files[i])
        print('############################################################################################')
        print('')
        loop_trigger.value=1       #reset loop_trigger to 1 to enable imu_recording
        run_num=run_num+i     
        os.makedirs(params.save_loc+'run_'+str(run_num))  #create new folder for each simulation run
        vid_data_loc=params.gp_save_loc+'/run_'+str(run_num)+'/sim_info.csv'
        vid_data_df=pd.DataFrame(columns=['filename','t_start','t_stop','sim_file'])
        vid_data_df.loc[vid_data_df.shape[0],:]=np.nan
        vid_data_df.loc[vid_data_df.index[0],'sim_file']=ptu_sim_files[i]
        vid_data_df.to_csv(vid_data_loc,index_label='run')
        
        #parse commands from provided ptu_cmd_list .csv file
        ptu_cmd_list = ptu_parse_sim(ptu_sim_files[i])
        #define file_prefix 
        file_prefix = datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')+'_'+ptu_sim_files[i].split('/')[-1]
        gopro_start = multiprocessing.Process(name='gopro_start', target=rec_video,args=(vid_data_loc,True))
        gopro_stop = multiprocessing.Process(name='gopro_stop', target=stop_video,args=(vid_data_loc,))
##        imu_record = multiprocessing.Process(name='imu_record', target=rec_imu,args=(params.imu_com_port,
##                                                                                    params.imu_baudrate,
##                                                                                    params.save_loc+'run_'+str(run_num),
##                                                                                    file_prefix,
##                                                                                    loop_trigger
##                                                                                    ))
        imu_record = multiprocessing.Process(name='imu_record', target=rec_imu_async,args=(params.imu_com_port,
                                                                                    params.imu_baudrate,
                                                                                    params.save_loc+'run_'+str(run_num),
                                                                                    file_prefix,
                                                                                    loop_trigger,
                                                                                    params.imu_freq
                                                                                    ))
        ptu_sim = multiprocessing.Process(name='ptu_simulate',target=ptu_simulate,args=(params.ptu_ebay_com_port,
                                                                                         params.ptu48_com_port,
                                                                                         params.ptu_ebay_baudrate,
                                                                                         params.ptu48_baudrate,
                                                                                         ptu_cmd_list,
                                                                                         params.save_loc+'run_'+str(run_num),
                                                                                         file_prefix,
                                                                                         params.ptu48_kp,
                                                                                         params.ptu48_ks,
                                                                                         params.ptu48_ka,
                                                                                         params.ptu48_vd,
                                                                                         params.ptu48_pd))
    
        gopro_start.start()
        #gopro_start.join()
        while gopro_start.is_alive():
            #print('whats up')
            pass
        #run2.put(1)
        imu_record.start()
        time.sleep(1)
        ptu_sim.start()
        while ptu_sim.is_alive():
            pass
        print('bout to turn off loop tirgger',loop_trigger.value)
        #print('done turnt off the loop trigger',loop_trigger.value)
        loop_trigger.value=0
        time.sleep(1)
        gopro_stop.start()
        while gopro_stop.is_alive():
            pass    
        time.sleep(2)
        
        #write all gain parameters to sim_info.csv
        vid_data = pd.read_csv(vid_data_loc,index_col='run')
        vid_data['d48_kp']=params.ptu48_kp
        vid_data['d48_ks']=params.ptu48_ks
        vid_data['d48_ka']=params.ptu48_ka
        vid_data['d48_vd']=params.ptu48_vd
        vid_data['d48_pd']=params.ptu48_pd
        vid_data.to_csv(vid_data_loc,index_label='run')
        
        #save command list to file
        cmd_data = pd.read_csv(ptu_sim_files[i])
        cmd_data.to_csv(params.gp_save_loc+'/run_'+str(run_num)+'/cmd_list.csv',index_label='cmd_num')
    print('End of simulation, thanks for playing!')


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
        