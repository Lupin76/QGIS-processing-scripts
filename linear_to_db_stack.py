# -*- coding: utf-8 -*-

"""
***************************************************************************
    
    linear-to-dB-processing.py

    Date         : December 2021
    Copyright : (C) 2021 by Giacomo Fontanelli
    Email        : giacomofontanelli76 at gmail dot com

***************************************************************************

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

***************************************************************************

    This script convert a stack of bands in linear scale
    to a stack of bands in dB

***************************************************************************
"""

# --------------------------------------------------------------------------------------------------------------------
# 0 -----------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------

__author__ = 'Giacomo Fontanelli'
__date__    = 'December 2021'
__copyright__ = '(C) 2021, Giacomo Fontanelli'

# --------------------------------------------------------------------------------------------------------------------
# 1 -----------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------
 
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterRasterDestination,
    QgsProcessingException,
    QgsProcessing,
    QgsRasterLayer)

from qgis.PyQt.QtCore import (
    QCoreApplication,
    QVariant)

from qgis import processing

# --------------------------------------------------------------------------------------------------------------------
# 2 ----- Define the algorithm as a class inheriting from QgsProcessingAlgorithm -------
# --------------------------------------------------------------------------------------------------------------------

class mioScript(QgsProcessingAlgorithm):
    
    # 2A
    INPUT  = "INPUT"
    OUTPUT = "OUTPUT"
 
    # 2B
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    # 2C
    def createInstance(self):
        return mioScript()
    
    # 2D
    def name(self):
        return 'Linear to dB'

    # 2E
    def displayName(self):
        return self.tr('Linear to dB')

    # 2F
    def group(self):
        return self.tr('Stack tools')

    # 2G
    def groupId(self):
        return 'stacktools'

    # 2H
    def shortHelpString(self):
        return self.tr("This script convert linear to dB values from a multiband raster")

    # --------------------------------------------------------------------------------------------------------------------
    # 3 ---------- Define the parameters of the processing framework -----------------------------
    # --------------------------------------------------------------------------------------------------------------------
    
    def initAlgorithm(self, config=None):

        # 3A Input stack
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.INPUT,
            self.tr('Input linear stack'),
            None,
            False))
                
        # 3B Output raster
        self.addParameter(QgsProcessingParameterRasterDestination(
            self.OUTPUT,
            self.tr('Output dB stack')))
            
    # --------------------------------------------------------------------------------------------------------------------
    # 4 ----------------------------------------- Import layers ----------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------------
    
    # 4A
    def processAlgorithm(
        self, 
        parameters, 
        context, 
        feedback):

       # 4B Input string 
        pathStackIn = self.parameterAsString(
            parameters,
            self.INPUT,
            context)
 
        # -------------------------------------------------------------------------------------------------------------
        # 5 ------------------------------------- Check -----------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        
        # 5A If source was not found, throw an exception
        if pathStackIn is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, INPUT))
   
        # 5B Check for cancelation
        if feedback.isCanceled():
            return {}

        # -------------------------------------------------------------------------------------------------------------
        # 6 -------------------------------------- Processing ----------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------    
        
        #6A deriving input stack
        stackIn = QgsRasterLayer(pathStackIn, "stack")

        # 6B loop over the bands
        nBand = stackIn.bandCount()
        
        bandList = []

        for band in range(1, nBand+1):
        
            # 6C db calculation 
            operation = "10 * ( log10 ( " + pathStackIn + "@" + str(band) + " ) )"
            
            parametersCalc = {
                "EXPRESSION": operation,
                "LAYERS": stackIn,
                "CELLSIZE": None,
                "EXTENT": None,
                "CRS": None,
                "OUTPUT": "TEMPORARY_OUTPUT"}

            # 6D
            outRas = processing.run(
                'qgis:rastercalculator',
                parametersCalc,
                is_child_algorithm = True,
                context = context,
                feedback = feedback)

            # 6E 
            bandList.append(outRas["OUTPUT"])
 
            # 6F Check for cancelation
            if feedback.isCanceled():
                return {}

        # 6G stacking
        parametersStack = {
            "INPUT": bandList,
            "PCT": False,
            "SEPARATE": True,
            "NODATA_INPUT": None,
            "NODATA_OUTPUT": None,
            "OPTIONS":"",
            "EXTRA":"",
            "DATA_TYPE": 5,
            "OUTPUT": parameters[self.OUTPUT]}

        # 6H
        outStack = processing.run(
            'gdal:merge', 
            parametersStack,
            is_child_algorithm = True,
            context = context,
            feedback = feedback)
            
        # 6I Check for cancelation
        if feedback.isCanceled():
            return {}
            
        return {self.OUTPUT: outStack["OUTPUT"]}
