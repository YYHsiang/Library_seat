import sys
import argparse
import math
import io
import time
#from yolo import YOLO

import os
from tkinter import *
from tkinter import filedialog, messagebox
import random
from tkinter import ttk
from keras.models import load_model
# difference
from skimage.metrics import structural_similarity
import numpy as np

# point inside polygon
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from numpy.lib.arraypad import pad
#from yolo import YOLO
from yolo3.utils import rand
from PIL import Image, ImageTk, ImageDraw
import requests
import cv2
import sqlite3

# Debug mode
DEBUG_MODE = True

# store mouse position
left_mouse_down_x = 0
left_mouse_down_y = 0
left_mouse_up_x = 0
left_mouse_up_y = 0
sole_rectangle = None

# store all seats' bounding box select by user
# bounding_box_list = ["file_type", "seat_name", point1, point2, point3, point4, "location", "camera_name", "original_talbe"]
bounding_box_list = []
BBL_FILE_TYPE_INDEX = 0
BBL_SEAT_NAME_INDEX = 1
BBL_PT1_INDEX = 2
BBL_PT2_INDEX = 3
BBL_PT3_INDEX = 4
BBL_PT4_INDEX = 5
BBL_LOCATION_INDEX = 6
BBL_CAM_NAME_INDEX = 7
BBL_ORIGINAL_T_INDEX = 8

#store all large table select by user
#large_table_list = ["table_name", point1, point2, point3, point4, <image PIL format>]
large_table_list = []
LTL_TABLE_NAME_INDEX = 0
LTL_PT1_INDEX = 1
LTL_PT2_INDEX = 2
LTL_PT3_INDEX = 3
LTL_PT4_INDEX = 4
LTL_IMAGE_INDEX = 5


#store text when display all bounding box
bounding_box_text = []

# 4 point clicking counter
point_cnt = 0
seat_divide_cnt = 0
sole_polygon = []
point_bounding_box_list = [] #temporally store bound for future use
sole_polygon_list = [] # for draw polygon

postdata_toserver = {"seat": "0", "location": "1F", "occupy": "1","camera": "0"}


#database path
DATABASE_PATH = "database/bounding_box.db"
TABLE_NAME = "seats_4point"
TABLE_XY_NAME = "seats"
TABLE = "large_table"

#file types
file_types = [
    "seat", "table"
]

class Object_detect():
    def __init__(self, video_path:str):
        self.video_path = video_path
        self.EROSION_FACTOR = 5

    def PIL2CV(self, image):  
        img = cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR)
        return img

    def CV2PIL(self, image):
        img = Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))  
        return img

    def difference(self, before, after):
        '''
        check the difference between two image and return the object coordinate
        '''
        # Convert images to grayscale
        before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
        after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

        # Compute SSIM between two images
        (score, diff) = structural_similarity(before_gray, after_gray, full=True)
        cv2.namedWindow("diff", cv2.WINDOW_NORMAL)
        cv2.imshow('diff',diff)
        print("Image similarity", score)
        diff_reshape = diff.reshape(1,175,35,1).astype("float32")
        
        predict_x=model.predict(diff_reshape)
        pre_y=np.argmax(predict_x,axis=1)
        print(pre_y)
        
        '''cv2.namedWindow("after", cv2.WINDOW_NORMAL)
        cv2.imshow('after',after)
        #cv2.namedWindow("blur_diff", cv2.WINDOW_NORMAL)
        #cv2.imshow('blur_diff',blur_diff)
        cv2.namedWindow("diff", cv2.WINDOW_NORMAL)
        cv2.imshow('diff',diff)
        cv2.namedWindow("thresh", cv2.WINDOW_NORMAL)
        cv2.imshow('thresh',thresh)
        #cv2.namedWindow("thresh_mask", cv2.WINDOW_NORMAL)
        #cv2.imshow('thresh_mask',thresh_mask)
        cv2.namedWindow("thresh_mask_gray", cv2.WINDOW_NORMAL)
        cv2.imshow('thresh_mask_gray',thresh_mask_gray)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        '''
        
        return pre_y

    def Pts_in_polygon(self, point:tuple or list, polygon_points:list or tuple):
        pts = Point(point[0], point[1])
        polygon = Polygon(polygon_points)
        #print(polygon.contains(pts))
        
        return polygon.contains(pts) #Ture or False


class yolo_detect():
    def __init__(self):
        self.object = Object_detect('none')
        self.occupied_table = [] # store the table which is occupied      

        if ip_entry.get() == "":
            messagebox.showerror("Error","Please enter Video Path")
        elif bounding_box_list == []:
            messagebox.showerror("Error","Bounding Box is Empty")
        elif large_table_list == []:
            messagebox.showerror("Error","Large Table is Empty")
        else:
            #yolo=YOLO()

            pretime = 0
            self.video = cv2.VideoCapture('rtsp://'+ip_entry.get())
            print("--CAMERA CONNECTED--")
            while True:
                if time.time() -  pretime > 1:
                    pretime = time.time()
                    self.video = cv2.VideoCapture('rtsp://'+ip_entry.get())
                    (self.grabbed, self.frame) = self.video.read()

                    image=Image.fromarray(self.frame)
                    #image.show()
                    for table in large_table_list:                       
                        # crop the image
                            
                        for seats in bounding_box_list:
                            if seats[BBL_FILE_TYPE_INDEX] == 'table' and seats[BBL_ORIGINAL_T_INDEX] == table[LTL_TABLE_NAME_INDEX]:
                                img_now_croped = crop_polygon('', (table[LTL_PT1_INDEX], table[LTL_PT2_INDEX], table[LTL_PT3_INDEX], table[LTL_PT4_INDEX]), image=image)
                                img_now_croped = self.object.PIL2CV(img_now_croped)
                                img_now_croped = crop_with_argwhere(img_now_croped)
                                img_now_croped = cv2.resize(img_now_croped, (175, 35), interpolation=cv2.INTER_AREA)
                                cv2.namedWindow("img_now_croped", cv2.WINDOW_NORMAL)
                                cv2.imshow("img_now_croped", img_now_croped)
                                
                                img_before = self.object.PIL2CV(table[LTL_IMAGE_INDEX].copy())
                                img_before = crop_with_argwhere(img_before)
                                img_before = cv2.resize(img_before, (175, 35), interpolation=cv2.INTER_AREA)
                                cv2.namedWindow("img_before", cv2.WINDOW_NORMAL)
                                cv2.imshow("img_before", img_before)
                                cv2.waitKey(30)

                                objects = self.object.difference(img_before, img_now_croped)
                                if objects==1:
                                    self.occupied_table.append([])
                                    self.occupied_table[-1].append(seats[BBL_SEAT_NAME_INDEX])
                                
                    '''#! yolo detect
                    print("-- YOLO --")
                    for seats in bounding_box_list:
                        people_num=0
                        print("seats"+ str(seats))
                        print("coor: "+ str((seats[BBL_PT1_INDEX], seats[BBL_PT2_INDEX], seats[BBL_PT3_INDEX], seats[BBL_PT4_INDEX])))
                        if seats[BBL_FILE_TYPE_INDEX] == 'seat':
                            
                            img = crop_polygon('', (seats[BBL_PT1_INDEX], seats[BBL_PT2_INDEX], seats[BBL_PT3_INDEX], seats[BBL_PT4_INDEX]), image=image)
                            img = self.object.PIL2CV(img)  #change format from Pillow Image to OpenCV image
                            img = crop_with_argwhere(img) # crop black area
                            img = self.object.CV2PIL(img)

                            #r_image, people_num = yolo.detect_image(img)

                            
                            for table in self.occupied_table:
                                if table[0] == seats[BBL_SEAT_NAME_INDEX]:
                                    people_num += 1
            
                        print(people_num)
                        #postdata_toserver["seat"]=seats[BBL_SEAT_NAME_INDEX]
                        #postdata_toserver["location"]=seats[BBL_LOCATION_INDEX]
                        #postdata_toserver["camera"]=seats[BBL_CAM_NAME_INDEX]
                        #postdata_toserver["occupy"]=str(people_num)
                        #r=requests.post('http://192.168.43.198:8000/create/', data = postdata_toserver)
                        #print("Django Data: " + str(postdata_toserver) + "\n\n")'''
                    
                    #yolo.close_session()
                    self.occupied_table = []

class DB_4point_xy():
    def __init__(self):
        # create a database or connect one
        self.conn = sqlite3.connect(DATABASE_PATH)
        #create a cursor
        self.c = self.conn.cursor()

        # create a table
        '''
        self.c.execute("""CREATE TABLE seats_4point_xy(
            file_name text,
            file_type text,
            seat_name text,
            point1_x integer,
            point1_y integer,
            point2_x integer,
            point2_y integer,
            point3_x integer,
            point3_y integer,
            point4_x integer,
            point4_y integer,
            location text,
            camera_name text
            )""")
        '''

        '''# store undivided table
        self.c.execute("""CREATE TABLE large_table(
            file_name text,
            file_type text,
            table_name text PRIMARY KEY,
            point1_x integer,
            point1_y integer,
            point2_x integer,
            point2_y integer,
            point3_x integer,
            point3_y integer,
            point4_x integer,
            point4_y integer,
            empty_table_img blob
            )""")'''

        '''self.c.execute("""CREATE TABLE seats(
            file_name text,
            file_type text,
            seat_name text,
            point1_x integer,
            point1_y integer,
            point2_x integer,
            point2_y integer,
            point3_x integer,
            point3_y integer,
            point4_x integer,
            point4_y integer,
            location text,
            camera_name text,
            original_table text,
            FOREIGN KEY(original_table) REFERENCES large_table(table_name)
            )""")'''

        # commit changes
        self.conn.commit()
        # close connection
        self.conn.close()

    def select(self, table_name:str, file_name:str):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.c = self.conn.cursor()

        self.c.execute("SELECT * FROM " + table_name + " WHERE file_name = '" + file_name + "'")
        records = self.c.fetchall()
        #print(records)

        self.conn.commit()
        self.conn.close()

        return records
    
    # add new file to database
    def seats_insert(self, table_name:str, file_name:str, file_type:str, seat_name:str, pt1:list, pt2:list, pt3:list, pt4:list, location:str, camera_name:str, original_table:str):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.c = self.conn.cursor()

        #Insert into table
        self.c.execute("INSERT INTO "+ table_name +" VALUES (:file_name, :file_type,:seat_name, :point1_x, :point1_y, :point2_x, :point2_y, :point3_x, :point3_y, :point4_x, :point4_y, :location, :camera_name, :original_table)",
                {
                    'file_name': file_name,
                    'file_type': file_type,
                    'seat_name': seat_name,
                    'point1_x':pt1[0],
                    'point1_y':pt1[1],
                    'point2_x':pt2[0],
                    'point2_y':pt2[1],
                    'point3_x':pt3[0],
                    'point3_y':pt3[1],
                    'point4_x':pt4[0],
                    'point4_y':pt4[1],
                    'location': location,
                    'camera_name': camera_name,
                    'original_table': original_table
                })

        self.conn.commit()
        self.conn.close()

    def large_table_insert(self, table_name:str, file_name:str, file_type:str, large_table_name:str, pt1:list, pt2:list, pt3:list, pt4:list, empty_table_img):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.c = self.conn.cursor()


        #Insert into table
        self.c.execute("INSERT INTO "+ table_name +" VALUES (:file_name, :file_type, :table_name, :point1_x, :point1_y, :point2_x, :point2_y, :point3_x, :point3_y, :point4_x, :point4_y, :empty_table_img)",
                {
                    'file_name': file_name,
                    'file_type': file_type,
                    'table_name': large_table_name,
                    'point1_x':pt1[0],
                    'point1_y':pt1[1],
                    'point2_x':pt2[0],
                    'point2_y':pt2[1],
                    'point3_x':pt3[0],
                    'point3_y':pt3[1],
                    'point4_x':pt4[0],
                    'point4_y':pt4[1],
                    'empty_table_img': empty_table_img
                })

        self.conn.commit()
        self.conn.close()

    def query(self, table_name:str):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.c = self.conn.cursor()

        self.c.execute("SELECT * FROM " + table_name)
        records = self.c.fetchall()
        #print(records)

        self.conn.commit()
        self.conn.close()

        return records

    #delete using file_name
    def delete(self, table_name:str, file_name:str):
        self.conn = sqlite3.connect(DATABASE_PATH)
        c = self.conn.cursor()

        c.execute("DELETE from "+ table_name +" WHERE file_name = '" + file_name + "'")

        self.conn.commit()
        self.conn.close()

class database_window():
    def __init__(self, tool):
        self.db_window=Toplevel()
        self.db_window.title("Database")
        self.db_window.geometry("500x400")

        self.tool = tool
        
        # Frame for query
        self.file_list= LabelFrame(self.db_window, text="Files")
        self.file_list.grid(row=1, column= 0,columnspan=3, padx=30, pady=10)

        #show data in database
        show_query_btn = Button(self.db_window, text="show query", command=self.show_query)
        show_query_btn.grid(row=0,column= 0, pady=10, )

        #Treeview
        self.query_tree = ttk.Treeview(self.file_list)
        self.query_tree["columns"] = ("File type", "seat #", "Location", "Camera")

        # define columns
        self.query_tree.column("#0", width=120, anchor=W)
        self.query_tree.column("File type", width=80, anchor=W)
        self.query_tree.column("seat #", width=80, anchor=CENTER)
        self.query_tree.column("Location", width=80, anchor=W)
        self.query_tree.column("Camera", width=80, anchor=W)

        # define headings
        self.query_tree.heading("#0", text="File Name", anchor=W)
        self.query_tree.heading("File type", text="File type", anchor=W)
        self.query_tree.heading("seat #", text="seat #", anchor=CENTER)
        self.query_tree.heading("Location", text="Location", anchor=W)
        self.query_tree.heading("Camera", text="Camera", anchor=W)
        self.query_tree.pack()

        self.query_tree.bind("<Double-1>", self.OnDoubleClick)

        #show query
        self.show_query()

        # File name box
        file_name_label = Label(self.db_window, text="File Name:")
        file_name_label.grid(row=2, column=0, pady=10)
        self.file_name_box = Entry(self.db_window, width=30)
        self.file_name_box.grid(row=2, column= 1)
        self.file_name_box.focus()

        #add new data in database
        add_new_btn = Button(self.db_window, text="Add new Data", command=lambda: self.add_new(self.file_name_box.get()))
        add_new_btn.grid(row=3, column=0, padx=5)

        #load data in database
        load_btn = Button(self.db_window, text="Load", width=25 , command=lambda: self.load(self.file_name_box.get()))
        load_btn.grid(row=3, column=1)

        #delete data in database
        delete_btn = Button(self.db_window, text="Delete Data", command=lambda: self.delete_file(self.file_name_box.get()))
        delete_btn.grid(row=3, column=2)

    # double click to select file
    def OnDoubleClick(self, event):
        item = self.query_tree.selection()[0]
        self.file_name_box.delete(0,'end')
        self.file_name_box.insert(0, self.query_tree.item(item,"text"))
        
    # show all files in db
    def show_query(self):
        print("--SHOW QUERY--")
        #db_win = DB_4point() #original table
        db_win = DB_4point_xy() #2nd table
        db_win_records = db_win.query(TABLE_XY_NAME)

        files = []
        '''
        2d array=[[file_name, file_type, seat_cnt, location, camera_name], [...],...]
        '''
        if db_win_records is None:
            messagebox.showerror("No data", "Database is Empty!")
        else:
            for record in db_win_records:
                # collect all file name, assume SAME file_name with SAME location and camera_name.
                # and only count seat #
                if files == [] :
                    files.append([])
                    files[0].append(record[0]) #file name
                    files[0].append(record[1]) #file type
                    files[0].append(1) #count seats with same file name
                    files[0].append(record[11]) #location
                    files[0].append(record[12]) #camera_name
                elif files != []:
                    #check for duplicate
                    ifnew = 0
                    for index in files:
                        if record[0] in index[0]:
                            ifnew =False
                            pass
                        else:
                            ifnew =True

                    #if file name in record already exist in file, add seat cnt.
                    if ifnew:
                        files.append([])
                        files[-1].append(record[0]) #file name
                        files[-1].append(record[1]) #file type
                        files[-1].append(1) #count seats with same file name
                        files[-1].append(record[11]) #location
                        files[-1].append(record[12]) #camera_name

                    #if file name in record doesnt exist in file, then add one.
                    elif ifnew == False  and record[1] == 'seat':
                        i = files.index(index)
                        files[i][2] +=1 
                    
        #print(files)

        
        self.query_tree.delete(*self.query_tree.get_children())
        count = 0 # for iid 
        for record in files:
            self.query_tree.insert(parent='', index='end', iid= count, text=record[0], values=(record[1],record[2],record[3],record[4]))
            count += 1
        

    #add bounding_box_list to database
    def add_new(self, file_name):
        print("--ADD NEW--")
        db_win = DB_4point_xy()

        if bounding_box_list == []:
            messagebox.showerror(title="No data!",message="No bounding box") 
            self.db_window.focus()  
        else:
            for table in large_table_list:
                #croped image
                img = table[LTL_IMAGE_INDEX]
                img.show() 
                #convert image to blob format
                stream = io.BytesIO()
                img.save(stream, format="JPEG")
                imagebytes = stream.getvalue()

                file_type ="original_table"
                db_win.large_table_insert(TABLE, file_name, file_type, 
                                            table[LTL_TABLE_NAME_INDEX], 
                                            table[LTL_PT1_INDEX], 
                                            table[LTL_PT2_INDEX], 
                                            table[LTL_PT3_INDEX], 
                                            table[LTL_PT4_INDEX], 
                                            imagebytes)

            for box in bounding_box_list:
                # bounding_box_list = ["file_type", "seat_name", point1, point2, point3, point4, "location", "camera_name", "original_talbe"]
                db_win.seats_insert(TABLE_XY_NAME, 
                                    file_name, 
                                    box[BBL_FILE_TYPE_INDEX],
                                    box[BBL_SEAT_NAME_INDEX], 
                                    box[BBL_PT1_INDEX], 
                                    box[BBL_PT2_INDEX],
                                    box[BBL_PT3_INDEX], 
                                    box[BBL_PT4_INDEX],
                                    box[BBL_LOCATION_INDEX],
                                    box[BBL_CAM_NAME_INDEX], 
                                    box[BBL_ORIGINAL_T_INDEX])

            self.db_window.destroy()
          
    #load the data in database to bounding_box_list
    def load(self, file_name):
        print("--LOAD--")
        db_win = DB_4point_xy()
        
        records = db_win.select(TABLE_XY_NAME, file_name)
        if records == []:
            messagebox.showwarning("No Data", "No Data")
        else:
            self.tool.listbox_update()

            global bounding_box_list
            bounding_box_list = []
            for record in records:
                # bounding_box_list = ["file_type", "seat_name", point1, point2, point3, point4, "location", "camera_name"]
                bounding_box_list.append([])
                bounding_box_list[(len(bounding_box_list)-1)].append(record[1]) #file type
                bounding_box_list[(len(bounding_box_list)-1)].append(record[2]) #seat name
                bounding_box_list[(len(bounding_box_list)-1)].append((record[3],record[4])) #pt1
                bounding_box_list[(len(bounding_box_list)-1)].append((record[5],record[6])) #pt2
                bounding_box_list[(len(bounding_box_list)-1)].append((record[7],record[8])) #pt1
                bounding_box_list[(len(bounding_box_list)-1)].append((record[9],record[10])) #pt2
                bounding_box_list[(len(bounding_box_list)-1)].append(record[11]) #location
                bounding_box_list[(len(bounding_box_list)-1)].append(record[12]) #camera name
                bounding_box_list[(len(bounding_box_list)-1)].append(record[13]) #original table

            # set default value in Entry
            seat_number_entry.delete(0,'end')
            seat_number_entry.insert(0, str(int(record[2]) + 1))
            floor_entry.delete(0,'end')
            floor_entry.insert(0, str(record[11]))
            camera_entry.delete(0,'end')
            camera_entry.insert(0, str(record[12]))

            table_records = db_win.select(TABLE, file_name)
            if table_records == None:
                messagebox.showwarning("No Data", "No Data")
            else:
                global large_table_list
                large_table_list = []
                for table_record in table_records:
                    large_table_list.append([])
                    large_table_list[-1].append(table_record[2]) # talbe name
                    large_table_list[-1].append((table_record[3],table_record[4])) # pt1
                    large_table_list[-1].append((table_record[5],table_record[6])) # pt2
                    large_table_list[-1].append((table_record[7],table_record[8])) # pt3
                    large_table_list[-1].append((table_record[9],table_record[10])) # pt4

                    # convert bytes to image
                    imageStream = io.BytesIO(table_record[11])
                    imageFile = Image.open(imageStream)
                    large_table_list[-1].append(imageFile)


            #update listbox
            self.tool.listbox_update()
            self.tool.clean_canvas()        
            self.db_window.destroy()
            win.focus()
            yolo_button.focus()


    #delete bounding_box_list in database
    def delete_file(self, file_name):
        db_win = DB_4point_xy()

        response = messagebox.askyesno(title="Delete", message="Delete the file?")
        if response == 1:
            db_win.delete(TABLE_XY_NAME, file_name) 
            self.db_window.focus() 

class Tool():
    def __init__(self, zoom):
        self.tool = "rect"
        self.long_side1 = [] #logn side 1
        self.long_side2 = [] #logn side 2
        self.canvas = zoom.canvas
        self.zoom = zoom

        #? ============ select tool frame ===========
        rect_select_btn = Button(select_tool_frame, text="Rect", command= lambda: self.change_tool("rect"), width=5)
        rect_select_btn.grid(row=0, column=0,padx= 10,pady= 5)

        point_select_btn = Button(select_tool_frame, text="Point", command= lambda: self.change_tool("point"), width=5)
        point_select_btn.grid(row=0, column=1, padx=10)

        move_select_btn = Button(select_tool_frame, text="Move", command= lambda: self.change_tool("move"), width=5)
        move_select_btn.grid(row=0, column=2,padx=10)
        #? ============ select tool frame ===========

    def change_tool(self, tool_name:str):
        global bounding_box_list

        if tool_name is None:
            messagebox.messagebox.showwarning("Wearning", "Please select tool")
        else:
            print("--" + tool_name + " TOOL--")
            self.tool = tool_name

            #clean all data
            self.clean_canvas()

        if self.tool == "rect":
            # change file type to seat
            file_type_data.set('seat')

            # disable widget in divider_frame
            for child in divider_frame.winfo_children():
                child.configure(state='disable')
            for child in entry_frame.winfo_children():
                child.configure(state='normal')

            # recreate button to dispaly DISABLE
            rect_select_btn = Button(select_tool_frame, text="Rect", state= DISABLED, 
                                    command= lambda: self.change_tool("rect"), width=5)
            rect_select_btn.grid(row=0, column=0,padx= 10,pady= 5)

            point_select_btn = Button(select_tool_frame, text="Point", state= NORMAL, 
                                    command= lambda: self.change_tool("point"), width=5)
            point_select_btn.grid(row=0, column=1, padx=10)

            move_select_btn = Button(select_tool_frame, text="Move", state= NORMAL, 
                                    command= lambda: self.change_tool("move"), width=5)
            move_select_btn.grid(row=0, column=2, padx=10)

            self.canvas.unbind('<ButtonPress-1>')
            self.canvas.unbind('<Configure>')
            self.canvas.unbind('<Button-1>')
            self.canvas.unbind('<ButtonRelease-1>')
            self.canvas.unbind('<B1-Motion>')

            self.canvas.bind('<Button-1>', self.rect_left_mouse_down) # 鼠标左键按下
            self.canvas.bind('<ButtonRelease-1>', self.rect_left_mouse_up) # 鼠标左键释放
            self.canvas.bind('<B1-Motion>', self.rect_moving_mouse) # 鼠标左键按下并移动

        elif tool.tool == "point":
            point_cnt = 0
            # change file type to table
            file_type_data.set('table')

            # enable widget in divider_frame
            for child in divider_frame.winfo_children():
                child.configure(state='normal')
            #enable widget in entry frame
            for child in entry_frame.winfo_children():
                child.configure(state='normal')

            # recreate button to dispaly DISABLE
            rect_select_btn = Button(select_tool_frame, text="Rect", state= NORMAL,
                                command= lambda: self.change_tool("rect"), width=5)
            rect_select_btn.grid(row=0, column=0,padx= 10,pady= 5)

            point_select_btn = Button(select_tool_frame, text="Point", state= DISABLED,
                                command= lambda: self.change_tool("point"), width=5)
            point_select_btn.grid(row=0, column=1, padx=10)

            move_select_btn = Button(select_tool_frame, text="Move", state= NORMAL, 
                                    command= lambda: self.change_tool("move"), width=5)
            move_select_btn.grid(row=0, column=2, padx=10)
            
            self.canvas.unbind('<ButtonPress-1>')
            self.canvas.unbind('<Configure>')
            self.canvas.unbind('<Button-1>')
            self.canvas.unbind('<ButtonRelease-1>')
            self.canvas.unbind('<B1-Motion>')

            self.canvas.bind('<Button-1>', self.point_mouse_down)

        elif tool.tool == "move":
            # disable widget in divider_frame
            for child in divider_frame.winfo_children():
                child.configure(state='disable')
            #disable widget in entry frame
            for child in entry_frame.winfo_children():
                child.configure(state='disable')

            rect_select_btn = Button(select_tool_frame, text="Rect", state= NORMAL,
                                command= lambda: self.change_tool("rect"), width=5)
            rect_select_btn.grid(row=0, column=0,padx= 10,pady= 5)

            point_select_btn = Button(select_tool_frame, text="Point", state= NORMAL,
                                command= lambda: self.change_tool("point"), width=5)
            point_select_btn.grid(row=0, column=1, padx=10)

            move_select_btn = Button(select_tool_frame, text="Move", state= DISABLED, 
                                    command= lambda: self.change_tool("move"), width=5)
            move_select_btn.grid(row=0, column=2, padx=10)

            self.canvas.unbind('<Button-1>')
            self.canvas.unbind('<ButtonRelease-1>')
            self.canvas.unbind('<B1-Motion>')

            # Bind events to the Canvas
            self.canvas.bind('<Configure>', self.zoom.show_image)  # canvas is resized
            self.canvas.bind('<ButtonPress-1>', self.zoom.move_from)
            self.canvas.bind('<B1-Motion>',     self.zoom.move_to)

    def LargeTable(self, img):
        global large_table_list
        large_table_list.append([])
        large_table_list[-1].append(original_table_entry.get())#table name
        large_table_list[-1].append(point_bounding_box_list[0]) #pt1
        large_table_list[-1].append(point_bounding_box_list[1]) #pt2
        large_table_list[-1].append(point_bounding_box_list[2])#pt3
        large_table_list[-1].append(point_bounding_box_list[3])#pt4
        large_table_list[-1].append(crop_polygon('', (point_bounding_box_list[0], point_bounding_box_list[1], point_bounding_box_list[2], point_bounding_box_list[3]),image=img))
        print(large_table_list)


    # TODO: divide selected aera
    def divide(self):
        print("--DIVIDE--")
        if divider_entry_col.get() == '' or divider_entry_row.get() == '' or original_table_entry.get() == '':
            messagebox.showerror('Error', 'Please input divider value')
        elif len(point_bounding_box_list) != 4:
            messagebox.showerror('Error', 'Bounding box error')
        else:
            global seat_divide_cnt
            self.long_side1 = []
            self.long_side2 = []
            pt1,pt2,pt3,pt4 = point_bounding_box_list


            #find short side
            self.short_side1, self.short_side2 = self.divide_point(pt1,pt2,pt3,pt4, "short")
            if DEBUG_MODE:
                print("s_1: " + str(self.short_side1) + "\ns_2: " + str(self.short_side2))

            for cnt in range(len(self.short_side1)-1) :
                long_side1_temp, long_side2_temp = self.divide_point(self.short_side1[cnt], self.short_side2[cnt],self.short_side2[cnt+1], self.short_side1[cnt+1], "long")
                self.long_side1.append(long_side1_temp)
                self.long_side2.append(long_side2_temp)
                     
            if DEBUG_MODE:
                print("l_1: " + str(self.long_side1) + "\nl_2: " + str(self.long_side2))
                col = len(self.long_side1)
                row = len(self.long_side1[0]) -1
                print("TOTAL: row: " + str(col) + "     col: " + str(row))
                print("CURRENT row: "+ str(int(seat_divide_cnt / col)) + '  col: ' +str(seat_divide_cnt % col))

            #clean_canvas
            self.clean_canvas()
            
            # draw divided polygon
            global sole_polygon
            # draw divided polygon
            for outer in range(len(self.long_side1)):
                for inner in range(len(self.long_side1[outer]) - 1):
                    sole_polygon.append(self.canvas.create_polygon(self.long_side1[outer][inner], self.long_side1[outer][inner+1], self.long_side2[outer][inner+1], self.long_side2[outer][inner], outline='green', fill=''))
            
            #reset seat_divide_cnt
            seat_divide_cnt = 0

            # draw polygon to display current seat that needs to define seat_name...
            sole_polygon.append(self.canvas.create_polygon(self.long_side1[0][seat_divide_cnt], self.long_side1[0][seat_divide_cnt+1], self.long_side2[0][seat_divide_cnt+1], self.long_side2[0][seat_divide_cnt],outline='yellow' , width= 5, fill=''))

                

    # TODO: devide area into specific seats
    def divide_seat(self):
        print("--DIVIDE SEAT--")
        global seat_divide_cnt, sole_polygon

        if seat_number_entry.get() == "" or floor_entry.get() == "" or camera_entry.get() == "":
            messagebox.showerror("Error","Please Enter parameter")
        elif self.long_side1 == [] or self.long_side2 == []:
            messagebox.showerror("Error","Bounding box error")
        else:          
            # if all divide seat was named
            if seat_divide_cnt < int(divider_entry_col.get()) * int(divider_entry_row.get()) :
                col = len(self.long_side1[0]) -1

                # append data to bounding box list
                bounding_box_list.append([])
                bounding_box_list[-1].append(file_type_data.get()) #file name
                bounding_box_list[-1].append(seat_number_entry.get()) #seat number
                bounding_box_list[-1].append((self.long_side1[int(seat_divide_cnt / col)][(seat_divide_cnt % col)][0],self.long_side1[int(seat_divide_cnt / col)][(seat_divide_cnt % col)][1])) #point1 coordinate
                bounding_box_list[-1].append((self.long_side1[int(seat_divide_cnt / col)][(seat_divide_cnt % col)+1][0],self.long_side1[int(seat_divide_cnt / col)][(seat_divide_cnt % col)+1][1]))
                bounding_box_list[-1].append((self.long_side2[int(seat_divide_cnt / col)][(seat_divide_cnt % col)+1][0],self.long_side2[int(seat_divide_cnt / col)][(seat_divide_cnt % col)+1][1]))
                bounding_box_list[-1].append((self.long_side2[int(seat_divide_cnt / col)][(seat_divide_cnt % col)][0],self.long_side2[int(seat_divide_cnt / col)][(seat_divide_cnt % col)][1]))
                bounding_box_list[-1].append(floor_entry.get())
                bounding_box_list[-1].append(camera_entry.get())
                bounding_box_list[-1].append(original_table_entry.get())


                #update listbox
                self.listbox_update()

                #seat number + 1 automatically
                seat_name = seat_number_entry.get()
                seat_number_entry.delete(0,'end')
                seat_number_entry.insert(0,str(int(seat_name)+ 1))             

                seat_divide_cnt += 1
                if DEBUG_MODE:
                    print("CURRENT row: "+ str(int(seat_divide_cnt / col)) + '  col: ' +str(seat_divide_cnt % col))           

                # draw polygon to display next seat that needs to define seat_name...
                if seat_divide_cnt < int(divider_entry_col.get()) * int(divider_entry_row.get()) :
                    if len(sole_polygon) > (int(divider_entry_col.get()) * int(divider_entry_row.get())):
                        self.canvas.delete(sole_polygon[-1])
                    sole_polygon.append(self.canvas.create_polygon(self.long_side1[int(seat_divide_cnt / col)][(seat_divide_cnt % col)], 
                                                                    self.long_side1[int(seat_divide_cnt / col)][(seat_divide_cnt % col)+1],
                                                                    self.long_side2[int(seat_divide_cnt / col)][(seat_divide_cnt % col)+1],
                                                                    self.long_side2[int(seat_divide_cnt / col)][(seat_divide_cnt % col)],
                                                                    outline='yellow' , width= 5, fill=''))
                    #print(len(sole_polygon))
                # all seat value input is complete
                else:
                    global point_bounding_box_list

                    #? store undivided table coordinate
                    self.LargeTable(self.zoom.ip_img())

                    seat_divide_cnt = 0
                    point_bounding_box_list = []
                    # clean canvas
                    self.clean_canvas()

                    # clean side1 side2
                    self.long_side1 = []
                    self.long_side1 = [] 

                    #clean large table 
                    original_table_entry.delete(0,'end')
            #print("Seat cnt: " + str(seat_divide_cnt))
        
    def divide_point(self, pt1, pt2, pt3, pt4, side:str):
        print("--DIVIDE POINT--")
        '''
        return two list which contain the divided point in each long side.
        FULL LIST 1: [(280, 304), [539.0, 247.5], (798, 191)]
        FULL LIST 2: [(344, 345), [603.0, 277.5], (862, 210)]
        the list data in between the tuples is the divide point
        '''
        segment_col = int(divider_entry_col.get())
        segment_row = int(divider_entry_row.get())
        #pt1, pt2, pt3, pt4 = point_bounding_box_list

        #line (pt1,pt2) > line (pt2,pt3) 
        if math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1]) > math.hypot(pt3[0] - pt2[0], pt3[1] - pt2[1]):
            # two long side, later will insert divide point
            long_side1 = [pt1, pt2]
            long_side2 = [pt4, pt3]
            short_side1 = [pt1, pt4]
            short_side2 = [pt2, pt3]
        else:
            long_side1 = [pt2, pt3]
            long_side2 = [pt1, pt4]
            short_side1 = [pt2, pt1]
            short_side2 = [pt3, pt4]
        #print("long side 1: "+ str(long_side1))

        
        if side == 'long':
            # find long side distant
            long_side1_dist = math.hypot(long_side1[0][0] - long_side1[1][0], long_side1[0][1] - long_side1[1][1])
            long_side2_dist = math.hypot(long_side2[0][0] - long_side2[1][0], long_side2[0][1] - long_side2[1][1])

            # find image correction ratio
            # correction_ratio_col = (short side1)/ (short side2)
            correction_ratio_col = math.hypot(long_side1[0][0] - long_side2[0][0], long_side1[0][1] - long_side2[0][1]) / math.hypot(long_side1[1][0] - long_side2[1][0], long_side1[1][1] - long_side2[1][1])
            CORRECTION_RATIO_OFFSET_COL = float(image_cor_col_entry.get())
            correction_ratio_col = correction_ratio_col * CORRECTION_RATIO_OFFSET_COL
            #print("correction RATIO: " + str(correction_ratio_col))

            #find distant in each segment_col
            long_side1_seg_dist = long_side1_dist / segment_col
            long_side2_seg_dist = long_side2_dist / segment_col
            #print("DIST: "+ str(long_side1_seg_dist))

            # caculate ratio
            # ex: x_ratio = (pt2.x - pt1.x)/ dist
            long_side1_x_ratio = (long_side1[1][0] - long_side1[0][0]) / long_side1_dist
            long_side1_y_ratio = (long_side1[1][1] - long_side1[0][1]) / long_side1_dist

            long_side2_x_ratio = (long_side2[1][0] - long_side2[0][0]) / long_side2_dist
            long_side2_y_ratio = (long_side2[1][1] - long_side2[0][1]) / long_side2_dist
            #print("X RATIO: "+ str(long_side1_x_ratio))
            #print("Y RATIO: "+ str(long_side1_y_ratio))

            # caculate divide point
            long_side1_div_pt = []
            long_side2_div_pt = []

            for point in range(1,segment_col):
                long_side1_div_pt.append([(long_side1[0][0] + point * long_side1_seg_dist * long_side1_x_ratio * correction_ratio_col), (long_side1[0][1] + point * long_side1_seg_dist * long_side1_y_ratio * correction_ratio_col)])
                long_side2_div_pt.append([(long_side2[0][0] + point * long_side2_seg_dist * long_side2_x_ratio * correction_ratio_col), (long_side2[0][1] + point * long_side2_seg_dist * long_side2_y_ratio * correction_ratio_col)])
            #print("DIVIDE point: " + str(long_side1_div_pt))

            # insert divide point to original long side list
            for div_pt in range(len(long_side1_div_pt)):
                long_side1.insert(1 + div_pt ,long_side1_div_pt[div_pt])
                long_side2.insert(1 + div_pt ,long_side2_div_pt[div_pt])

            return long_side1, long_side2


        elif side == 'short':
            #find short side distant
            short_side1_dist = math.hypot(short_side1[0][0] - short_side1[1][0], short_side1[0][1] - short_side1[1][1])
            short_side2_dist = math.hypot(short_side2[0][0] - short_side2[1][0], short_side2[0][1] - short_side2[1][1])

            # find image correction ratio
            # correction_ratio_col = (long side1)/ (long side2)
            correction_ratio_row = math.hypot(short_side1[0][0] - short_side2[0][0], short_side1[0][1] - short_side2[0][1]) / math.hypot(short_side1[1][0] - short_side2[1][0], short_side1[1][1] - short_side2[1][1])
            CORRECTION_RATIO_OFFSET_ROW = float(image_cor_row_entry.get())
            correction_ratio_row = correction_ratio_row * CORRECTION_RATIO_OFFSET_ROW
            
            #find distant in each segment_row
            short_side1_seg_dist = short_side1_dist / segment_row
            short_side2_seg_dist = short_side2_dist / segment_row

            # caculate ratio
            # ex: x_ratio = (pt2.x - pt1.x)/ dist
            short_side1_x_ratio = (short_side1[1][0] - short_side1[0][0]) / short_side1_dist
            short_side1_y_ratio = (short_side1[1][1] - short_side1[0][1]) / short_side1_dist        

            short_side2_x_ratio = (short_side2[1][0] - short_side2[0][0]) / short_side2_dist
            short_side2_y_ratio = (short_side2[1][1] - short_side2[0][1]) / short_side2_dist

            short_side1_div_pt = []
            short_side2_div_pt = []

            for point in range(1,segment_row):
                short_side1_div_pt.append([(short_side1[0][0] + point * short_side1_seg_dist * short_side1_x_ratio * correction_ratio_row), (short_side1[0][1] + point * short_side1_seg_dist * short_side1_y_ratio * correction_ratio_row)])
                short_side2_div_pt.append([(short_side2[0][0] + point * short_side2_seg_dist * short_side2_x_ratio * correction_ratio_row), (short_side2[0][1] + point * short_side2_seg_dist * short_side2_y_ratio * correction_ratio_row)])

            # insert divide point to original long side list
            for div_pt in range(len(short_side1_div_pt)):
                short_side1.insert(1 + div_pt ,short_side1_div_pt[div_pt])
                short_side2.insert(1 + div_pt ,short_side2_div_pt[div_pt])

            return short_side1, short_side2
            
        else:
            pass

    # TODO: 4 point selecting tool
    def point_mouse_down(self, event):
        print('--POINT MOUSE DOWN--')
        global point_cnt, sole_polygon, point_bounding_box_list, sole_polygon_list
        seat_name=seat_number_entry.get()
        
        if point_cnt == 0:
            point_bounding_box_list = []
            sole_polygon_list = []
            point_bounding_box_list.append(((event.x+self.canvas.canvasx(0))/app.zoom,(event.y+self.canvas.canvasy(0))/app.zoom))
            #draw polygon
            sole_polygon_list.append((event.x+self.canvas.canvasx(0)))
            sole_polygon_list.append((event.y+self.canvas.canvasy(0)))
            point_cnt += 1

        elif point_cnt < 4:
            point_bounding_box_list.append(((event.x+self.canvas.canvasx(0))/app.zoom,(event.y+self.canvas.canvasy(0))/app.zoom))
            #draw polygon
            sole_polygon_list.append((event.x+self.canvas.canvasx(0)))
            sole_polygon_list.append((event.y+self.canvas.canvasy(0)))

            if point_cnt == 3:
                if sole_polygon is not None:
                    self.clean_canvas()
                sole_polygon.append(self.canvas.create_polygon(sole_polygon_list, outline='red', fill=''))
                #print(len(sole_polygon))
                point_cnt = 0
            else:
                point_cnt += 1
        print(point_bounding_box_list)


    def rect_left_mouse_down(self, event):
        print('--MOUSE DOWN--')
        global left_mouse_down_x, left_mouse_down_y
        left_mouse_down_x = event.x
        left_mouse_down_y = event.y
 
    def rect_left_mouse_up(self, event):
        print('--MOUSE UP--')
        global left_mouse_up_x, left_mouse_up_y, seat_name, seat_floor, camera_number

        left_mouse_up_x = event.x
        left_mouse_up_y = event.y
        seat_name=seat_number_entry.get()
        seat_floor=floor_entry.get()
        camera_number=camera_entry.get()

        if seat_number_entry.get() == "" or floor_entry.get() == "" or camera_entry.get() == "":
            messagebox.showerror("Error","Please Enter parameter")
        else:
            # store image coordinate
            self.corp_img((left_mouse_down_x+self.canvas.canvasx(0))/app.zoom, 
                          (left_mouse_down_y+self.canvas.canvasy(0))/app.zoom,
                          (left_mouse_up_x+self.canvas.canvasx(0))/app.zoom, 
                          (left_mouse_up_y+self.canvas.canvasy(0))/app.zoom)

            #seat number + 1 automatically
            seat_number_entry.delete(0,'end')
            seat_number_entry.insert(0,str(int(seat_name)+ 1))
    
    def rect_moving_mouse(self, event):
        #print('鼠标左键按下并移动')
        global sole_rectangle
        global left_mouse_down_x, left_mouse_down_y
        moving_mouse_x = event.x
        moving_mouse_y = event.y
        if sole_rectangle is not None:
            self.clean_canvas() # 删除前一个矩形
        sole_rectangle = self.canvas.create_rectangle((left_mouse_down_x+self.canvas.canvasx(0)),
                                                    (left_mouse_down_y+self.canvas.canvasy(0)), 
                                                    (moving_mouse_x+ self.canvas.canvasx(0)),
                                                    (moving_mouse_y+self.canvas.canvasy(0)), 
                                                    outline='red')

    def corp_img(self, x_begin, y_begin, x_end, y_end):
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
        bounding_box_list.append([])
        bounding_box_list[-1].append(file_type_data.get()) #file type
        bounding_box_list[-1].append(seat_name)
        bounding_box_list[-1].append((min_x,min_y))
        bounding_box_list[-1].append((min_x,max_y))
        bounding_box_list[-1].append((max_x,max_y))
        bounding_box_list[-1].append((max_x,min_y))
        bounding_box_list[-1].append(seat_floor)
        bounding_box_list[-1].append(camera_number)
        bounding_box_list[-1].append(original_table_entry.get())

        #update listbox
        self.listbox_update()

        if DEBUG_MODE:
            print(bounding_box_list)

    #display all bounding box on canvas
    def display_all(self):
        global bounding_box_text
        #detect if bounding box already display on canvas
        if sole_polygon == []:
            for box in bounding_box_list:
                if box[0] == 'seat':
                    sole_polygon.append(self.canvas.create_polygon(box[2][0], box[2][1], box[3][0], box[3][1], box[4][0], box[4][1], box[5][0], box[5][1], outline='red', fill='', width=3))
                    #display text for bounding box
                    bounding_box_text.append(self.canvas.create_text(box[2][0],box[2][1], text=box[1], fill= 'red', anchor="nw", font=("Helvetica", 15)))
                    bounding_box_text.append(self.canvas.create_rectangle(self.canvas.bbox(bounding_box_text[-1]),fill="white"))
                else:
                    sole_polygon.append(self.canvas.create_polygon(box[2][0], box[2][1], box[3][0], box[3][1], box[4][0], box[4][1], box[5][0], box[5][1], outline='blue', fill='',width= 3))
                    #display text for bounding box
                    bounding_box_text.append(self.canvas.create_text(box[2][0],box[2][1], text=box[1], fill= 'blue', anchor="nw", font=("Helvetica", 15)))
                    bounding_box_text.append(self.canvas.create_rectangle(self.canvas.bbox(bounding_box_text[-1]),fill="white"))
                #move rectangle under the text
                self.canvas.tag_lower(bounding_box_text[-1],bounding_box_text[-2])
            for table in large_table_list:
                sole_polygon.append(self.canvas.create_polygon(table[LTL_PT1_INDEX][0], table[LTL_PT1_INDEX][1], 
                                                                table[LTL_PT2_INDEX][0], table[LTL_PT2_INDEX][1], 
                                                                table[LTL_PT3_INDEX][0], table[LTL_PT3_INDEX][1], 
                                                                table[LTL_PT4_INDEX][0], table[LTL_PT4_INDEX][1], 
                                                                outline='black', fill=''))
                bounding_box_text.append(self.canvas.create_text(table[LTL_PT2_INDEX][0], table[LTL_PT2_INDEX][1],  text=box[BBL_ORIGINAL_T_INDEX], fill= 'black', anchor="nw", font=("Helvetica", 15)))
                bounding_box_text.append(self.canvas.create_rectangle(self.canvas.bbox(bounding_box_text[-1]),fill="white"))
                self.canvas.tag_lower(bounding_box_text[-1],bounding_box_text[-2])
        else:
            self.clean_canvas()
            
    # clear canvas
    def clean_canvas(self):
        global sole_polygon, sole_rectangle, bounding_box_text
        for polygon in sole_polygon:
            self.canvas.delete(polygon)
        sole_polygon = []

        for text in bounding_box_text:
            self.canvas.delete(text)
        bounding_box_text = []

        self.canvas.delete(sole_rectangle)
        sole_rectangle =[]

    def listbox_update(self):
        bounding_box_listbox.insert(0, "  file type   |    name    |   original t")
        bounding_box_listbox.delete(1,'end')
        for box in bounding_box_list:
            bounding_box_listbox.insert('end', "  "+ box[BBL_FILE_TYPE_INDEX] +"               "+ box[BBL_SEAT_NAME_INDEX]+"                    "+box[BBL_ORIGINAL_T_INDEX])

    def undo_event(self):
        if len(bounding_box_list)<=0:
            messagebox.showerror("Error", "Bounding box list is Empty")
        else:
            print("\n\n--UNDO--")
            bounding_box_list.pop()
            self.listbox_update()

            # if no seat refer to last large table then pop it.
            ifdel = False
            for box in bounding_box_list:
                if box[8] == large_table_list[-1][LTL_TABLE_NAME_INDEX]:
                    ifdel=False
                else:
                    ifdel=True
            if ifdel or bounding_box_list == []:
                large_table_list.pop()
            
            print("bounding: " + str(bounding_box_list))
            print("large_t: " + str(large_table_list))

class AutoScrollbar(ttk.Scrollbar):
    ''' A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager '''
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise TclError('Cannot use place with this widget')

class Zoom_Advanced(ttk.Frame):
    ''' Advanced zoom of the image '''
    def __init__(self, mainframe):
        ''' Initialize the main Frame '''
        ttk.Frame.__init__(self, master=mainframe)
        #self.master.title('Zoom with mouse wheel')
        # Vertical and horizontal scrollbars for canvas
        vbar = AutoScrollbar(self.master, orient='vertical')
        hbar = AutoScrollbar(self.master, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')
        # Create canvas and put image on it
        self.canvas = Canvas(self.master, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set, width=1200, height=675)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.canvas.update()  # wait till canvas is created
        vbar.configure(command=self.scroll_y)  # bind scrollbars to the canvas
        hbar.configure(command=self.scroll_x)
        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        
        self.zoom=1
        
    def get_ip(self):
        try:
            cap = cv2.VideoCapture('rtsp://'+ip_entry.get())
            ret, frame = cap.read()
            frame = Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
            self.image = frame  # open image
            self.width, self.height = self.image.size
            # Put image into container rectangle and use it to set proper coordinates to the image
            self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)
            self.show_image()
        except:
            messagebox.showerror("Error", "Cannot Connect")

    def ip_img(self):
        return self.image

    def scroll_y(self, *args, **kwargs):
        ''' Scroll canvas vertically and redraw the image '''
        self.canvas.yview(*args, **kwargs)  # scroll vertically
        self.show_image()  # redraw the image

    def scroll_x(self, *args, **kwargs):
        ''' Scroll canvas horizontally and redraw the image '''
        self.canvas.xview(*args, **kwargs)  # scroll horizontally
        self.show_image()  # redraw the image

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image
        

    def zoom_in(self):
        self.zoom = self.zoom*1.3
        self.show_image()

    def zoom_out(self):
        self.zoom = self.zoom/1.3
        self.show_image()

    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        self.container = self.canvas.create_rectangle(0, 0, self.width*self.zoom, self.height*self.zoom)
        self.newimage=self.image.resize((int(self.width*self.zoom), int(self.height*self.zoom)))
        bbox1 = self.canvas.bbox(self.container)  # get image area
        self.canvas.configure(scrollregion=bbox1)  # set scroll region
        bbox2 = (self.canvas.canvasx(0)+1,  # get visible area of the canvas
                 self.canvas.canvasy(0)+1,
                 self.canvas.canvasx(self.canvas.winfo_width())+1,
                 self.canvas.canvasy(self.canvas.winfo_height())+1)

        print(bbox2)
        imagetk = ImageTk.PhotoImage(self.newimage)
        imageid = self.canvas.create_image(0, 0, anchor='nw', image=imagetk)
            
        self.canvas.lower(imageid)  # set image into background
        self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection


def crop_polygon(img_path:str, point:list or tuple, **kwargs):
    '''
    crop the image with polygon mask. Background is Black.
    PIL Image format
    '''
    print("--CROP POLYGON--")

    kwarg = kwargs.get("image", None)
    if kwarg != None:
        image = kwarg
    else:
        image = Image.open(img_path)
    xy = point
    print(xy)
    #print("xy: " + str(xy))

    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(xy, fill=255, outline=None)
    black =  Image.new("L", image.size, 0)
    image_result = Image.composite(image, black, mask)
    #image_result.show()

    return image_result

# @Gareth Rees's solution
def crop_with_argwhere(image):
    # Mask of non-black pixels (assuming image has a single channel).
    mask = image 
    
    # Coordinates of non-black pixels.
    coords = np.argwhere(mask)

    # Bounding box of non-black pixels.
    x0, y0,color = coords.min(axis=0)
    x1, y1, color = coords.max(axis=0) + 1   # slices are exclusive at the top
    
    # Get the contents of the bounding box.
    cropped = image[x0:x1, y0:y1]

    return cropped

def openSetupImage(): #select an image to setup bounding box
    print("--OPEN IMAGE--")
    img_path = filedialog.askopenfilename(initialdir="/", title="open an image", filetypes= ( ("all files", "*.*"), ("jpg files", "*.jpg"), ("mp4 files", "*.mp4") ))
    
    return img_path


if __name__ == '__main__':

    global var, model

    win = Tk()
    win.title("Library Seats")
    db_xy = DB_4point_xy()

    model = load_model("table.h5")
    model.summary()
    

    #Get the current screen width and height
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    win.geometry(str(screen_width) + 'x' + str(screen_height))

    #fix the missing cursor in text box bug. cause by filedialog.
    win.update_idletasks()

    #? ====== Frame ======
    frame1 =Frame(win,bg='#0071C5',bd=5)
    frame1.grid(row=0,column=0)
    frame2=Frame(win,bg='#C4DCE4',bd=20)
    frame2.grid(row=0,column=1)
    canvas_tool=Frame(frame1, bg='#016b97',bd=3)
    canvas_tool.grid(row=2,column=0, pady=10)
    # select tool frame
    select_tool_frame = LabelFrame(frame2, text="Select Tool")
    select_tool_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky='W')
    # divider Entry frame
    divider_frame = LabelFrame(frame2, text="Divider")
    divider_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky='W')

    entry_frame = LabelFrame(frame2)
    entry_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky='W')
    #? ====== /Frame ======
    # open file as setup image with zoom function 
    app = Zoom_Advanced(frame1)
    # set tool to rect tool
    tool = Tool(app) # Selecting tools
    
    #? ============ frame 2 ===========

    #? ============ divider frame ===========
    # foreign key
    original_table_label = Label(divider_frame, text="Original \nTable ")
    original_table_label.grid(row=0, column=0, pady=5, padx=5)
    original_table_entry = Entry(divider_frame)
    original_table_entry.grid(row=0,column=1, columnspan=3)

    # devide area into segments
    divider_label = Label(divider_frame, text= 'divide into:')
    divider_label.grid(row=1, column=0, pady= 5)

    divider_entry_col = Entry(divider_frame, width= 8)
    divider_entry_col.grid(row=1, column=1, sticky=W)
    divider_entry_col.insert(0,"1")

    x_label = Label(divider_frame, text="x")
    x_label.grid(row=1, column=2 , padx= 2, sticky=W)

    divider_entry_row= Entry(divider_frame, width= 8)
    divider_entry_row.grid(row=1, column=3)
    divider_entry_row.insert(0,"1")

    # Done btn
    divider_btn = Button(divider_frame, text="Done", command= tool.divide, height=5)
    divider_btn.grid(row=1, column=4, padx=5, rowspan=2)

    # divide correction offset
    image_cor_label = Label(divider_frame, text="Image \nCorrection:\n Offset")
    image_cor_label.grid(row=2, column=0, pady= 5,padx=5)
    image_cor_col_entry = Entry(divider_frame, width=8)
    image_cor_col_entry.grid(row=2, column=1)
    image_cor_col_entry.insert(0,"1.15")

    image_cor_row_entry = Entry(divider_frame, width=8)
    image_cor_row_entry.grid(row=2, column=3)
    image_cor_row_entry.insert(0,"1")

    
    #? ============ /divider frame ===========

    #? ============ entry frame ===========
    # Option for file types
    file_type_data = StringVar()
    file_type_data.set(file_types[0])
    file_type_label = Label(entry_frame, text="File Type:")
    file_type_label.grid(row=0, column=0,ipadx=5)
    file_type_drop = OptionMenu(entry_frame, file_type_data, *file_types)
    file_type_drop.grid(column=1, row=0, ipadx=5, pady=5, sticky=W+N)

    #display all bounding box
    display_all_btn = Button(entry_frame, text="Show All", command=tool.display_all)
    display_all_btn.grid(column=1, row=0, ipadx=5, pady=5, sticky=E)

    #Seat number label and Entry
    seat_number_label = Label(entry_frame,text = "Seat number")
    seat_number_label.grid(column=0, row=2, ipadx=5, pady=5, sticky=W+N)
    seat_number_entry = Entry(entry_frame)
    seat_number_entry.grid(column=1, row=2, padx=10, pady=5, sticky=N)

    #bounding box list
    var = StringVar()
    bounding_box_listbox = Listbox(entry_frame, listvariable=var,width=30)
    bounding_box_listbox.grid(column=0, row=3, padx=10, pady=5, columnspan=2, sticky=N)
    
    #Location label and Entry
    floor_label = Label(entry_frame,text = "Floor")
    floor_label.grid(column=0, row=4, ipadx=5, pady=5, sticky=W+N)
    floor_entry = Entry(entry_frame)
    floor_entry.grid(column=1, row=4, padx=10, pady=5, sticky=N)
    
    #Camera name label and Entry
    camera_label = Label(entry_frame,text = "Camera")
    camera_label.grid(column=0, row=5, ipadx=5, pady=5, sticky=W+N)
    camera_entry = Entry(entry_frame)
    camera_entry.grid(column=1, row=5, padx=10, pady=5, sticky=N)

    next_seat_btn = Button(entry_frame, text="Next", width=10, command=tool.divide_seat)
    next_seat_btn.grid(column=0, row=6, padx=10, pady=5, columnspan=3, sticky='E')
    #? ============ /entry frame ===========

    # undo button to clear last bounding box
    undobutton = Button(frame2, text='Undo', command=tool.undo_event, width=15)
    undobutton.grid(row=6, column=0, columnspan=3)

    #create database button
    db_button = Button(frame2, text="Database", command=lambda: database_window(tool), width=15)
    db_button.grid(row=7, column=0, columnspan=3,pady=(30,0))

    #proceed to YOLO
    yolo_button = Button(frame2, text='YOLO detect', command=yolo_detect, width=15)
    yolo_button.grid(row=8, column=0, columnspan=3,pady=10)
    #? ============ /frame 2 ===========

    #? ============ frame 3 ===========
    # zoom in
    zoom_in_button = Button(canvas_tool, text='+', command=app.zoom_in, width=7)
    zoom_in_button.grid(row=0, column=0, pady=3, padx=10)

    # zoom out
    zoom_out_button = Button(canvas_tool, text='-', command=app.zoom_out, width=7)
    zoom_out_button.grid(row=0, column=1, padx=10)

    ip_entry = Entry(canvas_tool)
    ip_entry.grid(row=0, column=2, padx=(50,0))

    ip_button = Button(canvas_tool, text='enter', command=app.get_ip, width=15)
    ip_button.grid(row=0, column=3, padx=5)
    #? ============ /frame 3 ===========
    
    tool.change_tool("point")
    original_table_entry.insert(0,"1")
    seat_number_entry.insert(0,"1")
    camera_entry.insert(0,"1")
    floor_entry.insert(0,"1")
    ip_entry.insert(0,"192.168.137.211:8080/h264_pcm.sdp")

    win.mainloop()