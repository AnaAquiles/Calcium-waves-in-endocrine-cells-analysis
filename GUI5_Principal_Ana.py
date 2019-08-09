# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 13:49:57 2019

@author: akire
"""

import sys
import os
import tifffile 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pyplot
from scipy.integrate import simps
from scipy import signal
from scipy import stats 
from matplotlib import cm
import pandas as pd
import seaborn as sns 


from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
from PyQt5 import uic

MainWin= uic.loadUiType("GUI5_MainWin.ui")[0]
FirstDialogWin = uic.loadUiType("GUI5_FirstDialog.ui")[0]
#SeconDialogWin = uic.loadUiType("GUI5_SecondDialog.ui")[0]
ThirdDialogWin = uic.loadUiType("GUI5_ThirdDialog.ui")[0]
FourthDialogWin = uic.loadUiType("GUI5_FourthDialog.ui")[0]


#class StackWinClass(QtGui.QMainWindow, StackWin):
#    def __init__(self, parent = MainWinClass):
#        super(StackWinClass, self).__init__()
#        self.setupUi(self)
##        form_class_1.show()
##        uic.loadUi("GUI4_PlotTableWin.ui", self).show()
        

class MainWinClass(QtGui.QMainWindow, MainWin):
    
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        
#        super(myWindow, self).__init__()
#        self.ui = myWindow() 
        self.setupUi(self)
        
#        uic.loadUi("GUI4_MainWin.ui", self)
        self.openAction.triggered.connect(self.openFile)
#        self.findRoiAction.triggered.connect(self.FindCells)
        
#    def StackWinShow(self):
#        print('Entrando a la matrix')
#        self.ChildStackWin = StackWinClass()
#        self.ChildStackWin.show()        
#        self.openFile()
        
        
    def openFile(self):                                                        #                                         <------Abre un archivo
#        self.imv1.clear()                                                      # Si se abre otro archivo se limpia la gráfica

        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File',\
                                                     os.getenv('HOME'))        #Obtiene la ruta del SO
        lista0 = str(filename[0])                                              #Ahora filename regresa el nombre como una tupla, hay que tomar su primera parte 
        lista1  = lista0.replace('/', '\\\\')                                  #Hay que corregir la ruta del archivo, cambiando los '/' con '\\' (antes no se tenía que hacer esto GUI1 monito)
        tif = tifffile.TiffFile(str(lista1))                                   #El stack se guarda en tif
        self.data = tif.asarray()                                              #El stack de imágenes se pasa a un arreglo
        (self.NoFrames, self.alto, self.ancho)=self.data.shape 
        tif = None                                                             #Se borra el contenido de tif (para liberar memoria)
        tr = pg.QtGui.QTransform()                                             #Para la aplicación de las rotaciones a la imagen               
        tr.rotate(90,QtCore.Qt.ZAxis)                                          #Rotación en el eje Z de 90°
        tr.rotate(180,QtCore.Qt.XAxis)                                         #Rotación en el eje X de 180°

        self.imv1.setImage(self.data, transform=tr)                            #Mostrar el video en la GUI 

        
        #Luego hay que preguntar si son neuronas o células de la hipófisis, y luego de qué frame a qué frame se va a realizar la segmentación en una ventana de diálogo
        #Hay que sacar la serie de tiempo del stack
        self.SerieTiempo = np.zeros(self.NoFrames)
        for frame in range(self.NoFrames):  
            imagen_i = self.data[frame,:,:] 
            self.SerieTiempo[frame] = np.mean(imagen_i) 

#        plt.plot(SerieTiempo)
#        plt.show()

        self.FirstDialogWin = FirstDialogWinClass()
        
        
        ItemGrafica = pg.PlotCurveItem(pen=(0,255,0))                          #Se hace un ítem de una gráfica  
        ItemGrafica.setData(self.SerieTiempo)                                   #Se agregan los datos al ítem
        self.FirstDialogWin.TimeSeriesPlot.addItem(ItemGrafica)  
#        self.ChildStackWin.imv1.setImage(self.data, transform=tr)              #Mostrar el video en la GUI    

        self.FirstDialogWin.show()          

#app = QtGui.QApplication(sys.argv)
#MyWindow = MainWinClass(None)
#MyWindow.show()
#app.exec_()

#%%
        
"""qt designer modal dialog python
https://forum.qt.io/topic/24027/qtdesigner-how-radio-button-group-together
https://www.youtube.com/watch?v=fSnTjrtkV9A   PARA CERRAR CON UN BOTÓN
https://stackoverflow.com/questions/41150669/open-second-window-from-main-with-pyqt5-and-qt-designer

"""
        
        
#    def FindCells(self):
#        print("Entra a la función")
#        self.myOtherWindow = OtherWindow()
#        self.myOtherWindow.show()
        
        
class FirstDialogWinClass(QtGui.QMainWindow, FirstDialogWin):
    def __init__(self, parent = MainWinClass):
        super(FirstDialogWinClass, self).__init__()
        self.setupUi(self)
        
#        #Para que la nueva ventana no se pueda cerrar y esté siempre encima de la ventana principal:
#        self.setWindowFlags(  
#        QtCore.Qt.FramelessWindowHint |
#        QtCore.Qt.WindowStaysOnTopHint )                                       #https://stackoverflow.com/questions/40866883/pyqt5-change-mainwindow-flags
#                                                                               #https://stackoverflow.com/questions/34160160/creating-window-that-has-no-close-button-in-qt
#        #Para que la ventana de dialogo no deje que se pueda modificar la ventana principal:                                                                      
#        self.setWindowModality(QtCore.Qt.ApplicationModal)                     #https://stackoverflow.com/questions/22410663/block-qmainwindow-while-child-widget-is-alive-pyqt                                                 

                               
                               
        self.FirstDialogButton.clicked.connect(self.FirstDialog)                      
        self.partnerDialog = MainWinClass()
        serie = self.partnerDialog.SerieTiempo   #¿CÓMO PASAR LOS DATOS DE LA VENTANA ANTERIOR A ESTA NUEVA VENTANA?? https://stackoverflow.com/questions/36772927/pyqt-how-to-pass-information-between-windows
#        print(serie)
        
    def FirstDialog(self):
        frame1 = self.Fr1_spinBox.value();
        frame2 = self.Fr2_spinBox.value();   
        print(frame1)                                             
        print(frame2)              
#        print(len(self.partnerDialog.SerieTiempo))                       
        if (frame2 <= frame1) or (frame2 - frame1 < 300):
            
            self.SecondDialogWin = SecondDialogWinClass()
            self.SecondDialogWin.show()                                    
     #fALTA LEER LOS RADIO BUTTONS                          
                               
#        self.PituitaryButton.clicked.connect(self.radio_button_clicked) 
#        self.NeuronButton.clicked.connect(self.radio_button_clicked) 
#        
#    def radio_button_clicked(self):
#        print(self.CellTypeGroup.checkedId())
#        print(self.CellTypeGroup.checkedButton().text())        

        
class SecondDialogWinClass(QtGui.QMainWindow, SeconDialogWin):
    def __init__(self, parent = FirstDialogWinClass):
        super(SecondDialogWinClass, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )    
        
          

#            print('Ya eligieron el tipo celular')

#%%

""""
                       Parte de analisis de Calcio / aaquiles

"""
    
       
class ThirdDialogWinClass(QtGui.QMainWindow, ThirdDialogWin):
    def __init__(self, data,value1,value2, value3, parent = MainWinClass):
        super(ThirdDialogWinClass, self).__init__()
        self.setupUi(self)
        self.spinBox.value = value1.astype(int)
        self.spinBox_2.value = value2.astype(int)
        self.spinBox_3.value = value3.astype(int)
        self.actionData_normalization.triggered.connect(self.NormF)    
        
        
    def NormF(self, data):
        baseline=np.amin(data[:,:,:],-1)[:,:,None]                              # Este valor tiene que ser igual al númerototal de imágenes a analizar por
        return data/baseline
                                                                               
        def detrend(self,data, value1, window= value1):                                  # NO deberia pedir self, antes de value1
            x=np.arange(0,window)
            x = x[None,:]*np.ones((data.shape[-2],1))
            x=np.ravel(x)
            slopes=[]
            intercepts=[]
            for dat in data:
                y = np.ravel(dat[:,:window])
                slope,inter,_,_,_=stats.linregress(x,y)
                slopes.append(slope)
                intercepts.append(inter)
                                                                                #-1 is the axis of ROI's
                slopes=np.array(slopes)
                intercepts=np.array(intercepts)
                t=np.arange(0,self.shape[-1])
                trends=np.array((intercepts)[:,None] + np.array(slopes)
                [:,None] * t[None,:])
                return data - trends[:,None,:]
    b,a = signal.bessel(3,0.3,btype='lowpass')                                  # Grado del filtrado en Hz, default 0.1             
    datosfilt=signal.filtfilt(b,a,data,axis=-1)
    datosNormFilt=(NormF(datosfilt)) #s/detrend, mejor ajuste a la linea
    dt= value3                                                                     # Tiempo de adquisicion en segundos
    time=np.arange(0,dt*datosNormFilt.shape[-1],dt)
            
                     
        
    series = [] 
  
    for ini in range(0,data.shape[1]):                                         # Crea un arreglo para plotear el raster plot
        for j in range(len(data)): 
            series.append(datosNormFilt[j,ini,:]) 
    series = np.array(series)


    
    ItemGrafica = pg.pyplot.matshow(series, interpolation=None, 
                                      aspect = 'auto', cmap='bone') 
    ItemGrafica.show()
    
                
        
class FourthDialogWinClass(QtGui.QMainWindow, FourthDialogWin):
    def __init__(self, data, datosNorm,parent = MainWinClass):
        super(FourthDialogWinClass, self).__init__()
        self.setupUi(self)
        index = ((len(data))/2).astype(int)
        self.CorrelationAction.triggered.connect(self.FourthDialog)  

    def FourthDialog(self):
        def Correlation(data,index, N=1000):
            
            fftdatos=np.fft.fft(data,axis=-1)
            ang=np.angle(fftdatos)
            amp=np.abs(fftdatos)
            #Cálculo de la matriz de correlación de los datos aleatorizados
            CorrMat=[]
            for i in range(N):
                angSurr=np.random.uniform(-np.pi,np.pi,size=ang.shape)
                angSurr[:,index:]= - angSurr[:,index:0:-1] 
                angSurr[:,index]=0                                                     # Tenemos que colocar únicamente el valor correspondiente a la mitad de las imágenes de nuestro estudio
                
                fftdatosSurr=np.cos(angSurr)*amp + 1j*np.sin(angSurr)*amp
            
                datosSurr=np.real(np.fft.ifft(fftdatosSurr,axis=-1))                # arroja la valores reales de los datos aleatorizados
                spcorr2,pval2=stats.spearmanr(datosSurr,axis=1)
                CorrMat.append(spcorr2)
                
            CorrMat=np.array(CorrMat)
            return CorrMat
          
    
     SCM=Correlation(datosNorm[i])                                               # Desviacion estandar y promedio de SCM=SurrogateCorrData
     meanSCM=np.mean(SCM,0)
     sdSCM=np.std(SCM,0)
    
                                                                                # GRAFICAS!!!
    IGrafica = pg.GraphicsView(plt.imshow(spcorr,interpolation='none',
                                                  cmap='inferno',vmin=-1,
                                                  vmax=1))
    
    IGrafica.plt.colorbar()
    IGrafica.plt.grid(False)    
    It = pg.GraphicsLayout (border=(100,100,100))
    IGrafica.setCentralItem(It)
    IGrafica.show()
    IGrafica.setWindowTitle('Correlation Analysis & Plots') 
            
    p1 = It.addPlot() 
    p2 = It.addPlot() 
    p3 = It.addPlot() 
    p4 = It.addPlot()  
    
    p1.plot(datosNorm[i].T)  
    p2.hist(spcorr.ravel(),bins=50)              
    p3.plot(SCM[i])              
    p4.plot(hist(SCM[:,5,8],bins=50))               
                  
    self.FourthDialogWin.It.addItem(ItemGrafica) 
    self.FourthDialogWin.show()          



#Plot scatter plot oh connections            
sns.set(style="ticks")
#sns.set(font_scale = 1.20)


df = pd.read_csv("Mapa100L290617L.csv")
ax1 = df.plot.scatter(x='X',
                      y= 'Y',
                      c = 'C',
                      alpha=.90,
                      colormap = 'seismic',
                      vmin=1,vmax=100)

        
               
app = QtGui.QApplication(sys.argv)
MyWindow = MainWinClass(None)
MyWindow.show()
app.exec_()























