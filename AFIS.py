# -*- coding: utf-8 -*-
"""
Created on Sun Oct  7 19:07:07 2018

@author: sangs
"""

import sys
import numpy as np
import cv2

from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap

import PyQt5.QtWidgets 


from imutils.video import WebcamVideoStream

#from socketIO_client import SocketIO, LoggingNamespace

from morse_function2 import morse_detection

import time



class Afis_1(QMainWindow):
    def __init__ (self):
        super(Afis_1,self).__init__()
        loadUi('gui.ui',self)
        
        self.image=None
        self.im_thresh=None
        self.start_counter = 0
        
        
        self.data = [[],[],[],[]]
        self.kata=[]
        self.data_compress = [[],[]]
        self.data_morse=[]
        
        # [ record, mode(0=single,1=multi)]
        self.rd_snl = [0,0]
        
        self.t1=0
        self.t2=0
        self.sinyal =[[],[]]
        
        self.massage=""
        
        self.position_cursor=[]
        
        self.capture = WebcamVideoStream(src=0).start()
#        self.capture = cv2.VideoCapture(0)
        
        
#        ret, self.image =self.capture.read()
        self.image =self.capture.read()
        
        height, width, can = np.shape(self.image)
        self.fy = 480/height
        self.fx = 640/width
        
        # print(self.fx)
        # print(self.fy)
        self.main_frame.mousePressEvent = self.getPos
        self.Button_Start.toggled.connect(self.start_cam)
        self.Button_Start.setCheckable(True)
        
        
        self.Button_Save.toggled.connect(self.start_record)
        self.Button_Save.setCheckable(True)
        
        self.Button_Clear.clicked.connect(self.clear_data)

        self.Button_Send.clicked.connect(self.send_data)
        
    def start_cam(self,status):
        
        if status:
            self.start = True
            self.Button_Start.setText("Pause")
            self.start_counter = self.start_counter+1
        
            
        elif status == False :
             self.Button_Start.setText("Start")
             self.start = False
             self.start_counter = self.start_counter+1
        
             
        if self.start_counter == 1:
            
    
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(40)
            
    
    def start_record(self,status):
        if status:
            self.rd_snl[0] = 1
            self.Button_Save.setText("Stop_record")
        else:
            self.rd_snl[0] = 0
            self.Button_Save.setText("Start_record")
            
            
    def clear_data(self):
        
        self.data = [[],[],[],[]]
        self.kata=[]
        self.data_compress = [[],[]]
        self.data_morse=[]
        
    def update_frame(self):
        
        if self.radioButton_single.isChecked():
            self.rd_snl[1] = 0
            
        if self.radioButton_multi.isChecked():
            self.rd_snl[1] = 1
            
            
        
        if self.start == True:
            
            self.image =self.capture.read()
#            ret, self.image =self.capture.read()
            
            self.image = cv2.resize(self.image, None, fx = self.fx , fy = self.fy , interpolation = cv2.INTER_CUBIC)
            
            self.image = cv2.flip(self.image,1)
            
            
            
            self.im_thresh = morse_detection.img_morf(self.image,morse_detection.kernel(11),230)

            self.t2=time.time()-self.t1

            self.data,self.data_compress = morse_detection.contour(self.im_thresh,self.data,self.t2,self.data_compress,self.rd_snl)
            self.t1=time.time()
            
            
            self.sinyal,self.rd_snl,self.data,self.data_compress = morse_detection.data_selection(self.data,self.data_compress,self.rd_snl,self.position_cursor,self.sinyal)
            
            self.satu,self.nol = morse_detection.data_partisi(self.data_compress)
            
            if len(self.satu)>0:
                self.kata,self.data_morse = morse_detection.data_reader(self.nol,self.satu)
                
            self.image = morse_detection.display(self.image,self.data,self.rd_snl,self.sinyal)
            
            # print(self.kata)
            
            self.data_display(self.kata)
 
            
        
        self.display(self.image,self.im_thresh)
        
        self.Status_label.setText("Frame Rate : "+str(1//self.t2))
        
        self.Status_label2.setText("Sent Massage : "+self.massage)
        
        
    
    def stop_cam(self):
        self.timer.stop()
        
    def display(self,img,thres):
        qformat = QImage.Format_Indexed8
        if len(img.shape)==3:
            if img.shape[2]==4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
                
        outImage = QImage(img,img.shape[1],img.shape[0],img.strides[0],qformat)
        outImage = outImage.rgbSwapped()
        
        # thres = cv2.resize(thres, None, fx = 0.25, fy = 0.25, interpolation = cv2.INTER_CUBIC)
        # im_thres = QImage(thres,thres.shape[1],thres.shape[0],thres.strides[0],QImage.Format_Indexed8)

        self.main_frame.setPixmap(QPixmap.fromImage(outImage))
        self.main_frame.setScaledContents(True)
        
        
        
        # self.second_frame.setPixmap(QPixmap.fromImage(im_thres))
        # self.second_frame.setScaledContents(True)
        
        
    def getPos(self , event):
        self.x = event.pos().x()
        self.y = event.pos().y() 
        H, W = self.main_frame.height(),  self.main_frame.width()
        w, h =  W/642,  H/502
        self.position_cursor = [int(self.x/w),int(self.y/h)]
    
    def data_display(self,kata):
        self.table_data.setRowCount(len(kata))
        
        max_column = 0
        for j in range(len(kata)):
                max_column = max(max_column,len(kata[j]))
                
        
        self.table_data.setColumnCount(max_column)
        
        
        for i in range(len(kata)):
            for n in range(len(kata[i])):

                self.table_data.setItem(i,n,PyQt5.QtWidgets.QTableWidgetItem(str(kata[i][n])))
                self.table_data.resizeColumnToContents(n)
            self.table_data.resizeRowToContents(i)
            
    def send_data(self):
        self.massage = self.data_input.text()
        
#        with SocketIO('localhost', 8000, LoggingNamespace) as socketIO:
#            
#            socketIO.emit('Data',self.massage)
#            socketIO.wait(seconds=1)
        
        # print(self.massage)

        
if __name__ == "__main__":

    app = QApplication(sys.argv)
    Dialog = Afis_1()
    Dialog.setWindowTitle("AFIS 1.0")
    Dialog.show()
    

#    vs = WebcamVideoStream(src=0).start()
#    vs.stop()
    sys.exit(app.exec_())
 