# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 19:03:03 2019

@author: akire
La función ContourTimeSeries va a generar las series de tiempo del diccionario 
de ROIs y las va a guardar en un diccionario, que se va a mandar a la función 
CellDetection de la clase MainWinClass

"""

import numpy as np
import cv2 


def ContourTimeSeries(Stack, ROI_dict, NoFrames, alto, ancho):
    print('paso 0')
    
    contours = ROI_dict.values()    
    NoContornos = len(contours)                     

    TimeSer_dict = {}                                                          #Diccionario que contendrá las series de tiempo


#    Matriz_Series = np.zeros((NoFrames, NoContornos))                          #Donde se guardarán las series
#    Posiciones = np.zeros((NoContornos,2))                                     #Donde se guardarán las posiciones de las ROIs, las posiciones son arreglos numpy, por lo que se deben guardar en una lista
    print('paso 1')
    
    for j in range(NoContornos):            
        binaria = np.zeros((alto, ancho));                                     #Máscara binaria para obtener la serie de tiempo
        print('paso 1.1')
        cv2.drawContours(binaria,contours,j,(255,255,255),-1);                 #Dibujamos el contorno relleno generando así la máscara binaria, int porque antes key es str
        print('paso 1.2')
        area = cv2.countNonZero(binaria)                                       #Encontramos el número de pixeles dentro del contorno (área)
        coordenadas = np.argwhere(binaria == 255)                              #Buscamos las coordenadas de los pixeles blancos en la imagen binaria
        print('paso 1.3')
        SerieTiempo = np.zeros(NoFrames)                                       #Una serie de tiempo de ceros de tamaño igual al número de frames
        print('paso 2')
        
        for frame in range(NoFrames):                                          #Recorremos cada frame
            imagen_i = Stack[frame,:,:] 
            suma = 0
            for coordenada in coordenadas:                                     #Recorremos cada coordenada
                suma = suma + imagen_i[coordenada[0],coordenada[1]]
            promedio = suma/area                                               #Sacamos el promedio
            SerieTiempo[frame] = round(promedio, 2)                            #El promedio se guarda en la serie
        print(j)
        TimeSer_dict[j] = SerieTiempo
                    
    print('paso 3')
#        #Ya se obtuvo la serie de tiempo, ahora hay que calcular el centro de la región (posición)
##            (x,y),radius = cv2.minEnclosingCircle(self.contours[j])            #El centro será la posición que se dará de la célula 
#        M = cv2.moments(contours[j])                                  #Se calculan los momentos del contorno
#        
#        if M['m00']==0:
#            coordenada = coordenadas[0]
#            cx = coordenada[0]
#            cy = coordenada[1]
#            
#        else:
#            cx = int(M['m10']/M['m00'])
#            cy = int(M['m01']/M['m00'])
#        
#        Posiciones[j,0] = cx
#        Posiciones[j,1] = cy
#        
#        Matriz_Series[:,j] = SerieTiempo      
#    
##        print(self.Posiciones)
#
#    return Matriz_Series, Posiciones
##        print(self.Matriz_Series)    
    return(TimeSer_dict)