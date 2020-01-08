# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 10:49:57 2018

@author: Fotonik 2
"""


import cv2
import numpy as np
from skimage import measure
from skimage import filters

class morse_detection():
    

        
    def kernel(length):
        """
        Membuat kernel filter berbentuk 'Plus' yang digunakan untuk pemrosesan 
        gambar morfologi.
        
        bentuk filter : (dengan 'length' =9)
                    0 0 0 0 1 0 0 0 0        
                    0 0 0 0 1 0 0 0 0            
                    0 0 0 0 1 0 0 0 0
                    0 0 0 0 1 0 0 0 0
                    1 1 1 1 1 1 1 1 1
                    0 0 0 0 1 0 0 0 0
                    0 0 0 0 1 0 0 0 0
                    0 0 0 0 1 0 0 0 0
                    0 0 0 0 1 0 0 0 0
        
        Input : lenght (lebar kernel, harus ganjil)
        
        Output : kernel dengan bentuk seperti diatas
        
        
        """
        kernel =  np.zeros((length,length),np.uint8)
        x,y=np.shape(kernel)
        
        kernel[:,x//2]=1
        kernel[x//2,:]=1
        
        return kernel 
    
    def img_morf(rgb, kernel,thrs_value):
        """
        menghilangkan noise(derau) kecil yang bukan merupakan objek yang diamati
        
        proses :
            1.  konversi dari citra RGB menjadi citra keabuan
            2.  gausian blurr untuk menghilangkan noise berfrekuensi tinggi
            3.  proses binerisari untuk mengubah menjadi citra biner dengan nilai 
                batas yang ditentukan (thrs_value)
            4.  proses opening dilakukan pada citra biner untuk menghilangkan objek 
                minor yang tidak dibutuhkan
                
        Input : rgb (citra RGB),
                kernel (bernilai ganjil)
                thrs_value (dapat bernilai 1-254)
                
        Output :thresh (citra biner yang telah terfilter)
            
        """
        x,y=np.shape(kernel)
        gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (x+12, y+12), 0)
        a,thresh1 = cv2.threshold(gray,thrs_value,255,cv2.THRESH_BINARY)
        thresh1 = cv2.morphologyEx(thresh1, cv2.MORPH_OPEN, kernel)
        

        return thresh1
    
        
    
    def contour(thresh,data,time,data_compress,rd_snl):

    
        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        
        if len(data[0])==0:
            for c in contours:
                          
                x,y,w,h = cv2.boundingRect(c)
                
                if np.abs(np.subtract(w,h))<10 and w > 50:
                
                    data[0].append([x,y,w,h])
                    data[1].append(0)
                    data[2].append([])
                    data[3].append([])
                    
                    
                    data_compress[0].append([])
                    data_compress[1].append([])
            
                    
        else:
            
            for c in contours:
                          
                x,y,w,h = cv2.boundingRect(c)
                
                            
                if np.abs(np.subtract(w,h))<50 and w > 80:
                    
                    sinyal = [0]
                    
                    for i in range(len(data[0])):
                        
                        x2 = x+(w//2)
                        y2 = y+(h//2)
                        
                        x1 = data[0][i][0]
                        y1 = data[0][i][1]
                        w1 = data[0][i][2]
                        h1 = data[0][i][3]
                        
                            
                        if ((np.abs(np.subtract(x2,(x1+(w1//2))))) < (0.7*(w1+w))) and ((np.abs(np.subtract(y2,(y1+(h1//2))))) < (0.7*(h1+h))):
                            
                            sinyal[0]=1
                            sinyal.append(i)
    
                            break
                        
                    if sinyal[0]==1:
                        data[0][sinyal[1]]=[x,y,w,h]
                        
                    elif sinyal[0]==0:
                        if rd_snl[0] == 1 and rd_snl[1]==0:
                            pass
                        else:
                            data[0].append([x,y,w,h])
                            data[1].append(0)
                            data[2].append([])
                            data[3].append([])
                            
                            data_compress[0].append([])
                            data_compress[1].append([])
            
        
        for i in range(len(data[0])):
            if (np.sum(thresh[data[0][i][1]:data[0][i][1]+data[0][i][3],data[0][i][0]:data[0][i][0]+data[0][i][2]]))>0:
                
                data[1][i]=0
                
                if rd_snl[0] == 1 :        
            
                    data[2][i].append(1)
                    data[3][i].append(time)
                    
            else:
                data[1][i] = data[1][i] + 1
                
                if rd_snl[0] == 1 :
                    
                    if len(data[2][i])>0:
        
                        data[2][i].append(0)
                        data[3][i].append(time)
                    
        indeks=[]            
        for k in range(len(data[1])):
            if data[1][k]>1000:
                indeks.append(k)
                
                
        data[0] = [i for j, i in enumerate(data[0]) if j not in indeks]
        data[1] = [i for j, i in enumerate(data[1]) if j not in indeks]
        data[2] = [i for j, i in enumerate(data[2]) if j not in indeks]
        data[3] = [i for j, i in enumerate(data[3]) if j not in indeks]
        
        
        data_compress[0] = [i for j, i in enumerate(data_compress[0]) if j not in indeks]
        data_compress[1] = [i for j, i in enumerate(data_compress[1]) if j not in indeks]
        
        
            
               
#=======================penyedehanaan data===================================================
        
        
        for i in range (len(data[1])):
            
            if len(data[2][i])==1:
                
                data_compress[0][i].append(data[2][i][-1])
                data_compress[1][i].append(data[3][i][-1])
                    
            
            if len(data[2][i])>1:
                
                if len(data_compress[0])<1:
                    data_compress[0][i].append(data[2][i][-1])
                    data_compress[1][i].append(data[3][i][-1])
                
                
                if data[2][i][-1]==data[2][i][-2]:
                    data_compress[1][i][-1] = data_compress[1][i][-1]+data[3][i][-1]
                    
                else:
                    data_compress[0][i].append(data[2][i][-1])
                    data_compress[1][i].append(data[3][i][-1])
        
        return data,data_compress
    
    

    def data_partisi(data_compress):
        """ 
        memisahkan antara sinyal hight dan low dalam bentuk variabel terpisah
        
        input :
            data_compress
            
        output:
            satu : data bernilai high tersiri dari short (0) dan long (1), beserta durasinya
            nol  : data bernilai low tersiri dari short (0) / pemisah antar sinyal dan long (1) / pemisah antar karakter, beserta durasinya
        
        """
        
        nol = []
        satu = []
        for k in range (len(data_compress[0])):
            nol.append([])
            satu.append([])
            
            if len(data_compress[0][k])>0:
                for i in range(len(data_compress[0][k])):
                    if data_compress[0][k][i] == 1:
                        satu[-1].append(data_compress[1][k][i])
                        
                    else:
                        nol[-1].append(data_compress[1][k][i])
                    

        return satu, nol

    def data_reader(nol,satu):
        
        """
        menerjemahkan data hasil partisi menjadi data yang tercah
        
        input:
            satu : data high
            nol  : data low
        
        output
            kata        : data dalam bentuk abjad atau angka
            data_morse  : data dalam bentuk sandi morse
        
        
        """
        
        
        mors = {
    	"01":"A",
    	"1000":"B",
    	"1010":"C",
    	"100":"D",
    	"0":"E",
    	"0010":"F",
    	"110":"G",
    	"0000":"H",
    	"00":"I",
    	"0111":"J",
    	"101":"K",
    	"0100":"L",
    	"11":"M",
    	"10":"N",
    	"111":"O",
    	"0110":"P",
    	"1101":"Q",
    	"010":"R",
    	"000":"S",
    	"1":"T",
    	"001":"U",
    	"0001":"V",
    	"011":"W",
    	"1001":"X",
    	"1011":"Y",
    	"1100":"Z",
    	"01111":"1",
    	"00111":"2",
    	"00011":"3",
    	"00001":"4",
    	"00000":"5",
    	"10000":"6",
    	"11000":"7",
    	"11100":"8",
    	"11110":"9",
    	"11111":"0",
    	}
        kata=[]
        data_morse=[]
        
        val_satu = 0.6
        val_nol = 0.5
        
        for i in range(len(satu)):
            kata.append([])
            
                
            satu_bin = np.array(satu[i])>val_satu
            satu_bin = list( map(int, satu_bin) )
            
            nol_bin = np.array(nol[i])>val_nol
            nol_bin = list( map(int, nol_bin) )
            
            
            data_morse.append([])
            
            
            
            j=0
            code=""
            
#====================memisahkan data morse menjadi data morse tiap karakter========================
        
            for i in range (len(nol_bin)):
                
                if nol_bin[i]==1:
                    for l in satu_bin[j:i+1]:
                        code=code+str(l)
                    
                    data_morse[-1].append(code)
                    code="" 
                    j=i+1

#=============================penerjemahan menjadi alfabed dan angka==============================
                
            for i in data_morse[-1]:
                try :
                    kata[-1].append(mors[i])
                except:
                    kata[-1].append(" ")
                
        return kata,data_morse


    def data_selection(data,data_compress,rd_snl,position_cursor,sinyal):
        if rd_snl[1] == 0:
            
            if len(position_cursor)>1:
                for indeks in range (len(data[0])):
                    
                    if data[0][indeks][0] < position_cursor[0] <data[0][indeks][0]+data[0][indeks][2] and data[0][indeks][1] < position_cursor[1] <data[0][indeks][1]+data[0][indeks][3]:
                        sinyal[0] = [indeks]
                        sinyal[1] = [1]
               
                
                del rd_snl[2:]
                
            if len(sinyal[1])==0:
                luas = 0
                
                for i in range(len(data[0])):
                    a = data[0][i][2]*data[0][i][3]
                    if a > luas :
                        sinyal[0] =[i]
                        luas = a
                
                
                

            if rd_snl[0] == 1:
                if len(data[0])>0:
                    if len(sinyal) > 0 :
                        
                        data[0] = [data[0][sinyal[0][0]]]
                        data[1] = [data[1][sinyal[0][0]]]
                        data[2] = [data[2][sinyal[0][0]]]
                        data[3] = [data[3][sinyal[0][0]]]
                        
                        data_compress[0] = [data_compress[0][sinyal[0][0]]]
                        data_compress[1] = [data_compress[1][sinyal[0][0]]]
                    sinyal=[[],[]]
                
        
        else:
            sinyal=[[],[]]
        
        return sinyal,rd_snl,data,data_compress
                        
                    

    def display(layar, data,rd_snl,sinyal):
        
   
        for i in range (len(data[0])):
            if len(sinyal[0])>0:
                if i == sinyal[0][0] :
                    cv2.rectangle(layar,(data[0][i][0],data[0][i][1]),(data[0][i][0]+data[0][i][2],data[0][i][1]+data[0][i][3]),(0,0,255),2)
                    cv2.rectangle(layar,(data[0][i][0]+5,data[0][i][1]+5),(data[0][i][0]+data[0][i][2]-5,data[0][i][1]+data[0][i][3]-5),(0,0,200),2)
                    
    #                cv2.putText(layar,str(data[1][i]),(data[0][i][0]+30,10+data[0][i][1]+data[0][i][3]), font, 1,(50,50,255),2,cv2.LINE_AA)
                else:
                    cv2.rectangle(layar,(data[0][i][0],data[0][i][1]),(data[0][i][0]+data[0][i][2],data[0][i][1]+data[0][i][3]),(0,0,255),2)

            else:
                
                if rd_snl[0]==1:
                    cv2.rectangle(layar,(data[0][i][0],data[0][i][1]),(data[0][i][0]+data[0][i][2],data[0][i][1]+data[0][i][3]),(0,255,0),2)
                else:
                    cv2.rectangle(layar,(data[0][i][0],data[0][i][1]),(data[0][i][0]+data[0][i][2],data[0][i][1]+data[0][i][3]),(0,0,255),2)
                    
#                cv2.putText(layar,str(data[1][i]),(data[0][i][0]+30,10+data[0][i][1]+data[0][i][3]), font, 1,(50,50,255),2,cv2.LINE_AA)
        

        return layar 
    
    
    def display2(gambar,rgb,thres,data,kalimat,data_morse,rd_snl,t2):

        """
        menampilkan gambar dan data dalam layar antar muka
        
        
        """
        
        thres = cv2.cvtColor(thres, cv2.COLOR_GRAY2RGB)
        thres = cv2.resize(thres, None, fx = 0.25, fy = 0.25, interpolation = cv2.INTER_CUBIC)
        

        gambar[510:630,30:190]=thres[:,:]
        gambar[10:490,30:670]=rgb[:,:]
        
                
        font = cv2.FONT_HERSHEY_SIMPLEX

#====================================memberi lingkaran pada objek yang diamati===========================
        if len(data[0]) > 0:
            
            if rd_snl[0]%2 ==1:
    #                rgb = cv2.circle(gambar,(data[0][0]+10,data[0][1]+10),data[0][3],(0,255,0),2)
                
                rgb = cv2.rectangle(gambar,(data[0][0]+30,data[0][1]+10),(data[0][0]+data[0][2]+30,10+data[0][1]+data[0][3]),(0,255,0),2)
        
                
            else:
    #                rgb = cv2.circle(gambar,(data[0][0]+10,data[0][1]+10),data[0][3],(0,0,255),2)    
                
                rgb = cv2.rectangle(gambar,(data[0][0]+30,data[0][1]+10),(data[0][0]+data[0][2]+30,10+data[0][1]+data[0][3]),(0,0,255),2)
        
            
    #====================================menampilkan data high dan low dalam layar antarmuka========================
            if len(data[2])<17:
                for i in range(len(data[2])):
                    cv2.putText(gambar,str(data[2][i]),(((i+1)*20)+290,550), font, 1,(50,50,255),2,cv2.LINE_AA)
            else:
                                
                for i in range(17):
                    cv2.putText(gambar,str(data[2][-(17-i)]),(((i+1)*20)+299,550), font, 1,(50,50,255),2,cv2.LINE_AA)
        
    #====================================menampilkan data kalimat dalam layar antarmuka========================
            i=0
            if len(kalimat)<14:
                for i in range(len(kalimat)):
                    cv2.putText(gambar,kalimat[i],(((i+1)*25)+290,610), font, 1,(50,50,255),2,cv2.LINE_AA)
            else:
                                
                for i in range(14):
                    cv2.putText(gambar,str(kalimat[-(14-i)]),(((i+1)*25)+290,610), font, 1,(50,50,255),2,cv2.LINE_AA)
        
            
        
#===================================merubah ikon tombol ketika di klik=====================================
        if rd_snl[0]%2 ==1:
            cv2.circle(gambar,(215,540), 5, (0,255,0), -1)
        if rd_snl[1]%2 ==1:
            cv2.circle(gambar,(215,600), 5, (0,255,0), -1)
        return gambar
        
  
