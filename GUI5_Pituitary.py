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



def PituitarySegm(frame0, frame1, CellRad, data):
    #abs(F - Fmean)/Fmean para aplanarla 
    #buscar la forma de normalizarla en el dominio!!!

    #Detección de spots    
    DesVest = np.std(data, 0)                                                  #Imagen de la desviación estándar
    
    blobs_log = blob_log(DesVest, min_sigma=CellRad, max_sigma=CellRad + 5, num_sigma=1, \
                         threshold=.1)                                         #Detección de spots
    
    blobs_log[:, 2] = blobs_log[:, 2] * sqrt(2)                                #Compute radii in the 3rd column.
    
    fig, axes = plt.subplots()
    #ax = axes.ravel()
    
    axes.imshow(DesVest, cmap='seismic')
    
    for blob in blobs_log:
        y, x, r = blob
        c = plt.Circle((x, y), r, color='yellow', linewidth=1, fill=False)
        axes.add_patch(c)
    axes.set_axis_off()
    
    plt.tight_layout()
    plt.show()
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
