#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 08:42:24 2018

@author: carstens
"""
#from scipy import misc
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os,errno
#from PIL import Image


vid_name1='GOPR0279'
vid_name2='GOPR0280'
vid_dir='/tesla/data/ISM_VIDEO/'
imgfolder=vid_dir+'ISM_v_MANUAL/'

try:
    os.makedirs(imgfolder)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

it0=int(8.5*120)
itn=int((8.5+30)*120)
i=it0
for i in range(it0,itn):
    frame_str=str(i).rjust(5,'0')
    ifile=vid_dir+vid_name1+'/'+vid_name1+'_'+frame_str+'.png'
    img1=cv2.imread(ifile)
    img1=img1[200:500,0:800,:]
    #img_plt=img1[...,::-1]
    #plt.imshow(img_plt)
    
    ifile=vid_dir+vid_name2+'/'+vid_name2+'_'+frame_str+'.png'
    img2=cv2.imread(ifile)
    img2=img2[200:500,0:800,:]
    
    img=np.concatenate((img1,img2))

    cv2.imwrite(imgfolder+'img_'+frame_str+'.png',img)