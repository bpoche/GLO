#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 24 07:51:14 2018

@author: ramble
"""

from glob import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

date='20180322'
run_dir = '/media/ramble/C61836BD1836AC75/laser_tracking/'+date+'/'
#calib_file = '/media/ramble/C61836BD1836AC75/laser_tracking/20180323/GOPR0342.csv'

#calib_file = '/media/ramble/C61836BD1836AC75/laser_tracking/20180323/GOPR0342.csv'

data={}
date=run_dir.split('laser_tracking')[-1][1:-1]
dirs = glob(run_dir+'run*')
data_calib_found=0
no_data=[]
for r in dirs:
       run_num = r.split('run_')[-1]
       data['run_'+str(run_num)]={}
       sim_info=pd.read_csv(r+'/sim_info.csv')    
       cmd_list=pd.read_csv(r+'/cmd_list.csv')
       imu_file=glob(r+'/imu_*')
       try:
              imu_data=pd.read_csv(imu_file[0],parse_dates=True,infer_datetime_format=True,index_col='time')
              data['run_'+str(run_num)]['imu_data']=imu_data
       except:
              print('cannot find imu data for run_'+str(run_num) )
       data['run_'+str(run_num)]['sim_info']=sim_info
       data['run_'+str(run_num)]['cmd_list']=cmd_list
       vid_file=data['run_'+str(run_num)]['sim_info'].filename[0].split('100GOPRO/')[-1]
       vid_num=data['run_'+str(run_num)]['sim_info'].filename[0].split('100GOPRO/')[-1].split('.MP4')[0]
       try:
              data['run_'+str(run_num)]['laser_data']=pd.read_csv(run_dir+vid_num+'.csv',parse_dates=True,infer_datetime_format=True)
       except:
              print('cannot find '+vid_num+'.csv for run_'+str(run_num))
              no_data.append('run_'+run_num)
       if 'calibrate' in sim_info.sim_file[0]:
              data_calib=data['run_'+str(run_num)]['laser_data']
              data_calib_found=1

#Process calibration data to calculate degrees per pixel to use for other runs (med_dpp)
if data_calib_found == 0:
       print('no calibration file found for '+date)
else:
       time=data_calib.time_elapsed.to_frame()/1e3
       
       #1 second smooth to remove stair step
       rm=data_calib.laser_cen_x.to_frame().rolling(120,center=True).mean()
       
       #plt.figure(1)
       #plt.plot(time,data.laser_cen_x,'x',color='black')
       #plt.plot(time,rm,'-+',color='blue')
       
       dif_pos=rm.diff().values
       dif_time=time.diff().values
       
       #angular rate in GOPRO pixels per second
       deriv=dif_pos/(dif_time)
       
       #PTU angular rate in degrees per second
       ptu_rate=-23.14285/60/60
       
       #degrees per pixel
       dpp=ptu_rate/deriv
       med_dpp=np.nanmedian(dpp)
       
       #just assume 0.6 degrees across entire 1280 pixels
       med_dpp=0.6/1280.0
       
       xpos=data_calib.laser_cen_x.to_frame()*med_dpp
       time=data_calib.time_elapsed.to_frame()/1e3
       
#Use calibration scale to plot jitter analysis
for r in data.keys():     
       if r not in no_data:        
              data[r]['time_laser']=data[r]['laser_data'].time_elapsed.to_frame()/1e3
              #data[r]['time_laser']=data[r]['laser_data'].time_elapsed.values/1e3
              try:
                     data[r]['imu_data']['time']=data[r]['imu_data'].index.to_datetime()-data[r]['imu_data'].index[0]
                     data[r]['imu_data']['time']=data[r]['imu_data']['time'].astype('timedelta64[ms]')/1000.0
                     data[r]['time_imu_sync']=data[r]['imu_data']['time']+2.2
              except:
                     continue
              data[r]['xpos_gopro']=data[r]['laser_data'].laser_cen_x.to_frame()
              
              #Convert GOPRO pixels to degrees ->xpos_deg
              data[r]['xpos_deg']=data[r]['laser_data'].laser_cen_x.to_frame()*med_dpp
              
              #Convert degrees to GLO pixels (1 GLO pixel = 0.0025 degrees)
              glo_dpp=0.53/211   #sun disc 0.53deg per 211 glo pixels
              data[r]['xpos_glo']=data[r]['xpos_deg']/glo_dpp
              
              data[r]['deg_per_sec'] = data[r]['xpos_deg'].diff().values/data[r]['time_laser'].diff().values
              
       #       plt.figure("Raw GLO relative pixel position for ISM errorsjupty")
       #       plt.plot(time,xpos/2.5e-3,marker='.',markersize=1,color='black',
       #                linestyle="None")
       #       plt.xlabel('Time (s)')
       #       plt.ylabel('Pixel')
       #       plt.grid()

              #Gain settings for run
              d48_kp=data[r]['sim_info'].d48_kp[0]
              d48_ks=data[r]['sim_info'].d48_ks[0]
              d48_ka=data[r]['sim_info'].d48_ka[0]
              d48_vd=data[r]['sim_info'].d48_vd[0]
              d48_pd=data[r]['sim_info'].d48_pd[0]
              
              data[r]['std_xpos_120']=data[r]['xpos_glo'].rolling(120,center=True).std()
              #20 frames at 120FPS ~ 1 stacked frame at 6Hz
              data[r]['std_xpos_020']=data[r]['xpos_glo'].rolling(20,center=True).std()
              data[r]['mean_xpos_020']=data[r]['std_xpos_020'].rolling(20,center=True).mean()
              
              plt.figure(figsize=(20,5))
#              plt.plot(data[r]['time_laser'],data[r]['std_xpos_020'],
#                            color='black',
#                            marker='.',
#                            linestyle="None",
#                            label='kp='+str(d48_kp)+' '+
#                                  'ks='+str(d48_ks)+' '+
#                                  'ka='+str(d48_ka)+' '+
#                                  'vd='+str(d48_vd)+' '+
#                                  'pd='+str(d48_pd)+' ')
              
              #Plot converted GLO pixels and subtract mean
              #plt.plot(data[r]['time_laser'],(data[r]['xpos_glo'])-(data[r]['xpos_glo']).mean())
              
              #plt.plot(data[r]['time_laser'],data[r]['deg_per_sec'],color='red')
              try:
                     #plt.plot(data[r]['imu_data'].index,data[r]['imu_data'].ang_z*180.0/np.pi,color='red')
                     plt.plot(data[r]['time_imu_sync'],(data[r]['imu_data'].ang_z*180.0/np.pi).values,'.',color='red')
                     plt.plot(data[r]['time_laser'],data[r]['std_xpos_020'])
                     plt.plot(data[r]['time_laser'],data[r]['xpos_glo'])
                     plt.grid()
                     plt.ylim((0,10))
                     plt.xlabel('Time (s)')
                     plt.ylabel('Sun pixel position FWHM in stacked frame')
                     plt.title("Glo sun position cloud width per stacked frame\n"+date+' '+r)
                     plt.legend()
              except:
                     continue

##calculate the speeds 
#spd=pd.DataFrame(data=xpos.diff().values/time.diff().values)
#
#pix_smear=spd*1e-3/2.5e-3
#
#fig4=plt.figure('GLO pixel smear per 1ms integration period')
#plt.plot(time,pix_smear,marker='.',markersize=1,linestyle="None",color="black")
#
#std_spd_120=pix_smear.rolling(120,center=True).std()
#plt.plot(time,std_spd_120,color='red')
#plt.grid()
#plt.ylim(-1,1)
#plt.xlabel('Time (s)')
#plt.ylabel('Pixels Per Integration Period')
