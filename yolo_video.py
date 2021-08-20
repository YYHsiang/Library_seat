import sys
import argparse
import math
#from yolo import YOLO

import os
from tkinter import *
from tkinter import filedialog, messagebox
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
bounding_box_list = ["seat_name", point1, point2, point3, point4, 0, "location", "camera_name"]
'''
bounding_box_list = []

# 4 point clicking counter
point_cnt = 0
sole_polygon = None
point_bounding_box_list = [] #temporally store bound for future use
sole_polygon_list = [] # for draw polygon

#x=YOLO()
postdata_toserver = {"seat": "0", "location": "1F", "occupy": "1","camera": "0"}

#database path
DATABASE_PATH = "database/bounding_box.db"
TABLE_NAME = "seats_4point"

class DB_4point():
    def __init__(self):
        # create a database or connect one
        self.conn = sqlite3.connect(DATABASE_PATH)
        #create a cursor
        self.c = self.conn.cursor()

        # create a table
        '''
        self.c.execute("""CREATE TABLE seats_4point(
            file_name text,
            seat_name text,
            point1 integer,
            point2 integer,
            point3 integer,
            point4 integer,
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
    def insert(self, table_name:str, file_name:str, seat_name:str, pt1:int, pt2:int, pt3:int, pt4:int, location:str, camera_name:str):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.c = self.conn.cursor()
        #Insert into table
        self.c.execute("INSERT INTO "+ table_name +" VALUES (:file_name, :seat_name, :point1, :point2, :point3, :point4, :location, :camera_name)",
                {
                    'file_name': file_name,
                    'seat_name': seat_name,
                    'point1':pt1,
                    'point2':pt2,
                    'point3':pt3,
                    'point4':pt4,
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

    #edit file
    def update(self, file_name:str, table_name:str,seat_name:str, pt1:int, pt2:int, pt3:int, pt4:int, location:str, camera_name:str, oid:int):
        self.conn = sqlite3.connect(DATABASE_PATH)
        c = self.conn.cursor()

        c.execute("UPDATE "+ table_name +" SET""""
        file_name = :file_name,
        seat_name = :seat_name, 
        point1 = :pt1, 
        point2 = :pt2, 
        point3 = :pt3, 
        point4 = :pt4, 
        location = :location, 
        camera_name = :camera_name

        WHERE oid = :oid""",
        {   
            'file_name': file_name,
            'seat_name': seat_name,
            'pt1': pt1,
            'pt2': pt2,
            'pt3': pt3,
            'pt4': pt4,
            'location': location,
            'camera_name': camera_name,
            'oid': oid,
        })

        self.conn.commit()
        self.conn.close()

class database_window():
    def __init__(self):
        self.db_window=Toplevel()
        self.db_window.title("Database")
        self.db_window.geometry("420x400")

        self.file_list= LabelFrame(self.db_window, text="Files")
        self.file_list.grid(row=1, column= 1, padx=(0,10), pady=10)

        #show data in database
        show_query_btn = Button(self.db_window, text="show query", command=self.show_query)
        show_query_btn.grid(row=0,column= 0, pady=10)

        #show query
        self.show_query()

        # File name box
        file_name_label = Label(self.db_window, text="File Name:")
        file_name_label.grid(row=2, column=0, pady=10)
        file_name_box = Entry(self.db_window, width=30)
        file_name_box.grid(row=2, column= 1)

        #add new data in database
        add_new_btn = Button(self.db_window, text="Add new Data", command=lambda: self.add_new(file_name_box.get()))
        add_new_btn.grid(row=3, column=0)

        #load data in database
        delete_btn = Button(self.db_window, text="Load", width=25 , command=lambda: self.load(file_name_box.get()))
        delete_btn.grid(row=3, column=1)

        #delete data in database
        delete_btn = Button(self.db_window, text="Delete Data", command=lambda: self.delete_file(file_name_box.get()))
        delete_btn.grid(row=3, column=2)

        
    # show all files in db
    def show_query(self):
        print("--SHOW QUERY--")
        db_win = DB_4point()
        db_win_records = db_win.query(TABLE_NAME)

        files = []
        '''
        2d array=[[file_name, seat_cnt, location, camera_name], [...],...]
        '''
        if db_win_records is None:
            messagebox.showerror("No data", "Database is Empty!")
        else:
            for record in db_win_records:
                # collect all file name, assume SAME file_name with SAME location and camera_name
                if files == []:
                    files.append([])
                    files[0].append(record[0])
                    files[0].append(1) #count seats with same file name
                    files[0].append(record[6]) #location
                    files[0].append(record[7]) #camera_name
                else:
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
                        files[-1].append(record[0])
                        files[-1].append(1) #count seats with same file name
                        files[-1].append(record[6]) #location
                        files[-1].append(record[7]) #camera_name

                    #if file name in record doesnt exist in file, then add one.
                    else:
                        i = files.index(index)
                        files[i][1] +=1 
                    
        print(files)
        f_name, seat_num, locat, cam_n = '','','',''
        for file in files:
            f_name += str(file[0]) +'\n'
            seat_num += str(file[1]) +'\n'
            locat += str(file[2]) +'\n'
            cam_n += str(file[3]) +'\n'

        # label for query data
        label_f_n_file = Label(self.file_list, text=f_name).grid(row=1, column= 0, pady=5, padx= 2)
        label_s_n_file = Label(self.file_list, text=seat_num).grid(row=1, column= 1, pady=5, padx= 2)
        label_loca_file = Label(self.file_list, text=locat).grid(row=1, column= 2, pady=5, padx= 2)
        label_cam_file = Label(self.file_list, text=cam_n).grid(row=1, column= 3, pady=5, padx= 2)

        # label for query title        
        label_f_n = Label(self.file_list, text="File name").grid(row=0, column= 0, pady=5, padx= 2)
        label_s_n = Label(self.file_list, text="Seat #").grid(row=0, column= 1, pady=5, padx= 2)
        label_loca = Label(self.file_list, text="Location").grid(row=0, column= 2, pady=5, padx= 2)
        label_cam = Label(self.file_list, text="Cam name").grid(row=0, column= 3, pady=5, padx= 2)


    #add bounding_box_list to database
    def add_new(self, file_name):
        print("--ADD NEW--")
        db_win = DB_4point()

        if bounding_box_list == []:
            messagebox.showerror(title="No data!",message="No bounding box") 
            self.db_window.focus()  
        else:
            for box in bounding_box_list:
                db_win.insert(TABLE_NAME, file_name, box[0], box[1], box[2], box[3], box[4], box[6], box[7])

    #load the data in database to bounding_box_list
    def load(self, file_name):
        print("--LOAD--")
        db_win = DB_4point()
        
        records = db_win.select(TABLE_NAME, file_name)
        bounding_box_listbox.delete(0,'end')

        global bounding_box_list
        bounding_box_list = []
        for record in records:
            #set entry to previous value
            bounding_box_listbox.insert('end', record[1])

            bounding_box_list.append([])
            bounding_box_list[(len(bounding_box_list)-1)].append(record[1])
            bounding_box_list[(len(bounding_box_list)-1)].append(record[2])
            bounding_box_list[(len(bounding_box_list)-1)].append(record[3])
            bounding_box_list[(len(bounding_box_list)-1)].append(record[4])
            bounding_box_list[(len(bounding_box_list)-1)].append(record[5])
            bounding_box_list[(len(bounding_box_list)-1)].append(0)
            bounding_box_list[(len(bounding_box_list)-1)].append(record[6])
            bounding_box_list[(len(bounding_box_list)-1)].append(record[7])

        #print(bounding_box_list)
        seat_number_entry.delete(0,'end')
        seat_number_entry.insert(0, str(int(record[1]) + 1))
        floor_entry.delete(0,'end')
        floor_entry.insert(0, str(record[6]))
        camera_entry.delete(0,'end')
        camera_entry.insert(0, str(record[7]))
        self.db_window.destroy()
        win.focus()


    #delete bounding_box_list in database
    def delete_file(self, file_name):
        db_win = DB_4point()

        response = messagebox.askyesno(title="Delete", message="Delete the file?")
        if response == 1:
            db_win.delete(TABLE_NAME, file_name) 
            self.db_window.focus() 

class Tool():
    def __init__(self):
        self.tool = "rect"

        #? ============ select tool frame ===========
        rect_select_btn = Button(select_tool_frame, text="Rect", command= lambda: self.change_tool("rect"), width=5)
        rect_select_btn.grid(row=0, column=0,padx= 10,pady= 5)

        point_select_btn = Button(select_tool_frame, text="Point", command= lambda: self.change_tool("point"), width=5)
        point_select_btn.grid(row=0, column=1, padx=10)
        #? ============ select tool frame ===========

    def change_tool(self, tool_name:str):
        global bounding_box_list

        if tool_name is None:
            messagebox.messagebox.showwarning("Wearning", "Please select tool")
        else:
            print("--" + tool_name + " TOOL--")
            self.tool = tool_name
            bounding_box_listbox.delete(0,'end')
            canvas.delete(sole_polygon)
            canvas.delete(sole_rectangle)

        if self.tool == "rect":
            #print("rectttt")
            bounding_box_list = []

            # recreate button to dispaly DISABLE
            rect_select_btn = Button(select_tool_frame, text="Rect", state= DISABLED, 
                                    command= lambda: self.change_tool("rect"), width=5)
            rect_select_btn.grid(row=0, column=0,padx= 10,pady= 5)

            point_select_btn = Button(select_tool_frame, text="Point", state= NORMAL, 
                                    command= lambda: self.change_tool("point"), width=5)
            point_select_btn.grid(row=0, column=1, padx=10)

            canvas.unbind('<Button-1>')
            canvas.unbind('<ButtonRelease-1>')
            canvas.unbind('<B1-Motion>')
            canvas.bind('<Button-1>', self.rect_left_mouse_down) # 鼠标左键按下
            canvas.bind('<ButtonRelease-1>', self.rect_left_mouse_up) # 鼠标左键释放
            canvas.bind('<B1-Motion>', self.rect_moving_mouse) # 鼠标左键按下并移动

        elif tool.tool == "point":
            #print("pointtttt")
            bounding_box_list = []
            point_cnt = 0
            # recreate button to dispaly DISABLE
            rect_select_btn = Button(select_tool_frame, text="Rect", state= NORMAL,
                                command= lambda: self.change_tool("rect"), width=5)
            rect_select_btn.grid(row=0, column=0,padx= 10,pady= 5)

            point_select_btn = Button(select_tool_frame, text="Point", state= DISABLED,
                                command= lambda: self.change_tool("point"), width=5)
            point_select_btn.grid(row=0, column=1, padx=10)

            canvas.unbind('<Button-1>')
            canvas.unbind('<ButtonRelease-1>')
            canvas.unbind('<B1-Motion>')
            canvas.bind('<Button-1>', self.point_mouse_down)

    # TODO: divide selected aera
    def divide(self):
        if divider_entry.get() == '' or len(point_bounding_box_list) != 4:
            messagebox.showerror('Error', 'Wrong input value')
        else:
            #find long side
            side1, side2 = self.divide_point()
    
    def divide_point(self):
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
            long_side1_div_pt.append([(long_side1[0][0] + point * long_side1_seg_dist * long_side1_x_ratio), (long_side1[0][1] + point * long_side1_seg_dist * long_side1_y_ratio)])
            long_side2_div_pt.append([(long_side2[0][0] + point * long_side2_seg_dist * long_side2_x_ratio), (long_side2[0][1] + point * long_side2_seg_dist * long_side2_y_ratio)])
        #print("DIVIDE point: " + str(long_side1_div_pt))

        # insert divide point to original long side list
        for div_pt in range(len(long_side1_div_pt)):
            long_side1.insert(1 + div_pt ,long_side1_div_pt[div_pt])
            long_side2.insert(1 + div_pt ,long_side2_div_pt[div_pt])
        print("FULL LIST 1: " + str(long_side1))
        print("FULL LIST 2: " + str(long_side2))

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
                    canvas.delete(sole_polygon) # 删除前一个矩形
                sole_polygon = canvas.create_polygon(sole_polygon_list, outline='red', fill='')

                point_cnt = 0
            else:
                point_cnt += 1
        print(point_bounding_box_list)

        '''
        if seat_number_entry.get() == "" or floor_entry.get() == "" or camera_entry.get() == "":
            messagebox.showerror("Error","Please Enter parameter")
        else:
            if point_cnt == 0:
                bounding_box_list.append([])
                bounding_box_list[(-1)].append(seat_number_entry.get())
                bounding_box_list[(-1)].append(event.x)
                bounding_box_list[(-1)].append(event.y)
                point_cnt += 1

            elif point_cnt < 4:
                bounding_box_list[(-1)].append(event.x)
                bounding_box_list[(-1)].append(event.y)

                if point_cnt == 3:
                    bounding_box_list[-1].append(0)
                    bounding_box_list[-1].append(floor_entry.get())
                    bounding_box_list[-1].append(camera_entry.get())
                    # add seat name to bounding_box_listbox
                    bounding_box_listbox.insert('end', seat_number_entry.get())
                    #seat number + 1 automatically
                    seat_number_entry.delete(0,'end')
                    seat_number_entry.insert(0,str(int(seat_name)+ 1))

                    if sole_polygon is not None:
                        canvas.delete(sole_polygon) # 删除前一个矩形
                    sole_polygon = canvas.create_polygon(bounding_box_list[-1][1:9], outline='red', fill='')

                    point_cnt = 0
                else:
                    point_cnt += 1

        print(bounding_box_list)
        '''


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
            bounding_box_listbox.insert('end', seat_name)
            corp_img(img_path, 'one_corp.jpg', left_mouse_down_x, left_mouse_down_y,
            left_mouse_up_x, left_mouse_up_y)

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
            canvas.delete(sole_rectangle) # 删除前一个矩形
        sole_rectangle = canvas.create_rectangle(left_mouse_down_x, left_mouse_down_y, moving_mouse_x,
                        moving_mouse_y, outline='red')

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
                for i in range(len(bounding_box_list)):
                    img=image.crop((bounding_box_list[i][1],bounding_box_list[i][2],bounding_box_list[i][3],bounding_box_list[i][4]))
                    r_image, people_num = yolo.detect_image(img)
                    bounding_box_list[i][5]=people_num
                    
                    postdata_toserver["seat"]=bounding_box_list[i][0]
                    postdata_toserver["location"]=bounding_box_list[i][6]
                    postdata_toserver["camera"]=bounding_box_list[i][7]
                    postdata_toserver["occupy"]=str(people_num)
                    r=requests.post('http://127.0.0.1:8000/create/', data = postdata_toserver)
                    
    yolo.close_session()

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
    bounding_box_list.append([])
    bounding_box_list[-1].append(seat_name)
    bounding_box_list[-1].append(min_x)
    bounding_box_list[-1].append(min_y)
    bounding_box_list[-1].append(max_x)
    bounding_box_list[-1].append(max_y)
    bounding_box_list[-1].append(0)
    bounding_box_list[-1].append(seat_floor)
    bounding_box_list[-1].append(camera_number)
    print(bounding_box_list)

def undo_event():
    if len(bounding_box_list)>0:
        bounding_box_list.pop()
        bounding_box_listbox.delete(len(bounding_box_list))
        print("--UNDO--")
        print(bounding_box_list)

def openSetupImage(): #select an image to setup bounding box
    print("--OPEN IMAGE--")
    global setup_img, setup_image, img_path
    #img_path = filedialog.askopenfilename(initialdir="/", title="open an image", filetypes= ( ("all files", "*.*"), ("jpg files", "*.jpg") ))
    img_path = "test_image/seat_angle1_ref.jpg"
    image = Image.open(img_path)
    setup_image=image.resize((1200, 600))
    setup_img = ImageTk.PhotoImage(setup_image)

if __name__ == '__main__':

    global var

    win = Tk()
    db = DB_4point() # data base
    

    #Get the current screen width and height
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    win.geometry(str(screen_width) + 'x' + str(screen_height))

    #fix the missing cursor in text box bug. cause by filedialog.
    win.update_idletasks()

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

    # set tool to rect tool
    tool = Tool() # Selecting tools
    
    #? ============ divider frame ===========
    divider_label = Label(divider_frame, text= 'divide into:')
    divider_label.grid(row=0, column=0, pady= 5)
    divider_entry = Entry(divider_frame)
    divider_entry.grid(row=0, column=1)
    divider_entry.insert(0,"1")
    divider_btn = Button(divider_frame, text="Done", command= tool.divide)
    divider_btn.grid(row=0, column=2, padx=5)
    #? ============ divider frame ===========

    #? ============ frame 2 ===========
    #Seat number label and Entry
    seat_number_label = Label(frame2,text = "Seat number")
    seat_number_label.grid(column=0, row=2, ipadx=5, pady=5, sticky=W+N)
    seat_number_entry = Entry(frame2)
    seat_number_entry.grid(column=1, row=2, padx=10, pady=5, sticky=N)

    #bounding box list
    var = StringVar()
    bounding_box_listbox = Listbox(frame2, listvariable=var)
    bounding_box_listbox.grid(column=1, row=3, padx=10, pady=5, sticky=N)
    
    #Location label and Entry
    floor_label = Label(frame2,text = "Floor")
    floor_label.grid(column=0, row=4, ipadx=5, pady=5, sticky=W+N)
    floor_entry = Entry(frame2)
    floor_entry.grid(column=1, row=4, padx=10, pady=5, sticky=N)
    
    #Camera name label and Entry
    camera_label = Label(frame2,text = "Camera")
    camera_label.grid(column=0, row=5, ipadx=5, pady=5, sticky=W+N)
    camera_entry = Entry(frame2)
    camera_entry.grid(column=1, row=5, padx=10, pady=5, sticky=N)

    # undo button to clear last bounding box
    undobutton = Button(frame2, text='Undo', command=undo_event, width=15)
    undobutton.grid(row=6, column=0, columnspan=1)

    #create database button
    db_button = Button(frame2, text="Database", command=database_window, width=15)
    db_button.grid(row=7, column=0, columnspan=3,pady=(30,0))

    #proceed to YOLO
    okbutton = Button(frame2, text='YOLO detect', command=ok_event, width=15)
    okbutton.grid(row=8, column=0, columnspan=3,pady=10)
    #? ============ frame 2 ===========

    

    #select a image to setup bounding box
    openSetupImage() 
    
    #bulit canvas
    setup_image_x, setup_image_y = setup_image.size
    canvas = Canvas(frame1, width=setup_image_x, height=setup_image_y, bg='pink')
    i = canvas.create_image(0, 0, anchor='nw', image=setup_img)
    canvas.pack()

    tool.change_tool("rect")

    win.mainloop()
    
   
