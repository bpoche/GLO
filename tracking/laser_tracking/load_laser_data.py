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
import os

def load_data(date='20180323',runs='all'):

    #Load Data
    cwd = os.getcwd()
    run_dir = cwd+'/'+date+'/'
    data={}
    if runs == 'all':
           dirs = glob(run_dir+'run*')
    else:
           dirs = glob(run_dir+runs)
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
            #print('cannot find imu data for run_'+str(run_num)+' on '+date)
            continue
        data['run_'+str(run_num)]['sim_info']=sim_info
        data['run_'+str(run_num)]['cmd_list']=cmd_list
        vid_file=data['run_'+str(run_num)]['sim_info'].filename[0].split('100GOPRO/')[-1]
        vid_num=data['run_'+str(run_num)]['sim_info'].filename[0].split('100GOPRO/')[-1].split('.MP4')[0]
        try:
            data['run_'+str(run_num)]['laser_data']=pd.read_csv(run_dir+vid_num+'.csv',parse_dates=True,infer_datetime_format=True)
        except:
            #print('cannot find '+vid_num+'.csv for run_'+str(run_num)+' on '+date)
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

        xpos=data_calib.laser_cen_x.to_frame()*med_dpp
        time=data_calib.time_elapsed.to_frame()/1e3

    for r in sorted(data):     
        if r not in no_data: 
            
            #just assume 0.6 degrees across entire 1280 pixels
            med_dpp=0.6/1280.0
            
            #Set delays between gopro, imu, and ptu
            #Gopro starts first, so define delays for imu data and ptu commands to start
            delay_imu=2.2
            delay_ptu=5.62
            
            try:
                #Extract time_laser and time_imu_sync to plot laser and imu data together
                data[r]['time_laser']=data[r]['laser_data'].time_elapsed.to_frame()/1e3
                data[r]['imu_data']['time']=data[r]['imu_data'].index.to_datetime()-data[r]['imu_data'].index[0]
                data[r]['imu_data']['time']=data[r]['imu_data']['time'].astype('timedelta64[ms]')/1000.0
                #Add in delay for imu_data recording ~2.2seconds
                data[r]['time_imu_sync']=data[r]['imu_data']['time']+2.2   

                #Laser data in gopro pixels
                data[r]['xpos_gopro']=data[r]['laser_data'].laser_cen_x.to_frame()

                #Convert GOPRO pixels to degrees ->xpos_deg
                data[r]['xpos_deg']=data[r]['laser_data'].laser_cen_x.to_frame()*med_dpp

                #Convert degrees to GLO pixels (1 GLO pixel = 0.0025 degrees)
                glo_dpp=0.53/211   #sun disc 0.53deg per 211 glo pixels
                data[r]['xpos_glo']=data[r]['xpos_deg']/glo_dpp

                #Laser data in degrees/second
                data[r]['deg_per_sec'] = data[r]['xpos_deg'].diff().values/data[r]['time_laser'].diff().values

                data[r]['std_xpos_120']=data[r]['xpos_glo'].rolling(120,center=True).std()
                #20 frames at 120FPS ~ 1 stacked frame at 6Hz
                data[r]['std_xpos_020']=data[r]['xpos_glo'].rolling(20,center=True).std()
                
                data[r]['pix_smear']=data[r]['xpos_glo'].diff().values/data[r]['time_laser'].diff().values/1e3
                data[r]['pix_smear_120']=pd.DataFrame(data[r]['pix_smear']).rolling(120,center=True).std()

                #Combine laser data and imu data into single dataframe
                data[r]['imu_laser']=pd.DataFrame(index=data[r]['imu_data'].index[0]+
                                                        pd.to_timedelta(data[r]['laser_data']['time_elapsed'].values,'ms')+
                                                        pd.to_timedelta(-delay_imu,'s'))
                data[r]['imu_laser']['xpos_gopro']=data[r]['laser_data'].laser_cen_x.values
                data[r]['imu_laser']['ypos_gopro']=data[r]['laser_data'].laser_cen_y.values
                data[r]['imu_laser']['xpos_deg']=data[r]['laser_data'].laser_cen_x.values*med_dpp
                data[r]['imu_laser']['ypos_deg']=data[r]['laser_data'].laser_cen_y.values*med_dpp
                data[r]['imu_laser']['xpos_glo']=data[r]['imu_laser']['xpos_deg']/glo_dpp
                data[r]['imu_laser']['ypos_glo']=data[r]['imu_laser']['ypos_deg']/glo_dpp
                data[r]['imu_laser']['time_elapsed']=data[r]['laser_data']['time_elapsed'].values
                #Resample laser data and IMU data onto evenly spaced (120 FPS ~ 8.333ms) time intervals
                data[r]['imu_laser']=pd.concat([data[r]['imu_laser'].resample('8333us').fillna(method = 'ffill'),
                                                data[r]['imu_data'].resample('8333us').fillna(method = 'ffill')],
                                                 axis=1)
                #Use z-axis angular rate as approximation for base speed (IMU was not exactly centered on z-axis)
                data[r]['imu_laser']['base_spd']=data[r]['imu_laser']['ang_z']*180.0/np.pi
                
                #Bin IMU data into speed bins
                ds=0.1
                max_spd=2.0
                speeds=np.linspace(0,max_spd,np.int(np.ceil(max_spd/ds))+1)
                data[r]['speed_bins']={}
                data[r]['speed_bins']['speeds']=np.linspace(0,max_spd,np.int(np.ceil(max_spd/ds))+1)
                data[r]['speed_bins']['std']=np.zeros(len(speeds))
                data[r]['speed_bins']['std']=[]
                for i in range(len(speeds)-1):
                       data[r]['speed_bins']['mask_'+str(i)] = (data[r]['imu_laser']['base_spd'] > speeds[i]) & ((data[r]['imu_laser']['base_spd'] <= speeds[i+1]))
                       data[r]['speed_bins']['std'].append(data[r]['imu_laser'].loc[data[r]['speed_bins']['mask_'+str(i)],'xpos_glo'].std())
                       
            except:
                print('could not extract data '+date +' '+ r)
                continue
    return data

if __name__ == '__main__':
       #Pick date to plot
       date='20180322'
       runs='all'
       data = load_data(date=date,runs=runs)
       
       delay_cmd_list=5.62
       delay_imu_data=2.2
       
       #Select which plots to show
       plot_stacked_cloud = False
       plot_glo_pixel_centered = False
       plot_imu_deg_per_sec = False
       plot_pixel_smear = False
       plot_binned_imu_chair = False
       plot_base_speed_chair_test = False
       plot_laser_imu_speed_bin = True
       
       #Plot sun position cloud per stacked frame
       if plot_stacked_cloud == True:          
              for r in sorted(data):
                  try:   
                      plt.figure(figsize=(20,5))
                      plt.plot(data[r]['time_laser'],
                               3*data[r]['std_xpos_020'],
                               color='black',
                               marker='.',
                               linestyle="None",
                               label='kp='+str(data[r]['sim_info'].d48_kp[0])+' '+
                                     'ks='+str(data[r]['sim_info'].d48_ks[0])+' '+
                                     'ka='+str(data[r]['sim_info'].d48_ka[0])+' '+
                                     'vd='+str(data[r]['sim_info'].d48_vd[0])+' '+
                                     'pd='+str(data[r]['sim_info'].d48_pd[0])+' ')
                      plt.ylabel('Sun pixel position FWHM in stacked frame')
                      plt.xlabel('Time Elasped (seconds)')
                      plt.title("Glo sun position cloud width per stacked frame\n"+date+' '+r)
                      plt.legend(loc='upper left')
                      plt.ylim((0,30))
                      for i in range(len(data[r]['cmd_list'].index)):
                             plt.axvline(x=data[r]['cmd_list']['delay'][i]+delay_cmd_list,color='red')
                  except:
                      continue
       
       #Plot GLO pixels centered on mean       
       if plot_glo_pixel_centered == True:
              for r in sorted(data):
                  try:   
                      #Plot converted GLO pixels and subtract mean
                      plt.figure(figsize=(20,5))
                      plt.plot(data[r]['time_laser'],
                              (data[r]['xpos_glo'])-(data[r]['xpos_glo']).mean(),
                               label='kp='+str(data[r]['sim_info'].d48_kp[0])+' '+
                                     'ks='+str(data[r]['sim_info'].d48_ks[0])+' '+
                                     'ka='+str(data[r]['sim_info'].d48_ka[0])+' '+
                                     'vd='+str(data[r]['sim_info'].d48_vd[0])+' '+
                                     'pd='+str(data[r]['sim_info'].d48_pd[0])+' ')
                      plt.legend(loc='upper left')
                  except:
                      continue
               
       #Plot GLO pixels centered on mean       
       if plot_imu_deg_per_sec == True:
              for r in sorted(data):
                  plt.figure(figsize=(20,5))
                  try:
                       #plt.plot(data[r]['imu_data'].index,data[r]['imu_data'].ang_z*180.0/np.pi,color='red')
                       plt.plot(data[r]['time_imu_sync'],(data[r]['imu_data'].ang_z*180.0/np.pi).values,'.',color='red',label='IMU deg/sec')
                       plt.plot(data[r]['time_laser'],data[r]['std_xpos_020'],'.',label='GLO pixel stacked cloud')
                       plt.grid()
                       plt.ylim((-2,10))
                       plt.xlabel('Time (s)')
                       plt.ylabel('Sun pixel position FWHM in stacked frame')
                       plt.title("Glo sun position cloud width per stacked frame\n"+date+' '+r)
                       plt.legend()
                  except:
                       continue

       #Plot pixel smear per integration period      
       if plot_pixel_smear == True:
              for r in sorted(data):
                  try:   
                      #Plot converted GLO pixels and subtract mean
                      fig4=plt.figure('GLO pixel smear per 1ms integration period '+r,figsize=(20,5))
                      plt.plot(data[r]['time_laser'],
                               data[r]['pix_smear'],
                               '.',
                               color='black',
                               label=r+' '+
                                     'kp='+str(data[r]['sim_info'].d48_kp[0])+' '+
                                     'ks='+str(data[r]['sim_info'].d48_ks[0])+' '+
                                     'ka='+str(data[r]['sim_info'].d48_ka[0])+' '+
                                     'vd='+str(data[r]['sim_info'].d48_vd[0])+' '+
                                     'pd='+str(data[r]['sim_info'].d48_pd[0])+' ')
                      plt.plot(data[r]['time_laser'],
                               data[r]['pix_smear_120'],
                               color='red')
                      plt.legend(loc='upper left')
                  except:
                      continue
               
       #Plot pixel cloud for binned imu speed values when ptu stack was mounted on chair      
       if plot_binned_imu_chair == True:
              for r in sorted(data):
                  data[r]['imu_data']['pan_dps']=data[r]['imu_data']['ang_z']*180.0/np.pi
                  ds=0.1
                  max_spd=2.0
                  speeds=np.linspace(0,max_spd,np.int(np.ceil(max_spd/ds))+1)
                  speed_bins={}
                  speed_bins['speeds']=np.linspace(0,max_spd,np.int(np.ceil(max_spd/ds))+1)
                  speed_bins['std']=np.zeros(len(speeds))
                  speed_bins['std']=[]
                  for i in range(len(speeds)-1):
                         speed_bins['mask_'+str(i)] = (data[r]['imu_laser']['base_spd'] > speeds[i]) & ((data[r]['imu_laser']['base_spd'] <= speeds[i+1]))
                         speed_bins['std'].append(data[r]['imu_laser'].loc[speed_bins['mask_'+str(i)],'xpos_glo'].std())
                         #speed_bins['count'].append(data[r]['imu_data'].loc[speed_bins['mask_'+str(i)],'pan_dps'].count())
                         #speed_bins['std'][i+1]=data[r]['imu_data']['pan_dps'].loc(speed_bins['mask_'+str(i)],'pan_dps').std()

                  try:   
                      #Plot converted GLO pixels and subtract mean
                      fig4=plt.figure('IMU data binned '+r,figsize=(20,5))
                      plt.plot(data[r]['time_laser'],
                               data[r]['pix_smear'],
                               '.',
                               color='black',
                               label=r+' '+
                                     'kp='+str(data[r]['sim_info'].d48_kp[0])+' '+
                                     'ks='+str(data[r]['sim_info'].d48_ks[0])+' '+
                                     'ka='+str(data[r]['sim_info'].d48_ka[0])+' '+
                                     'vd='+str(data[r]['sim_info'].d48_vd[0])+' '+
                                     'pd='+str(data[r]['sim_info'].d48_pd[0])+' ')
                      plt.plot(data[r]['time_laser'],
                               data[r]['pix_smear_120'],
                               color='red')
                      plt.legend(loc='upper left')
                  except:
                      continue
       
       if plot_base_speed_chair_test == True:        
              for r in sorted(data):
                  try:   
                      #Plot base speed (deg/sec) from chair test
                      plt.figure('Base Unit Speed (imu 10hz data upsampled to 120hz timescale)',figsize=(20,5))
                      plt.plot(data[r]['imu_laser']['base_unit_speed'],
                               label='kp='+str(data[r]['sim_info'].d48_kp[0])+' '+
                                     'ks='+str(data[r]['sim_info'].d48_ks[0])+' '+
                                     'ka='+str(data[r]['sim_info'].d48_ka[0])+' '+
                                     'vd='+str(data[r]['sim_info'].d48_vd[0])+' '+
                                     'pd='+str(data[r]['sim_info'].d48_pd[0])+' ')
                      plt.legend(loc='upper left')
                      plt.xlabel('Time')
                      plt.ylabel('Base Unit Speed (deg/sec)')
                  except:
                      continue
               
       if plot_laser_imu_speed_bin == True:            
              for r in sorted(data):
                  try:   
                      #Plot base speed (deg/sec) from chair test
                      #plt.figure('Base Unit Speed (imu 10hz data upsampled to 120hz timescale)',figsize=(20,5))
                      plt.figure(figsize=(20,5))
                      plt.plot(data[r]['imu_laser'].loc[data[r]['speed_bins']['mask_1'],'time_elapsed']/1.0e3,
                               data[r]['imu_laser'].loc[data[r]['speed_bins']['mask_1'],'xpos_glo'],
                               '.',
                               label='kp='+str(data[r]['sim_info'].d48_kp[0])+' '+
                                     'ks='+str(data[r]['sim_info'].d48_ks[0])+' '+
                                     'ka='+str(data[r]['sim_info'].d48_ka[0])+' '+
                                     'vd='+str(data[r]['sim_info'].d48_vd[0])+' '+
                                     'pd='+str(data[r]['sim_info'].d48_pd[0])+' ')
                      plt.legend(loc='upper left')
                      plt.xlabel('Time')
                      plt.ylabel('GLO pixel equivalent')
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
