# -*- coding: utf-8 -*-
from goprohero import GoProHero
import argparse
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Record VN100 IMU Data')
    parser.add_argument('-p','--passw',
                        default='@d@lie4444',
                        type=str,
                        help='gopro pass')
    parser.add_argument('-m','--mode',
                        default='video',
                        type=str,
                        help='mode: video, still, burst, timelapse, timer')
    parser.add_argument('-v','--vid_res',
                        default='720p',
                        type=str,
                        help='video resolution: 720p, 1080p')
    parser.add_argument('-f','--fov',
                    default='90',
                    type=str,
                    help='camera field of view: 90, 127, or 170')
    parser.add_argument('-r','--record',
                        default='off',
                        type=str,
                        help='record mode: on or off')
    parser.add_argument('-s','--sleep',
                        default='off',
                        type=str,
                        help='sleep mode: on or off')
        
    params=parser.parse_args()
    
    cam = GoProHero(password=params.passw)
    
    if params.mode == 'video':
        cam.command('mode', '00') #set to video mode
    else: 
        cam.command('mode', '01') #set to still capture mode
        
    if params.vid_res == '720p':
        cam.command('vidres', '01') #set resolution to 720p
    else:
        cam.command('vidres',params.vid_res) #set resolution to 720p
        
    if params.fov == '90':
        cam.command('fov','02')
    else:
        cam.command('fov',params.fov)
        
    if params.record == 'on':
        cam.command('record','01')
    else: 
        cam.command('record','00')
        
    if params.sleep == 'on':
        cam.command('power','00')
    else:
        cam.command('power','01')
        