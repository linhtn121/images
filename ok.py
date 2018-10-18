import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
import xml.etree.ElementTree as ET
import os
imgsDir = 'JPEGImages'
annoDir = 'Annotations'
pwdImgs = os.getcwd() + '/' + imgsDir
pwdAnnoDir = os.getcwd() + '/' + annoDir

class App:
     def __init__(self, window, window_title, video_source=0):
         self.window = window
         self.window.title(window_title)
         self.video_source = video_source
         self.arr_head = []
 
         # open video source (by default this will try to open the computer webcam)
         self.vid = MyVideoCapture(self.video_source)
 
         # Create a canvas that can fit the above video source size
         self.canvas = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height)
		 
         self.canvas.bind("<ButtonPress-1>", self.on_button_press)
         self.canvas.bind("<B1-Motion>", self.on_move_press)
         self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
		 			
         self.rect = None
         self.isUpdate = True
         self.start_x = None
         self.start_y = None
         self.curX = None
         self.curY = None
         self.frame = None
         self.x = self.y = 0
         #self.canvas.bind("<Key-Up>", self.handle_up_key)
         self.window.bind('<KeyRelease>', self.handle_up_key)
         self.canvas.pack()
 
         # Button that lets the user take a snapshot
         self.btn_snapshot=tkinter.Button(window, text="Save", width=50, command=self.snapshot)
         self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)
         self.btn_snapshot['state'] = 'disable'
 
         self.btn_pause = tkinter.Button(window, text = "Pause", width =50, command = self.on_pause)
         self.btn_pause.pack()

         # After it is called once, the update method will be automatically called every delay milliseconds
         self.delay = 15
         self.update()
 
         self.window.mainloop()
     def handle_up_key(self, event):
         print('hand key up')
         if self.isUpdate:
            self.isUpdate = False
            self.btn_snapshot['state'] = 'normal'
            self.btn_pause['text'] = 'Continue'
         else:
            self.btn_pause['text'] = 'Pause'
            self.btn_snapshot['state'] = 'disable'
            self.isUpdate = True
            self.window.after(self.delay, self.update)
     def snapshot(self):
         # Get a frame from the video source
         if len(self.arr_head) <=0:
             return
         filename = time.strftime("%d-%m-%Y-%H-%M-%S")
         path_image = pwdImgs + '/' + filename + '.jpg'
         self.annotate_saving(filename, path_image)
         cv2.imwrite(path_image, cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))
         print('saved')
     
     def annotate_saving(self, _filename, path_image):
         global pwdAnnoDir

         annotation = ET.Element('annotation')  
         folder = ET.SubElement(annotation, 'folder') 
         folder.text = 'JPEGImages'   
         filename = ET.SubElement(annotation, 'filename')  
         filename.text = _filename
         path = ET.SubElement(annotation, 'path')  
         path.text = path_image
         source = ET.SubElement(annotation, 'source')  
         database = ET.SubElement(source, 'database')  

         size = ET.SubElement(annotation, 'size')  
         segmented = ET.SubElement(annotation, 'segmented')  
         segmented.text = '0'
 
         for val in self.arr_head:
             object = ET.SubElement(annotation, 'object')  
             name = ET.SubElement(object, 'name') 
             name.text = 'head' 
             pose = ET.SubElement(object, 'pose') 
             pose.text = 'Unspecified' 
             truncated = ET.SubElement(object, 'truncated') 
             truncated.text = '0' 
             difficult = ET.SubElement(object, 'difficult') 
             difficult.text = '0' 
             bndbox = ET.SubElement(object, 'bndbox') 
             xmin = ET.SubElement(bndbox, 'xmin') 
             ymin = ET.SubElement(bndbox, 'ymin') 
             xmax = ET.SubElement(bndbox, 'xmax') 
             ymax = ET.SubElement(bndbox, 'ymax') 
             xmin.text = str(int(val[0]))
             ymin.text = str(int(val[1])) 
             xmax.text = str(int(val[2]))
             ymax.text = str(int(val[3]))

         mydata = ET.tostring(annotation)
         print(pwdAnnoDir)
         uri_anno = pwdAnnoDir + '/' + _filename + '.xml'
         #print(uri_anno)
         myfile = open(uri_anno, "w")  
         myfile.write(mydata.decode("utf-8"))  

     def update(self):

         if not self.isUpdate:
            return
         # Get a frame from the video source
         ret, frame = self.vid.get_frame()
 
         if ret:
             self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
             self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
             self.frame = frame
 
         self.window.after(self.delay, self.update)
     
     def on_button_press(self, event):
        # save mouse drag start position
        print("mouse press")
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # create rectangle if not yet exist
        #if   self.rect:
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline='red')

     def on_move_press(self, event):
        print("mouse on_move_press")
        self.curX = self.canvas.canvasx(event.x)
        self.curY = self.canvas.canvasy(event.y)

        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        #if event.x > 0.9*w:
            #self.canvas.xview_scroll(1, 'units') 
        #elif event.x < 0.1*w:
            #self.canvas.xview_scroll(-1, 'units')
        #if event.y > 0.9*h:
            #self.canvas.yview_scroll(1, 'units') 
        #elif event.y < 0.1*h:
            #self.canvas.yview_scroll(-1, 'units')

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)    

     def on_button_release(self, event):
        self.arr_head.append([self.start_x, self.start_y, self.curX, self.curY])
 
     def on_pause(self):
        self.arr_head = []
        self.handle_up_key(None)       
class MyVideoCapture:
     def __init__(self, video_source=0):
         # Open the video source
         self.vid = cv2.VideoCapture(video_source)
         if not self.vid.isOpened():
             raise ValueError("Unable to open video source", video_source)
 
         # Get video source width and height
         self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
         self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
 
     def get_frame(self):
         if self.vid.isOpened():
             ret, frame = self.vid.read()
             if ret:
                 # Return a boolean success flag and the current frame converted to BGR
                 return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
             else:
                 return (ret, None)
         else:
             return (ret, None)
 
     # Release the video source when the object is destroyed
     def __del__(self):
         if self.vid.isOpened():
             self.vid.release()
 

#url = 'http://115.78.72.90/jpgmulreq/1/image.jpg'
 # Create a window and pass it to the Application object



if not os.path.isdir(pwdImgs):
	os.makedirs(pwdImgs)
if not os.path.isdir(pwdAnnoDir):
	os.makedirs(pwdAnnoDir)



App(tkinter.Tk(), "Tkinter and OpenCV", url)
