#-*- coding: utf-8 -*-
"""
Created on Mon Jan 14 13:49:57 2019

@author: akire
CAMBIÉ LA PARTE DE ELIMINAR REGIONES CON UN BOTÓN EN CADA RENGLÓN A UN SOLO BOTÓN AL LADO DE AÑADIR ROI
Y AUNQUE PARECE QUE FUNCIONA, AL AGREGAR UN RENGLÓN A LA TABLA SE MUEVEN LOS ITEMS DE LA 
SEGUNDA COLUMNA HACIA ABAJO, AL PARECER SOLO ES AL AGREGAR EL PRIMER RENGLÓN, DESPUÉS PARECE QUE YA NO!!!
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



MainWin= uic.loadUiType("GUI5_MainWin.ui")[0]                                  #Ventana que tendrá el stack y el menú
ContourTableWin = uic.loadUiType("GUI5_ContoursTable.ui")[0]



class MainWinClass(QtGui.QMainWindow, MainWin):    
    def __init__(self, ROI, parent=None):
        super().__init__(parent)        
        self.setupUi(self)
        self.findRoiAction.triggered.connect(self.CellDetection)               #El botón se conecta primero a la función que permite abrir un stack
        MainWinClass.statusbar = self.statusbar                                #Para poder cambiar esta variable por fuera de la clase https://stackoverflow.com/questions/44046920/changing-class-attributes-by-reference
        MainWinClass.ROI = ROI


    #Esta función va a realizar la parte de segmentación 
    #(desde la ventana principal)    
    def CellDetection(self):                                                   #Función que realizará la segmentación de células
        self.imv1.clear()                                                      #Limipiar la imagen principal
        
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
        
        #Buscar el alrchivo y guardarlo en una matriz
        lista1  = lista0.replace('/', '\\\\')                                  #Hay que corregir la ruta del archivo, cambiando los '/' con '\\' (antes no se tenía que hacer esto GUI1 monito)  
        tif = tifffile.TiffFile(str(lista1))                                   #El stack se guarda en tif
        self.data = tif.asarray()                                              #El stack de imágenes se pasa a un arreglo
        forma = self.data.shape
        
        #Si el archivo NO tiene más de 300 frames O si está abriendo una imagen
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
                
        #Obtención de la viewbox y el imageitem de imv1
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
        #crea uno nuevo
        #self.viewbox.setMenuEnabled(False)                                    #con esto se deshabilita el menú con el clic derecho de la imv1 https://stackoverflow.com/questions/44402399/how-to-disable-the-default-context-menu-of-pyqtgraph
        self.viewbox.menu = None                                               #Para quitar todo lo que no es Export... en el menú
        self.imv1.scene.contextMenu = None                                     #Para quitar el Export... en el menú   https://groups.google.com/forum/#!topic/pyqtgraph/h-dyr0l6yZU
        self.viewbox.menu = self.NewMenu()                                     #Para crear un nuevo menú https://groups.google.com/forum/#!topic/pyqtgraph/3jWiatJPilc
                
        #Obtiene la serie de tiempo del stack completo
        self.SerieTiempo = np.zeros(self.NoFrames)
        for frame in range(self.NoFrames):  
            imagen_i = self.data[frame,:,:] 
            self.SerieTiempo[frame] = np.mean(imagen_i) 
                                        
        #Ventana que pide datos del video y deben proporcionarse forzosamente 
        #para el análisis posterior
        PlotDialogWin = adv.PlotDialogWinClass(self.NoFrames)                  #"Llamamos" a la clase de la primera ventana
        ItemGrafica = pg.PlotCurveItem(pen=(0,255,0))                          #Se hace un ítem de una gráfica  
        ItemGrafica.setData(self.SerieTiempo)                                  #Se agregan los datos de la serie de tiempo al ítem} 
        PlotDialogWin.TimeSeriesPlot.addItem(ItemGrafica)                      #Se agrega el ítem a la primera ventana        
        PlotDialogWin.show()                                                   #Se muestra la ventana para pedir datos al usuario
                
        #Se obtiene la información que introdujo el usuario en la ventana 
        #de diálogo anterior 
        #https://stackoverflow.com/questions/52560496/getting-a-second-window-
        #pass-a-variable-to-the-main-ui-and-close
        if PlotDialogWin.exec_() == QtWidgets.QDialog.Accepted:                #Si ya se le dio clic en aceptar a la ventana de dialogo
            inFrame = PlotDialogWin.frame1                                     #Frame inicial para el análisis
            finFrame = PlotDialogWin.frame2                                    #Frame final para el análisis
            self.CellDiam = PlotDialogWin.CellSize                             #Diámetro de la célula
            cellType = PlotDialogWin.indexOfChecked                            #Neuronas o hipófisis
            
        SerieTiempoParc = self.SerieTiempo[inFrame:finFrame]                   #Serie de tiempo parcial depende de lo que introduzca el usuario

        #Analisis por tipo celular
        #0 para hipófisis, 1 para neuronas
        if cellType == 0:                                                      
            #Se encuentran las células, se obtiene un diccionario con los 
            #contornos y una imagen binaria, los superponemos al video
            self.ROI_dict = PituitarySegm(inFrame, finFrame, self.CellDiam, \
                                          SerieTiempoParc, self.data)          #Llama a la func que hace la segmentación 

            #Crear el diccionario de series de tiempo (se va a usar para 
            #graficar en la ventana de tabla)
            self.TimeSerDict = ContourTimeSeries(self.data, self.ROI_dict, \
                                        self.NoFrames, self.alto, self.ancho, \
                                        self.CellDiam)                         #Función que crea el diccionario de series de tiempo 
            
            #Se crea la tabla de contornos en la imagen      
            bandera_ROI = 0                                                    #Bandera para indicar que no hay una ROI circular en la imagen             
            self.TableWin = ContourTableWinClass(self.ROI_dict,\
                                self.TimeSerDict,self.imv1, self.alto,\
                                self.ancho, self.CellDiam, bandera_ROI, \
                                self.data, self.NoFrames, row=False)  
                                                                                                              
            self.TableWin.show()
            self.TableWin.ContourCheckBox.setChecked(True)                     #Marcando la checkbox de los contornos
            
        #0 para hipófisis, 1 para neuronas    
        elif cellType == 1:                                                    #Si el botón que eligió es 1 (neuronas)
            self.segmNeuron(inFrame, finFrame)

            
    #Función que va a hacer la segmentación de neuronas, hay que pasarla a 
    #un archivo aparte, como la de hipófisis        
    def segmNeuron(self, a, b):
        print('Aquí va el análisis de neuronas')

        
    #Menú que sale cada vez que se hace clic derecho en la imagen 
    #(para la nueva ROI)    
    def NewMenu(self):
        self.viewbox.menu = QMenu()
        
        #Para agregar una nueva ROI
        self.NuevaROIimg = QtGui.QAction("New ROI", self.viewbox.menu)
        self.NuevaROIimg.triggered.connect(self.NewROIimg)
        self.viewbox.menu.addAction(self.NuevaROIimg)

        #Para quitar la ROI superpuesta
        self.QuitarROIimg = QtGui.QAction("Remove ROI", self.viewbox.menu)
        self.QuitarROIimg.triggered.connect(self.RemoveROIimg)
        self.viewbox.menu.addAction(self.QuitarROIimg)

        #zoom = QtGui.QAction(u'Zoomer', self.viewbox.menu)                    #Para mostrar cómo se agrega un separador en el menú
        #self.viewbox.menu.addSeparator()
        #self.viewbox.menu.addAction(zoom)
        return self.viewbox.menu   


    #Función que agrega un círculo en el video que va a servir para añadir 
    #una ROI a la tabla
    def NewROIimg(self):
        #Primero hay que revisar la bandera, si hay una ROI circular encima 
        #del video hay que quitarla primero
        bandera = ContourTableWinClass.bandera
        if bandera == 1:
            self.imv1.removeItem(self.ROI)                                     #Si sí hay una ROI circular en la imagen, quítala            
            
        #Se obtiene la posición del mouse a partir del label en la imagen, 
        #ahí se pondrá el círculo
        words = str(self.labelPRUEBA.text()) 
        lista=re.findall(r'\d+', words)                                        #https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python
        x=lista[3]                                                             #En teoría siempre van a estar en estas posciones de la lista los enteros de las posiciones del label
        y=lista[6]
        print([x,y])
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

        ContourTableWinClass.bandera = 1                                       #Bandera dentro de la clase tabla que indica que sí hay una ROI circular en la imagen
        MainWinClass.ROI = self.ROI


    #Función que va a quitar el círculo anterior si ya hay uno mostrado 
    #(con el menú que sale al hacer clic derecho en la imagen)
    def RemoveROIimg(self):
        bandera_ROI = ContourTableWinClass.bandera                             #Hay que obtener el valor de la bandera, par asaber si hay o no un círculo en la imagen
        if bandera_ROI == 1:
            self.imv1.removeItem(self.ROI)                                     #Si sí hay una ROI circular en la imagen, quítala
            ContourTableWinClass.bandera = 0                                   #Y pon la bandera en cero    
            MainWinClass.ROI = 0

        else:
            self.statusbar.showMessage("There is no ROI in the image",1000)    #Si no hay una ROI, avisa que no hay nada que quitar desde la barra de status
                                                                          


#Se crea la tabla de contornos presentes en la imagen 
class ContourTableWinClass(QtWidgets.QDialog, ContourTableWin):                #Ventana con la tabla de contornos
    def __init__(self, ContoursDict, TimeSerDict, imv1, alto, ancho, CellRad,\
                 bandera, data, NoFrames, row, parent = MainWinClass):
                                                        
        super(ContourTableWinClass, self).__init__()
        self.setupUi(self)
        
        #Esta bandera indica si hay una ROI circular que se va a añadir a 
        #la tabla
        ContourTableWinClass.bandera = bandera                                 #Para poder cambiar esta variable por fuera de la clase https://stackoverflow.com/questions/44046920/changing-class-attributes-by-reference
        ContourTableWinClass.row = row                                         #Para saber qué renglón es el que se ha seleccionado para graficar 
                
        #Se hacen "self" diferentes variables aceptadas en la clase
        self.ContoursDict = ContoursDict
        self.TimeSerDict = TimeSerDict  
        self.imv1 = imv1
        self.CellRad = CellRad
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
            scatterItem = pg.ScatterPlotItem(pxMode=False, size=self.CellRad, \
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
            key = self.ContoursTable.item(row,0).text()                            #Texto que aparece en la primer columna de la tabla   
            key = int(key)                                                         #Hay que cambiarlo a integer porque era string, este es el key del diccionario                                                                                         

            #Se quita el renglón de la tabla
            self.ContoursTable.removeRow(row)                                      #Se quita el renglón de la tabla
    
            #Hay que quitar el contorno y la serie de tiempo de los 
            #diccionarios correspondientes
            del self.ContoursDict[key]                                             #Hay que quitar la ROI del diccionario de ROIs
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
        
        flag = ContourTableWinClass.bandera                                    #Para saber qué valor tiene la variable bandera 
        if flag ==0:                                                           #0= No hay ROI en la imagen
            MainWinClass.statusbar.showMessage("There is no ROI in the image",\
                                       1000)                                   #Para indicar en la barra de status que no hay una ROI que se pueda agregar a la tabla

        elif flag ==1:                                                         #1= Hay una ROI en la imagen
            
            pos=MainWinClass.ROI.pos()                                         #Es la posición de la esquina superior izquierda del rectángulo que contiene al círculo (pyqtgraph)                     
            diametro = int((self.CellRad-1)/2)                                 #El -1 es por ser un número impar
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

            
    def Save(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', \
                                                     os.getenv('HOME'))        #Obtiene la ruta del SO
        lista0 = str(filename[0])                                              #Ahora filename regresa el nombre como una tupla, hay que tomar su primera parte 
        lista1  = lista0.replace('/', '\\\\')                                  #Hay que corregir la ruta del archivo, cambiando los '/' con '\\' (antes no se tenía que hacer esto GUI1 monito)        
        #lista1 tiene la ruta incompleta de dónde guardar el archivo
        #https://pythonprogramming.net/file-saving-pyqt-tutorial/         
        
        #Rutas completas de donde se guardarán los archivos
        namePos = str(lista1) + str('_ROI.csv')
        nameData = str(lista1) + str('_Data.csv')
        
        #Para guardar las series de tiempo
        series = np.array(list(self.TimeSerDict.values()))                     #Lista de listas de las series de tiempo, cada lista es una columna!!!
        series = series.transpose()                                            #Array de series de tiempo en columnas
        llaves = list(self.TimeSerDict.keys())                                 #Lista de las llaves de cada serie 
        frames = np.array(list(range(len(series[:,0]))))                       #Lista con el número de frames
        frames = frames.transpose()
        frames = frames.reshape(len(series[:,0]),1)                            #Hay que cambiar la forma del arreglo para el siguiente paso
        series2 = np.hstack((frames,series))                                   #Esto es para poner al inicio de cada columna el número de ROI

        #Generar el encabezado para el archivo de datos
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
            
        
                   
app = QtGui.QApplication(sys.argv)
MyWindow = MainWinClass(None)
MyWindow.show()
app.exec_()




