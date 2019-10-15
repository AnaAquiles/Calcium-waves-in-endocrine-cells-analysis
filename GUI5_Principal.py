#-*- coding: utf-8 -*-
"""
Created on Mon Jan 14 13:49:57 2019

@author: akire
Ya se añadió la parte de cargar datos para continuar con la segmentación
"""


import sys
import os
import tifffile 
import numpy as np
import matplotlib.pyplot as plt
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from PyQt5 import uic
import cv2
from GUI5_Pituitary import PituitarySegm
from GUI5_CellTimeSeries import ContourTimeSeries, ContourTimeSerie
from PyQt5.QtWidgets import QMenu
import re
import csv
import GUI5_Advices as adv
from os.path import isfile, join
from scipy import stats 
from scipy import signal




MainWin= uic.loadUiType("GUI5_MainWin.ui")[0]                                  #Ventana principal
ContourTableWin = uic.loadUiType("GUI5_ContoursTable.ui")[0]                   #Ventana que contiene la tabla


class MainWinClass(QtGui.QMainWindow, MainWin):    
    def __init__(self, ROI, close, parent=None):
        super().__init__(parent)        
        self.setupUi(self)
        self.openAction.triggered.connect(self.openStack)
        self.findRoiAction.triggered.connect(self.dataCheck1)                  #Cuando se elige el menú Segmentation -> Cell Segmentation hay que ir a la función dataCheck1
        self.actionContinueSeg.triggered.connect(self.ContinueSegm)            #Cuando se elige el menú Segmentation -> Load Segmentation hay que ir a la función Continue Segm
        
        
        
        """%%%%%%%%%%%%%%%%%%%%%%%%%
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%
            Inicio Parte de ANA        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%""" 
    
        self.actionData_Normalization.triggered.connect(self.dataChek2)        #Cuando se elige el menú Calcium Analysis -> Data Normalization, hay que ir a la función de dataCheck2

        """%%%%%%%%%%%%%%%%%%%%%%%%%
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%
              Fin Parte de ANA        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%""" 
        
        
        
        
        self.TableWin = 0                                                      #Primero es una bandera que indica que la tabla hasta ahora no existe, si entra a su función correspondiente entonces se convertirá en la variable asociada a la tabla
        
        
        MainWinClass.statusbar = self.statusbar                                #Para poder cambiar esta variable por fuera de la clase https://stackoverflow.com/questions/44046920/changing-class-attributes-by-reference
        MainWinClass.ROI = ROI                                                 #Bandera para saber si hay una ROI roja encima del video
        MainWinClass.close = close                                             #Bandera para indicar que se va a cerrar la ventana principal
        MainWinClass.stack = 0                                                 #Bandera que indica si se ha cargado o no un stack en la ventana 
        
        
    def openStack(self):
        self.imv1.clear()                                                      #Limpiar la imagen principal
        MainWinClass.stack = 0                                                 #Bandera que indica si se ha cargado o no un stack en la ventana 
        
        #Se va a abrir el archivo que se desea analizar
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File',\
                                                     os.getenv('HOME'))        #Obtiene la ruta del SO
        lista0 = str(filename[0])                                              #Ahora filename regresa el nombre como una tupla, hay que tomar su primera parte 
        file_extention = lista0[-3:]                                           #últimos tres carcateres del string anterior

        #Si el archivo NO es tipo tiff manda un mensaje de error y se sale 
        #de la función
        if file_extention != str('tif'):
            self.FileTypeErrorAdviceWin1 = adv.FileTypeAdviceWinClass1()
            self.FileTypeErrorAdviceWin1.show()  
            return                                                             #Salir de la función
        
        #Buscar el archivo y guardarlo en una matriz
        lista1  = lista0.replace('/', '\\\\')                                  #Hay que corregir la ruta del archivo, cambiando los '/' con '\\' (antes no se tenía que hacer esto GUI1 monito)  
        tif = tifffile.TiffFile(str(lista1))                                   #El stack se guarda en tif
        self.data = tif.asarray()                                              #El stack de imágenes se pasa a un arreglo
        forma = self.data.shape
        
        #Si el archivo NO tiene más de 300 frames ó si está abriendo una imagen
        #y NO video, manda un mensaje de error y se sale de la función
        if (len(forma) != 3 or forma[0] < 300):
            self.FileTypeErrorAdviceWin2 = adv.FileTypeAdviceWinClass2()
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
        
        #Mostrar el video y quitar el histograma y los botones que salen 
        #por default
        self.imv1.setImage(self.data, transform=tr)                            #Mostrar el video en la GUI 
        self.imv1.ui.histogram.hide()                                          #Para quitar el histograma y los botones de ROI y menú https://stackoverflow.com/questions/38065570/pyqtgraph-is-it-possible-to-have-a-imageview-without-histogram
        self.imv1.ui.roiBtn.hide()
        self.imv1.ui.menuBtn.hide()
                
        #Obtención de la viewbox y el imageitem de imv1, para poder mostrar la
        #posición del mouse cuando está sobre el video
        self.viewbox = self.imv1.getView()                                     #La viewbox de la imagen imv1
        self.imageitem = self.imv1.getImageItem()                              #el imageitem de la imagen imv1        
              
        #Función que permite mostrar la posición del mouse en la imagen, 
        #junto con el tamaño de la misma
        #En la laptop (porque no funcionó el SignalProxy)
        #https://groups.google.com/forum/#!topic/pyqtgraph/ZlxPGqHCZJ0
        #https://stackoverflow.com/questions/50833107/mouse-coordinates-of-
        #pytqt-graph-line
        def mouseMoved(point):
            #Primero se verifica que el mouse esté dentro de la viewbox
            if self.viewbox.sceneBoundingRect().contains(point):               
                mousePoint = self.viewbox.mapSceneToView(point)                #Cambiamos las coordenadas a posiciones respecto a la imagen
                index_x = int(mousePoint.x())
                index_y = int(mousePoint.y())
                #Ahora verificamos que dichas coordenadas estén dentro de la 
                #imagen, no de la viewbox
                if index_x > 0 and index_x < self.ancho and index_y>0 \
                and index_y<self.alto:
                    self.labelPRUEBA.setText("<span>Size: \
                            <span>%dx<span>%d \<span>pixels, <span>Position: \
                            <span style='font-size: 8pt'>x=%0.1f, \
                            <span style='font-size: 8pt'>y=%0.1f</span>" % \
                            (int(self.ancho), int(self.alto), mousePoint.x(), \
                             mousePoint.y()))        
        self.imv1.scene.sigMouseMoved.connect(mouseMoved)                      #Aquí llamamos a la función que da la posición del mouse en la imagen      

        #Deshabilita el menú que sale con el clic derecho sobre la imagen y 
        #crea uno nuevo, para permitir que el usuario añada ROIs 
        #self.viewbox.setMenuEnabled(False)                                    #con esto se deshabilita el menú con el clic derecho de la imv1 https://stackoverflow.com/questions/44402399/how-to-disable-the-default-context-menu-of-pyqtgraph
        self.viewbox.menu = None                                               #Para quitar todo lo que no es Export... en el menú
        self.imv1.scene.contextMenu = None                                     #Para quitar el Export... en el menú   https://groups.google.com/forum/#!topic/pyqtgraph/h-dyr0l6yZU
        
        MainWinClass.stack = 1                                                 #Indicamos que el stack se está desplegando en la ventana
        

    #Esta función va a revisar que el archivo a abrir sea un video, y va a 
    #pedir los datos del mismo y revisar que tienen sentido, si pasa todos los 
    #filtros procederá a realizar la segmentación
    def dataCheck1(self):      
                                                       
        if MainWinClass.stack == 1:                                            #bandera que indica que SÍ se está desplegndo un video en la ventana
#            self.viewbox.menu = self.NewMenu()                                #Función que crea el nuevo menú al hacer clic derecho sobre el video https://groups.google.com/forum/#!topic/pyqtgraph/3jWiatJPilc
                    
            #Se obtiene la serie de tiempo del stack completo, se va graficar 
            #en la ventana de diálogo 
            self.SerieTiempo = np.zeros(self.NoFrames)
            for frame in range(self.NoFrames):  
                imagen_i = self.data[frame,:,:] 
                self.SerieTiempo[frame] = np.mean(imagen_i) 
                                            
            #Ventana que pide datos del video y deben proporcionarse forzosamente 
            #para el análisis posterior
            self.PlotDialogWin = adv.PlotDialogWinClass(self.NoFrames)         #"Llamamos" a la clase de la ventana de datos
            self.PlotDialogWin.okClicked.connect(self.cellSegm)                #Señal emitida si los datos ingresados a la ventana de diálogo fueron aceptados
#            self.PlotDialogWin.closeClicked.connect(self.closePlotDialog)     #Señal emitida si la ventana de datos se cerró
            ItemGrafica = pg.PlotCurveItem(pen=(0,255,0))                      #Se hace un ítem de una gráfica  
            ItemGrafica.setData(self.SerieTiempo)                              #Se agregan los datos de la serie de tiempo al ítem} 
            self.PlotDialogWin.TimeSeriesPlot.addItem(ItemGrafica)             #Se agrega el ítem a la ventana de datos                
            self.PlotDialogWin.show()                                          #Se muestra la ventana de datos
        
        elif MainWinClass.stack == 0:                                          #Si no se está desplegando un video en la ventana
            self.statusbar.showMessage("There is no stack in the window",1000)
            return
        
        
        
   #CREO QUE ESTO SE PUEDE QUITAR    
#    #Función llamada si la ventana de datos se cerró y los datos proporcionados 
#    #no fueron adecuados
#    def closePlotDialog(self):
#        self.imv1.clear()                                                      #Se quita el video de la imagen
#        MainWinClass.stack = 0                                                 #Se indica que el video se quitó de la ventana


    #Función llamada si los datos se proporcionaron de manera adecuada 
    #es decir se llevará a cabo la segmentación y se llama a la clase tabla
    def cellSegm(self):
        
        self.viewbox.menu = self.NewMenu()                                     #Función que crea el nuevo menú al hacer clic derecho sobre el video https://groups.google.com/forum/#!topic/pyqtgraph/3jWiatJPilc
        
        inFrame = self.PlotDialogWin.frame1                                    #Frame inicial para el análisis
        finFrame = self.PlotDialogWin.frame2                                   #Frame final para el análisis
        self.CellDiam = self.PlotDialogWin.CellSize                            #Diámetro de la célula
        cellType = self.PlotDialogWin.indexOfChecked                           #Neuronas o hipófisis     
        SerieTiempoParc = self.SerieTiempo[inFrame:finFrame]                   #Serie de tiempo parcial depende de lo que introduzca el usuario


        #Analisis por tipo celular
        #1 para hipófisis, 0 para neuronas
        if cellType == 1:                                                      
            #Se encuentran las células, se obtiene un diccionario con los 
            #contornos (Número consecutivo:[x,y])
            self.ROI_dict = PituitarySegm(inFrame, finFrame, self.CellDiam, \
                                          SerieTiempoParc, self.data)          #Llama a la func que hace la segmentación 


            #Crear el diccionario de series de tiempo (se va a usar para 
            #graficar en la ventana de tabla)
            self.TimeSerDict = ContourTimeSeries(self.data, self.ROI_dict, \
                                        self.NoFrames, self.alto, self.ancho, \
                                        self.CellDiam)                         #Función que crea el diccionario de series de tiempo 
            
            #Se crea la tabla de contornos       
            bandera_ROI = 0                                                    #Bandera para indicar que no hay una ROI circular en la imagen             
            self.TableWin = ContourTableWinClass(self.ROI_dict,\
                                self.TimeSerDict,self.imv1, self.alto, \
                                self.ancho, self.CellDiam, bandera_ROI, \
                                self.data, self.NoFrames, cellType, inFrame, \
                                finFrame, row=False, cancel=0, parent=self) 
                                                                                              
            self.TableWin.show()                                               #Se muestra la tabla de contornos
            self.TableWin.ContourCheckBox.setChecked(True)                     #Marcando la checkbox de los contornos para indicar que se están mostrando
            
            
            
        #1 para hipófisis, 0 para neuronas    
        elif cellType == 0:                                                    #Si el botón que eligió es 1 (neuronas)
            self.segmNeuron(inFrame, finFrame)
                                                               

    #Función que va a hacer la segmentación de neuronas, hay que pasarla a 
    #un archivo aparte, como la de hipófisis        
    def segmNeuron(self, a, b):
        print('Aquí va el análisis de neuronas')

        
    #Menú que sale cada vez que se hace clic derecho en la imagen 
    #(para la ROI agregada por el usuario)    
    def NewMenu(self):
        self.viewbox.menu = QMenu()                                            #Se crea un menú asociado a la viewbox de imv1, ver función dataCheck1
        
        #Para agregar al menú la opción de crear una nueva ROI
        self.NuevaROIimg = QtGui.QAction("New ROI", self.viewbox.menu)         #Se crea una opción de menú 
        self.NuevaROIimg.triggered.connect(self.NewROIimg)                     #Cuando se de clic se llama a la función NewROIimg
        self.viewbox.menu.addAction(self.NuevaROIimg)                          #Se agrega la opción al menú

        #Para agregar la menú la opción de quitar la ROI superpuesta
        self.QuitarROIimg = QtGui.QAction("Remove ROI", self.viewbox.menu)     #Se crea una opción de menú
        self.QuitarROIimg.triggered.connect(self.RemoveROIimg)                 #Cuando se de clic se llamará a la función RemoveROIimg
        self.viewbox.menu.addAction(self.QuitarROIimg)                         #Se agrega la opción al menú

        #zoom = QtGui.QAction(u'Zoomer', self.viewbox.menu)                    #Para mostrar cómo se agrega un separador en el menú
        #self.viewbox.menu.addSeparator()
        #self.viewbox.menu.addAction(zoom)
        return self.viewbox.menu                                               


    #Función que agrega un círculo en el video que va a servir para que el 
    #el usuario añada una ROI a la tabla
    def NewROIimg(self):
        #Primero hay que revisar la bandera, si hay una ROI circular encima 
        #del video hay que quitarla primero
        bandera = ContourTableWinClass.bandera                                 #Bandera que viene de la clase tabla, permite saber si hay una ROI roja en la imagen o no
        if bandera == 1:
            self.imv1.removeItem(self.ROI)                                     #Si sí hay una ROI circular en la imagen, quítala            
            
        #Se obtiene la posición del mouse a partir del label en la barra de 
        #status, ahí se pondrá el círculo
        words = str(self.labelPRUEBA.text()) 
        lista=re.findall(r'\d+', words)                                        #https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python
        x=lista[3]                                                             #En teoría siempre van a estar en estas posciones de la lista los enteros de las posiciones del label
        y=lista[6]
        
        #Se agrega el círculo en la posición (x,y) anterior
        #https://stackoverflow.com/questions/41488864/pyqtgraph-widget-addline
        #-change-color-width
        self.ROI = pg.CircleROI([x,y], [self.CellDiam,self.CellDiam], \
                          pen=pg.mkPen('r'), \
                          maxBounds=QtCore.QRectF(0, 0, self.ancho, self.alto))#Para limitar el círculo al video https://github.com/pyqtgraph/pyqtgraph/issues/288 y https://github.com/pyqtgraph/pyqtgraph/issues/288

        #Se elimina la posibilidad de cambiar el tamaño del círculo
        lista = self.ROI.getHandles()                                          #Como es un círculo solo tiene un handle que es para cambiar el tamaño de la roi
        indice = self.ROI.indexOfHandle(lista[0])                              #da el índice del handle anterior (creo que siempre será 0 pero no estoy segura)        
        self.imv1.addItem(self.ROI)                                            #Se agrega la ROI circular en la imagen
        self.ROI.removeHandle(int(indice))                                     #para quitar el handle del resize (se evita que se pueda modificar el tamaño de la ROI)https://www.programcreek.com/python/example/94481/pyqtgraph.RectROI                                                           

        ContourTableWinClass.bandera = 1                                       #Se cambia a 1 la bandera de la clase tabla para indicar que se ha agregado una ROI roja
        MainWinClass.ROI = self.ROI                                            #Permitirá conocer la posición de la ROI para agregarla a la tabla


    #Función que va a quitar el círculo anterior si ya hay uno mostrado 
    #(con el menú que sale al hacer clic derecho en la imagen)
    def RemoveROIimg(self):
        bandera_ROI = ContourTableWinClass.bandera                             #Hay que obtener el valor de la bandera, para saber si hay o no un círculo en la imagen
        if bandera_ROI == 1:
            self.imv1.removeItem(self.ROI)                                     #Si sí hay una ROI circular en la imagen, quítala
            ContourTableWinClass.bandera = 0                                   #Y pon la bandera en cero    
            MainWinClass.ROI = 0                                               #Y hay que indicar que no hay una ROI en la imagen, es decir no se puede obtener una posición

        else:
            self.statusbar.showMessage("There is no ROI in the image",1000)    #Si no hay una ROI, avisa en la barra de status que no hay nada que quitar 
    
    
    #Función que será llamada para continuar con la segmentación a partir de 
    #datos previamente guardados en archivos
    def ContinueSegm(self):

        if MainWinClass.stack == 1:                                            #Si el stack ya está desplegado en la ventana
            #Se va a abrir el archivo que se desea analizar, se debe abrir el 
            #archivo Nombre_RawData.csv 
            filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File',\
                                                         os.getenv('HOME'))    #Obtiene la ruta del SO
            lista0 = str(filename[0])                                          #Ahora filename regresa el nombre como una tupla, hay que tomar su primera parte 
            file_extention = lista0[-12:]                                      #últimos 12 caracteres del string anterior        
    
            #Si el archivo NO es tipo Name_RawData.csv manda un mensaje de 
            #error y se sale de la función 
            if file_extention != str('_RawData.csv'):
                self.FileTypeErrorAdviceWin3 = adv.FileTypeAdviceWinClass3() 
                self.FileTypeErrorAdviceWin3.show()  
                return                                                         #Salir de la función
    
            #Vamos a obtener el nombre completo del archivo con su extensión
            contador = 0
            for character in reversed(lista0):                                 #Se repasa cada caracter dentro del path de atrás hacia adelante 
                if character != str("/"):                                      #Si aún no es un caracter de / sigue contando
                    contador += 1                    
                else:
                    break                                                      #Si ya encontraste un signo de / detén el contador y salte del for
                
            dataFile =lista0[-contador:]                                       #Nombre del archivo con todo y extensión 
            path = lista0[0:len(lista0)-(contador+1)]                          #Path del archivo, donde se van a buscar los demás archivos
            parcName = dataFile[0:len(dataFile)-12]                            #Porque len(_RawData.csv) = 12
            roiFile = parcName + str("_ROI.csv")                               #Este debe ser el nombre del archivo con la información de las ROIs
            infoFile = parcName + str("_Info.csv")                             #Este debe ser el nombre del archivo con la  información del análisis
            
            #Lista de los archivos en el directorio del path
            lista1  = path.replace('/', '\\\\')                                #Hay que corregir la ruta del archivo, cambiando los '/' con '\\' (antes no se tenía que hacer esto GUI1 monito)  
            onlyfiles = [f for f in os.listdir(lista1) if isfile(join(path,f))]#Solo los archivos en el directorio
                        
            lista2 = [dataFile, roiFile, infoFile]                             #Lista de los archivos requeridos para continuar                        
            resultado = all(x in onlyfiles for x in lista2)                    #Revisar si todos los archivos requeridos están en el directorio
                      
            if resultado == False:                                             #Los archivos requeridos NO están en el directorio
                self.FileTypeErrorAdviceWin4 = adv.FileTypeAdviceWinClass4() 
                self.FileTypeErrorAdviceWin4.show()  
                return                                                         #Salir de la función                

            #Hay que leer la información de los archivos, y guardarla en arrays
            rawDataArr = np.loadtxt(lista1+'\\'+'\\'+str(dataFile), \
                                    delimiter=",", comments='#', skiprows=1)   #Su primer columna es del número de frame, entonces no hay que tomarlo en cuenta
            roiPosArr = np.loadtxt(lista1+'\\'+'\\'+str(roiFile),\
                                   delimiter=",", comments='#', skiprows=1)

            #Para obtener la información que está dada en strings no en datos
            #en una lista de listas
            infoFile = lista1+'\\'+'\\'+str(infoFile)
            with open(infoFile, 'r') as f:
              reader = csv.reader(f)
              dataInfoList = list(reader)

            #separamos cada lista de la lista anterior
            cellTypeInfo = dataInfoList[0]
            initFrame = dataInfoList[1]
            finalFrame = dataInfoList[2]
            cellDiam = dataInfoList[3]
            
            #Obtenemos la información de cada lista y la guardamos en la
            #variable final
            self.CellDiam = int(cellDiam[1])
            inFrame = int(initFrame[1])
            finFrame = int(finalFrame[1])
            
            if cellTypeInfo[1] == 'Pituitary':
                cellType = 1

            elif cellTypeInfo[1] == 'Neurons':
                 cellType = 0

            else:
                self.statusbar.showMessage("There is an error with \
                                           the info File ",1000)               #Si la información del tipo de célula no es de neurona o pituitaria, la info es incorrecta
                return 

            #Crear los diccionarios a partir de los arreglos anteriores
            Keys = roiPosArr[:,0]                                              #Array de llaves de los contornos
            Keys = Keys.astype(int)
            print(Keys)
            self.TimeSerDict = {}
            self.ROI_dict = {}
            
            contador=1                                                         #Cuenta el número de células a partir del archivo
            for key in Keys:
                self.TimeSerDict[key] = rawDataArr[:,contador]                 #Creación diccionario de series de tiempo
                self.ROI_dict[key]=[roiPosArr[contador-1,1],\
                              roiPosArr[contador-1,2]]                         #Creación diccionario de posiciones
                contador += 1


            #Se crea la tabla de contornos       
            self.viewbox.menu = self.NewMenu()                                 #Función que crea el nuevo menú al hacer clic derecho sobre el video https://groups.google.com/forum/#!topic/pyqtgraph/3jWiatJPilc
            
            bandera_ROI = 0                                                    #Bandera para indicar que no hay una ROI circular en la imagen             
            self.TableWin = ContourTableWinClass(self.ROI_dict,\
                                self.TimeSerDict,self.imv1, self.alto, \
                                self.ancho, self.CellDiam, bandera_ROI, \
                                self.data, self.NoFrames, cellType, inFrame, \
                                finFrame, row=False, cancel=0, parent=self) 
                                                                                              
            self.TableWin.show()                                               #Se muestra la tabla de contornos
            self.TableWin.ContourCheckBox.setChecked(True)                     #Marcando la checkbox de los contornos para indicar que se están mostrando
            
        
        elif MainWinClass.stack == 0:                                          #Si no se está desplegando un video en la ventana
            self.statusbar.showMessage("There is no open stack in the \
                                       window",1000)
            return
            

    #Función que va a permitir cerrar adecuadamente las ventanas abiertas
    def closeEvent(self, event):                                               #Es para quitar todo en la imagen cuando se cierre la tabla de contornos https://www.qtcentre.org/threads/20895-PyQt4-Want-to-connect-a-window-s-close-button
        event.ignore()                                                         #Detenemos el evento para cerrar primero las ventanas hijas
        MainWinClass.close = 1                                                 #Ponemos la bandera en 1 para indicar que el programa principal se va a cerrar

#        oculta = self.TableWin.isHidden()
#        print(oculta)
#        tableVis = self.TableWin.isVisible()                                   #Con esto sabemos si la tabla es visible o no, para cerrarla adecuadamente        
        print("Se abrió o no se abrió la tabla:")
        print(self.TableWin)
        
        if self.TableWin != 0 :                                                #Si la tabla SÍ es visible Ó SÍ se abrió y ya se cerró, hay que invocar su función de cerrado
            if self.TableWin.isHidden() == 1:                                  #Si la tabla está oculta (i.e. se abrió antes y ya se cerró)
                event.accept()                                                 #Cierra la ventana principal

            else:                                                              #Si la tabla ES visible
                self.TableWin.close()                                          #Invoca su opción de cerrado          
                tableFlag = ContourTableWinClass.cancel                        #Para saber si se presionó cancelar en la tabla
                if tableFlag == 0:                                             #Si NO se presionó el botón de cancelar en la tabla, HAY que cerrar la ventana principal
                    event.accept()

        else:                                                                  #Si la tabla nunca se abrió, cierra la ventana principal
            event.accept()                                                     #Cerramos la ventana principal
        #Aquí invocamos el cierre del resto de ventanas hijas






    """%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%
        Inicio Parte de ANA        
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%"""     
    #Función que va a revisar primero si el archivo que se va a abrir es tipo 
    #Nombre_RawData.csv , si no va a arrojar un error
    def dataChek2(self):

        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File',\
                                                     os.getenv('HOME'))        #Obtiene la ruta del SO
        lista0 = str(filename[0])                                              #Ahora filename regresa el nombre como una tupla, hay que tomar el primer valor
        file_extention = lista0[-12:]                                          #últimos 12 caracteres del string anterior        

        #Si el archivo NO es tipo _RawData.csv manda un mensaje de 
        #error y se sale de la función 
        if file_extention != str('_RawData.csv'):
            self.FileTypeErrorAdviceWin3 = adv.FileTypeAdviceWinClass3() 
            self.FileTypeErrorAdviceWin3.show()  
            return                                                             #Salir de la función

        #Buscar el archivo y guardarlo en una matriz
        lista1  = lista0.replace('/', '\\\\')                                  #Hay que corregir la ruta del archivo, cambiando los '/' con '\\' (antes no se tenía que hacer esto GUI1 monito)  
        #Hay que leer la información del archivo y guardarla en un array
        self.rawDataArr = np.loadtxt(lista1, delimiter=",", comments='#',\
                                skiprows=1)
        self.rawDataArr =  self.rawDataArr[:,1:]                             #Su primer columna es del número de frame, entonces no hay que tomarlo en cuenta
                
        #Ahora hay que pedir el tiempo de muestreo
        self.TimeSamplingWin = adv.SamplingTimeClass()
        self.TimeSamplingWin.okClicked.connect(self.dataNormalization)
        self.TimeSamplingWin.show()
        
        
    #Función que va a realizar la normalización de los datos brutos, pero solo 
    #si el archivo es tipo Nombre_RawData.csv     
    def dataNormalization(self):
        
        sampleTime = self.TimeSamplingWin.samplTime                            #Tiempo de muestreo que ingresó el usuario 
        totalFrames = self.TimeSamplingWin.totFrame                            #Número de frames totales ingresado por el usuario
#        datos = self.rawDataArr
        self.rawDataArr = np.swapaxes(self.rawDataArr,0,1)

        print(totalFrames)
        print(sampleTime)
        
        b,a = signal.bessel(3,sampleTime,btype='lowpass') #grado del filtrado 0.1
        datosfilt=signal.filtfilt(b,a,self.rawDataArr,axis=-1)
        datosNorm=self.detrend(self.fmin(self.rawDataArr, totalFrames),totalFrames)
        datosNormFilt=(self.fmin(datosfilt,totalFrames)) #s/detrend
        dt=sampleTime
        time =np.arange(0,dt*datosNorm.shape[-1],dt)         
        
        plt.figure(0)
        plt.clf()
        plt.subplot(221)
        plt.plot(self.rawDataArr[:,0].T)
        
        plt.subplot(222)
        plt.plot(datosNormFilt[:,0].T)

        
        #Aquí iría la parte de normalización de los datos brutos
        #Esto solo es para que veas cuáles son las variables que tienen el 
        #arreglo de datos brutos y el tiempo de muestreo    
    def fmin (self, datos, totalFrames):
        baseline=np.amin(datos[:,:totalFrames],-1)[:,None] 
        return datos/baseline 
    
    def detrend(self, datos, window):#mismo valor que en baseline
        print(window)
        print(datos.shape)
        x=np.arange(0,window)
        x = x[None,:]*np.ones((datos.shape[-2],1))
        x=np.ravel(x)
        slopes=[]
        intercepts=[]
        y = np.ravel(datos)
        slope,inter,_,_,_=stats.linregress(x,y)
        slopes.append(slope)
        intercepts.append(inter)
        #-1 is the axis of ROI's
        slopes=np.array(slopes)
        intercepts=np.array(intercepts)
        t=np.arange(0,datos.shape[-1])
        trends=np.array((intercepts)[:,None] + np.array(slopes)[:,None] * t[None,:])
        return datos - trends[:,None,:]


                             
#        print("Tiempo de muestreo: ")
#        print(sampleTime)
#        print("Frames totales")
#        print(totalFrames)
#        print("Forma del arreglo: ")
#        print(self.rawDataArr.shape)                                           #self.rawDataArr es el array que contiene a los datos brutos 



    """%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%
          Fin Parte de ANA        
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%"""     





 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


#Se crea la tabla de contornos presentes en la imagen 
class ContourTableWinClass(QtWidgets.QDialog, ContourTableWin):                #Ventana con la tabla de contornos
    def __init__(self, ContoursDict, TimeSerDict, imv1, alto, ancho, CellDiam,\
                 bandera, data, NoFrames, cellType, inFrame, \
                 finFrame, row, cancel,  parent ):                                            # bandera, data, NoFrames, row, parent = MainWinClass):

                                                        
        super(ContourTableWinClass, self).__init__()
        self.setupUi(self)
        
        #Esta bandera indica si hay una ROI circular que se va a añadir a 
        #la tabla
        ContourTableWinClass.bandera = bandera                                 #Para poder cambiar esta variable por fuera de la clase https://stackoverflow.com/questions/44046920/changing-class-attributes-by-reference
        ContourTableWinClass.row = row                                         #Para saber qué renglón es el que se ha seleccionado para graficar 
        ContourTableWinClass.cancel = cancel                                   #Para indicar que al tratar de cerrar la tabla se presionó el botón de cancelar
                
        #Se hacen "self" diferentes variables aceptadas en la clase
        self.cellType = cellType
        self.inFrame = inFrame
        self.finFrame = finFrame
        self.parent = parent
        self.ContoursDict = ContoursDict
        self.TimeSerDict = TimeSerDict  
        self.imv1 = imv1
        self.CellDiam = CellDiam
        self.data = data
        self.NoFrames = NoFrames
        self.ContoursTable.setRowCount(len(self.ContoursDict))                 #Número de renglones que tendrá la tabla dependiendo del número de ROIs
        self.ContoursTable.setColumnCount(2)                                   #COLUMNAS QUE TENDRÁ LA TABLA, SI NO SE PONE UNA TERCER COLUMNA LA SEGUNDA COLUMNA SE MUEVE HACIA ABAJO
        self.botones_series = QtGui.QButtonGroup()                             #Grupo de radio buttons para mostrar las series
        self.botones_remove = QtGui.QButtonGroup()                             #Grupo de radio buttons para eliminar las series
        
        #Son los check box para poner y quitar ROIs y etiquetas
        self.LabelCheckBox.clicked.connect(lambda: self.LabelContour(imv1, \
                                        alto, ancho))
        self.ContourCheckBox.clicked.connect(lambda: self.LabelContour(imv1, \
                                        alto, ancho))
        
        #Es el boton de añadir una ROI a la tabla a partir de la ROI añadida 
        #a la imagen
        self.addROIbutton.clicked.connect(lambda: self.AddROI(imv1, alto, \
                                                              ancho))              
        
        #Es el botón de quitar una ROI de la tabla 
        self.removeROIbutton.clicked.connect(lambda: self.RemoveROI(imv1,  \
                                                              alto, ancho))
        
        #Es el botón para guardar las ROIs y las series de tiempo
        self.saveButton.clicked.connect(lambda: self.Save())
        
        
        #Para generar la tabla de contornos se repasa cada key del diccionario
        renglon=0                                                              #Contador para agregar renglones a la tabla
        for key in self.ContoursDict.keys():                                                                               
            pos = self.ContoursDict[key]                                       #Esto era porque lo contornos encontrados no tenían forma definida, pero eso va a cambiar!!!
            self.ItemsTabla(renglon, key, pos, alto, ancho, imv1)                                     
            renglon = renglon + 1                                              #Para pasar al siguiente renglón
                    
        self.ContoursTable.setHorizontalHeaderLabels(str("No.;Plot [Pos]"\
                                                         ).split(";"))         #Etiquetas de las columnas 

#        self.ContoursTable.setHorizontalHeaderLabels(str("No.;Plot [Pos]\
#        ;Remove").split(";"))                                                  #Etiquetas de las columnas 
        self.ContoursTable.verticalHeader().hide()                             #Quitar letrero vertical   https://stackoverflow.com/questions/14910136/how-can-i-enable-disable-qtablewidgets-horizontal-vertical-header                                             

        #Mostrando las ROIs sobre el video 
        self.scatterItem = self.ContoursOnVideo()                              #Se genera el ítem de los contornos
        imv1.addItem(self.scatterItem)                                         #Se agrega el item de la gráfica de puntos a la imagen
        

    #Función que superpone las ROIs sobre el video, para corregir la posición 
    #se añadió el 0.5 (así ya sale como en matplotlib)
    def ContoursOnVideo(self):
            posiciones = np.array(list(self.ContoursDict.values()))+0.5            #Se obtienen los centros de los círculos dentro de una matriz, y se corrigen por 0.5
            scatterItem = pg.ScatterPlotItem(pxMode=False, size=self.CellDiam, \
                                             pen=pg.mkPen('y', width=1), \
                                             brush=pg.mkBrush(0,0,0,0))            #Los círculos se generan como un scatterplot (pyqtgraph->ejemplos->scatterplot)
                                                                                   #pxMode=False :spots must be completely re-drawn every time because their apparent transformation may have changed
            scatterItem.setData(pos=posiciones)                                    #http://www.pyqtgraph.org/documentation/graphicsItems/scatterplotitem.html                            
            return(scatterItem)
        

    #Función que grafica las series de tiempo a partir de la tabla de contornos 
    #(a partir del diccionario de series de tiempo)     
    def  PlotTimeSeries(self):            
        self.TimeSeriesGraph.clear()                                           #Se borra la gráfica que exista previamente

        #Para saber qué serie de tiempo es la que hay que mostrar 
        #(a partir de su key)
        button = self.sender()                                                 #https://stackoverflow.com/questions/54316791/pyqt5-how-does-a-button-delete-a-row-in-a-qtablewidget-where-it-sits
        row = self.ContoursTable.indexAt(button.pos()).row()                   #Renglón donde está la checkbox que se ha presionado
        key = self.ContoursTable.item(row,0).text()                            #Texto que aparece en la primer columna de la tabla   
        key = int(key)                                                         #Key para el diccionario de series de tiempo
        ContourTableWinClass.row = row

        #Se muestra la gráfica de la serie de tiempo
        plot1 = self.TimeSerDict[key]                                          #Serie de tiempo del diccionario        
        ItemGrafica = pg.PlotCurveItem(pen=(0,255,255))                        #Se hace un ítem de una gráfica  
        ItemGrafica.setData(plot1)                                             #Se agregan los datos al ítem
        self.TimeSeriesGraph.addItem(ItemGrafica)                              #Se agrega el ítem a la GUI  

        
    #Para quitar las ROIs a partir de la tabla de contornos
    def RemoveROI(self, imv1, alto, ancho):        

        #Para saber qué contorno es el que hay que quitar (a partir de su key)
        row = ContourTableWinClass.row
        
        if row is False:
            MainWinClass.statusbar.showMessage("ROI not selected", 1000)       #Para indicar en la barra de status que no hay una ROI que se pueda agregar a la tabla
        
        else:                                                     
            key = self.ContoursTable.item(row,0).text()                        #Texto que aparece en la primer columna de la tabla   
            key = int(key)                                                     #Hay que cambiarlo a integer porque era string, este es el key del diccionario                                                                                         

            #Se quita el renglón de la tabla
            self.ContoursTable.removeRow(row)                                  #Se quita el renglón de la tabla
    
            #Hay que quitar el contorno y la serie de tiempo de los 
            #diccionarios correspondientes
            del self.ContoursDict[key]                                         #Hay que quitar la ROI del diccionario de ROIs
            del self.TimeSerDict[key]                      
    
            #Hay que llamar a la función de LabelContour para revisar las 
            #checkbox de la tabla 
            self.LabelContour(imv1, alto, ancho)
    
            #Después de quitar la ROI de la tabla, ya no hay ninguna ROI 
            #elegida dentro de la tabla, hay que poner esta bandera en False 
            #si no va quita las ROIs consecutivas
            ContourTableWinClass.row = False
            
            #Hay que quitar la gráfica si se está quitando la ROI??        
                    
        
    #Para controlar las checkbox que muestran los contornos y las etiquetas 
    #junto con la imagen que se despliega de los contornos!!
    def LabelContour(self, imv1, alto, ancho):
        if self.ContourCheckBox.isChecked() == True:                           #Si la check box de los contornos está activada
             if self.LabelCheckBox.isChecked() == True:                        #Si la check box de las etiquetas está activada
                 imv1.removeItem(self.scatterItem)
                 self.scatterItem = self.ContoursOnVideo()                     #Se genera el ítem de los contornos
                 imv1.addItem(self.scatterItem)                                #Se agrega el item de la gráfica de puntos a la imagen
                         
                 for key in self.ContoursDict.keys():                          #Para poner las etiquetas de los contornos                         
                     text = pg.TextItem(anchor=(0.3,0.3), fill=(0, 0, 0, 150)) 
                     text.setText(str(key), color=(255, 255, 255))             #Texto que se desplegará al lado de la ROI
                     text.setParentItem(self.scatterItem) 
                     contorno = self.ContoursDict[key];
                     a,b = contorno;
                     text.setPos(a,b)                       
                 
             else:                                                             #Si la check box de las etiquetas no está activada
                 imv1.removeItem(self.scatterItem)          
                 self.scatterItem = self.ContoursOnVideo()                     #Se genera el ítem de los contornos
                 imv1.addItem(self.scatterItem)                                #Se agrega el item de la gráfica de puntos a la imagen
                                          
        if self.ContourCheckBox.isChecked() == False:                          #Si la check box de los contornos no está activada
            if self.LabelCheckBox.isChecked() == True:                         #Si la check box de las etiquetas está activada
               imv1.removeItem(self.scatterItem)                               #Se va a quitar todo y se va a desactivar la check box de etiquetas         
               self.scatterItem = self.ContoursOnVideo()                
               self.LabelCheckBox.setChecked(False) 
                
            else:                                                              #Si la check box de las etiquetas no está activada
               imv1.removeItem(self.scatterItem)                               #Entonces hay que quitar todo                 
               self.scatterItem = self.ContoursOnVideo() 


    #Para agregar los ítems a los renglones de la tabla, se usa varias veces
    def ItemsTabla(self, rowPosition, llave, posicion, alto, ancho, imv1):
        
        item1 = QtGui.QTableWidgetItem(str(llave))                             #El string de numeración de la tabla
        self.ContoursTable.setItem(rowPosition, 0, item1)                      #El string se pone en el i-ésimo renglón y columna 0
       
        item2 = QtGui.QRadioButton(str(posicion))                              #Ponemos un radiobutton en cada renglón con la posición del contorno
        item2.setChecked(False)                                                #Y que el radiobutton no esté marcado
        item2.clicked.connect(lambda: self.PlotTimeSeries())                   #Cuando se presione un radiobutton, llamar a la función PlotTimeSeries https://www.tutorialspoint.com/pyqt/pyqt_qradiobutton_widget.htm
        self.botones_series.addButton(item2)                                   #El radio button se agrega al grupo self.botones_series
        self.ContoursTable.setCellWidget(rowPosition, 1, item2)                #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview
                    
        return


    #Función que agrega la ROI del usuario al diccionario de ROIs, a la imagen  
    #de contornos, al diccionario de series de tiempo, a la tabla                
    def AddROI(self, imv1, alto, ancho):
        
        flag = ContourTableWinClass.bandera                                    #Para saber si sí hay una ROI roja encima del video
        if flag ==0:                                                           #0= No hay ROI en la imagen
            MainWinClass.statusbar.showMessage("There is no ROI in the image",\
                                       1000)                                   #Para indicar en la barra de status que no hay una ROI que se pueda agregar a la tabla

        elif flag ==1:                                                         #1= Hay una ROI en la imagen
            
            pos=MainWinClass.ROI.pos()                                         #Es la posición de la esquina superior izquierda del rectángulo que contiene al círculo (pyqtgraph)                     
            diametro = int((self.CellDiam-1)/2)                                 #El -1 es por ser un número impar
            x = round(pos[0])+diametro                                         #Se calcula el centro del círculo 
            y = round(pos[1])+diametro
            centro = [x,y]

            #Encontrar la key más grande del diccionario para elegir la 
            #consecutiva
            llaves = list(self.ContoursDict.keys())
            llave = max(llaves)+1
            self.ContoursDict[llave] = [x,y]                                   #Agregar la nueva posición al diccionario

            
            #Agregar la serie de tiempo de la ROI al diccionario
            serie = ContourTimeSerie(self.data, centro, self.NoFrames, alto, \
                                     ancho, diametro)            
            self.TimeSerDict[llave] = serie
            
            
            #Agregar la ROI a la tabla
            rowPosition = self.ContoursTable.rowCount()                        #último renglón de la tabla
            self.ContoursTable.insertRow(rowPosition)                          #Se agrega un renglón vacío al final de la tabla
            self.ItemsTabla(rowPosition, llave, centro, alto, ancho, imv1)


            #Hay que llamar a la función de LabelContour para revisar las 
            #checkbox de la tabla (con esto agregamos también la ROI al video
            #dependiendo si se están mostrando o no en pantalla las ROIs)
            self.LabelContour(imv1, alto, ancho)
            
            
            #Quitar la ROI roja del video
            #Por ahora se quedará así, parece que es mejor ir arrastrando 
            #la misma ROI en lugar de dar clic cada vez 


    #Función que guarda la información en archivos csv         
    def Save(self):        
        self.filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', \
                                                     os.getenv('HOME'))        #Obtiene la ruta del SO
        lista0 = str(self.filename[0])                                         #Ahora filename regresa el nombre como una tupla, hay que tomar su primera parte 
        lista1  = lista0.replace('/', '\\\\')                                  #Hay que corregir la ruta del archivo, cambiando los '/' con '\\' (antes no se tenía que hacer esto GUI1 monito)        
        #lista1 tiene la ruta incompleta de dónde guardar el archivo
        #https://pythonprogramming.net/file-saving-pyqt-tutorial/         
        
        #Rutas completas de donde se guardarán los archivos
        namePos = str(lista1) + str('_ROI.csv')
        nameData = str(lista1) + str('_RawData.csv')
        nameInfo = str(lista1) + str('_Info.csv')
        
        #Para guardar las series de tiempo (Data)
        series = np.array(list(self.TimeSerDict.values()))                     #Lista de listas de las series de tiempo, cada lista es una columna!!!
        series = series.transpose()                                            #Array de series de tiempo en columnas
        llaves = list(self.TimeSerDict.keys())                                 #Lista de las llaves de cada serie 
        frames = np.array(list(range(len(series[:,0]))))                       #Lista con el número de frames
        frames = frames.transpose()
        frames = frames.reshape(len(series[:,0]),1)                            #Hay que cambiar la forma del arreglo para el siguiente paso
        series2 = np.hstack((frames,series))                                   #Esto es para poner al inicio de cada columna el número de ROI

        #Generar el encabezado para el archivo de Data
        dataHead = "Frame,"
        for llave in llaves:
            dataHead = dataHead + str('ROI')+str(llave)+str(',')
        
        dataHead = dataHead[:-1]

        #Guardar el archivo de datos 
        np.savetxt(nameData, series2, delimiter=",", fmt="%.3f", \
                   header=dataHead, comments='')                               #%.3f es para guardar los datos como float con 3 decimales después del punto
        #https://thatascience.com/learn-numpy/save-numpy-array-to-csv/
        #https://stackoverflow.com/questions/36210977/python-numpy-savetxt-hea\
        #der-has-extra-character/36211002
        
        #Para guardar las posiciones de las ROIs
        llaves = np.array(llaves)
        llaves = llaves.transpose()
        llaves = llaves.reshape(len(llaves),1)                                 #Para usar las llaves de las ROIs como primer columna
        pos = np.array(list(self.ContoursDict.values()))
        pos2 = np.hstack((llaves,pos))                                          #Esta es una matriz con las columnas llaves|pos X|posY

        #Guardar el archivo de datos 
        np.savetxt(namePos, pos2, delimiter=",", fmt="%u", header='ROI, X, Y',\
                   comments='')                                                #%.3f es para guardar los datos como float con 3 decimales después del punto        
            
        #Guardar el archivo de Info
        if self.cellType == 1:                                                 #El tipo celular cambia con la bandera self.cellType
            Info = [['Cell type','Pituitary'],['Initial frame', self.inFrame],\
                    ['Final frame', self.finFrame],\
                    ['Cell radius', self.CellDiam]]
            
        elif self.cellType == 0:    
            Info = [['Cell type','Neurons'],['Initial frame', self.inFrame],\
                    ['Final frame', self.finFrame],\
                    ['Cell radius', self.CellDiam]]     

        with open(nameInfo, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(Info)            


 
    
    def closeEvent(self, event):                                               #Es para quitar todo en la imagen cuando se cierre la tabla de contornos https://www.qtcentre.org/threads/20895-PyQt4-Want-to-connect-a-window-s-close-button
        event.ignore()                                                         #Evitamos que la tabla se cierre enseguida

        result = QtGui.QMessageBox.question(self, 'Confirm', 
                        'Do you want to save the data before close the table?',
                        QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard |\
                        QtGui.QMessageBox.Cancel)                              #Ventana de mensaje que pregunta si el usuario desea guardar los datos, descartarlos o cancelar el cerrar la tabla 
                                                                               #https://pythonprogramming.net/pop-up-messages-pyqt-tutorial/
        flag = ContourTableWinClass.bandera                                    #Para saber si hay una ROI roja en la imagen

        if result == QtGui.QMessageBox.Save:                                   #Si se presionó el botón de guardar
            ContourTableWinClass.cancel = 0                                    #Indicamos que SÍ se desea cerrar la ventana de la tabla, sirve cuando la ventana principal se va a cerrar
            self.Save()                                                        #Si se van a guardar los datos, abrir la ventana de guardar datos
            if self.filename[0] != str(''):                                    #Si sí se guardaron los datos
                self.imv1.removeItem(self.scatterItem)                         #Quitar el video de las ventanas y las etiquetas
                self.imv1.clear()  
                MainWinClass.stack = 0                                         #Indicar que se quitó el stack de la ventana
         
                if flag == 1:                                                  #Si sí hay una ROI roja encima de la imagen
                    redROI = MainWinClass.ROI                                  #Hay que quitarla
                    self.imv1.removeItem(redROI)
                event.accept()                                                 #Después hay que cerrar la tabla, si no se guardaron los datos hay que dejar la tabla como estaba

        elif result == QtGui.QMessageBox.Discard:                              #Si se presionó el botón de descartar
            ContourTableWinClass.cancel = 0                                    #Indicamos que SÍ se desea cerrar la ventana de la tabla, sirve cuando la ventana principal se va a cerrar
            self.imv1.removeItem(self.scatterItem)                             #Quitar el video de las ventanas y las etiquetas
            self.imv1.clear()        
            MainWinClass.stack = 0                                             #Indicamos que se quitó el stack de la ventana
            
            
            if flag == 1:                                                      #Si sí hay una ROI roja encima de la imagen
                redROI = MainWinClass.ROI                                      #Hay que quitarla
                self.imv1.removeItem(redROI)
            event.accept()                                                     #Después hay que cerrar la tabla
        
        elif result == QtGui.QMessageBox.Cancel:                               #Si se presionó el botón de cancelar
            flag = MainWinClass.close                                          #La bandera se activa si la ventana principal se va a cerrar            
            if flag:                                                           #Si la ventana principal se desea cerrar, pero se presionó cancelar en la tabla, hay que evitar el cierre de todo
                ContourTableWinClass.cancel = 1                                #Indicamos que no se desea cerrar la ventana de la tabla, ya que se presionó cancelar

                
#                event.accept() 
#            mainWinVis = self.parent.isVisible()        
        


        


        
app = QtGui.QApplication(sys.argv)
MyWindow = MainWinClass(0,None)
MyWindow.show()
app.exec_()




