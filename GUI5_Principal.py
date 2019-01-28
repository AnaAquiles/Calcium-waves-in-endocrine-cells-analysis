#-*- coding: utf-8 -*-
"""
Created on Mon Jan 14 13:49:57 2019

@author: akire
"""

import sys
import os
import tifffile 
import numpy as np
import matplotlib.pyplot as plt
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from PyQt5 import uic
from GUI5_Pituitary import PituitarySegm



MainWin= uic.loadUiType("GUI5_MainWin.ui")[0]                                  #Ventana que tendrá el stack y el menú
PlotDialogWin = uic.loadUiType("GUI5_FirstDialog.ui")[0]                       #Ventana de serie tiempo completa
AdviseDialogWin1 = uic.loadUiType("GUI5_SecondDialog.ui")[0]                   #Ventana de error, advertencia



class MainWinClass(QtGui.QMainWindow, MainWin):    
    def __init__(self, parent=None):
        super().__init__(parent)        
        self.setupUi(self)
        self.openAction.triggered.connect(self.openFile)
        
        
    def openFile(self):                                                        #Abre un archivo
#        self.imv1.clear()                                                     # Si se abre otro archivo se limpia la gráfica
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File',\
                                                     os.getenv('HOME'))        #Obtiene la ruta del SO
        lista0 = str(filename[0])                                              #Ahora filename regresa el nombre como una tupla, hay que tomar su primera parte 
        lista1  = lista0.replace('/', '\\\\')                                  #Hay que corregir la ruta del archivo, cambiando los '/' con '\\' (antes no se tenía que hacer esto GUI1 monito)
        tif = tifffile.TiffFile(str(lista1))                                   #El stack se guarda en tif
        self.data = tif.asarray()                                              #El stack de imágenes se pasa a un arreglo
        forma = self.data.shape
        self.NoFrames = forma[0]
        self.alto = forma[1]
        self.ancho = forma[2]
        (self.NoFrames, self.alto, self.ancho)=self.data.shape                 #https://ipython-books.github.io/48-processing-large-numpy-arrays-with-memory-mapping/
        tif = None                                                             #Se borra el contenido de tif (para liberar memoria)
        tr = pg.QtGui.QTransform()                                             #Para la aplicación de las rotaciones a la imagen               
        tr.rotate(90,QtCore.Qt.ZAxis)                                          #Rotación en el eje Z de 90°
        tr.rotate(180,QtCore.Qt.XAxis)                                         #Rotación en el eje X de 180°
        self.imv1.setImage(self.data, transform=tr)                            #Mostrar el video en la GUI 

                
        #Hay que sacar la serie de tiempo del stack completo
        self.SerieTiempo = np.zeros(self.NoFrames)
        for frame in range(self.NoFrames):  
            imagen_i = self.data[frame,:,:] 
            self.SerieTiempo[frame] = np.mean(imagen_i) 
        
                    
        #Para poner la gráfica en la ventana de diálogo
        PlotDialogWin = PlotDialogWinClass(self.NoFrames)                      #"Llamamos" a la clase de la primera ventana
        ItemGrafica = pg.PlotCurveItem(pen=(0,255,0))                          #Se hace un ítem de una gráfica  
        ItemGrafica.setData(self.SerieTiempo)                                  #Se agregan los datos de la serie de tiempo al ítem} 
        PlotDialogWin.TimeSeriesPlot.addItem(ItemGrafica)                      #Se agrega el ítem a la primera ventana        
        PlotDialogWin.show()                                                   #Se muestra la primer ventana
        

        #Para obtener la información que introdujo el usuario en la ventana de diálogo: https://stackoverflow.com/questions/52560496/getting-a-second-window-pass-a-variable-to-the-main-ui-and-close
        if PlotDialogWin.exec_() == QtWidgets.QDialog.Accepted:
            inFrame = PlotDialogWin.frame1
            finFrame = PlotDialogWin.frame2
            cellType = PlotDialogWin.indexOfChecked

            
        #Analisis por tipo celular
        if cellType == 0:
            PituitarySegm(inFrame, finFrame)
            
        elif cellType == 1:
            self.segmNeuron(inFrame, finFrame)
            

            
    def segmNeuron(self, a, b):
        print('Aquí va el análisis de neuronas')
        
            
class PlotDialogWinClass(QtWidgets.QDialog, PlotDialogWin):
    def __init__(self, NoFrames, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        #Para que la nueva ventana no se pueda cerrar y esté siempre encima de la ventana principal:
        self.setWindowFlags(  
        QtCore.Qt.FramelessWindowHint |
        QtCore.Qt.WindowStaysOnTopHint )                                       #https://stackoverflow.com/questions/40866883/pyqt5-change-mainwindow-flags
                                                                               #https://stackoverflow.com/questions/34160160/creating-window-that-has-no-close-button-in-qt
        #Para que la ventana de dialogo no deje que se pueda modificar la ventana principal:                                                                      
        self.setWindowModality(QtCore.Qt.ApplicationModal)                     #https://stackoverflow.com/questions/22410663/block-qmainwindow-while-child-widget-is-alive-pyqt                                                 

        #Para obtener el número de frames que tiene el stack completo (que ya se había calculado en la ventana principal)
        self.NoFrames = NoFrames            
        self.FirstDialogButton.clicked.connect(self.CheckFramesInfo)           

    #Se verifica primero que los datos dados por el usuario "tienen sentido" :
    #1.- Que el frame inicial sea menor al frame final
    #2.- Que al menos la porción de video contenga 300 frames
    #3.- Que no se rebase el número total de frames del stack cargado
    def CheckFramesInfo(self):
        self.frame1 = self.Fr1_spinBox.value();
        self.frame2 = self.Fr2_spinBox.value();   
      
        if (self.frame2 <= self.frame1) or (self.frame2 - self.frame1 < 300) \
            or (self.frame2 - self.frame1 > self.NoFrames) :            
            #Ventana que avisa al usuario que eligió mal los frames inicial y final
            self.SecondDialogWin = FramesAdviceWinClass()
            self.SecondDialogWin.show()           

        else:
            #Iterar sobre los radio buttons para saber cúal se eligió:
            self.indexOfChecked = [self.CellTypeGroup.buttons()[x].isChecked() \
                for x in range(len(self.CellTypeGroup.buttons()))].index(True)  
            super().accept()                                                   #Call parent method



class FramesAdviceWinClass(QtGui.QMainWindow, AdviseDialogWin1):               #Esta ventana solo es de advertencia de un error
    def __init__(self, parent = PlotDialogWinClass):
        super(FramesAdviceWinClass, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )    
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        
app = QtGui.QApplication(sys.argv)
MyWindow = MainWinClass(None)
MyWindow.show()
app.exec_()



