import os,sys
import cv2
import ids
import numpy as np
from time import time,sleep

import atb
from ctypes import c_int, c_double,c_float

import platform
os_name = platform.system()
del platform

#logging
import logging
logger = logging.getLogger(__name__)


class CameraCaptureError(Exception):
    """General Exception for this module"""
    def __init__(self, arg):
        super(FileCaptureError, self).__init__()
        self.arg = arg

class Frame(object):
    """docstring of Frame"""
    def __init__(self, timestamp,img,index=None,compressed_img=None, compressed_pix_fmt=None):
        self.timestamp = timestamp
        self.index = index
        #self.img = img
	#ids_img, ids_meta = self.cam.next() 	
	self.img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        self.compressed_img = compressed_img
        self.compressed_pix_fmt = compressed_pix_fmt


class IdsCapture(object):
    """docstring for FakeCapture"""
    def __init__(self, size=(640,480),fps=30,timestamps=None,timebase=None):
        super(IdsCapture, self).__init__()
        self.size = size
        self.fps = c_float(fps)
        self.timestamps = timestamps
        self.presentation_time = time()
	self.cam = ids.Camera()
	#self.cam.auto_exposure = True
	self.cam.continuous_capture = True
        self.make_img()
	logger.error(self)

        if timebase == None:
            logger.debug("Capture will run with default system timebase")
            self.timebase = c_double(0)
        elif isinstance(timebase,c_double):
            logger.debug("Capture will run with app wide adjustable timebase")
            self.timebase = timebase
        else:
            logger.error("Invalid timebase variable type. Will use default system timebase")
            self.timebase = c_double(0)

    def make_img(self):
        #c_w ,c_h = max(1,self.size[0]/20),max(1,self.size[1]/20)
        #coarse = np.random.randint(0,255,size=(c_h,c_w,3)).astype(np.uint8)
        # self.img = np.ones((size[1],size[0],3),dtype=np.uint8)
        #self.img = cv2.resize(coarse,self.size,interpolation=cv2.INTER_NEAREST)
	ids_img, ids_meta = self.cam.next()	
	#bgr_img = 	
	#self.img = cv2.cvtColor(ids_img, cv2.COLOR_RGB2BGR)
	self.img = cv2.cvtColor(ids_img, cv2.COLOR_RGB2GRAY)

    def fastmode(self):
        self.fps.value = 2000

    def get_frame(self):
        now =  time()
        spent = now - self.presentation_time
        wait = max(0,1./self.fps.value - spent)
        sleep(wait)
        self.presentation_time = time()
	ids_img, ids_meta = self.cam.next()
	# changed using copy	
	return Frame(time()-self.timebase.value,ids_img.copy())
        #return Frame(time()-self.timebase.value,self.img.copy())

    def get_size(self):
        return self.size

    def get_fps(self):
        return self.fps.value

    def get_now(self):
        return time()

    def create_atb_bar(self,pos):
        # add uvc camera controls to a separate ATB bar
        size = (250,100)

        self.bar = atb.Bar(name="Capture_Controls", label='Could not start real capture.',
            help="Fake Capture Controls", color=(250,50,50), alpha=100,
            text='light',position=pos,refresh=2., size=size)


        # cameras_enum = atb.enum("Capture",dict([(c.name,c.src_id) for c in Camera_List()]) )
        # self.bar.add_var("Capture",vtype=cameras_enum,getter=lambda:self.src_id, setter=self.re_init_cam_by_src_id)
        self.bar.add_var("fps",self.fps,min=0,step=1)
        self.bar.add_button("as fast as possible",self.fastmode)

        return size

    def kill_atb_bar(self):
        #since we never replace this plugin during runtime. Just let the app handle it.
        pass

    def close(self):
        pass
