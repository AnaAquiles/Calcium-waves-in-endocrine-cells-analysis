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

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
from PyQt5 import uic

MainWin= uic.loadUiType("C:\\Users\\akire\\Desktop\\GUITHUB_VentanasSeperadas\\GUI5_MainWin.ui")[0]
FirstDialogWin = uic.loadUiType("C:\\Users\\akire\\Desktop\\GUITHUB_VentanasSeperadas\\GUI5_FirstDialog.ui")[0]


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
        SerieTiempo = np.zeros(self.NoFrames)
        for frame in range(self.NoFrames):  
            imagen_i = self.data[frame,:,:] 
            SerieTiempo[frame] = np.mean(imagen_i)

#        plt.plot(SerieTiempo)
#        plt.show()

        self.FirstDialogWin = FirtsDialogWinClass()
        
        
        ItemGrafica = pg.PlotCurveItem(pen=(0,255,0))                          #Se hace un ítem de una gráfica  
        ItemGrafica.setData(SerieTiempo)                                       #Se agregan los datos al ítem
        self.FirstDialogWin.TimeSeriesPlot.addItem(ItemGrafica)  
#        self.ChildStackWin.imv1.setImage(self.data, transform=tr)                            #Mostrar el video en la GUI    

        
        self.FirstDialogWin.show()                

        
"""qt designer modal dialog python
https://forum.qt.io/topic/24027/qtdesigner-how-radio-button-group-together
https://www.youtube.com/watch?v=fSnTjrtkV9A   PARA CERRAR CON UN BOTÓN
https://stackoverflow.com/questions/41150669/open-second-window-from-main-with-pyqt5-and-qt-designer

"""
        
        
#    def FindCells(self):
#        print("Entra a la función")
#        self.myOtherWindow = OtherWindow()
#        self.myOtherWindow.show()
        
        
class FirtsDialogWinClass(QtGui.QMainWindow, FirstDialogWin):
    def __init__(self, parent = MainWinClass):
        super(FirtsDialogWinClass, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(  
        QtCore.Qt.FramelessWindowHint |
        QtCore.Qt.WindowStaysOnTopHint |
        QtCore.Qt.X11BypassWindowManagerHint)                                       #https://stackoverflow.com/questions/40866883/pyqt5-change-mainwindow-flags
                                                                               #https://stackoverflow.com/questions/34160160/creating-window-that-has-no-close-button-in-qt
        self.setWindowModality(Qt.ApplicationModal)                                                                      

        #        form_class_1.show()
#        uic.loadUi("GUI4_PlotTableWin.ui", self).show()


        
app = QtGui.QApplication(sys.argv)
MyWindow = MainWinClass(None)
MyWindow.show()
app.exec_()