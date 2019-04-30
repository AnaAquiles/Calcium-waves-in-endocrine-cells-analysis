# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 16:04:15 2019

@author: akire
Aquí va la parte de clasificación (América)
"""
import cv2
import numpy as np

from skimage.feature import blob_log
from math import sqrt
import matplotlib.pyplot as plt



def Clasification(serie):
    print('H')
    
    
def PituitarySegm(frame0, frame1, CellRad, data):
    #abs(F - Fmean)/Fmean para aplanarla 
    #buscar la forma de normalizarla en el dominio!!!

    #Información de los datos
    (NoFrames, alto, ancho) = data.shape
    DiameterDict = {3:1, 5:2, 7:2.5, 9:3, 11:4, 13:4.5}                        #Variación sigma con el diámetro (impar)
    Sigma = DiameterDict[CellRad]                                              #Sigma para el blob

    #Detección de spots    
    DesVest = np.std(data, 0)                                                  #Imagen de la desviación estándar    
    blobs_log = blob_log(DesVest, min_sigma=Sigma, max_sigma=Sigma, \
                         num_sigma=1, threshold=.1)                            #Detección de spots
    
    blobs_log[:, 2] = blobs_log[:, 2] * sqrt(2)                                #Compute radii in the 3rd column.    
    fig, axes = plt.subplots()
    axes.imshow(DesVest, cmap='seismic')
    
    for blob in blobs_log:
        y, x, r = blob
        c = plt.Circle((x, y), r, color='yellow', linewidth=1, fill=False)
        axes.add_patch(c)
    
    axes.set_axis_off()
    
    plt.tight_layout()
    plt.show()
    
    #Imagen final de la máscara binaria!! con cv2 van a salir cruces y cosas raras
    mask = np.zeros((alto, ancho))
    
    #Generación de las series en los spots    
    LenSerie = int(frame1-frame0)                                              #Longitud de la serie de tiempo (va a depender de lo que el usuario haya determinado inicialmente)
    for blob in blobs_log:                                                     #Para cada spot encontrado
        binaria = np.zeros((alto, ancho))                                      #Imagen binaria que contendrá la máscara del spot
        y, x, r = blob                                                         #Centro y radio del spot
        cv2.circle(binaria,(int(x),int(y)), int(r), (255,255,255), -1)         #Creación de la máscara del spot
        area = cv2.countNonZero(binaria)                                       #Encontramos el número de pixeles diferentes de cero
        coordenadas = np.argwhere(binaria == 255)                              #Buscamos las coordenadas de los pixeles blancos en la imagen binaria
        SerieTiempo = np.zeros(LenSerie)                                       #Contendrá la serie de tiempo

        for frame in range(frame0,frame1,1):                                   #Para generar la serie de tiempo de una longitud determinada 
            imagen_i = data[frame,:,:]                                         #Recorremos cada frame
            suma = 0                                                           #Suma de los pixeles en el frame
            for coordenada in coordenadas:                                     #Recorremos cada coordenada
                suma = suma + imagen_i[coordenada[0],coordenada[1]]            #Suma de las intensidades
            promedio = suma/area                                               #Sacamos el promedio
            SerieTiempo[frame] = promedio                                      #El promedio se guarda en la serie        
        Clasification(SerieTiempo)                                             #Función que hace la clasificación de la serie obtenida
        
    
    
    
#%% 
    #Esta parte es la que solo llama a la imagen binaria que ya se tiene
    #No hace ningún cálculo, es para la pueba de concepto
    print('Segmentación de Hipófisis, aquí hay que poner lo que está haciendo Ame')
    
    binaria = cv2.imread("G:\\Mi unidad\\EAGV\\Proyectos\\Segmentacion y Analisis de Celulas con GUI\\Datos brutos\\Videos_Daniel\\1\\BINARIA2.png",0)                                 #Para que se abra en blanco y negro (1 solo canal)                                         #El stack de imágenes se pasa a un arreglo
    (alto, ancho)=binaria.shape 

    # Detección de contornos de la imagen binaria
    copia_bin = binaria.astype(dtype='uint8')*255;

    # Detección de contornos de la imagen binaria
    (imagen1,contours,hierarchy)=cv2.findContours(copia_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);

    #Máscara tendrá el arreglo de la imagen que se va a superponer al video, será en formato RGBA
    mascara = np.zeros((alto, ancho, 4));
    mascara1 = np.zeros((alto, ancho, 3));
    cv2.drawContours(mascara1,contours,-1,(255,255,0),1);     #-1 en lugar del 0
    mascara[:,:,0:3] = mascara1;
    mascara[:,:,3][mascara1[:,:,0]>200]=255;                               #Solo se pondrá en no transparente la parte de las ROIs
    
    mascara2 = np.transpose(mascara,(1,0,2))                          #El (1,0,2) indica cómo se va a trasponer la matriz 3D (ejes)

        
    #Se generará un diccionario con los contornos
    keys = np.arange(len(contours));                                  #Las llaves serán el número consecutivo de los contornos
    ROI_dict = dict(zip(keys, contours));                        #https://stackoverflow.com/questions/209840/convert-two-lists-into-a-dictionary-in-python        
#
#    button1.setChecked(True)                                          #Ponemos en true el botón de "Show ROIs"
#
##        print(len(self.ROI_dict))
#
#    #Hay que hacer la clasificación de las series de tiempo
#    clasificacion = Series_Clasif()
##        print(self.clasificacion)
#    
#    #Ahora hay que poner la tabla donde se muestre la clasificacion y que también deje ver las series de tiempo y permita quitarlas
#
#    self.TablaFinal()        
#
#    self.Fig_dict = {}                                                     #Diccionario que tendrá las ROIs remarcadas con los checkbox
#%%
    return (mascara2, ROI_dict)   



#def Clasification(serie, frame0, frame1, i):
#    print(i)
#    
    