import sys
import argparse
#from yolo import YOLO
from PIL import Image, ImageTk
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import cv2
left_mouse_down_x = 0
left_mouse_down_y = 0
left_mouse_up_x = 0
left_mouse_up_y = 0
sole_rectangle = None
cord = []
#x=YOLO()
postdata_toserver = {"seat": "0", "location": "1F", "occupy": "1","camera": "0"}

def ok_event(): 
    win.destroy()
    #detect_img(x)

def detect_img(yolo):
    video_path = "seat_video1.mp4"
    capture = cv2.VideoCapture(video_path)
    fps = int(capture.get(cv2.CAP_PROP_FPS))
    total_frame = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    while True:
        for j in range(int(total_frame)):
            ret, frame = capture.read()
            if not ret:
                break
            #一秒
            if j % fps == 0:
                image=Image.fromarray(frame)
                image = image.resize((1200, 600))
                for i in range(len(cord)):
                    img=image.crop((cord[i][1],cord[i][2],cord[i][3],cord[i][4]))
                    r_image, people_num = yolo.detect_image(img)
                    cord[i][5]=people_num
                    
                    postdata_toserver["seat"]=cord[i][0]
                    postdata_toserver["location"]=cord[i][6]
                    postdata_toserver["camera"]=cord[i][7]
                    postdata_toserver["occupy"]=str(people_num)
                    r=requests.post('http://127.0.0.1:8000/create/', data = postdata_toserver)
                    
    yolo.close_session()

def left_mouse_down(event):
    # print('鼠标左键按下')
    global left_mouse_down_x, left_mouse_down_y
    left_mouse_down_x = event.x
    left_mouse_down_y = event.y
 
def left_mouse_up(event):
    # print('鼠标左键释放')
    global left_mouse_up_x, left_mouse_up_y, seat_name, seat_floor, camera_number
    left_mouse_up_x = event.x
    left_mouse_up_y = event.y
    seat_name=seat_number_entry.get()
    seat_floor=floor_entry.get()
    camera_number=camera_entry.get()
    listbox.insert('end', seat_name)
    corp_img(img_path, 'one_corp.jpg', left_mouse_down_x, left_mouse_down_y,
       left_mouse_up_x, left_mouse_up_y)
 
def moving_mouse(event):
    # print('鼠标左键按下并移动')
    global sole_rectangle
    global left_mouse_down_x, left_mouse_down_y
    moving_mouse_x = event.x
    moving_mouse_y = event.y
    if sole_rectangle is not None:
        canvas.delete(sole_rectangle) # 删除前一个矩形
    sole_rectangle = canvas.create_rectangle(left_mouse_down_x, left_mouse_down_y, moving_mouse_x,
                       moving_mouse_y, outline='red')
 
def corp_img(source_path, save_path, x_begin, y_begin, x_end, y_end):
    if x_begin < x_end:
        min_x = x_begin
        max_x = x_end
    else:
        min_x = x_end
        max_x = x_begin
    if y_begin < y_end:
        min_y = y_begin
        max_y = y_end
    else:
        min_y = y_end
        max_y = y_begin
    cord.append([])
    cord[(len(cord)-1)].append(seat_name)
    cord[(len(cord)-1)].append(min_x)
    cord[(len(cord)-1)].append(min_y)
    cord[(len(cord)-1)].append(max_x)
    cord[(len(cord)-1)].append(max_y)
    cord[(len(cord)-1)].append(0)
    cord[(len(cord)-1)].append(seat_floor)
    cord[(len(cord)-1)].append(camera_number)
    print(cord)

def undo_event():
    if len(cord)>0:
        cord.pop()
        listbox.delete(len(cord))
        print(cord)

def openSetupImage(): #select an image to setup bounding box
    global setup_img, setup_image, img_path
    img_path = filedialog.askopenfilename(initialdir="/", title="open an image", filetypes= ( ("all files", "*.*"), ("jpg files", "*.jpg") ))
    image = Image.open(img_path)
    setup_image=image.resize((1200, 600))
    setup_img = ImageTk.PhotoImage(setup_image)

if __name__ == '__main__':

    global var

    win = tk.Tk()
    win.geometry('1200x1000')

    #fix the missing cursor in text box bug. cause by filedialog.
    win.update_idletasks()

    frame1 = tk.Frame(win,bg='red',bd=10)
    frame1.pack()
    frame2=tk.Frame(win,bg='yellow',bd=20)
    frame2.pack()
    frame3=tk.Frame(win,bg='blue',bd=20)
    frame3.pack()

    seat_number_label = tk.Label(frame3,text = "Seat number")
    seat_number_label.grid(column=0, row=0, ipadx=5, pady=5, sticky=tk.W+tk.N)
    seat_number_entry = tk.Entry(frame3)
    seat_number_entry.grid(column=1, row=0, padx=10, pady=5, sticky=tk.N)
    
    floor_label = tk.Label(frame3,text = "Floor")
    floor_label.grid(column=0, row=1, ipadx=5, pady=5, sticky=tk.W+tk.N)
    floor_entry = tk.Entry(frame3)
    floor_entry.grid(column=1, row=1, padx=10, pady=5, sticky=tk.N)
    
    camera_label = tk.Label(frame3,text = "Camera")
    camera_label.grid(column=0, row=2, ipadx=5, pady=5, sticky=tk.W+tk.N)
    camera_entry = tk.Entry(frame3)
    camera_entry.grid(column=1, row=2, padx=10, pady=5, sticky=tk.N)

    var = tk.StringVar()
    listbox = tk.Listbox(frame3, listvariable=var)
    listbox.grid(column=2, row=0, padx=10, pady=5, sticky=tk.N)

    undobutton = tk.Button(frame2, text='Undo', command=undo_event, width=15)
    undobutton.pack(side='left')
    okbutton = tk.Button(frame2, text='Ok', command=ok_event, width=15)
    okbutton.pack(side='right')
    
    #select a image to setup bounding box
    openSetupImage()
    
    #bulit canvas
    setup_image_x, setup_image_y = setup_image.size
    canvas = tk.Canvas(frame1, width=setup_image_x, height=setup_image_y, bg='pink')
    i = canvas.create_image(0, 0, anchor='nw', image=setup_img)
    canvas.pack()

    canvas.bind('<Button-1>', left_mouse_down) # 鼠标左键按下
    canvas.bind('<ButtonRelease-1>', left_mouse_up) # 鼠标左键释放
    canvas.bind('<B1-Motion>', moving_mouse) # 鼠标左键按下并移动

    win.mainloop()
    
   
