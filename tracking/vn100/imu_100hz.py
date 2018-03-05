from vnpy import *
import time
from datetime import datetime
import pandas as pd
import numpy as np

ez = EzAsyncData.connect('/dev/ttyUSB0', 921600) #921600
ez.sensor.write_async_data_output_frequency(100)
ypr = []
accel=[]
ang_r=[]
timestamp=[]
t0 = time.time()
elapsed = time.time()-t0
while elapsed < 120:
    #print('hello')
    t1=time.time()
    ypr.append(ez.current_data.yaw_pitch_roll)
    accel.append(ez.current_data.acceleration)
    ang_r.append(ez.current_data.angular_rate)
    timestamp.append(datetime.now())
    elapsed = time.time()-t0
    dt=time.time()-t1
    time.sleep(.01-dt)
#ez.disconnect()
yaw=[]
pitch=[]
roll=[]
accel_x=[]
accel_y=[]
accel_z=[]
ang_x=[]
ang_y=[]
ang_z=[]
utc=[]
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
        utc.append(timestamp[i])
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
        utc.append(timestamp[i])
    
data = pd.DataFrame({'utc':utc,
                     'yaw':yaw,
                     'pitch':pitch,
                     'roll':roll,
                     'accel_x':accel_x,
                     'accel_y':accel_y,
                     'accel_z':accel_z,
                     'ang_x':ang_x,
                     'ang_y':ang_y,
                     'ang_z':ang_z})
data = data.set_index('utc')

data.to_csv('imu_test.csv')
                      
##ez.sensor.read_async_data_output_frequency()
##ez.sensor.change_baudrate(921600)
##ez.sensor.write_async_data_output_frequency(100)
    