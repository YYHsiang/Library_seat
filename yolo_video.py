import sys
import argparse
from yolo import YOLO
from PIL import Image
import os
import tkinter as tk
from PIL import ImageTk
import requests

left_mouse_down_x = 0
left_mouse_down_y = 0
left_mouse_up_x = 0
left_mouse_up_y = 0
sole_rectangle = None
cord = []
#x=YOLO()
postdata_toserver = {"seat": "0", "location": "1F", "occupy": "1"}

def ok_event(): 
    win.destroy()
    #detect_img(x)

def detect_img(yolo):
    while True:
    #img = input('Input image filename:')
        try:
            image = Image.open('test2.jpg')
        except:
            print('Open Error! Try again!')
            continue
        else:
            for i in range(len(cord)):
                img=image.crop((cord[i][1],cord[i][2],cord[i][3],cord[i][4]))
                r_image, people_num = yolo.detect_image(img)
                cord[i][5]=people_num
                #r_image.show()
                postdata_toserver["seat"]=cord[i][0]
                postdata_toserver["location"]=cord[i][6]
                postdata_toserver["occupy"]=str(people_num)
                r=requests.post('http://127.0.0.1:8000/create/', data = postdata_toserver)
    yolo.close_session()

FLAGS = None

def left_mouse_down(event):
  # print('鼠标左键按下')
  global left_mouse_down_x, left_mouse_down_y
  left_mouse_down_x = event.x
  left_mouse_down_y = event.y
 
def left_mouse_up(event):
  # print('鼠标左键释放')
  global left_mouse_up_x, left_mouse_up_y, seat_name, seat_floor
  left_mouse_up_x = event.x
  left_mouse_up_y = event.y
  seat_name=seat_number_entry.get()
  seat_floor=floor_entry.get()
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
  print(cord)

def undo_event():
  if len(cord)>0:
    cord.pop()
    listbox.delete(len(cord))
    print(cord)


if __name__ == '__main__':

    global var

    win = tk.Tk()
    win.geometry('1000x1000')

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
    var = tk.StringVar()
    listbox = tk.Listbox(frame3, listvariable=var)
    listbox.grid(column=2, row=0, padx=10, pady=5, sticky=tk.N)

    undobutton = tk.Button(frame2, text='Undo', command=undo_event)
    undobutton.pack()
    okbutton = tk.Button(frame2, text='Ok', command=ok_event)
    okbutton.pack()

    img_path = 'test2.jpg'
    image = Image.open(img_path)
    image_x, image_y = image.size
    screenwidth = win.winfo_screenwidth()
    screenheight = win.winfo_screenheight()
    if image_x > screenwidth or image_y > screenheight:
      print('The picture size is too big,max should in:{}x{}, your:{}x{}'.format(screenwidth,
                                            screenheight,
                                            image_x,
                                            image_y))
    img = ImageTk.PhotoImage(image)
    canvas = tk.Canvas(frame1, width=image_x, height=image_y, bg='pink')
    i = canvas.create_image(0, 0, anchor='nw', image=img)
    canvas.pack()
    canvas.bind('<Button-1>', left_mouse_down) # 鼠标左键按下
    canvas.bind('<ButtonRelease-1>', left_mouse_up) # 鼠标左键释放
    canvas.bind('<B1-Motion>', moving_mouse) # 鼠标左键按下并移动
    win.mainloop()
    
   
