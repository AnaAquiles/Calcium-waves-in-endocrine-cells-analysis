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
from GUI5_CellTimeSeries import ContourTimeSeries




MainWin= uic.loadUiType("GUI5_MainWin.ui")[0]                                  #Ventana que tendrá el stack y el menú
PlotDialogWin = uic.loadUiType("GUI5_FirstDialog.ui")[0]                       #Ventana de serie tiempo completa
AdviseDialogWin1 = uic.loadUiType("GUI5_SecondDialog.ui")[0]                   #Ventana de error, advertencia
ErrorDialogWin1 = uic.loadUiType("GUI5_ErrorWin1.ui")[0] 
ErrorDialogWin2 = uic.loadUiType("GUI5_ErrorWin2.ui")[0] 
ContourTableWin = uic.loadUiType("GUI5_ContoursTable2.ui")[0]



class MainWinClass(QtGui.QMainWindow, MainWin):    
    def __init__(self, parent=None):
        super().__init__(parent)        
        self.setupUi(self)
        self.findRoiAction.triggered.connect(self.CellDetection)                    #El botón se conecta primero a la función que permite abrir un stack
        
        
    def CellDetection(self):                                                   #Función que realizará la segmentación de células
        self.imv1.clear()                                                      #Limipiar la imagen principlal
        
        #Se va a abrir el archivo que se desea analizar
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File',\
                                                     os.getenv('HOME'))        #Obtiene la ruta del SO

        lista0 = str(filename[0])                                              #Ahora filename regresa el nombre como una tupla, hay que tomar su primera parte 
        file_extention = lista0[-3:]                                           #últimos tres carcateres del string anterior

        #Hay que verificar que el archivo sea tipo tiff
        if file_extention != str('tif'):
            self.FileTypeErrorAdviceWin = FileTypeAdviceWinClass()
            self.FileTypeErrorAdviceWin.show()  
            return                                                             #Salir de la función
        
        #Buscar el alrchivo y guardarlo en una matriz
        lista1  = lista0.replace('/', '\\\\')                                  #Hay que corregir la ruta del archivo, cambiando los '/' con '\\' (antes no se tenía que hacer esto GUI1 monito)  
        tif = tifffile.TiffFile(str(lista1))                                   #El stack se guarda en tif
        self.data = tif.asarray()                                              #El stack de imágenes se pasa a un arreglo
        forma = self.data.shape
        
        #Hay que verificar que el archivo tenga más de 300 frames, si no ocurre esto hay que salir de la función y sacar un mensaje de error        
        if (len(forma) != 3 or forma[0] < 300):
            self.FileTypeErrorAdviceWin2 = FileTypeAdviceWinClass2()
            self.FileTypeErrorAdviceWin2.show()        
            return                                                             #Salir de la función

        #Datos de la imagen, rotación de la misma y despliegue en pantalla     
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
                            
        #Se abre la ventana de diálogo con la gráfica anterior
        PlotDialogWin = PlotDialogWinClass(self.NoFrames)                      #"Llamamos" a la clase de la primera ventana
        ItemGrafica = pg.PlotCurveItem(pen=(0,255,0))                          #Se hace un ítem de una gráfica  
        ItemGrafica.setData(self.SerieTiempo)                                  #Se agregan los datos de la serie de tiempo al ítem} 
        PlotDialogWin.TimeSeriesPlot.addItem(ItemGrafica)                      #Se agrega el ítem a la primera ventana        
        PlotDialogWin.show()                                                   #Se muestra la ventana para pedir datos al usuario
        
        #Para obtener la información que introdujo el usuario en la ventana de diálogo: https://stackoverflow.com/questions/52560496/getting-a-second-window-pass-a-variable-to-the-main-ui-and-close
        if PlotDialogWin.exec_() == QtWidgets.QDialog.Accepted:
            inFrame = PlotDialogWin.frame1
            finFrame = PlotDialogWin.frame2
            cellType = PlotDialogWin.indexOfChecked
            
        #Analisis por tipo celular
        if cellType == 0:                                                      #Si el botón que eligió es 0 (hipófisis)
            #Se encuentran las células, se obtiene un diccionario con los contornos y una imagen binaria, los superponemos al video
            self.mascara, self.ROI_dict = PituitarySegm(inFrame, finFrame)     #Llama a la func que hace la segmentación [Falta pasarle la imagen original!!!]
            encima = pg.ImageItem(self.mascara)                                #Hacemos el ítem para mostrar la imagen de contornos
            self.imv1.addItem(encima)                                          #Ponemos la imagen de contornos encima del video
            
            #Crear el diccionario de series de tiempo (se va a usar para graficar en la ventana de tabla)
            self.TimeSer_dict = ContourTimeSeries(self.data, self.ROI_dict, self.NoFrames, self.alto, self.ancho)
                        
            self.TableWin = ContourTableWinClass(self.ROI_dict)
            self.TableWin.show()
            
        elif cellType == 1:                                                    #Si el botón que eligió es 1 (neuronas)
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



class FramesAdviceWinClass(QtGui.QMainWindow, AdviseDialogWin1):               #Ventana de advertencia de error
    def __init__(self, parent = PlotDialogWinClass):
        super(FramesAdviceWinClass, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )    
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        
class FileTypeAdviceWinClass(QtGui.QMainWindow, ErrorDialogWin1):              #Ventana de advertencia de error
    def __init__(self, parent = MainWinClass):
        super(FileTypeAdviceWinClass, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )    
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        
class FileTypeAdviceWinClass2(QtGui.QMainWindow, ErrorDialogWin2):             #Ventana de advertencia de error
    def __init__(self, parent = MainWinClass):
        super(FileTypeAdviceWinClass2, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )    
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        

class ContourTableWinClass(QtGui.QMainWindow, ContourTableWin):                #Ventana con la tabla de contornos
    def __init__(self, ContoursDict, parent = MainWinClass):
        super(ContourTableWinClass, self).__init__()
        self.setupUi(self)
        
        self.ContoursTable.setRowCount(len(ContoursDict))                             #Número de renglones que tendrá la tabla dependiendo del número de ROIs
        self.ContoursTable.setColumnCount(3)                                           #Número de columnas que tendrá la tabla    
        renglon=0     
        self.botones_series = QtGui.QButtonGroup()                          #Grupo de radio buttons
        self.botones_remove = QtGui.QButtonGroup()
        
        for key in ContoursDict.keys():                                       #Para saber las posiciones de cada ROI encontrada   
            contorno = ContoursDict[key];
            pos = contorno[0,0]

            item1 = QtGui.QRadioButton(str(pos))                               #Ponemos un radiobutton en cada renglón
            item1.setChecked(False)            
#            item1.clicked.connect(self.CheckBox)                               #Si el radio button se presiona, mándalo a la función CheckBox
            self.botones_series.addButton(item1)                                 #El radio button es parte del grupo radio buttons
            self.ContoursTable.setCellWidget(renglon, 1, item1)                        #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview
                        
            item2 = QtGui.QTableWidgetItem(str(key))                           #El string de numeración de la tabla
            self.ContoursTable.setItem(renglon, 0, item2)                              #El string se pone en el i-ésimo renglón y columna 0
           
            item3 = QtGui.QRadioButton()                           #Ponemos un radiobutton en cada renglón
            item3.setChecked(False)            
#            item3.clicked.connect(self.QuitarROI)                              #Si el radio button se presiona, mándalo a la función CheckBox
            self.botones_remove.addButton(item3)                               #El radio button es parte del grupo radio buttons
            self.ContoursTable.setCellWidget(renglon, 2, item3)                        #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview
                         
            renglon = renglon + 1                                              #Para pasar al siguiente renglón
                           
        self.ContoursTable.setHorizontalHeaderLabels(str("N°;Pos;Remove").split(";"))      #Etiqueta de la columna 
        self.ContoursTable.verticalHeader().hide()                                     #Quitar letrero vertical   https://stackoverflow.com/questions/14910136/how-can-i-enable-disable-qtablewidgets-horizontal-vertical-header                                             
        
        self.ContoursTable.resizeColumnToContents(0)                           #https://stackoverflow.com/questions/40995778/resize-column-width-to-fit-into-the-qtablewidget-pyqt
        self.ContoursTable.resizeColumnToContents(1)
        self.ContoursTable.resizeColumnToContents(2)
        self.ContoursTable.setFixedWidth(self.ContoursTable.columnWidth(0) + \
        self.ContoursTable.columnWidth(1) + self.ContoursTable.columnWidth(2))
  
    
    
app = QtGui.QApplication(sys.argv)
MyWindow = MainWinClass(None)
MyWindow.show()
app.exec_()



