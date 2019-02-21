# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 16:44:33 2018
Quinta interfaz con QtDesigner
@author: Araceli
"""


#python -m PyQt5.uic.pyuic -o ARCHIVO_OUY.py archivo_IN.ui    --------->Para convertir de ui a py
#Hay que revisar los radio button
#no está poniendo las cosas en la tabla por lo de la main window
#Parece que solo falta lo del botón de reset
#Problema para hacer el ejecutable: ImportError: No module named 'pywt._extensions._cwt'
#https://stackoverflow.com/questions/41998403/pyinstaller-importerror-on-pywt-ctw-module
#Para poner el archivo externo py (que contiene a la GUI) dentro de este código:
#https://es.stackoverflow.com/questions/120771/usar-dise%C3%B1o-generado-en-qt-designer-y-convertido-a-m%C3%B3dulo-python-py
#Después de hacer el ejecutable (qutando ya el archivo ui) apareció este error:
#https://stackoverflow.com/questions/47468705/pyinstaller-could-not-find-or-load-the-qt-platform-plugin-windows
#Donde dicen que actualizando pyt resolvía el problema, pero eso hizo que tronara anaconda!!!!
#En la laptop tuve este problema: ImportError: No module named 'scipy._lib.messagestream'  :
#https://stackoverflow.com/questions/47055712/error-when-executing-compiled-file-no-module-named-scipy-lib-messagestream
#Después de corregir lo de pywt y de scipy._lib.messagestream, salió este error: 
#Traceback (most recent call last):
#  File "GUI4_Principal.py", line 47, in <module>
#ImportError: No module named 'GUI4_MainWin'
#[452] Failed to execute script GUI4_Principal
#https://stackoverflow.com/questions/20495620/qt-5-1-1-application-failed-to-start-because-platform-plugin-windows-is-missi?rq=1
#

import sys
import os
#import random
#import functools
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import tifffile  
import cv2
#from skimage import exposure
#from skimage.feature import peak_local_max
#import copy
#from itertools import groupby
import math
#from skimage import morphology
#from scipy import ndimage
#from skimage.morphology import watershed
from scipy.optimize import curve_fit
import scipy.stats
from collections import Counter
from pywt import wavedec, threshold, waverec
from statsmodels.robust import mad
import imageio
#from PyQt5 import QtCore, QtGui, uic
from GUI4_MainWin import Ui_MainWindow                                         #Para la interfaz
import warnings                                                                #Para omitir las runtimewarning que salen del ajuste exponencial (y creo que todos en general!!)
warnings.filterwarnings("ignore")

# Cargar nuestro archivo .ui, OJO: para el exe hay que poner la ruta completa!!! (el ejecutable no sirve para otras computadoras, porque buscan el archivo ui en la ruta especificada!!!!)
#form_class = uic.loadUiType("C:\\Users\\Imagenologia\\Documents\\EAGV\\SegmentacionAnalisisGUI\\BitacoraSeguimiento\\Codigo\\GUI4-QtDesigner\\GUI4_MainWin.ui")[0]
#form_class = uic.loadUiType("GUI4_MainWin.ui")[0]

#class MyWindowClass(QtGui.QMainWindow, form_class):
 
class MyWindowClass(QtGui.QMainWindow, Ui_MainWindow ):
    
    def __init__(self, parent=None):
            
#        QtGui.QMainWindow.__init__(self, parent)
        super(MyWindowClass, self).__init__()
        
#        self.ui = Ui_MainWindow() 
#        self.ui.setupUi(self)
        
        self.setupUi(self)
          
        self.openAction.triggered.connect(self.openFile)
          
        self.findRoiAction.triggered.connect(self.FindCells)
          
        self.button1.clicked.connect(self.Estado_Boton1)                     # Llama a la función NuevaROI al presionar el botón Nueva ROI     
          
        self.button2.clicked.connect(self.Estado_Boton2)                             # Llama a la función NuevaROI al presionar el botón Nueva ROI                
        
        self.Tabla.itemClicked.connect(self.CheckBox)                          #Llama a la función FuncCheckBox al hacer clic en una celda de la tabla
        
        self.ResetButton.clicked.connect(self.Reset)  
          
        self.saveTimeSerAction.triggered.connect(self.GuardarSeriesTiemp)
        
        self.saveImgAction.triggered.connect(self.GuardarImgBinaria)
        
        self.LoadImageAction.triggered.connect(self.openBinary)
        
        self.saveImgesAction.triggered.connect(self.GuardarImagenesBin)
        
        
            
    def openFile(self):                                                        #                                         <------Abre un archivo
        self.imv1.clear()                                                      # Si se abre otro archivo se limpia la gráfica
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
        
        
    def FindCells(self):  
        #Se obtiene la serie de tiempo "general" de todo el stack en la variable Promedios (por cada frame)
        Promedios = np.zeros(self.NoFrames);
        for i in range(self.NoFrames):
            mean_i = np.mean(self.data[i,:,:]);
            Promedios[i]=mean_i                                                
        
        
        #Se hará un ajuste exponencial a la serie de tiempo "general"    
        def func(x, a, b, c):                                                  
            return a * np.exp(-b * x)+c
        
        x=np.arange(self.NoFrames);                                                         #Valores en el eje x
        popt, pcov = curve_fit(func, x, Promedios, method='trf');                      #Ajuste!:  https://stackoverflow.com/questions/3433486/how-to-do-exponential-and-logarithmic-curve-fitting-in-python-i-found-only-poly                        
        y_ajustada=func(x, *popt);     

        b=popt[1];                                                                     #constante k del exponente                        
        Frames_corregidos = [];                                                        #Lista que contendrá los frames después de la corrección por debleach
        for i in range(self.NoFrames):                                         
            frame_nuevo = self.data[i,:,:]/np.exp(-b*(i))                                   #Para que sea más parecido a lo que sale en Fiji, hay que redondear con np.round(self.data[i,:,:]/np.exp(-b*i))
            Frames_corregidos.append(frame_nuevo);
            
        Frames_corregidos=np.asarray(Frames_corregidos);                               #Estos son los frames sobre los que se va a trabajar, es decir los corregidos
        
        
        #Hacer la clasificación por ventanas y no por pixeles
        widthwin = self.Text1.value();       #Ancho y alto de la ventana
        heightwin = self.Text1.value();
        
        ww = np.remainder(self.ancho, widthwin);
        wh = np.remainder(self.alto, heightwin);

        #Tamaño real de la imagen sobre el que se va a hacer el análisis
        self.ancho1 = self.ancho - ww;
        self.alto1 = self.alto - wh;
        
        def Entropia(Serie):
            diccionario = Counter(np.round(Serie, decimals=1));
            prob = np.asarray(list(diccionario.values()));
            prob = prob/self.NoFrames;
            suma = 0;
            NoOperaciones = len(prob);
            for k in range(NoOperaciones):
                suma = suma + (prob[k]*math.log(prob[k]));
            diccionario.clear();    
            return[abs(suma)]
    
    
        def FiltroWave(Serie):
            coeff = wavedec(Serie, "db3", mode="per")
            sigma = mad(coeff[-1])
            uthresh = sigma*np.sqrt(2*np.log(len(Serie)))                          #Universal Threshold 
            coeff[1:] = (threshold( i, value=uthresh, mode="soft" ) for i in coeff[1:] )
            return(waverec( coeff, "db3", mode="per" ))
            
            
        
#        Skew = np.zeros([alto1, ancho1]); 
#        Entrop = np.zeros([alto1, ancho1]); 
#        Area = np.zeros([alto1, ancho1]); 
        binaria = np.zeros((self.alto1, self.ancho1));


        #for x in range(0, ancho1, widthwin):   
        #    for y in range(0, alto1, heightwin):
                        
        for x in range(0, self.ancho1):   
            for y in range(0, self.alto1):
                serie = np.zeros(self.NoFrames);
                for N in range(self.NoFrames):
                    serie[N] = np.average(Frames_corregidos[N, y:y+heightwin, x:x+widthwin]);   #Para recorrer el stack por ventana, quitarlo si se quiere recorrer por pixel
                    
                    #serie[N] = Frames_corregidos[N,y,x]          #Para recorrer el stack por pixel
                
                #Sesgo
                sesgo = scipy.stats.skew(serie);
#                Skew[y:y+heightwin, x:x+widthwin] = sesgo;
                
                #Entropía
                entrop = Entropia(serie);
#                Entrop[y:y+heightwin, x:x+widthwin] = entrop;
                
                #Normalización de la serie
                serie_min = np.amin(serie);
                serie_max = np.amax(serie);
                serie = (serie - serie_min)/(serie_max-serie_min);
                
                #Filtro wavelet
                serie = FiltroWave(serie)
                
                #Área
                area = scipy.integrate.simps(serie, dx=1);
#                Area[y:y+heightwin, x:x+widthwin] = area;
                
                #Clasificación
                resultado = 0.27019 - 0.0385489*area + 1.11891*sesgo + 0.847669*entrop[0];
                if resultado >= 0:
                    binaria[y:y+heightwin, x:x+widthwin] = 1;     #Para recorrer el stack por ventana, quitarlo si se quiere hacer por pixel
                    #binaria[y,x] = 1                             #Para recorrer el stack por pixel

        # Detección de contornos de la imagen binaria
        copia_bin = binaria.astype(dtype='uint8')*255;
#        (imagen,contours,hierarchy)=cv2.findContours(copia_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);

        # Detección de contornos de la imagen binaria
        (imagen1,self.contours,hierarchy)=cv2.findContours(copia_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);

        #Máscara tendrá el arreglo de la imagen que se va a superponer al video, será en formato RGBA
        self.mascara = np.zeros((self.alto, self.ancho, 4));
        mascara1 = np.zeros((self.alto, self.ancho, 3));
        cv2.drawContours(mascara1,self.contours,-1,(255,255,0),1);     #-1 en lugar del 0
        self.mascara[:,:,0:3] = mascara1;
        self.mascara[:,:,3][mascara1[:,:,0]>200]=255;                               #Solo se pondrá en no transparente la parte de las ROIs
        
        #Se suporpone la imagen de las ROIs
        mascara2 = np.transpose(self.mascara,(1,0,2))                          #El (1,0,2) indica cómo se va a trasponer la matriz 3D (ejes)
        self.encima = pg.ImageItem(mascara2)
        self.imv1.addItem(self.encima)
        
        #Se generará un diccionario con los contornos
        keys = np.arange(len(self.contours));                                  #Las llaves serán el número consecutivo de los contornos
#        values = [item[0,0] for item in self.contours];
        self.ROI_dict = dict(zip(keys, self.contours));                        #https://stackoverflow.com/questions/209840/convert-two-lists-into-a-dictionary-in-python        

        self.button1.setChecked(True)                                          #Ponemos en true el botón de "Show ROIs"

#        print(len(self.ROI_dict))

        self.TablaInicial()        

        self.Fig_dict = {}                                                     #Diccionario que tendrá las ROIs remarcadas con los checkbox
        
#        print(self.Text1.value())


    
    def TablaInicial(self):                                                    #Func que genera la tabla con las primeras ROIs            
        self.Tabla.setRowCount(len(self.ROI_dict))                             #Número de renglones que tendrá la tabla dependiendo del número de ROIs
        self.Tabla.setColumnCount(3)                                           #Número de columnas que tendrá la tabla    

        renglon=0     
        self.botones_series = QtGui.QButtonGroup( self.centralwidget)                          #Grupo de radio buttons
        self.botones_remove = QtGui.QButtonGroup( self.centralwidget)
        
        for key in self.ROI_dict.keys():                                       #Para saber las posiciones de cada ROI encontrada   
            contorno = self.ROI_dict[key];
            pos = contorno[0,0]

            item1 = QtGui.QRadioButton(str(pos))                               #Ponemos un radiobutton en cada renglón
            item1.setChecked(False)            
            item1.clicked.connect(self.CheckBox)                               #Si el radio button se presiona, mándalo a la función CheckBox
            self.botones_series.addButton(item1)                                 #El radio button es parte del grupo radio buttons
            self.Tabla.setCellWidget(renglon, 1, item1)                        #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview
                        
            item2 = QtGui.QTableWidgetItem(str(key))                           #El string de numeración de la tabla
            self.Tabla.setItem(renglon, 0, item2)                              #El string se pone en el i-ésimo renglón y columna 0
            
            item3 = QtGui.QRadioButton()                           #Ponemos un radiobutton en cada renglón
            item3.setChecked(False)            
            item3.clicked.connect(self.QuitarROI)                              #Si el radio button se presiona, mándalo a la función CheckBox
            self.botones_remove.addButton(item3)                               #El radio button es parte del grupo radio buttons
            self.Tabla.setCellWidget(renglon, 2, item3)                        #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview
                         
            renglon = renglon + 1                                              #Para pasar al siguiente renglón
                            
        self.Tabla.setHorizontalHeaderLabels(str("Número;Posición;Quitar ROI").split(";"))      #Etiqueta de la columna 
        self.Tabla.verticalHeader().hide()                                     #Quitar letrero vertical   https://stackoverflow.com/questions/14910136/how-can-i-enable-disable-qtablewidgets-horizontal-vertical-header        
        
            
    def TablaNueva(self, Checked_Key):                                         #Func que genera la tabla nueva pero con un botón marcado       
        self.Tabla.setRowCount(len(self.ROI_dict))                             #Número de renglones que tendrá la tabla dependiendo del número de ROIs
        self.Tabla.setColumnCount(3)                                           #Número de columnas que tendrá la tabla    

        renglon=0     
        self.botones_series = QtGui.QButtonGroup( self.centralwidget)                          #Grupo de radio buttons
        self.botones_remove = QtGui.QButtonGroup( self.centralwidget)
        
        for key in self.ROI_dict.keys():                                       #Para saber las posiciones de cada ROI encontrada   
            contorno = self.ROI_dict[key];
            pos = contorno[0,0]

            item1 = QtGui.QRadioButton(str(pos))                               #Ponemos un radiobutton en cada renglón
            if key == Checked_Key:
                item1.setChecked(True)
            else:
                item1.setChecked(False)            
                
            item1.clicked.connect(self.CheckBox)                               #Si el radio button se presiona, mándalo a la función CheckBox
            self.botones_series.addButton(item1)                                 #El radio button es parte del grupo radio buttons
            self.Tabla.setCellWidget(renglon, 1, item1)                        #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview
                        
            item2 = QtGui.QTableWidgetItem(str(key))                           #El string de numeración de la tabla
            self.Tabla.setItem(renglon, 0, item2)                              #El string se pone en el i-ésimo renglón y columna 0
            
            item3 = QtGui.QRadioButton()                           #Ponemos un radiobutton en cada renglón
            item3.setChecked(False)            
            item3.clicked.connect(self.QuitarROI)                              #Si el radio button se presiona, mándalo a la función CheckBox
            self.botones_remove.addButton(item3)                               #El radio button es parte del grupo radio buttons
            self.Tabla.setCellWidget(renglon, 2, item3)                        #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview
                         
            renglon = renglon + 1                                              #Para pasar al siguiente renglón
                            
        self.Tabla.setHorizontalHeaderLabels(str("Número;Posición;Quitar ROI").split(";"))      #Etiqueta de la columna 
        self.Tabla.verticalHeader().hide()                                     #Quitar letrero vertical   https://stackoverflow.com/questions/14910136/how-can-i-enable-disable-qtablewidgets-horizontal-vertical-header        
        
            
    def Estado_Boton1(self):                                                   #Botón de Show ROI's
        if self.button1.isChecked() == True:                                   #Si el botón 1 está marcado, hay que poner las ROIs encima
            if self.button2.isChecked() == True:                               #Si también el botón 2 está marcado, hay que poner las etiquetas también
                
                self.imv1.removeItem(self.encima)                              #Primero quitamos todo lo que está encima del video                
                self.Agregar_ROIs()                                            #Ponemos las ROIs abajo
                self.Agregar_Etiquetas()                                       #Encima ponemos las etiquetas

            else:                                                              #Si el botón 2 no está marcado, solo hay que poner las ROIs
                self.imv1.removeItem(self.encima)                              #Primero quitamos todo lo que está encima del video  
                self.Agregar_ROIs()                                            #Ponemos las ROIs 
        
        elif self.button1.isChecked() == False:                                #Si el botón 1 no está marcado, hay que quitar las ROIs
            if self.button2.isChecked() == True:                               #Si el botón 2 está marcado, hay que poner las etiquetas

                self.imv1.removeItem(self.encima)                              #Primero quitamos todo lo que está encima del video   
                self.Agregar_Solo_Etiquetas()                                  #Ponemos solo las etiquetas (sobre una imagen transparente)

            else:                                                              #Si ninguno de los dos botones está marcado
                self.imv1.removeItem(self.encima)                              #Quitamos todo lo que está encima del video
                
    
    def Estado_Boton2(self):                                                   #Botón de Show Labels
        if self.button2.isChecked() == True:                                   #Si el botón 2 está marcado, hay que poner las etiquetas encima
            if self.button1.isChecked() == True:                               #Si también el botón 1 está marcado, hay que poner las ROIs abajo también
                
                self.imv1.removeItem(self.encima)                              #Primero quitamos todo lo que está encima del video                
                self.Agregar_ROIs()                                            #Ponemos las ROIs abajo
                self.Agregar_Etiquetas()                                       #Encima ponemos las etiquetas

            else:                                                              #Si el botón 1 no está marcado, hay que quitar las ROIs
                self.imv1.removeItem(self.encima)                              #Primero quitamos todo lo que está encima del video   
                self.Agregar_Solo_Etiquetas()                                  #Ponemos solo las etiquetas (sobre una imagen transparente)

        
        elif self.button2.isChecked() == False:                                #Si el botón 2 no está marcado, hay que quitar las etiquetas 
            if self.button1.isChecked() == True:                               #Si el botón 1 está marcado, hay que poner solo las ROIs abajo

                self.imv1.removeItem(self.encima)                              #Primero quitamos todo lo que está encima del video   
                self.Agregar_ROIs()                                            #Ponemos las ROIs

            else:                                                              #Si el botón 1 tampoco está marcado, hay que quitar todo
                self.imv1.removeItem(self.encima)                              #Quitamos todo lo que está encima del video
         

    def Agregar_Etiquetas(self):        
        for key in self.ROI_dict.keys():                                   #Agregamos las etiquetas
            text = pg.TextItem(anchor=(0.5,0.5), fill=(0, 255, 255, 100)) 
            text.setText(str(key), color=(255, 255, 255))                    #Texto que se desplegará al lado de la ROI
            text.setParentItem(self.encima) 
            contorno = self.ROI_dict[key];
            a,b = contorno[0,0];
            text.setPos(a,b)           
        
            
    def Agregar_ROIs(self):
        mascara2 = np.transpose(self.mascara,(1,0,2));                     #Agregamos las ROIs
        self.encima = pg.ImageItem(mascara2);
        self.imv1.addItem(self.encima);
        
    
    def Agregar_Solo_Etiquetas(self):
        mascara2 = np.zeros((self.alto, self.ancho, 4));               #Imagen transparente
        mascara2 = np.transpose(mascara2,(1,0,2));                     
        self.encima = pg.ImageItem(mascara2);                          
        self.imv1.addItem(self.encima);                                #Se pone la imagen transparente encima del video        
        
        for key in self.ROI_dict.keys():                                   #Agregamos las etiquetas
            text = pg.TextItem(anchor=(0.5,0.5), fill=(0, 255, 255, 100)) 
            text.setText(str(key), color=(255, 255, 255))                    #Texto que se desplegará al lado de la ROI
            text.setParentItem(self.encima) 
            contorno = self.ROI_dict[key];
            a,b = contorno[0,0];
            text.setPos(a,b)         
#61

    def CheckBox(self, item):
        self.GraficaSerieTiempo.clear() 
        boton = abs(self.botones_series.checkedId())                           #ID del botón seleccionado algo falla con esto
        ID = boton -2                                                          #Hay que corregir el ID, porque empieza en -2 por alguna razón
        key = self.Tabla.item(ID,0).text()                                     #Key del diccionario (texto que aparece en la primer columna de la tabla)
        binaria = np.zeros((self.alto, self.ancho));                       #Máscara binaria para obtener la serie de tiempo
        lista_keys = list(self.ROI_dict.keys())       
                         #Hay que revisar la lista de las llaves
        pos_key = lista_keys.index(int(key))                                   #Para saber la posición específica del contorno que queremos observar (porque si se quitan ROIs, la posición se pierde!!!)
        cv2.drawContours(binaria,self.contours,int(pos_key),(255,255,255),-1);      #Dibujamos el contorno relleno generando así la máscara binaria, int porque antes key es str
        area = cv2.countNonZero(binaria)                                   #Encontramos el número de pixeles dentro del contorno (área)
        coordenadas = np.argwhere(binaria == 255)                              #Buscamos las coordenadas de los pixeles blancos en la imagen binaria
        SerieTiempo = np.zeros(self.NoFrames)

        for frame in range(self.NoFrames):                                     #Recorremos cada frame
            imagen_i = self.data[frame,:,:] 
            suma = 0
            for coordenada in coordenadas:                                     #Recorremos cada coordenada
                suma = suma + imagen_i[coordenada[0],coordenada[1]]
            promedio = suma/area                                               #Sacamos el promedio
            SerieTiempo[frame] = promedio                                      #El promedio se guarda en la serie

        ItemGrafica = pg.PlotCurveItem(pen=(0,255,0))                          #Se hace un ítem de una gráfica  
        ItemGrafica.setData(SerieTiempo)                                       #Se agregan los datos al ítem
        self.GraficaSerieTiempo.addItem(ItemGrafica)                           #Se agrega el ítem a la GUI  
        
        
    def QuitarROI(self):
        boton_remove = abs(self.botones_remove.checkedId())                    #ID del botón seleccionado
#        print(boton_remove)
        ID_boton_remove = boton_remove -2                                      #Hay que corregir el ID, porque empieza en -2 por alguna razón
        key_remove = int(self.Tabla.item(ID_boton_remove,0).text())            #Key del diccionario (texto que aparece en la primer columna de la tabla)
#        print(str(key_remove))
        

        boton_serie = abs(self.botones_series.checkedId())                     #boton_serie será -1 si no hay ningún botón seleccionado!!!
        ID_boton_serie = boton_serie -2 
        key_serie = int(self.Tabla.item(ID_boton_serie,0).text())              #Hay que pasarlo de str a integer
#        print(key_serie)
        

        del self.ROI_dict[key_remove]                                          #Hay que quitar la ROI del diccionario de ROIs
              
        self.contours = list(self.ROI_dict.values())                           #Los contornos "generales" se obtienen a partir del diccionario
        
     
        if boton_serie > 1:                                                    #Si sí hay una serie de tiempo graficada                  
            if key_serie == key_remove:                                        #Si la serie de tiempo que se quiere quitar es la correspondiente a la ROI que se quiere quitar
                self.GraficaSerieTiempo.clear()                                #Hay que quitar la serie de tiempo de la gráfica        
                self.Tabla.clear()                                             #Quitamos la tabla primero 
                self.TablaInicial()                                            #Podemos poner la tabla sin la ROI quitada y sin marcar ningún botón porque ya no hay gráfica
            else:                                                              #Como la serie de tiempo que está en la gráfica no es la misma que la de la ROI que se quitó
                self.Tabla.clear()                                             #Quitamos la tabla primero 
                self.TablaNueva(key_serie)                                     #Hay que rehacer la tabla sin esa ROI pero con un botón marcado
                item = self.Tabla.item(key_serie, 0)                           #Se desplaza la tabla hasta donde está el último botón marcado de la serie de tiempo 
                self.Tabla.scrollToItem(item, QtGui.QAbstractItemView.PositionAtTop) #https://stackoverflow.com/questions/24211182/how-to-set-a-qtablewidget-to-consistently-scroll-to-bottom-during-live-data-inpu
        #        self.Tabla.selectRow(Checked_Key)

        #Creamos una nueva self.mascara que tendrá las ROIs con un canal alfa para que sea transparente 
        self.mascara = np.zeros((self.alto, self.ancho, 4));
        mascara1 = np.zeros((self.alto, self.ancho, 3));
        cv2.drawContours(mascara1,self.contours,-1,(255,255,0),1);             #-1 en lugar del 0
        self.mascara[:,:,0:3] = mascara1;
        self.mascara[:,:,3][mascara1[:,:,0]>200]=255;                          #Solo se pondrá en no transparente la parte de las ROIs
        
        self.Estado_Boton1()                                                   #Vamos a poner las ROIs (o no), dependiendo de qué botones están presionados
                                                                               #Tomando en cuenta la nueva máscara creada
                                                                               
                                                                                   
    def GenerarSeries(self):
#        print('Generar Series')
        NoContornos = len(self.contours)                 
        self.Matriz_Series = np.zeros((self.NoFrames, NoContornos))            #Donde se guardarán las series
        self.Posiciones = np.zeros((NoContornos,2))                                                  #Donde se guardarán las posiciones de las ROIs, las posiciones son arreglos numpy, por lo que se deben guardar en una lista
        
        for j in range(NoContornos):            
            binaria = np.zeros((self.alto, self.ancho));                       #Máscara binaria para obtener la serie de tiempo
            cv2.drawContours(binaria,self.contours,j,(255,255,255),-1);      #Dibujamos el contorno relleno generando así la máscara binaria, int porque antes key es str
            area = cv2.countNonZero(binaria)                                   #Encontramos el número de pixeles dentro del contorno (área)
            coordenadas = np.argwhere(binaria == 255)                              #Buscamos las coordenadas de los pixeles blancos en la imagen binaria
            SerieTiempo = np.zeros(self.NoFrames)
    
            for frame in range(self.NoFrames):                                     #Recorremos cada frame
                imagen_i = self.data[frame,:,:] 
                suma = 0
                for coordenada in coordenadas:                                     #Recorremos cada coordenada
                    suma = suma + imagen_i[coordenada[0],coordenada[1]]
                promedio = suma/area                                               #Sacamos el promedio
                SerieTiempo[frame] = round(promedio, 2)                                      #El promedio se guarda en la serie

            #Ya se obtuvo la serie de tiempo, ahora hay que calcular el centro de la región (posición)
#            (x,y),radius = cv2.minEnclosingCircle(self.contours[j])            #El centro será la posición que se dará de la célula 
            M = cv2.moments(self.contours[j])                                  #Se calculan los momentos del contorno
            
            if M['m00']==0:
                coordenada = coordenadas[0]
                cx = coordenada[0]
                cy = coordenada[1]
                
            else:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
            
            self.Posiciones[j,0] = cx
            self.Posiciones[j,1] = cy
            
            self.Matriz_Series[:,j] = SerieTiempo      
        
#        print(self.Posiciones)

        return self.Matriz_Series, self.Posiciones
#        print(self.Matriz_Series)

    
    def GuardarImgBinaria(self):
        
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', \
                                                     os.getenv('HOME'))        #Obtiene la ruta del SO
        lista0 = str(filename[0])                                              #Ahora filename regresa el nombre como una tupla, hay que tomar su primera parte 
        lista1  = lista0.replace('/', '\\\\')                                  #Hay que corregir la ruta del archivo, cambiando los '/' con '\\' (antes no se tenía que hacer esto GUI1 monito)        
        #lista1 ya tiene la ruta donde guardar el archivo
        #https://pythonprogramming.net/file-saving-pyqt-tutorial/
        name = str(lista1) + str('.png')

#        scipy.misc.imsave(name, self.mascara[:,:,0:3])
        mascara = np.zeros((self.alto, self.ancho, 1))+255;
        cv2.drawContours(mascara,self.contours,-1,(0,0,0),-1);             #https://docs.opencv.org/master/d6/d6e/group__imgproc__draw.html#ga746c0625f1781f1ffc9056259103edbc
        #El último -1 es para rellenar los contornos,se refiere al thickness, el (0,0,0) es para el color, osea debería ser las células en negro!
        mascara = mascara.astype(np.uint8) 
        imageio.imwrite(name, mascara)                                         #https://imageio.github.io/
        self.statusbar.showMessage('Finish', 1000)
        
            
    def GuardarSeriesTiemp(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', \
                                                     os.getenv('HOME'))        #Obtiene la ruta del SO
        lista0 = str(filename[0])                                              #Ahora filename regresa el nombre como una tupla, hay que tomar su primera parte 
        lista1  = lista0.replace('/', '\\\\')                                  #Hay que corregir la ruta del archivo, cambiando los '/' con '\\' (antes no se tenía que hacer esto GUI1 monito)        
        #lista1 ya tiene la ruta donde guardar el archivo
        #https://pythonprogramming.net/file-saving-pyqt-tutorial/
        name1 = str(lista1) + str('.csv')                                      #Para las series
        name2 = str(lista1) + str('_Pos') + str('.csv')
#        print(name)
#        print(self.Matriz_Series) 
        matriz, posiciones = self.GenerarSeries()                              #Se guardan las series de acuerdo a como estén los contornos hasta ahora
#        print(posiciones)

        NoRoi = np.arange(0, len(self.contours))
        NoRoi = NoRoi.reshape((1,len(self.contours)))
        matriz = np.vstack([NoRoi,matriz])
        np.savetxt(name1, matriz, delimiter=",")
        np.savetxt(name2, posiciones, delimiter=",")
        
        self.statusbar.showMessage('Finish', 1000)
#        print('Guardar Series de tiempo')


    def GuardarImagenesBin(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', \
                                                     os.getenv('HOME'))        #Obtiene la ruta del SO
        lista0 = str(filename[0])                                              #Ahora filename regresa el nombre como una tupla, hay que tomar su primera parte 
        lista1  = lista0.replace('/', '\\\\')                                  #Hay que corregir la ruta del archivo, cambiando los '/' con '\\' (antes no se tenía que hacer esto GUI1 monito)        
        #lista1 ya tiene la ruta donde guardar el archivo
        #https://pythonprogramming.net/file-saving-pyqt-tutorial/
        name1 = str(lista1) + str('_UnMax.png')
        name2 = str(lista1) + str('_MultMax.png')

#        scipy.misc.imsave(name, self.mascara[:,:,0:3])

        contours_1max = []
        contours_multmax = []

        for j in range(len(self.clasificacion)):                               #Vamos a revisar cada contorno
            if self.clasificacion[j] == 0:
                contours_1max.append(self.contours[j])
            elif self.clasificacion[j] == 1:
                contours_multmax.append(self.contours[j])
        
        mascara = np.zeros((self.alto, self.ancho, 1))+255;
        cv2.drawContours(mascara,contours_1max,-1,(0,0,0),-1);             #-1 en lugar del 0
        mascara = mascara.astype(np.uint8) 
        imageio.imwrite(name1, mascara)   

        mascara = np.zeros((self.alto, self.ancho, 1))+255;
        cv2.drawContours(mascara,contours_multmax,-1,(0,0,0),-1);             #-1 en lugar del 0
        mascara = mascara.astype(np.uint8) 
        imageio.imwrite(name2, mascara)   
                                      #https://imageio.github.io/
        self.statusbar.showMessage('Finish', 1000)

#Antes de abrir la imagen binaria (que ya tiene todas las ROIs de interés para el experto) hay que abrir el Stack asociado a 
#esa imagen binaria

    def openBinary(self):                                                      #Esta opción hará que se abra la imagen binaria que ya tendrá marcadas todas las células de interés
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File',\
                                                     os.getenv('HOME'))        #Obtiene la ruta del SO
        lista0 = str(filename[0])                                              #Ahora filename regresa el nombre como una tupla, hay que tomar su primera parte 
        lista1  = lista0.replace('/', '\\\\')                                  #Hay que corregir la ruta del archivo, cambiando los '/' con '\\' (antes no se tenía que hacer esto GUI1 monito)                
        binaria = cv2.imread(str(lista1),0)                                 #Para que se abra en blanco y negro (1 solo canal)                                         #El stack de imágenes se pasa a un arreglo
        (self.alto, self.ancho)=binaria.shape 

        tr = pg.QtGui.QTransform()                                             #Para la aplicación de las rotaciones a la imagen               
        tr.rotate(90,QtCore.Qt.ZAxis)                                          #Rotación en el eje Z de 90°
        tr.rotate(180,QtCore.Qt.XAxis)                                         #Rotación en el eje X de 180°
#        self.imv1.setImage(self.data, transform=tr)                            #Mostrar el video en la GUI    
        
        #Encontrar los contornos de la imagen binaria
        # Detección de contornos de la imagen binaria
        copia_bin = binaria.astype(dtype='uint8')*255;
#        (imagen,contours,hierarchy)=cv2.findContours(copia_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);

        # Detección de contornos de la imagen binaria
        (imagen1,self.contours,hierarchy)=cv2.findContours(copia_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);

        #Máscara tendrá el arreglo de la imagen que se va a superponer al video, será en formato RGBA
        self.mascara = np.zeros((self.alto, self.ancho, 4));
        mascara1 = np.zeros((self.alto, self.ancho, 3));
        cv2.drawContours(mascara1,self.contours,-1,(255,255,0),1);     #-1 en lugar del 0
        self.mascara[:,:,0:3] = mascara1;
        self.mascara[:,:,3][mascara1[:,:,0]>200]=255;                               #Solo se pondrá en no transparente la parte de las ROIs
        
        #Se suporpone la imagen de las ROIs
        mascara2 = np.transpose(self.mascara,(1,0,2))                          #El (1,0,2) indica cómo se va a trasponer la matriz 3D (ejes)
        self.encima = pg.ImageItem(mascara2)
        self.imv1.addItem(self.encima)
        
        #Se generará un diccionario con los contornos
        keys = np.arange(len(self.contours));                                  #Las llaves serán el número consecutivo de los contornos
#        values = [item[0,0] for item in self.contours];
        self.ROI_dict = dict(zip(keys, self.contours));                        #https://stackoverflow.com/questions/209840/convert-two-lists-into-a-dictionary-in-python        

        self.button1.setChecked(True)                                          #Ponemos en true el botón de "Show ROIs"

#        print(len(self.ROI_dict))

        #Hay que hacer la clasificación de las series de tiempo
        self.clasificacion = self.Series_Clasif()
#        print(self.clasificacion)
        
        #Ahora hay que poner la tabla donde se muestre la clasificacion y que también deje ver las series de tiempo y permita quitarlas

        self.TablaFinal()        

        self.Fig_dict = {}                                                     #Diccionario que tendrá las ROIs remarcadas con los checkbox
        
        
    def Series_Clasif(self):
        matriz, posiciones = self.GenerarSeries()                              #Llamamos a la función que obtiene las series de las ROIs y sus posiciones

        #Después hay que hacer el ajuste de decaimiento exponencial, así que declaramos la función que vamos a ocupar
        def func_exp(x, a, b):                                                  
            return a * np.exp(-b * x) 
        
        X=list(range(self.NoFrames));                                          #Valores X de la serie (se obtuvo el valor después de haber puesto el stack)
        clasificacion = {}                           #vector que tendrá la calsificación de cada serie

        Ventana = 50 
        MediaVentana = math.ceil(Ventana/2) 
        
        for k in range(len(self.contours)):                                    #Vamos a clasificar cada serie de tiempo dentro de este for
            serie = matriz[:,k]                                                #Las series están en la matriz antes encontrada
            popt, pcov = curve_fit(func_exp, X, serie, method='trf');          #Ajuste!:  https://stackoverflow.com/questions/3433486/how-to-do-exponential-and-logarithmic-curve-fitting-in-python-i-found-only-poly                        

            a=popt[0];
            b=popt[1]; 
            divisor = list(map(lambda X: a*np.exp(-b*X), X))

            serie_corregida = serie/divisor                                    #Serie después del ajuste exponencial
            
            #Ahora hay que filtrar la serie por wavelet
            coeff = wavedec(serie_corregida, "db20", mode="per")
            sigma = mad(coeff[-1])
            uthresh = sigma*np.sqrt(2*np.log(len(serie)))                          #Universal Threshold 
            coeff[1:] = (threshold( i, value=uthresh, mode="soft" ) for i in coeff[1:] )
            Y = waverec( coeff, "db20", mode="per" )                 #Aquí está la serie filtrada
            
            
            #Ahora hay que encontrar los máximos
            MaximosX = []
            MaximosY = []
            
            #Primero encontramos los máximos
            for i in range(0, self.NoFrames-Ventana):   #No está tomando los valores, está tomando los índices!!!
            
                SubconX = X[i:i+Ventana]     #Subconjunto de los valores de lambda
                SubconY = Y[i:i+Ventana]     #Subconjunto de los valores de intensidad
                Max = max(SubconY)                #Encuentra el máximo del subconjunto de intensidad
                Max_index = np.argmax(SubconY)    #Encuentra el índice de ese máximo
                Max_X = SubconX[Max_index]        #Encuentra el valor de lambda correspondiente a ese máximo
            
                
                if Max_index == MediaVentana:     # Si el máximo encontrado está a la mitad de la ventana guárdalo
                    MaximosX.append(Max_X)        # También guarda su lambda correspondiente
                    MaximosY.append(Max)            

            #Ahora hay que filtrar esos máximos usando la mediana y la desviación estándar (porque suele encontrar más de los que debe)
            #https://pdal.io/tutorial/python-filtering.html
            mediana = np.median(Y)
            stddev = np.std(Y)
            MaximosX_filtr = []
            MaximosY_filtr = []
            
            for j in range(len(MaximosY)):                                     #Vamos a revisar cada uno de los máximos encontrados antes
                if (MaximosY[j]-mediana) > 2*stddev:                           #el máximo - la mediana de la serie debe ser 2 veces mayor que la desviación estándar
                    MaximosX_filtr.append(MaximosX[j])
                    MaximosY_filtr.append(MaximosY[j])
                              
            
            #Ahora hay que revisar si se encontron 1 máximo, más de un máximo o ningún máximo            
            if len(MaximosY_filtr) == 1:
                clasificacion[k] = 1                                           #Es decir, va a ser 1 si tiene un pico la serie
            else:
                clasificacion[k] = 0                                           #si tiene más de uno o cero (suponiendo que no encontró máximos) entonces será cero
        
        return clasificacion        


    def TablaFinal(self):                                                    #Func que genera la tabla con las primeras ROIs            
        self.Tabla.setRowCount(len(self.ROI_dict))                             #Número de renglones que tendrá la tabla dependiendo del número de ROIs
        self.Tabla.setColumnCount(5)                                           #Número de columnas que tendrá la tabla    

        renglon=0     
        self.botones_series = QtGui.QButtonGroup( self.centralwidget)                          #Grupo de radio buttons
        self.botones_remove = QtGui.QButtonGroup( self.centralwidget)
        
        self.dict_botones_class = {}                                   
        
        for key in self.ROI_dict.keys():                                       #Para saber las posiciones de cada ROI encontrada   
            contorno = self.ROI_dict[key];
            pos = contorno[0,0]
            
            #Item que muestra los números de cada contorno
            item1 = QtGui.QTableWidgetItem(str(key))                           #El string de numeración de la tabla
            self.Tabla.setItem(renglon, 0, item1)                              #El string se pone en el i-ésimo renglón y columna 0
 
            #Item que muestra los radio buttons para mostrar la serie de tiempo
            item2 = QtGui.QRadioButton(str(pos))                               #Ponemos un radiobutton en cada renglón
            item2.setChecked(False)                                            #Este radiobutton es para mostrar las series de tiempo
            item2.clicked.connect(self.CheckBox)                               #Si el radio button se presiona, mándalo a la función CheckBox
            self.botones_series.addButton(item2)                                 #El radio button es parte del grupo radio buttons
            self.Tabla.setCellWidget(renglon, 1, item2)                        #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview
                        
            #Porque cada renglón debe tener radio buttons differentes (para indicar la clasificación de la serie)
            self.dict_botones_class['botones_class'+str(key)] = QtGui.QButtonGroup( self.centralwidget)           #Hay que poner un grupo de radio button por cada renglón en dos columnas!!! ent tiene que ir dentro del for y cambiar de nombre en cada renglón

            item3 = QtGui.QRadioButton()                                       #Radiobutton 1 máximo      
            self.dict_botones_class['botones_class'+str(key)].addButton(item3)                                 #El radio button es parte del grupo radio buttons
            self.Tabla.setCellWidget(renglon, 2, item3)                        #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview
            
            item4 = QtGui.QRadioButton()                                       #Radiobutton múltiples máximos
            self.dict_botones_class['botones_class'+str(key)].addButton(item4)      #El radio button es parte del grupo radio buttons
            self.Tabla.setCellWidget(renglon, 3, item4)                        #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview

            #Con esto vamos a poner los radio buttons en la clasificación hecha en la función anterior                        
            if self.clasificacion[key] == 1:    
                item3.setChecked(True)     
                item4.setChecked(False)  
            else:
                item3.setChecked(False)     
                item4.setChecked(True)                 

            #Por si se quiere quitar la serie                 
            item5 = QtGui.QRadioButton()                                       #Ponemos un radiobutton en cada renglón
            item5.setChecked(False)                                            #Esre radio button será para poder quitar las ROIs
            item5.clicked.connect(self.QuitarROI2)                              #Si el radio button se presiona, mándalo a la función CheckBox
            self.botones_remove.addButton(item5)                               #El radio button es parte del grupo radio buttons
            self.Tabla.setCellWidget(renglon, 4, item5)                        #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview
                         
            renglon = renglon + 1                                              #Para pasar al siguiente renglón
                            
        self.Tabla.setHorizontalHeaderLabels(str("Number;Position;One Max;Multiple Max;Remove ROI").split(";"))      #Etiqueta de la columna 
        self.Tabla.verticalHeader().hide()                                     #Quitar letrero vertical   https://stackoverflow.com/questions/14910136/how-can-i-enable-disable-qtablewidgets-horizontal-vertical-header        

        

    #Esta función es para quitar ROIs en la tabla donde están las series clasificadas (que no es igual a la primera tabla)
    def QuitarROI2(self):
        #Hay que volver a crear el diccionario de la clasificación, por si alguna ROI se reclasificó!!!
        #Si ni creo que no importa, solo hasta que se guarden las ROIs entonces habrpa que volver a 
        #Crear ese diccionario!!
        #El botón de la ROI que se quiere quitar
        boton_remove = abs(self.botones_remove.checkedId())                    #ID del botón seleccionado
#        print(boton_remove)
        ID_boton_remove = boton_remove -2                                      #Hay que corregir el ID, porque empieza en -2 por alguna razón
        key_remove = int(self.Tabla.item(ID_boton_remove,0).text())            #Key del diccionario (texto que aparece en la primer columna de la tabla)
#        print(str(key_remove))
        
        #El botón que muestra a la serie de tiempo
        boton_serie = abs(self.botones_series.checkedId())                     #boton_serie será -1 si no hay ningún botón seleccionado!!!
        ID_boton_serie = boton_serie -2 
        key_serie = int(self.Tabla.item(ID_boton_serie,0).text())              #Hay que pasarlo de str a integer
#        print(key_serie)
        

        del self.ROI_dict[key_remove]                                          #Hay que quitar la ROI del diccionario de ROIs
        del self.clasificacion[key_remove]                                     #Quitamos la clasficación de la ROI que se quitó
              
        
        #Con esto creamos un nuevo diccionario de clasificación (por si el usuario hizo algún cambio, hay que hacer esto también al guardar las imágenes finales)
        for key in self.clasificacion.keys():                                  #Vamos a repasar las llaves de la clasificación de las series            
            ID = abs(self.dict_botones_class['botones_class'+str(key)].checkedId())  #el ID da -3 si es un caso de múltiples picos, y da -2 si es un caso de 1 pico
            if ID == 2:
                self.clasificacion[key] = 1
            elif ID == 3:
                self.clasificacion[key] = 0            
        
        self.contours = list(self.ROI_dict.values())                           #Los contornos "generales" se obtienen a partir del diccionario
        
     
        if boton_serie > 1:                                                    #Si sí hay una serie de tiempo graficada                  
            if key_serie == key_remove:                                        #Si la serie de tiempo que se quiere quitar es la correspondiente a la ROI que se quiere quitar
                self.GraficaSerieTiempo.clear()                                #Hay que quitar la serie de tiempo de la gráfica        
                self.Tabla.clear()                                             #Quitamos la tabla primero 
                self.TablaFinal()                                            #Podemos poner la tabla sin la ROI quitada y sin marcar ningún botón porque ya no hay gráfica
            else:                                                              #Como la serie de tiempo que está en la gráfica no es la misma que la de la ROI que se quitó
                self.Tabla.clear()                                             #Quitamos la tabla primero 
                self.TablaFinalNueva(key_serie)                                     #Hay que rehacer la tabla sin esa ROI pero con un botón marcado
                item = self.Tabla.item(key_serie, 0)                           #Se desplaza la tabla hasta donde está el último botón marcado de la serie de tiempo 
                self.Tabla.scrollToItem(item, QtGui.QAbstractItemView.PositionAtTop) #https://stackoverflow.com/questions/24211182/how-to-set-a-qtablewidget-to-consistently-scroll-to-bottom-during-live-data-inpu
        #        self.Tabla.selectRow(Checked_Key)

        #Creamos una nueva self.mascara que tendrá las ROIs con un canal alfa para que sea transparente 
        self.mascara = np.zeros((self.alto, self.ancho, 4));
        mascara1 = np.zeros((self.alto, self.ancho, 3));
        cv2.drawContours(mascara1,self.contours,-1,(255,255,0),1);             #-1 en lugar del 0
        self.mascara[:,:,0:3] = mascara1;
        self.mascara[:,:,3][mascara1[:,:,0]>200]=255;                          #Solo se pondrá en no transparente la parte de las ROIs
        
        self.Estado_Boton1()                                                   #Vamos a poner las ROIs (o no), dependiendo de qué botones están presionados
                                                                               #Tomando en cuenta la nueva máscara creada

    #Tabla que va a tener un botón marcado ya que se eliminó una ROI diferente a la de la serie mostrada en la gráfica
    def TablaFinalNueva(self, Checked_Key):                                         #Func que genera la tabla nueva pero con un botón marcado       
        self.Tabla.setRowCount(len(self.ROI_dict))                             #Número de renglones que tendrá la tabla dependiendo del número de ROIs
        self.Tabla.setColumnCount(5)                                           #Número de columnas que tendrá la tabla    

        renglon=0     
        self.botones_series = QtGui.QButtonGroup( self.centralwidget)                          #Grupo de radio buttons
        self.botones_remove = QtGui.QButtonGroup( self.centralwidget)
        
        self.dict_botones_class = {}                                                #Este diccionario se irá llenando con los radio buttons horizontales (de las series clasificadas)
        
        for key in self.ROI_dict.keys():                                       #Para saber las posiciones de cada ROI encontrada   
            contorno = self.ROI_dict[key];
            pos = contorno[0,0]

            #Es el ítem de las llaves (número de los contornos)
            item1 = QtGui.QTableWidgetItem(str(key))                           #El string de numeración de la tabla
            self.Tabla.setItem(renglon, 0, item1)                              #El string se pone en el i-ésimo renglón y columna 0
            
            item2 = QtGui.QRadioButton(str(pos))                               #Ponemos un radiobutton en cada renglón
            if key == Checked_Key:                                             #Si la llave es igual que la serie checada antes de la eliminación de la ROI
                item2.setChecked(True)
            else:
                item2.setChecked(False)            
            
            #Este item es el de las series de tiempo
            item2.clicked.connect(self.CheckBox)                               #Si el radio button se presiona, mándalo a la función CheckBox
            self.botones_series.addButton(item2)                                 #El radio button es parte del grupo radio buttons
            self.Tabla.setCellWidget(renglon, 1, item2)                        #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview
                        
            #Porque cada renglón debe tener radio buttons differentes (para indicar la clasificación de la serie)
            self.dict_botones_class['botones_class'+str(key)] = QtGui.QButtonGroup( self.centralwidget)           #Hay que poner un grupo de radio button por cada renglón en dos columnas!!! ent tiene que ir dentro del for y cambiar de nombre en cada renglón

            #Estos ítems son los de la clasificación
            item3 = QtGui.QRadioButton()                                       #Radiobutton 1 máximo      
            self.dict_botones_class['botones_class'+str(key)].addButton(item3)                                 #El radio button es parte del grupo radio buttons
            self.Tabla.setCellWidget(renglon, 2, item3)                        #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview
            
            item4 = QtGui.QRadioButton()                                       #Radiobutton múltiples máximos
            self.dict_botones_class['botones_class'+str(key)].addButton(item4)      #El radio button es parte del grupo radio buttons
            self.Tabla.setCellWidget(renglon, 3, item4)                        #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview

            #Con esto vamos a poner los radio buttons en la clasificación hecha en la función anterior                        
            if self.clasificacion[key] == 1:    
                item3.setChecked(True)     
                item4.setChecked(False)  
            else:
                item3.setChecked(False)     
                item4.setChecked(True)     
                
            #Este ítem es para lo de quitar una ROI    
            item5 = QtGui.QRadioButton()                           #Ponemos un radiobutton en cada renglón
            item5.setChecked(False)            
            item5.clicked.connect(self.QuitarROI2)                              #Si el radio button se presiona, mándalo a la función CheckBox
            self.botones_remove.addButton(item5)                               #El radio button es parte del grupo radio buttons
            self.Tabla.setCellWidget(renglon, 4, item5)                        #El string y la check Box se ponen en el i-ésimo renglón y columna 1 https://stackoverflow.com/questions/24148968/how-to-add-multiple-qpushbuttons-to-a-qtableview
                         
            renglon = renglon + 1                                              #Para pasar al siguiente renglón
                            
        self.Tabla.setHorizontalHeaderLabels(str("Number;Position;One Max;Multiple Max;Remove ROI").split(";"))      #Etiqueta de la columna 
        self.Tabla.verticalHeader().hide()                                     #Quitar letrero vertical   https://stackoverflow.com/questions/14910136/how-can-i-enable-disable-qtablewidgets-horizontal-vertical-header        
        
                                 
                                        
    def Reset(self):
        self.imv1.close()
        self.imv1 = pg.ImageView(self.dockWidgetContents)
        self.imv1.setObjectName("imv1")
        self.horizontalLayout.addWidget(self.imv1)        
        self.dockWidget.setWidget(self.dockWidgetContents)

        self.Tabla.clear()
        
        self.GraficaSerieTiempo.clear()
        
        self.button1.setChecked(False) 
        
        self.button1.setChecked(False) 
        
        del self.data

            
app = QtGui.QApplication(sys.argv)
MyWindow = MyWindowClass(None)
MyWindow.show()
app.exec_()