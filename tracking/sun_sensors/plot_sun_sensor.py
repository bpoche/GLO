# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 17:14:33 2018

@author: GLOtastic
"""

from calc_sun_sensor_stats import sensor_stats
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

################################################################################
mpl.rcParams['legend.fontsize'] = 15
mpl.rcParams['figure.figsize'] = (10,7.5)
mpl.rcParams['figure.titlesize']=20
mpl.rcParams['xtick.labelsize']=15
mpl.rcParams['ytick.labelsize']=15
mpl.rcParams['font.size']=15
mpl.rcParams['axes.titlesize']=15
mpl.rcParams['axes.labelsize']=15
mpl.rcParams['lines.markersize'] = 4           # markersize, in points
mpl.rcParams['legend.markerscale'] = 3     # line width in points
mpl.rcParams['lines.markeredgewidth'] = 0.2 # the line width around the marker symbol
mpl.rcParams['lines.linewidth'] = 1.5
#####################################

def plot_sun_sensor(files=['Q:/git_repos/GLO/tracking/data/20180123/sun_sensor_31.csv'],
                    cols=['angle_x_raw_R','angle_y_raw_R'],
                    date=None,
                    stats_out=False,
                    plot_best_fit=False,
                    fit_type=None):
    '''
    Quick way to plot sun sensor data
    
    Inputs:
        files: list of .csv files created after running sun_sensor_capture.py
        cols: list of columns to plot (defaults to ['angle_x_raw_R','angle_y_raw_R'])
        date: date string to use as a date in the plot title (date='2018 01-13-18')
        stats_out: set to True to output the stats in a dataframe
        plot_best_fit: set to True to plot best fit line for each column
        fit_type: specify which type of line to fit ('line_fit','polyfit_02','polyfit_03' etc)
        
    Outputs:
        stats_out: optional output - dataframe of stats for all columns
        
    Example Usage:
        1) simple plot for a single file:
        
            files=['Q:/git_repos/GLO/tracking/data/20180123/sun_sensor_31.csv']
            cols=    cols=['angle_x_raw_R',
                           'angle_y_raw_R']
            stats = plot_sun_sensor(files=files,
                            cols=cols,
                            date='2018 01-13-18',
                            stats_out=True,
                            plot_best_fit=True,
                            fit_type='line_fit')
    '''
    for i in range(len(files)):
        stats = sensor_stats(files[i],cols)
        for key in list(stats.keys()):
            plt.plot(list(stats[key]['utc'].to_pydatetime()),stats[key]['raw'],'o',label=key+' std='+str(round(stats[key]['std'],4)))
            plt.ylabel('Degrees')
            plt.gcf().autofmt_xdate()
            if date != None:
                plt.title(date+' Sensor raw data run'+str(i+1))
            else:
                plt.title('Sensor raw data run'+str(i+1))
            plt.legend()
            plt.grid()
            plt.show()
            
            if plot_best_fit==True:
                plt.plot(stats[key]['fit'][fit_type])
    if stats_out == True:
        for key in stats:
            print('RUN '+str(i+1))
            print('std of different fitted curves for '+key)
            print(stats[key]['fit'].subtract(stats[key]['raw'],axis=0).std())
            print('')
        return stats
            #legend(loc='upper left', bbox_to_anchor=(1, 1))