# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 22:14:08 2018

@author: addiewan
"""

# -*- coding: utf-8 -*-
"""
Various methods of drawing scrolling plots.
"""
import os
os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

from glob import glob
import pandas as pd
from natsort import natsorted

files = glob("C:/git_repos/GLO/tracking/data/20180129/run**/*.csv")
files = natsorted(files)
data = pd.read_csv(files[0],infer_datetime_format=True,index_col='time',parse_dates=['time'])
if len(files) > 1:
    for file in files[1:]:
        data = data.append(pd.read_csv(file,infer_datetime_format=True,index_col='time',parse_dates=['time']))
data['seconds'] = data.index.to_datetime() - data.index[0]
data.seconds = data.seconds.astype('timedelta64[ms]').divide(1000.0)

win = pg.GraphicsWindow()
win.setWindowTitle('pyqtgraph example: Scrolling Plots')


startTime = pg.ptime.time()

#Set up live plotting
win.nextRow()
p1 = win.addPlot()
win.nextRow()
p2 = win.addPlot()
win.nextRow()
p3 = win.addPlot()


p1.setLabel('top', 'X-axis offset')
p1.setLabel('bottom', 'Time', 's')
p1.setLabel('left', 'Degrees')
#p1.setDownsampling(mode='peak')
p1.setClipToView(True)
p1.setRange(xRange=[-20, 0])
p1.addLegend()

p2.setLabel('top', 'X-axis offset')
p2.setLabel('bottom', 'Time', 's')
p2.setLabel('left', 'Degrees')
#p2.setDownsampling(mode='peak')
p2.setClipToView(True)
p2.setRange(xRange=[-20, 0])
p2.addLegend()

p3.setLabel('top', 'Solar Intensity')
p3.setLabel('bottom', 'Time', 's')
p3.setLabel('left', 'Watts/m^2')
#p3.setDownsampling(mode='peak')
p3.setClipToView(True)
p3.setRange(xRange=[-20, 0])
p3.addLegend()


curve1 = p1.plot(pen="r",name='sesnor_R')
curve2 = p1.plot(pen="g",name='sesnor_M')
curve3 = p1.plot(pen="b",name='sesnor_L')
ptr1=0

curve4 = p2.plot(pen="r",name='sesnor_R')
curve5 = p2.plot(pen="g",name='sesnor_M')
curve6 = p2.plot(pen="b",name='sesnor_L')
ptr2=0

curve7 = p3.plot(pen="r",name='sesnor_R')
curve8 = p3.plot(pen="g",name='sesnor_M')
curve9 = p3.plot(pen="b",name='sesnor_L')
ptr3=0

data1 = np.array((data.seconds.values.tolist(),data.angle_x_raw_R.values.tolist())).T
data2 = np.array((data.seconds.values.tolist(),data.angle_x_raw_M.values.tolist())).T
data3 = np.array((data.seconds.values.tolist(),data.angle_x_raw_L.values.tolist())).T

data4 = np.array((data.seconds.values.tolist(),data.angle_y_raw_R.values.tolist())).T
data5 = np.array((data.seconds.values.tolist(),data.angle_y_raw_M.values.tolist())).T
data6 = np.array((data.seconds.values.tolist(),data.angle_y_raw_L.values.tolist())).T

data7 = np.array((data.seconds.values.tolist(),data.radiation_R.values.tolist())).T
data8 = np.array((data.seconds.values.tolist(),data.radiation_M.values.tolist())).T
data9 = np.array((data.seconds.values.tolist(),data.radiation_L.values.tolist())).T


def update1():
    global data1,data2,data3,ptr1
    ptr1 += 1
    curve1.setData(data1[:ptr1,0],data1[:ptr1,1])
    curve1.setPos(-data1[ptr1,0], 0)
    curve2.setData(data2[:ptr1,0],data2[:ptr1,1])
    curve2.setPos(-data2[ptr1,0], 0)
    curve3.setData(data3[:ptr1,0],data3[:ptr1,1])
    curve3.setPos(-data3[ptr1,0], 0)

def update2():
    global data4,data5,data6,ptr2
    ptr2 += 1
    curve4.setData(data4[:ptr1,0],data4[:ptr1,1])
    curve4.setPos(-data4[ptr1,0], 0)
    curve5.setData(data5[:ptr1,0],data5[:ptr1,1])
    curve5.setPos(-data5[ptr1,0], 0)
    curve6.setData(data6[:ptr1,0],data6[:ptr1,1])
    curve6.setPos(-data6[ptr1,0], 0)
    
def update3():
    global data7,data8,data9,ptr3
    ptr3 += 1
    curve7.setData(data7[:ptr1,0],data7[:ptr1,1])
    curve7.setPos(-data7[ptr1,0], 0)
    curve8.setData(data8[:ptr1,0],data8[:ptr1,1])
    curve8.setPos(-data8[ptr1,0], 0)
    curve9.setData(data9[:ptr1,0],data9[:ptr1,1])
    curve9.setPos(-data9[ptr1,0], 0)

# update all plots
def update():
    update1()
    update2()
    update3()
    
timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(100)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
