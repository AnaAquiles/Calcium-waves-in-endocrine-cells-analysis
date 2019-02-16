# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 19:03:03 2019

@author: akire
La función ContourTimeSeries genera las series de tiempo del diccionario 
de ROIs y las guarda en un diccionario, que se manda a la función 
CellDetection de la clase MainWinClass

Poner otra función que saque la serie de tiempo de un solo contorno para que 
se agregue al diccionario

"""

import numpy as np
import cv2 
import matplotlib.pyplot as plt


# Genera el diccionario de series de tiempo
def ContourTimeSeries(Stack, ROI_dict, NoFrames, alto, ancho):
    contours = list(ROI_dict.values())                                         #Los contornos se obtienen a partir del diccionario, pero deben pasarse a una lista, si no la variable es tipo "dict_values"
    NoContornos = len(contours)                     

    TimeSer_dict = {}                                                          #Diccionario que contendrá las series de tiempo

    
    for j in range(NoContornos):            
        binaria = np.zeros((alto, ancho));                                     #Máscara binaria para obtener la serie de tiempo

        cv2.drawContours(binaria,contours,j,(255,255,255),-1);                 #Dibujamos el contorno relleno generando así la máscara binaria, int porque antes key es str
        area = cv2.countNonZero(binaria)                                       #Encontramos el número de pixeles dentro del contorno (área)
        coordenadas = np.argwhere(binaria == 255)                              #Buscamos las coordenadas de los pixeles blancos en la imagen binaria
        SerieTiempo = np.zeros(NoFrames)                                       #Una serie de tiempo de ceros de tamaño igual al número de frames
        
        for frame in range(NoFrames):                                          #Recorremos cada frame
            imagen_i = Stack[frame,:,:] 
            suma = 0
            for coordenada in coordenadas:                                     #Recorremos cada coordenada
                suma = suma + imagen_i[coordenada[0],coordenada[1]]
            promedio = suma/area                                               #Sacamos el promedio
            SerieTiempo[frame] = round(promedio, 2)                            #El promedio se guarda en la serie

        TimeSer_dict[j] = SerieTiempo                                          #Creación del diccionario de series de tiempo

#    cv2.imshow('ImageWindow',binaria)
#    plt.plot(SerieTiempo)
    return(TimeSer_dict)


