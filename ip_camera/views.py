#source: https://stackoverflow.com/questions/49680152/opencv-live-stream-from-camera-in-django-webpage

from django.shortcuts import redirect, render
from django.views.decorators import gzip
from django.http import StreamingHttpResponse, response
from .models import Camera
from main.models import Location

#update thumbnail
import time
import os
from pathlib import Path
from django.core.files import File  # you need this somewhere
import urllib

import cv2
import threading

#new camera form
from .forms import *

class VideoCamera(object):
    def __init__(self, ip, name):
        self.video = cv2.VideoCapture(ip)   
        self.ip = ip
        self.name = name
        self.pretime = 0 #thumbnail update time refence
        self.thumbnail_update_interval = 10 #thumbnail update interval
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame

        ## update thumbnail
        if(time.time() - self.pretime > self.thumbnail_update_interval):
            print(self.name + "-- thumbnail updated")
            url = "media/img/thumbnail/" + self.name + ".jpg"
            cv2.imwrite(url, image)
            self.pretime = time.time()

        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()


def gen(camera_gen):
    while True:
        frame = camera_gen.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        #source: https://www.reddit.com/r/learnpython/comments/3l242p/what_this_code_belongs_to_from_a_camera_streaming/



@gzip.gzip_page
def livefe(response, ip):
    print("LIVE:: " + ip)
    try:
        cam_temp = Camera.objects.get(ip_address = ip)
        cam = VideoCamera("rtsp://" + ip + "/h264_pcm.sdp", cam_temp.name)
        #! 重複多開問題
        
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:  # This is bad! replace it with proper handling
        pass

def camera_list(response):
    location_list = Location.objects.all()
    try:       
        camera = Camera.objects.all()
            
        return render(response, "ip_camera/camera_list.html", {"location_list":location_list, 'camera':camera})
    except:
        pass


def add_new_camera(response):
    location_list = Location.objects.all()
    if response.method == "POST": 
        form = Add_new_camera(response.POST, response.FILES)

        if form.is_valid():
            form.save()
            return redirect("/cameras/")

    else:
        form = Add_new_camera()
    return render(response, "ip_camera/add_camera.html", {"location_list":location_list, "form":form})