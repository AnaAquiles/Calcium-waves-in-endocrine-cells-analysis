# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 14:35:54 2019

@author: akire
"""

from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PyQt5 import uic
#from GUI5_Principal import MainWinClass

ErrorDialogWin1 = uic.loadUiType("GUI5_ErrorWin1.ui")[0] 
ErrorDialogWin2 = uic.loadUiType("GUI5_ErrorWin2.ui")[0] 
PlotDialogWin = uic.loadUiType("GUI5_FirstDialog.ui")[0]                       #Ventana de serie tiempo completa
AdviseDialogWin1 = uic.loadUiType("GUI5_SecondDialog.ui")[0]                   #Ventana de error, advertencia



#Mensaje de error que sale si el archivo no es tipo tiff       
class FileTypeAdviceWinClass1(QtGui.QMainWindow, ErrorDialogWin1):             
    def __init__(self, parent = None):
        super(FileTypeAdviceWinClass1, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )    
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        
        
#Mensaje de error que sale si el archivo NO tiene más de 300 frames o si está 
#abriendo una imagen y no video 
class FileTypeAdviceWinClass2(QtGui.QMainWindow, ErrorDialogWin2):             
    def __init__(self, parent = None):
        super(FileTypeAdviceWinClass2, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )    
        self.setWindowModality(QtCore.Qt.ApplicationModal)     
        
        
        
#Ventana que pide datos del video y deben proporcionarse forzosamente para el 
#análisis posterior            
class PlotDialogWinClass(QtWidgets.QDialog, PlotDialogWin):
    def __init__(self, NoFrames, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        #Para que la nueva ventana no se pueda cerrar y esté siempre encima 
        #de la ventana principal:
        self.setWindowFlags(  
        QtCore.Qt.FramelessWindowHint |
        QtCore.Qt.WindowStaysOnTopHint )                                       #https://stackoverflow.com/questions/40866883/pyqt5-change-mainwindow-flags
                                                                               #https://stackoverflow.com/questions/34160160/creating-window-that-has-no-close-button-in-qt                                                                                     
                                                                                                                                                              
        #Para que la ventana de dialogo no deje que se pueda modificar la 
        #ventana principal:                                                                      
        self.setWindowModality(QtCore.Qt.ApplicationModal)                     #https://stackoverflow.com/questions/22410663/block-qmainwindow-while-child-widget-is-alive-pyqt                                                 

        #Para obtener el número de frames que tiene el stack completo 
        #(que ya se había calculado en la ventana principal)
        self.NoFrames = NoFrames            
        self.FirstDialogButton.clicked.connect(self.CheckFramesInfo)           

    #Se verifica primero que los datos dados por el usuario "tienen sentido" :
    #1.- Que el frame inicial sea menor al frame final
    #2.- Que al menos la porción de video contenga 300 frames
    #3.- Que no se rebase el número total de frames del stack cargado
    def CheckFramesInfo(self):
        self.frame1 = self.Fr1_spinBox.value()
        self.frame2 = self.Fr2_spinBox.value()   
        self.CellSize = self.Fr3_spinBox.value()
      
        if (self.frame2 <= self.frame1) or (self.frame2 - self.frame1 < 300) \
            or (self.frame2 - self.frame1 > self.NoFrames) :            
                
            #Ventana que avisa al usuario que eligió mal los frames inicial 
            #y final
            self.SecondDialogWin = FramesAdviceWinClass()
            self.SecondDialogWin.show()           

        else:
            #Iterar sobre los radio buttons para saber cúal se eligió:
            self.indexOfChecked = [self.CellTypeGroup.buttons()[x].isChecked() \
                for x in range(len(self.CellTypeGroup.buttons()))].index(True)  
            super().accept()                                                   #Call parent method



#Mensaje de error que avisa al usuario que eligió mal los frames inicial y 
#final para el análisis
class FramesAdviceWinClass(QtGui.QMainWindow, AdviseDialogWin1):               #Ventana de advertencia de error sobre el número de frames que debe tener el stack
    def __init__(self, parent = PlotDialogWinClass):
        super(FramesAdviceWinClass, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )    
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        