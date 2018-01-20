# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 16:16:52 2018

@author: addiewan
"""
################################################################################
#mpl.rcParams['legend.fontsize'] = 15
#mpl.rcParams['figure.figsize'] = (10,7.5)
#mpl.rcParams['figure.titlesize']=20
#mpl.rcParams['xtick.labelsize']=15
#mpl.rcParams['ytick.labelsize']=15
#mpl.rcParams['font.size']=15
#mpl.rcParams['axes.titlesize']=15
#mpl.rcParams['axes.labelsize']=15
#mpl.rcParams['lines.markersize'] = 5           # markersize, in points
#mpl.rcParams['legend.markerscale'] = 1     # line width in points
#mpl.rcParams['lines.markeredgewidth'] = 0.2 # the line width around the marker symbol
#mpl.rcParams['lines.linewidth'] = 1.5
#####################################

from scipy.stats import linregress
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta

#file="C:/git_repos/GLO/tracking/sun_sensors/sun_sensor_20180118_run3.csv"
#data = pd.read_csv("C:/git_repos/GLO/tracking/sun_sensors/sun_sensor_20180118_run3.csv",infer_datetime_format=True,index_col='time',parse_dates=['time'])

def linear_fit(x,y,params=False):
    
    from scipy.stats import linregress
    linear_fit = linregress(x, y)
    slope = linear_fit[0]
    yint = linear_fit[1]
    r = linear_fit[2]
    y_fit= x*slope + yint
    
    if params==False:
        return y_fit
    if params==True:
        return {'y_fit':y_fit,
                'slope':slope,
                'yint':yint,
                'r':r}

def poly_fit(x,y,order):
    z = np.polyfit(x, y,order)
    f = np.poly1d(z)
    y_fit = f(x)  
    
    return y_fit

def sensor_stats(file,cols,t_min=None,t_max=None,t_drop_start=None,t_drop_stop=None):
    '''
    inputs:
        file - .csv file location with sun sensor data
        cols - list of columns of data to analyze
        
    output:
        stats: dict containing the following keys:
            slope: value of the slope of the best fit linear line using linear regression
            yint: value of the y-intercept of the best fit linear line using linear regression
            r: r-value of the best fit linear line using linear regression
            utc: timestamp in utc time
            local: timestamp in local time
            raw: raw data values
            fit: corresponding values for the best fit line from linear regression
            off: differce between the linear regression line and raw data
            std: standard deviation of the off values
            mean: mean of the off values
        
    example usage:
        1. get stats for single column:
            file="C:/git_repos/GLO/tracking/sun_sensors/sun_sensor_20180118_run3.csv"
            cols=['angle_y_raw_L']
            stats = sensor_stats(file,cols)
        
        2. get stats for all columns:
            file="C:/git_repos/GLO/tracking/sun_sensors/sun_sensor_20180118_run3.csv"
            cols=list(pd.read_csv(file,infer_datetime_format=True,index_col='time',parse_dates=['time']).columns)
            stats = sensor_stats(file,cols)
            
        3. sun sensor M went out of FOV at 19:03:13 on run3, only use data prior to this time to calculate stats:
            file="C:/git_repos/GLO/tracking/sun_sensors/sun_sensor_20180118_run3.csv"
            cols=['angle_x_raw_M',
                  'angle_y_raw_M',
                  'angle_x_filter_M',
                  'angle_y_filter_M']
            stats = sensor_stats(file,cols,t_max=pd.datetime(2018,1,18,19,3,13))
            
        4. all sensors experience noise between 18:35:47 and 18:35:48 on run2, only use data outside of this window to calculate stats:
            file="C:/git_repos/GLO/tracking/sun_sensors/sun_sensor_20180118_run2.csv"
            cols=['angle_x_raw_M',
                  'angle_y_raw_M',
                  'angle_x_filter_M',
                  'angle_y_filter_M']
            stats = sensor_stats(file,cols,t_drop_start=pd.datetime(2018,1,18,18,34,47),t_drop_stop=pd.datetime(2018,1,18,18,34,48))
            
         
        column choices:     
        ['angle_x_raw_L'
        'angle_x_raw_M',
        'angle_x_raw_R',
        'angle_y_raw_L',
        'angle_y_raw_M',
        'angle_y_raw_R',
        'angle_x_filter_L',
        'angle_x_filter_M',
        'angle_x_filter_R',
        'angle_y_filter_L',
        'angle_y_filter_M',
        'angle_y_filter_R',
        'radiation_L'
        'radiation_M',
        'radiation_R',
        'temp_L',
        'temp_M',
        'temp_R']
    '''
    data = pd.read_csv(file,infer_datetime_format=True,index_col='time',parse_dates=['time'])
    if t_min != None:
        mask=data.index > t_min
        data = data.loc[mask]
    if t_max != None:
        mask=data.index < t_max
        data = data.loc[mask]
    if t_drop_start !=None:
        mask =(data.index < t_drop_start) | (data.index > t_drop_stop)
        data = data.loc[mask]
    stats={}    
    x = np.arange(0,len(data.index))
    for col in cols:
        stats[col]={}
        y=data[col]
        #linear_fit = linregress(xdata, ydata)
        line_fit = linear_fit(x,y,params=True)
        poly_fit_1 = poly_fit(x,y,1)
        poly_fit_2 = poly_fit(x,y,2)
        poly_fit_3 = poly_fit(x,y,3)
        poly_fit_4 = poly_fit(x,y,4)
        poly_fit_10 = poly_fit(x,y,10)
        stats[col]['utc']=data.index
        stats[col]['local']=data.index- timedelta(hours=5)
        stats[col]['slope'] = line_fit['slope']
        stats[col]['yint'] = line_fit['yint']
        stats[col]['r'] = line_fit['r']
        stats[col]['raw']=data[col]
        stats[col]['linear']=x*stats[col]['slope']+ stats[col]['yint']
        stats[col]['fit']=pd.DataFrame({'utc':stats[col]['utc'],
                                         'line_fit':stats[col]['linear'],
                                         'polyfit_01':poly_fit_1,
                                         'polyfit_02':poly_fit_2,
                                         'polyfit_03':poly_fit_3,
                                         'polyfit_04':poly_fit_4,
                                         'polyfit_10':poly_fit_10})
        stats[col]['fit'] = stats[col]['fit'].set_index('utc')
        stats[col]['off']=stats[col]['fit'].line_fit.subtract(data[col],axis=0)
        stats[col]['std']=stats[col]['off'].std()
        stats[col]['mean']=stats[col]['off'].mean()
    #stats['angle_raw_total_L'] = np.sqrt(stats['angle_x_raw_L']['raw']**2 + stats['angle_y_raw_L']['raw']**2)
    #stats['angle_raw_total_M'] = np.sqrt(stats['angle_x_raw_M']['raw']**2 + stats['angle_y_raw_M']['raw']**2)
    #stats['angle_raw_total_R'] = np.sqrt(stats['angle_x_raw_R']['raw']**2 + stats['angle_y_raw_R']['raw']**2)
    return stats




#plt.plot(fit)
#plt.plot(xdata,data[column],'o')
    
#fitting = pd.DataFrame({'raw':stats['angle_x_raw_L']['raw'],
#                        'linear':ynew1,
#                        'poly_1':ynew1
#                        'poly_2':ynew1
#                        'poly_3':ynew1
#                        'poly_4':ynew1
#})