#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 11:04:13 2018

@author: carstens
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdb

calib_video="C:/git_repos/GLO/tracking/ptu_simulations/data/20180321/GOPR0312.csv"
data_video="C:/git_repos/GLO/tracking/ptu_simulations/data/20180321/GOPR0314.csv"

calib_video='/media/ramble/C61836BD1836AC75/laser_tracking/20180323/GOPR0342.csv'
data_video='/media/ramble/C61836BD1836AC75/laser_tracking/20180323/GOPR0337.csv'
#def tracker_analysis(calib_video,data_video):

<<<<<<< HEAD:tracking/laser_tracking/tracker_analysis.py
b=calibrate_video_coordinates(vid_name='GOPR0276')


=======
#Determine the scale by looking at the slope of the 1 pos/sec video
#vid_name='GOPR0123'
#vid_dir='/tesla/data/ISM_VIDEO/'


#data=pd.read_csv(vid_dir+vid_name+'.csv')
data_calib=pd.read_csv(calib_video)

time=data_calib.time_elapsed.to_frame()/1e3

#1 second smooth to remove stair step
rm=data_calib.laser_cen_x.to_frame().rolling(120,center=True).mean()
>>>>>>> 7c849bb5e8a6a7aa1979bf8c62e547696836f284:tracking/laser_tracking/old/tracker_analysis.py

#open another video to analyze using the scale above
vid_name='GOPR0279'
vid_dir='/tesla/data/ISM_VIDEO/'

clear_val=False
color1='black'
color2='red'

#approximate timing of simulation start
t0=8.5 

#plotting limits
ylim_raw=(0,200)
xlim=(0,35)

ylim_stack=(0,15)
ylim_int=(-1,1)

<<<<<<< HEAD:tracking/laser_tracking/tracker_analysis.py
data=pd.read_csv(vid_dir+vid_name+'.csv')

#get pixel values of laser dot
xpix=data.laser_cen_x.values
ypix=data.laser_cen_y.values

#convert to angles using calibration map
x_ang, y_ang = evaluate_coordinates(b,xpix,ypix)

xpos=pd.DataFrame(x_ang)
ypos=pd.DataFrame(y_ang)
=======
xpos=data_calib.laser_cen_x.to_frame()*med_dpp
time=data_calib.time_elapsed.to_frame()/1e3

plt.figure(1)
plt.plot(time,xpos)
#plt.figure(2)
#plt.plot(time,dpp,color='blue')
#plt.plot([0,80],[med_dpp,med_dpp],color='red')

#open another video to analyze using the scale above
#vid_name='GOPR0117'
#vid_dir='/tesla/data/ISM_VIDEO/'

#data=pd.read_csv(vid_dir+vid_name+'.csv')
data=pd.read_csv(data_video)
>>>>>>> 7c849bb5e8a6a7aa1979bf8c62e547696836f284:tracking/laser_tracking/old/tracker_analysis.py

time=data.time_elapsed.to_frame()/1e3-t0

<<<<<<< HEAD:tracking/laser_tracking/tracker_analysis.py
raw_fig=plt.figure("Raw GLO relative pixel position for ISM errors",clear=clear_val)
plt.plot(time,xpos/2.5e-3,marker='.',markersize=1,color=color1,
=======
plt.figure("Raw GLO relative pixel position for ISM errors")
plt.plot(time,xpos/2.5e-3,marker='.',markersize=1,color='black',
>>>>>>> 7c849bb5e8a6a7aa1979bf8c62e547696836f284:tracking/laser_tracking/old/tracker_analysis.py
         linestyle="None")
#plt.plot(time,ypos/2.5e-3,marker='.',markersize=1,color=color2,
#         linestyle="None")
plt.xlabel('Time (s)')
plt.ylabel('Pixel')
plt.grid(True)
plt.xlim(xlim)
plt.ylim(ylim_raw)
raw_fig.savefig('raw_pixel_pos_comparison.png')

std_xpos_120=xpos.rolling(120,center=True).std()
std_xpos_020=xpos.rolling(20,center=True).std()

<<<<<<< HEAD:tracking/laser_tracking/tracker_analysis.py
stack_fig=plt.figure("Glo sun position cloud width per stacked frame",clear=clear_val)
=======
fig3=plt.figure("Glo sun position cloud width per stacked frame")
>>>>>>> 7c849bb5e8a6a7aa1979bf8c62e547696836f284:tracking/laser_tracking/old/tracker_analysis.py
#plt3=plt.plot(time,std_xpos_120,color='black')
plt3=plt.plot(time,std_xpos_020*2e0/2.5e-3,color=color1,marker='.',
              markersize=1,linestyle="None")
plt.grid(True)
plt.xlabel('Time (s)')
plt.ylabel('Sun pixel position FWHM in stacked frame')
plt.xlim(xlim)
plt.ylim(ylim_stack)
stack_fig.savefig('stack_variance_comparison.png')


#calculate the speeds 
spd=pd.DataFrame(data=xpos.diff().values/time.diff().values)

pix_smear=spd*1e-3/2.5e-3

<<<<<<< HEAD:tracking/laser_tracking/tracker_analysis.py
int_fig=plt.figure('GLO pixel smear per 1ms integration period',clear=clear_val)
plt.plot(time,pix_smear,marker='.',markersize=1,linestyle="None",color=color1)
=======
fig4=plt.figure('GLO pixel smear per 1ms integration period')
plt.plot(time,pix_smear,marker='.',markersize=1,linestyle="None",color="black")
>>>>>>> 7c849bb5e8a6a7aa1979bf8c62e547696836f284:tracking/laser_tracking/old/tracker_analysis.py

std_spd_120=pix_smear.rolling(120,center=True).std()
plt.plot(time,std_spd_120,color=color2)
plt.grid(True)
plt.ylim(ylim_int)
plt.xlim(xlim)
plt.xlabel('Time (s)')
plt.ylabel('Pixels Per Integration Period')
int_fig.savefig('single_integration_smear_comparison.png')



