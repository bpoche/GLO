#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 11:04:13 2018

@author: carstens
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


#Determine the scale by looking at the slope of the 1 pos/sec video
vid_name='GOPR0123'
vid_dir='/tesla/data/ISM_VIDEO/'

data=pd.read_csv(vid_dir+vid_name+'.csv')

time=data.time_elapsed.to_frame()/1e3

#1 second smooth to remove stair step
rm=data.laser_cen_x.to_frame().rolling(120,center=True).mean()

#plt.figure(1)
#plt.plot(time,data.laser_cen_x,'x',color='black')
#plt.plot(time,rm,'-+',color='blue')

dif_pos=rm.diff().values
dif_time=time.diff().values

#angular rate in GOPRO pixels per second
deriv=dif_pos/(dif_time)

#PTU angular rate in degrees per second
ptu_rate=-92.0/60/60/4

#degrees per pixel
dpp=ptu_rate/deriv
med_dpp=np.nanmedian(dpp)

xpos=data.laser_cen_x.to_frame()*med_dpp
time=data.time_elapsed.to_frame()/1e3

plt.figure(1,clear=True)
plt.plot(time,xpos)
#plt.figure(2)
#plt.plot(time,dpp,color='blue')
#plt.plot([0,80],[med_dpp,med_dpp],color='red')

#open another video to analyze using the scale above
vid_name='GOPR0117'
vid_dir='/tesla/data/ISM_VIDEO/'

data=pd.read_csv(vid_dir+vid_name+'.csv')

xpos=data.laser_cen_x.to_frame()*med_dpp
time=data.time_elapsed.to_frame()/1e3

plt.figure("Raw GLO relative pixel position for ISM errors",clear=True,)
plt.plot(time,xpos/2.5e-3,marker='.',markersize=1,color='black',
         linestyle="None")
plt.xlabel('Time (s)')
plt.ylabel('Pixel')
plt.grid()

std_xpos_120=xpos.rolling(120,center=True).std()
std_xpos_020=xpos.rolling(20,center=True).std()

fig3=plt.figure("Glo sun position cloud width per stacked frame",clear=True)
#plt3=plt.plot(time,std_xpos_120,color='black')
plt3=plt.plot(time,std_xpos_020*2e0/2.5e-3,color='black',marker='.',
              markersize=1,linestyle="None")
plt.grid()
#plt.ylim(-1,1)
plt.xlabel('Time (s)')
plt.ylabel('Sun pixel position FWHM in stacked frame')


#calculate the speeds 
spd=pd.DataFrame(data=xpos.diff().values/time.diff().values)

pix_smear=spd*1e-3/2.5e-3

fig4=plt.figure('GLO pixel smear per 1ms integration period',clear=True)
plt.plot(time,pix_smear,marker='.',markersize=1,linestyle="None",color="black")

std_spd_120=pix_smear.rolling(120,center=True).std()
plt.plot(time,std_spd_120,color='red')
plt.grid()
plt.ylim(-1,1)
plt.xlabel('Time (s)')
plt.ylabel('Pixels Per Integration Period')
