#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 14:14:31 2018

@author: carstens
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
#from mpl_toolkits.mplot3d import Axes3D


def fit_second_order_surface(tX,tY,tZ):  
    """"Given XYZ arrays, compute best fit 2nd order surface """
    X = tX.flatten()
    Y = tY.flatten()
    B = tZ.flatten()
    
    good=np.logical_and(np.isfinite(X),np.isfinite(Y))
    
    X=X[good]
    Y=Y[good]
    B=B[good]
    
    A = np.array([X*0+1, X, Y, X**2, X**2*Y, X**2*Y**2, Y**2, X*Y**2, X*Y]).T


    coeff, r, rank, s = np.linalg.lstsq(A, B)
    
    return coeff

def evaluate_surface(b,X,Y):
    """Given coefficients evaluate second order surface at XY grid points"""

    Z=(b[0]+
       X*b[1]+
       Y*b[2]+
       X**2*b[3]+
       X**2*Y*b[4]+
       X**2*Y**2*b[5]+
       Y**2*b[6]+
       X*Y**2*b[7]+
       X*Y*b[8])
    
    return Z

def evaluate_coordinates(b,X,Y):
    x_ang=evaluate_surface(b['bx'],X,Y)
    y_ang=evaluate_surface(b['by'],X,Y)
    
    return (x_ang,y_ang)
    
    
    

def calibrate_video_coordinates(vid_name='GOPR0276',
                                vid_dir='/tesla/data/ISM_VIDEO/',
                                do_plot=False):

    #restore the digitized CSV of the video
    data=pd.read_csv(vid_dir+vid_name+'.csv')
    
    #time array
    time=data.time_elapsed.values/1e3
    
    #extract the x and y pixel positions
    x_pix=data.laser_cen_x.to_frame()
    y_pix=data.laser_cen_y.to_frame()
    
    dif_x_pos=x_pix.diff().values.flatten()
    #dif_x_pos=dif_x_pos.values
    
    #find the first instance of a difference greater than 10 and call that the 
    #start time of the calibration
    tmove=time[dif_x_pos > 10]
    t0=tmove[0]-1
    
    #index of calibration start
    it0=(np.where(time > t0)[0])[0]
    
    #crop such t>t0 is kept
    time=time[it0:]-t0
    x_pix=(x_pix[it0:])
    y_pix=(y_pix[it0:])
    
    #smooth over half second windows (=-30 frames)
    x_pix_smooth=x_pix.rolling(60,center=True).median()
    y_pix_smooth=y_pix.rolling(60,center=True).median()
    
    #stable time indexs 70 frames following
    its=70+np.arange(150)*120
    
    #sample at its
    times=time[its]
    x_pixs=x_pix_smooth.values[its]
    y_pixs=y_pix_smooth.values[its]
    
    if do_plot:
        plt.figure(1,clear=True)
        plt.plot(time,x_pix)
        plt.plot(times,x_pixs,'x',color='red')
        plt.plot(time,y_pix)
        plt.plot(times,y_pixs,'x',color='red')
    
    #PTU resolution rate in degrees per microstep
    ptu_res=23.14285/60/60
    
    x_ang=(np.arange(150) % 15)*ptu_res*8
    y_ang=(np.arange(150)//15)*ptu_res*8
    
    # shape into 2d arrays
    x_pixs.shape=(10,15)
    y_pixs.shape=(10,15)
    x_ang.shape=(10,15)
    y_ang.shape=(10,15)
      
    
    plt.plot(x_ang,x_pixs,'x',color='red')
    plt.plot(y_ang,y_pixs,'x',color='blue')
    
    
    
    #ax2 = fig.gca(projection='3d')
    #surf = ax2.plot_surface(x_pixs, y_pixs, y_ang, cmap=cm.coolwarm,
    #                       linewidth=0, antialiased=False)
    
    #find the best fit quadratic surfaces
    bx=fit_second_order_surface(x_pixs,y_pixs,x_ang)    
    by=fit_second_order_surface(x_pixs,y_pixs,y_ang)    
    
    # Plot the surface.
    if do_plot:
        fx_ang=evaluate_surface(bx,x_pixs,y_pixs)
        fy_ang=evaluate_surface(by,x_pixs,y_pixs)
        
        fig1 = plt.figure("Raw Positions",clear=True)
        ax1 = fig1.gca(projection='3d')
        surf = ax1.plot_surface(x_pixs, y_pixs, x_ang, cmap=cm.rainbow,
                               linewidth=0, antialiased=False)
        surf = ax1.plot_surface(x_pixs, y_pixs, fx_ang, cmap=cm.coolwarm,
                               linewidth=0, antialiased=False)
        surf = ax1.plot_surface(x_pixs, y_pixs, y_ang, cmap=cm.rainbow,
                               linewidth=0, antialiased=False)
        surf = ax1.plot_surface(x_pixs, y_pixs, fy_ang, cmap=cm.coolwarm,
                               linewidth=0, antialiased=False)
        
        
        fig2 = plt.figure("Difference Positions",clear=True)
        ax2 = fig2.gca(projection='3d')
        surf = ax2.plot_surface(x_pixs, y_pixs, fx_ang-x_ang, cmap=cm.rainbow,
                               linewidth=0, antialiased=False)
        surf = ax2.plot_surface(x_pixs, y_pixs, fy_ang-y_ang, cmap=cm.coolwarm,
                               linewidth=0, antialiased=False)

    return {'bx':bx,'by':by}