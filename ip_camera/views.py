#source: https://stackoverflow.com/questions/49680152/opencv-live-stream-from-camera-in-django-webpage

from django.shortcuts import render
from django.views.decorators import gzip
from django.http import StreamingHttpResponse, response
from .models import Camera

import cv2
import threading

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture('rtsp://192.168.137.61:8080/h264_pcm.sdp')
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(frame)
        #yield(b'--frame\r\n'
        #      b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        #source: https://www.reddit.com/r/learnpython/comments/3l242p/what_this_code_belongs_to_from_a_camera_streaming/



@gzip.gzip_page
def livefe(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:  # This is bad! replace it with proper handling
        pass

def camera_list(response):
    try:
        
        frame = Camera.objects.get(name="test")
        return render(response, "ip_camera/camera_list.html", {'frame':frame})
    except:
        pass