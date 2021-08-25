import sys
import argparse
import math
#from yolo import YOLO

import os
from tkinter import *
from tkinter import filedialog, messagebox
import random
from tkinter import ttk
from yolo import YOLO
from yolo3.utils import rand
from PIL import Image, ImageTk
import requests
import cv2
import sqlite3

# store mouse position
left_mouse_down_x = 0
left_mouse_down_y = 0
left_mouse_up_x = 0
left_mouse_up_y = 0
sole_rectangle = None

# store all bounding box select by user
'''
bounding_box_list = ["file_type", "seat_name", point1, point2, point3, point4, "location", "camera_name"]
'''
bounding_box_list = []

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
TABLE_XY_NAME = "seats_4point_xy"

#file types
file_types = [
    "seat", "table"
]

class yolo_window():
    def __init__(self):
        #self.yolo = YOLO()

        yolo_win = Toplevel()
        yolo_win.title("YOLO image detection")
        yolo_win.geometry("400x400")

        # enter video path
        video_path_label = Label(yolo_win, text="Video Path: ")
        video_path_label.grid(row=0, column=0, pady=10, padx=5)
        self.video_path_entry = Entry(yolo_win)
        self.video_path_entry.grid(row=0, column=1, pady=5)

        # start detect
        yolo_done_btn = Button(yolo_win, text="Done", command=self.detect_img)
        yolo_done_btn.grid(row=5, column=0 ,columnspan=3, padx=10, pady= 10)

        if bounding_box_list == []:
            messagebox.showerror("Error", "Bounding Box is Empty")
            yolo_win.destroy()
            
    # TODO new function to list yolo detect result
    #! need new crop function!!!!!!!!
    def detect_img(self):
        pass
        if self.video_path_entry.get() == "":
            messagebox.showerror("Error","Please enter Video Path")
        else:
            video_path = self.video_path_entry.get()
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
                        for i in range(len(bounding_box_list)):
                            img=image.crop((bounding_box_list[i][1],bounding_box_list[i][2],bounding_box_list[i][3],bounding_box_list[i][4]))
                            r_image, people_num = self.yolo.detect_image(img)
                            bounding_box_list[i][5]=people_num
                            
                            postdata_toserver["seat"]=bounding_box_list[i][0]
                            postdata_toserver["location"]=bounding_box_list[i][6]
                            postdata_toserver["camera"]=bounding_box_list[i][7]
                            postdata_toserver["occupy"]=str(people_num)
                            r=requests.post('http://127.0.0.1:8000/create/', data = postdata_toserver)
                            
            yolo.close_session()

    def ok_event(self): 
        win.destroy()
        #detect_img()

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
        # commit changes
        self.conn.commit()
        # close connection
        self.conn.close()

    def select(self, table_name:str, file_name:str):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.c = self.conn.cursor()

        self.c.execute("SELECT * FROM " + table_name + " WHERE file_name = '" + file_name + "'")
        records = self.c.fetchall()
        print(records)

        self.conn.commit()
        self.conn.close()

        return records
    
    # add new file to database
    def insert(self, table_name:str, file_name:str, file_type:str, seat_name:str, pt1:list, pt2:list, pt3:list, pt4:list, location:str, camera_name:str):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.c = self.conn.cursor()
        #Insert into table
        self.c.execute("INSERT INTO "+ table_name +" VALUES (:file_name, :file_type,:seat_name, :point1_x, :point1_y, :point2_x, :point2_y, :point3_x, :point3_y, :point4_x, :point4_y, :location, :camera_name)",
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
                    'camera_name': camera_name
                })

        self.conn.commit()
        self.conn.close()

    def query(self, table_name:str):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.c = self.conn.cursor()

        self.c.execute("SELECT * FROM " + table_name)
        records = self.c.fetchall()
        print(records)

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
    def __init__(self):
        self.db_window=Toplevel()
        self.db_window.title("Database")
        self.db_window.geometry("500x400")

        self.file_list= LabelFrame(self.db_window, text="Files")
        self.file_list.grid(row=1, column= 1, padx=(0,10), pady=10)

        #show data in database
        show_query_btn = Button(self.db_window, text="show query", command=self.show_query)
        show_query_btn.grid(row=0,column= 0, pady=10, )

        #show query
        self.show_query()

        # File name box
        file_name_label = Label(self.db_window, text="File Name:")
        file_name_label.grid(row=2, column=0, pady=10)
        file_name_box = Entry(self.db_window, width=30)
        file_name_box.grid(row=2, column= 1)

        #add new data in database
        add_new_btn = Button(self.db_window, text="Add new Data", command=lambda: self.add_new(file_name_box.get()))
        add_new_btn.grid(row=3, column=0, padx=5)

        #load data in database
        load_btn = Button(self.db_window, text="Load", width=25 , command=lambda: self.load(file_name_box.get()))
        load_btn.grid(row=3, column=1)

        #delete data in database
        delete_btn = Button(self.db_window, text="Delete Data", command=lambda: self.delete_file(file_name_box.get()))
        delete_btn.grid(row=3, column=2)

        
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
                if files == [] and record[1] == 'seat':
                    files.append([])
                    files[0].append(record[0]) #file name
                    files[0].append(record[1]) #file type
                    files[0].append(1) #count seats with same file name
                    files[0].append(record[11]) #location
                    files[0].append(record[12]) #camera_name
                elif files != [] and record[1] == 'seat':
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
                    else:
                        i = files.index(index)
                        files[i][2] +=1 
                    
        #print(files)

        f_name, f_type, seat_num, locat, cam_n = '','','','',''
        for file in files:
            f_name += str(file[0]) +'\n'
            f_type += str(file[1]) +'\n'
            seat_num += str(file[2]) +'\n'
            locat += str(file[3]) +'\n'
            cam_n += str(file[4]) +'\n'

        # label for query data
        label_f_n_file = Label(self.file_list, text=f_name).grid(row=1, column= 0, pady=5, padx= 2)
        label_f_t_file = Label(self.file_list, text=f_type).grid(row=1, column= 1, pady=5, padx= 2)
        label_s_n_file = Label(self.file_list, text=seat_num).grid(row=1, column= 2, pady=5, padx= 2)
        label_loca_file = Label(self.file_list, text=locat).grid(row=1, column= 3, pady=5, padx= 2)
        label_cam_file = Label(self.file_list, text=cam_n).grid(row=1, column= 4, pady=5, padx= 2)

        # label for query title        
        label_f_n = Label(self.file_list, text="File name").grid(row=0, column= 0, pady=5, padx= 2)
        label_f_t = Label(self.file_list, text="File type").grid(row=0, column= 1, pady=5, padx= 2)
        label_s_n = Label(self.file_list, text="Seat #").grid(row=0, column= 2, pady=5, padx= 2)
        label_loca = Label(self.file_list, text="Location").grid(row=0, column= 3, pady=5, padx= 2)
        label_cam = Label(self.file_list, text="Cam name").grid(row=0, column= 4, pady=5, padx= 2)


    #add bounding_box_list to database
    def add_new(self, file_name):
        print("--ADD NEW--")
        db_win = DB_4point_xy()

        if bounding_box_list == []:
            messagebox.showerror(title="No data!",message="No bounding box") 
            self.db_window.focus()  
        else:
            for box in bounding_box_list:
                # bounding_box_list = ["file_type", "seat_name", point1, point2, point3, point4, "location", "camera_name"]
                db_win.insert(TABLE_XY_NAME, file_name, box[0], box[1], box[2], box[3], box[4], box[5],box[6],box[7])

    #load the data in database to bounding_box_list
    def load(self, file_name):
        print("--LOAD--")
        db_win = DB_4point_xy()
        
        records = db_win.select(TABLE_XY_NAME, file_name)
        bounding_box_listbox.delete(0,'end')

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

        #update listbox
        tool = Tool()
        tool.listbox_update()

        #print(bounding_box_list)

        # set default value in Entry
        seat_number_entry.delete(0,'end')
        seat_number_entry.insert(0, str(int(record[2]) + 1))
        floor_entry.delete(0,'end')
        floor_entry.insert(0, str(record[11]))
        camera_entry.delete(0,'end')
        camera_entry.insert(0, str(record[12]))
        self.db_window.destroy()
        win.focus()


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
        self.side1 = [] #logn side 1
        self.side2 = [] #logn side 2
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

            # disable widget in divider_frame
            for child in divider_frame.winfo_children():
                child.configure(state='disable')

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

            self.canvas.unbind('<MouseWheel>')
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

            # enable widget in divider_frame
            for child in divider_frame.winfo_children():
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
            
            self.canvas.unbind('<MouseWheel>')
            self.canvas.unbind('<ButtonPress-1>')
            self.canvas.unbind('<Configure>')
            self.canvas.unbind('<Button-1>')
            self.canvas.unbind('<ButtonRelease-1>')
            self.canvas.unbind('<B1-Motion>')

            self.canvas.bind('<Button-1>', self.point_mouse_down)

        elif tool.tool == "move":
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
            self.canvas.bind('<MouseWheel>', self.zoom.wheel)  # with Windows and MacOS, but not Linux

    # TODO: divide selected aera
    def divide(self):
        print("--DIVIDE--")
        if divider_entry.get() == '':
            messagebox.showerror('Error', 'Please input divider value')
        elif len(point_bounding_box_list) != 4:
            messagebox.showerror('Error', 'Bounding box error')
        else:
            #find long side
            self.side1, self.side2 = self.divide_point()

            #clean_canvas
            self.clean_canvas()
            
            # draw divided polygon
            global sole_polygon
            for cnt in range(len(self.side1) - 1):
                sole_polygon.append(self.canvas.create_polygon(self.side1[cnt], self.side1[cnt+1], self.side2[cnt+1], self.side2[cnt], outline='green', fill=''))

            print(len(sole_polygon))
            global seat_divide_cnt
            seat_divide_cnt = 0

            # draw polygon to display current seat that needs to define seat_name...
            sole_polygon.append(self.canvas.create_polygon(self.side1[seat_divide_cnt], self.side1[seat_divide_cnt+1], self.side2[seat_divide_cnt+1], self.side2[seat_divide_cnt],outline='yellow' , width= 5, fill=''))
            print(len(sole_polygon))

    # TODO: devide aear into specific seats
    def divide_seat(self):
        print("--DIVIDE SEAT--")
        global seat_divide_cnt, sole_polygon

        if seat_number_entry.get() == "" or floor_entry.get() == "" or camera_entry.get() == "":
            messagebox.showerror("Error","Please Enter parameter")
        elif self.side1 == [] or self.side2 == []:
            messagebox.showerror("Error","Bounding box error")
        else:          
            # if all divide seat was named
            if seat_divide_cnt < int(divider_entry.get()) :

                # append data to bounding box list
                bounding_box_list.append([])
                bounding_box_list[-1].append(file_type_data.get()) #file name
                bounding_box_list[-1].append(seat_number_entry.get()) #seat number
                bounding_box_list[-1].append((self.side1[seat_divide_cnt][0],self.side1[seat_divide_cnt][1])) #point1 coordinate
                bounding_box_list[-1].append((self.side1[seat_divide_cnt+1][0],self.side1[seat_divide_cnt+1][1]))
                bounding_box_list[-1].append((self.side2[seat_divide_cnt+1][0],self.side2[seat_divide_cnt+1][1]))
                bounding_box_list[-1].append((self.side2[seat_divide_cnt][0],self.side2[seat_divide_cnt][1]))
                bounding_box_list[-1].append(floor_entry.get())
                bounding_box_list[-1].append(camera_entry.get())

                #update listbox
                self.listbox_update()

                #seat number + 1 automatically
                seat_name = seat_number_entry.get()
                seat_number_entry.delete(0,'end')
                seat_number_entry.insert(0,str(int(seat_name)+ 1))             
            
                print(bounding_box_list)

                seat_divide_cnt += 1

                # draw polygon to display next seat that needs to define seat_name...
                if seat_divide_cnt < int(divider_entry.get()) :
                    if len(sole_polygon) > (int(divider_entry.get())):
                        self.canvas.delete(sole_polygon[-1])
                    sole_polygon.append(self.canvas.create_polygon(self.side1[seat_divide_cnt], self.side1[seat_divide_cnt+1], self.side2[seat_divide_cnt+1], self.side2[seat_divide_cnt],outline='yellow' , width= 5, fill=''))
                    print(len(sole_polygon))
                # all seat value input is complete
                else:
                    global point_bounding_box_list
                    seat_divide_cnt = 0
                    point_bounding_box_list = []
                    # clean canvas
                    self.clean_canvas()

                    # clean side1 side2
                    self.side1 = []
                    self.side1 = [] 
            #print("Seat cnt: " + str(seat_divide_cnt))
        
    def divide_point(self):
        print("--DIVIDE POINT--")
        '''
        return two list which contain the divided point in each long side.
        FULL LIST 1: [(280, 304), [539.0, 247.5], (798, 191)]
        FULL LIST 2: [(344, 345), [603.0, 277.5], (862, 210)]
        the list data in between the tuples is the divide point
        '''
        segment = int(divider_entry.get())
        pt1, pt2, pt3, pt4 = point_bounding_box_list

        #line (pt1,pt2) > line (pt2,pt3) 
        if math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1]) > math.hypot(pt3[0] - pt2[0], pt3[1] - pt2[1]):
            # two long side, later will insert divide point
            long_side1 = [pt1, pt2]
            long_side2 = [pt4, pt3]
        else:
            long_side1 = [pt2, pt3]
            long_side2 = [pt1, pt4]
        #print("long side 1: "+ str(long_side1))

        # find long side distant
        long_side1_dist = math.hypot(long_side1[0][0] - long_side1[1][0], long_side1[0][1] - long_side1[1][1])
        long_side2_dist = math.hypot(long_side2[0][0] - long_side2[1][0], long_side2[0][1] - long_side2[1][1])

        # find image correction ratio
        # correction_ratio = (short side1)/ (short side2)
        correction_ratio = math.hypot(long_side1[0][0] - long_side2[0][0], long_side1[0][1] - long_side2[0][1]) / math.hypot(long_side1[1][0] - long_side2[1][0], long_side1[1][1] - long_side2[1][1])
        CORRECTION_RATIO_OFFSET = float(image_cor_entry.get())
        correction_ratio = correction_ratio * CORRECTION_RATIO_OFFSET
        #print("correction RATIO: " + str(correction_ratio))

        #find distant in each segment
        long_side1_seg_dist = long_side1_dist / segment
        long_side2_seg_dist = long_side2_dist / segment
        #print("DIST: "+ str(long_side1_seg_dist))

        # caculate ratio
        # ex: x_ratio = (pt2.x - pt1.x)/ dist
        long_side1_x_ratio = (long_side1[1][0] - long_side1[0][0]) / long_side1_dist
        long_side1_y_ratio = (long_side1[1][1] - long_side1[0][1]) / long_side1_dist
        #print("X RATIO: "+ str(long_side1_x_ratio))
        #print("Y RATIO: "+ str(long_side1_y_ratio))

        long_side2_x_ratio = (long_side2[1][0] - long_side2[0][0]) / long_side2_dist
        long_side2_y_ratio = (long_side2[1][1] - long_side2[0][1]) / long_side2_dist

        # caculate divide point
        long_side1_div_pt = []
        long_side2_div_pt = []

        for point in range(1,segment):
            long_side1_div_pt.append([(long_side1[0][0] + point * long_side1_seg_dist * long_side1_x_ratio * correction_ratio), (long_side1[0][1] + point * long_side1_seg_dist * long_side1_y_ratio * correction_ratio)])
            long_side2_div_pt.append([(long_side2[0][0] + point * long_side2_seg_dist * long_side2_x_ratio * correction_ratio), (long_side2[0][1] + point * long_side2_seg_dist * long_side2_y_ratio * correction_ratio)])
        #print("DIVIDE point: " + str(long_side1_div_pt))

        # insert divide point to original long side list
        for div_pt in range(len(long_side1_div_pt)):
            long_side1.insert(1 + div_pt ,long_side1_div_pt[div_pt])
            long_side2.insert(1 + div_pt ,long_side2_div_pt[div_pt])
        #print("FULL LIST 1: " + str(long_side1))
        #print("FULL LIST 2: " + str(long_side2))

        return long_side1, long_side2

    # TODO: 4 point selecting tool
    def point_mouse_down(self, event):
        print('--POINT MOUSE DOWN--')
        global point_cnt, sole_polygon, point_bounding_box_list, sole_polygon_list
        seat_name=seat_number_entry.get()
        

        if point_cnt == 0:
            point_bounding_box_list = []
            sole_polygon_list = []
            point_bounding_box_list.append((event.x,event.y))
            #draw polygon
            sole_polygon_list.append(event.x)
            sole_polygon_list.append(event.y)
            point_cnt += 1

        elif point_cnt < 4:
            point_bounding_box_list.append((event.x,event.y))
            #draw polygon
            sole_polygon_list.append(event.x)
            sole_polygon_list.append(event.y)

            if point_cnt == 3:
                if sole_polygon is not None:
                    self.clean_canvas()
                sole_polygon.append(self.canvas.create_polygon(sole_polygon_list, outline='red', fill=''))
                print(len(sole_polygon))
                point_cnt = 0
            else:
                point_cnt += 1
        #print(point_bounding_box_list)


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
            self.corp_img(img_path, 'one_corp.jpg', 
                        left_mouse_down_x+self.canvas.canvasx(0), 
                        left_mouse_down_y+self.canvas.canvasy(0),
                        left_mouse_up_x+self.canvas.canvasx(0), 
                        left_mouse_up_y+self.canvas.canvasy(0))

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
        sole_rectangle = self.canvas.create_rectangle(left_mouse_down_x+self.canvas.canvasx(0),
                                                    left_mouse_down_y+self.canvas.canvasy(0), 
                                                    moving_mouse_x+ self.canvas.canvasx(0),
                                                    moving_mouse_y+self.canvas.canvasy(0), 
                                                    outline='red')

    def corp_img(self,source_path, save_path, x_begin, y_begin, x_end, y_end):
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

        #update listbox
        self.listbox_update()

        print(bounding_box_list)

    #display all bounding box on canvas
    def display_all(self):
        global bounding_box_text
        #detect if bounding box already display on canvas
        if sole_polygon == []:
            for box in bounding_box_list:
                if box[0] == 'seat':
                    sole_polygon.append(self.canvas.create_polygon(box[2][0], box[2][1], box[3][0], box[3][1], box[4][0], box[4][1], box[5][0], box[5][1], outline='red', fill=''))
                    #display text for bounding box
                    bounding_box_text.append(self.canvas.create_text(box[2][0],box[2][1], text=box[1], fill= 'red', anchor="nw", font=("Helvetica", 15)))
                    bounding_box_text.append(self.canvas.create_rectangle(self.canvas.bbox(bounding_box_text[-1]),fill="white"))
                else:
                    sole_polygon.append(self.canvas.create_polygon(box[2][0], box[2][1], box[3][0], box[3][1], box[4][0], box[4][1], box[5][0], box[5][1], outline='yellow', fill=''))
                    #display text for bounding box
                    bounding_box_text.append(self.canvas.create_text(box[2][0],box[2][1], text=box[1], fill= 'blue', anchor="nw", font=("Helvetica", 15)))
                    bounding_box_text.append(self.canvas.create_rectangle(self.canvas.bbox(bounding_box_text[-1]),fill="white"))
                #move rectangle under the text
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
        bounding_box_listbox.insert(0, "  file type   |    seat name")
        bounding_box_listbox.delete(1,'end')
        for box in bounding_box_list:
            bounding_box_listbox.insert('end', "  "+ box[0] +"                    "+ box[1])

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
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')

class Zoom_Advanced(ttk.Frame):
    ''' Advanced zoom of the image '''
    def __init__(self, mainframe, path):
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
        
        self.image = Image.open(path)  # open image
        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.show_image()

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

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        else: return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30: return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale        /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale        *= self.delta
        self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        self.show_image()

    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        bbox1 = self.canvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.canvas.configure(scrollregion=bbox)  # set scroll region
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]

        print("x1: " + str(x1) + " y1: " + str(y1) + " x2: " + str(x2) + " y2: " + str(y2))
        #print(bbox1)
        #print(bbox2)
        #print(bbox)
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.width)   # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not
            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                               anchor='nw', image=imagetk)
            self.canvas.lower(imageid)  # set image into background
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection
            

def undo_event():
    tool = Tool()
    if len(bounding_box_list)>0:
        bounding_box_list.pop()
        tool.listbox_update()
        print("--UNDO--")
        print(bounding_box_list)

def openSetupImage(): #select an image to setup bounding box
    print("--OPEN IMAGE--")
    global setup_img, setup_image, img_path
    #img_path = filedialog.askopenfilename(initialdir="/", title="open an image", filetypes= ( ("all files", "*.*"), ("jpg files", "*.jpg") ))
    img_path = "test_image/diff2.jpg"
    image = Image.open(img_path)
    #setup_image=image.resize((1200, 675))
    #setup_img = ImageTk.PhotoImage(setup_image)

if __name__ == '__main__':

    global var

    win = Tk()
    win.title("Library Seats")
    db_xy = DB_4point_xy()
    

    #Get the current screen width and height
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    win.geometry(str(screen_width) + 'x' + str(screen_height))

    #fix the missing cursor in text box bug. cause by filedialog.
    win.update_idletasks()

    #? ====== Frame ======
    frame1 =Frame(win,bg='red',bd=10)
    frame1.grid(row=0,column=0)
    frame2=Frame(win,bg='yellow',bd=20)
    frame2.grid(row=0,column=1)
    # select tool frame
    select_tool_frame = LabelFrame(frame2, text="Select Tool")
    select_tool_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky='W')
    # divider Entry frame
    divider_frame = LabelFrame(frame2, text="Divider")
    divider_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky='W')

    entry_frame = LabelFrame(frame2)
    entry_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky='W')
    #? ====== Frame ======
    
    #! +++++++++++++++++++++
    img_path = "test_image/diff2.jpg"
    app = Zoom_Advanced(frame1, img_path)

    # set tool to rect tool
    tool = Tool(app) # Selecting tools
    

    #? ============ frame 2 ===========

    #? ============ divider frame ===========
    divider_label = Label(divider_frame, text= 'divide into:')
    divider_label.grid(row=0, column=0, pady= 5)
    divider_entry = Entry(divider_frame)
    divider_entry.grid(row=0, column=1)
    divider_entry.insert(0,"1")
    divider_btn = Button(divider_frame, text="Done", command= tool.divide, height=5)
    divider_btn.grid(row=0, column=2, padx=5, rowspan=2)

    image_cor_label = Label(divider_frame, text="Image \nCorrection:\n Offset")
    image_cor_label.grid(row=1, column=0, pady= 5,padx=5)
    image_cor_entry = Entry(divider_frame)
    image_cor_entry.grid(row=1, column=1)
    image_cor_entry.insert(0,"1.15")
    #? ============ divider frame ===========

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
    bounding_box_listbox = Listbox(entry_frame, listvariable=var)
    bounding_box_listbox.grid(column=1, row=3, padx=10, pady=5, sticky=N)
    
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
    #? ============ entry frame ===========

    # undo button to clear last bounding box
    undobutton = Button(frame2, text='Undo', command=undo_event, width=15)
    undobutton.grid(row=6, column=0, columnspan=3)

    #create database button
    db_button = Button(frame2, text="Database", command=database_window, width=15)
    db_button.grid(row=7, column=0, columnspan=3,pady=(30,0))

    #proceed to YOLO
    okbutton = Button(frame2, text='YOLO detect', command=yolo_window, width=15)
    okbutton.grid(row=8, column=0, columnspan=3,pady=10)
    #? ============ frame 2 ===========

    

    #select a image to setup bounding box
    #openSetupImage() 
    
    
    '''
    #bulit canvas
    setup_image_x, setup_image_y = setup_image.size
    canvas = Canvas(frame1, width=setup_image_x, height=setup_image_y, bg='pink')
    i = canvas.create_image(0, 0, anchor='nw', image=setup_img)
    canvas.pack()
    '''
    tool.change_tool("move")

    win.mainloop()
    
   
