# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 06:10:40 2018

@author: addiewan
"""
import pandas as pd
import numpy as np

df=pd.DataFrame(columns=['delay','ptu_ebay_cmd','ptu_d48_cmd'])
time=0.0
n=0
df.loc[n]=[time,'i','i']
time+=0.5
n+=1
df.loc[n]=[time,'ci','ci']
time+=1.0
n+=1
speed_ebay=1
df.loc[n]=[time,'ps'+str(speed_ebay),'se']
time+=4.0
n+=1
offset_ebay=10
df.loc[n]=[time,'po'+str(offset_ebay),'']
time+=0.5+ offset_ebay/speed_ebay
n+=1
df.loc[n]=[time,'po-'+str(offset_ebay),'']
time+=0.5+ offset_ebay/speed_ebay
n+=1
speed_ebay=0
offset_ebay=80

for i in range(10):
    speed_ebay+=10
    df.loc[n]=[time,'ps'+str(speed_ebay),'']
    n+=1
    time+=0.5 
    df.loc[n]=[time,'po'+str(offset_ebay),'']
    time+=0.5+ np.ceil(offset_ebay/speed_ebay)
    n+=1
    df.loc[n]=[time,'po-'+str(offset_ebay),'']
    time+=0.5+ np.ceil(offset_ebay/speed_ebay)
    n+=1

df.to_csv('C:/git_repos/GLO/tracking/ptu_simulations/not_now/speed_bins.csv',index=False)