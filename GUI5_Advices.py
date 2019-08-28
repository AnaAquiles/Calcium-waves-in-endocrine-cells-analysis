# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 14:35:54 2019

@author: akire
"""

from pyqtgraph.Qt import QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5 import QtCore
#from GUI5_Principal import MainWinClass

ErrorDialogWin1 = uic.loadUiType("GUI5_ErrorWin1.ui")[0] 
ErrorDialogWin2 = uic.loadUiType("GUI5_ErrorWin2.ui")[0] 
ErrorDialogWin3 = uic.loadUiType("GUI5_ErrorWin3.ui")[0] 
ErrorDialogWin4 = uic.loadUiType("GUI5_ErrorWin4.ui")[0] 
PlotDialogWin = uic.loadUiType("GUI5_FirstDialog2.ui")[0]                      #Ventana de serie tiempo completa
AdviseDialogWin1 = uic.loadUiType("GUI5_SecondDialog.ui")[0]                   #Ventana de error, advertencia




"""%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    Inicio Parte de ANA        
%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%""" 
SamplingTimeWin = uic.loadUiType("GUI5_SamplingTime_Ana.ui")[0]                #Ventana que solicita el tiempo de muestreo
ErrorDialogWin5 = uic.loadUiType("GUI5_ErrorWin5_Ana.ui")[0]                   #Ventana que avisa que no se indicó el tiempo de muestreo

"""%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%
      Fin Parte de ANA        
%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%""" 






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
        


#Mensaje de error que sale si el archivo no es tipo csv       
class FileTypeAdviceWinClass3(QtGui.QMainWindow, ErrorDialogWin3):             
    def __init__(self, parent = None):
        super(FileTypeAdviceWinClass3, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )    
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        

#Mensaje de error que sale si el archivo no es tipo csv       
class FileTypeAdviceWinClass4(QtGui.QMainWindow, ErrorDialogWin4):             
    def __init__(self, parent = None):
        super(FileTypeAdviceWinClass4, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )    
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        
        
#Ventana que pide datos del video y deben proporcionarse forzosamente para el 
#análisis posterior        
"""ESTA VENTANA ES LA QUE QUITA LA PARTE SUPERIOR DE LA VENTANA, FUNCIONA
BIEN """
#class PlotDialogWinClass(QtWidgets.QDialog, PlotDialogWin):
#    def __init__(self, NoFrames, parent=None):
#        super().__init__(parent)
#        self.setupUi(self)
#        
#        #Para que la nueva ventana no se pueda cerrar y esté siempre encima 
#        #de la ventana principal:
#        self.setWindowFlags(  
#        QtCore.Qt.FramelessWindowHint |
#        QtCore.Qt.WindowStaysOnTopHint )                                       #https://stackoverflow.com/questions/40866883/pyqt5-change-mainwindow-flags
#                                                                               #https://stackoverflow.com/questions/34160160/creating-window-that-has-no-close-button-in-qt                                                                                     
#                                                                                                                                                              
#        #Para que la ventana de dialogo no deje que se pueda modificar la 
#        #ventana principal:                                                                      
#        self.setWindowModality(QtCore.Qt.ApplicationModal)                     #https://stackoverflow.com/questions/22410663/block-qmainwindow-while-child-widget-is-alive-pyqt                                                 
#
#        #Para obtener el número de frames que tiene el stack completo 
#        #(que ya se había calculado en la ventana principal)
#        self.NoFrames = NoFrames            
#        self.FirstDialogButton.clicked.connect(self.CheckFramesInfo)           
#
#    #Se verifica primero que los datos dados por el usuario "tienen sentido" :
#    #1.- Que el frame inicial sea menor al frame final
#    #2.- Que al menos la porción de video contenga 300 frames
#    #3.- Que no se rebase el número total de frames del stack cargado
#    def CheckFramesInfo(self):
#        self.frame1 = self.Fr1_spinBox.value()
#        self.frame2 = self.Fr2_spinBox.value()   
#        self.CellSize = self.Fr3_spinBox.value()
#      
#        if (self.frame2 <= self.frame1) or (self.frame2 - self.frame1 < 300) \
#            or (self.frame2 - self.frame1 > self.NoFrames) :            
#                
#            #Ventana que avisa al usuario que eligió mal los frames inicial 
#            #y final
#            self.SecondDialogWin = FramesAdviceWinClass()
#            self.SecondDialogWin.show()           
#
#        else:
#            #Iterar sobre los radio buttons para saber cúal se eligió:
#            self.indexOfChecked = [self.CellTypeGroup.buttons()[x].isChecked() \
#                for x in range(len(self.CellTypeGroup.buttons()))].index(True)  
#            super().accept()                                                   #Call parent method        



        
"""ESTA PARTE ES PARA HACER FUNCIONAR LA VENTANA SIN TENER QUE QUITAR SU PARTE
SUPERIOR"""        
#class PlotDialogWinClass(QtWidgets.QDialog, PlotDialogWin):
#Ventana de diálogo que pide ingresar datos para poder hacer la segmentación, 
#si hay algo extraño en los datos salen ventanas de error

class PlotDialogWinClass(QtGui.QMainWindow, PlotDialogWin):
    
    okClicked = QtCore.pyqtSignal()                                            #Esto es para emitir una señal cuando las condiciones sean adecuadas para hacer el análisis
                                                                               #https://www.linuxquestions.org/questions/programming-9/pyqt-controlling-one-window-with-widgets-from-a-different-window-4175527226/
    closeClicked = QtCore.pyqtSignal()                                         #Señal emitida cuando se quiere cerrar la ventana
    
    def __init__(self, NoFrames, parent=None):
        super(PlotDialogWinClass, self).__init__()
#        super().__init__(parent)
        self.setupUi(self)  #(self)
        
        #Para que la ventana de dialogo no deje que se pueda modificar la 
        #ventana principal:                                                                      
        self.setWindowModality(QtCore.Qt.ApplicationModal)                     #https://stackoverflow.com/questions/22410663/block-qmainwindow-while-child-widget-is-alive-pyqt                                                 

        #Para que la nueva ventana esté siempre encima de la ventana principal
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )                   #Par aque la ventana siempre esté encima de la ventana principal
        
        #Para obtener el número de frames que tiene el stack completo 
        #(que ya se había calculado en la ventana principal)
        self.NoFrames = NoFrames            
        
        self.FirstDialogButton.clicked.connect(self.CheckFramesInfo)           #Cuando se de clic en el botón aceptar, llamar a la función CheckFramesInfo
        
        self.Flag = 0                                                          #Bandera que indica si los datos son incorrectos, si se checan y están bien se cambiará la bandera a 1

    #Se verifica primero que los datos dados por el usuario "tienen sentido" :
    #1.- Que el frame inicial sea menor al frame final
    #2.- Que al menos la porción de video contenga 300 frames
    #3.- Que no se rebase el número total de frames del stack cargado
    def CheckFramesInfo(self):        
        self.frame1 = self.Fr1_spinBox.value()                                 #Dato ingresado por el usuario para el frame inicial
        self.frame2 = self.Fr2_spinBox.value()                                 #Dato ingresado por el usuario para el frame final
        self.CellSize = self.Fr3_spinBox.value()                               #Dato ingresado por el usuario para el tamaño de la célula
      
        if (self.frame2 <= self.frame1) or (self.frame2 - self.frame1 < 300)\
            or (self.frame2 - self.frame1 > self.NoFrames) :                   
                
            #Ventana que avisa al usuario que eligió mal los frames inicial 
            #y final
            self.SecondDialogWin = FramesAdviceWinClass()
            self.SecondDialogWin.show()  
            
        else:
            #Iterar sobre los radio buttons para saber si son neuronas o 
            #de hipófisis
            self.indexOfChecked = [self.CellTypeGroup.buttons()[x].isChecked()\
                for x in range(len(self.CellTypeGroup.buttons()))].index(True)  

            self.Flag = 1                                                      #Los datos son correctos, ponemos la bandera en 1
            self.close()                                                       #Cerramos la ventana
            self.okClicked.emit()                                              #Se emite la señal porque los datos ingresados por el usuario tienen sentido

#    #Función que indica qué hacer en caso de que se desee cerrar la ventana
#    def closeEvent(self, event):
#        if self.Flag == 0:                                                     #Si los datos no son adecuados y se va a cerrar la ventana 
#            self.closeClicked.emit()                                           #Emite una señal de que se va a cerrar la ventana y los datos son inadecuados
#            event.accept()                                                     #Cierra la ventana
#        elif self.Flag == 1:                                                   #Si los datos tienen sentido 
#            event.accept()                                                     #Cierra la ventana normalmente
        
        

#Mensaje de error que avisa al usuario que eligió mal los frames inicial y 
#final para el análisis
class FramesAdviceWinClass(QtGui.QMainWindow, AdviseDialogWin1):               #Ventana de advertencia de error sobre el número de frames que debe tener el stack
    def __init__(self, parent = PlotDialogWinClass):
        super(FramesAdviceWinClass, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )    
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        




"""%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    Inicio Parte de ANA        
%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%""" 
#Ventana que solicita el tiempo de muestreo
class SamplingTimeClass(QtWidgets.QDialog, SamplingTimeWin):                   #Ventana de advertencia de error sobre el número de frames que debe tener el stack
    okClicked = QtCore.pyqtSignal()                                            #Señal emitida cuando se dio aceptar en la ventana

    def __init__(self, parent = None):
        super(SamplingTimeClass, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )    
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.buttonBox.accepted.connect(self.clickAccept)                      #Qué hacer si se da clic en aceptar 
                
    def clickAccept(self):
        self.samplTime = self.st_spinBox.value()                               #Obtenemos el tiempo de muestreo que ingresó el usuario
        self.okClicked.emit()                                                  #Se emite la señal indicando que se dio en aceptar en la ventana

    def closeEvent(self, event):                                               #Si la ventana se va a cerrra
        self.samplAdvice = SamplTimeAdviceWinClass()                           
        self.samplAdvice.show()                                                #Mostrar la ventana que indica que faltó dar el tiempo de muestreo
                                                               


#Ventana de error que sale cuando no se indica el tiempo de muestreo
class SamplTimeAdviceWinClass(QtGui.QMainWindow, ErrorDialogWin5):             #Ventana de advertencia de error sobre la falta de tiempo de muestreo
    def __init__(self, parent = PlotDialogWinClass):
        super(SamplTimeAdviceWinClass, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )    
        self.setWindowModality(QtCore.Qt.ApplicationModal)



"""%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%
      Fin Parte de ANA        
%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%"""         