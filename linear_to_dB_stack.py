# -*- coding: utf-8 -*-

"""
***************************************************************************

    linear-to-dB-processing.py

    Date         : May 2021
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
__date__    = 'May 2021'
__copyright__ = '(C) 2021, Giacomo Fontanelli'

# --------------------------------------------------------------------------------------------------------------------
# 1 -----------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------
 
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterRasterDestination,
    QgsProcessingException,
    QgsProcessing,
    QgsWkbTypes)

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
        return self.tr("This script convert linear to dB froma multiband raster")

    # --------------------------------------------------------------------------------------------------------------------
    # 3 ---------- Define the parameters of the processing framework -----------------------------
    # --------------------------------------------------------------------------------------------------------------------
    
    def initAlgorithm(self, config=None):

        # 3A Input raster stack
        #self.addParameter(QgsProcessingParameterRasterLayer(
        #    self.INPUT,
        #    self.tr('Input linear stack'),
        #        types=[QgsProcessing.TypeRaster]))

         #class qgis.core.QgsProcessingParameterRasterLayer(
         #name: str, 
         #description: str = '', 
         #defaultValue: Any = None, 
         #optional: bool = False)
        
        # oppure
        self.addParameter(QgsProcessingParameterMultipleLayers(
            self.INPUT,
            self.tr('Input linear stack'),
            QgsProcessing.TypeRaster,
            optional=True))        
        
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

        # 4B Input stack 
        stackIn = self.parameterAsSource(
            parameters,
            self.INPUT,
            context)

       # 4B Output stack 
        stackOut = self.parameterAsSource(
            parameters,
            self.Output,
            context)
 
        # -------------------------------------------------------------------------------------------------------------
        # 5 ------------------------------------- Check -----------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        
        # 5A If source was not found, throw an exception
        if stackIn is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, INPUT))
   
        # 5B Check for cancelation
        if feedback.isCanceled():
            return {}

        # -------------------------------------------------------------------------------------------------------------
        # 6 -------------------------------------- Processing ----------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------    
        
        # 6A loop
        nBand = stackIn.bandCount()
        
        bandList = []

        for band in range(1, nBand+1):
        
            # print("calculating image n. {}".format(str(band)))

            # 6B db calculation 
            operation = "10 ^ ( " + pathFileIn + "@" + str(band) + " / 10 )"
            parametersCalc = {
                "EXPRESSION": operation,
                "LAYERS": pathFileIn,
                "CELLSIZE": None,
                "EXTENT": None,
                "CRS": None,
                "OUTPUT": "TEMPORARY_OUTPUT"}

            # 6C
            outRas = processing.run(
                'qgis:rastercalculator',
                parametersCalc,
                is_child_algorithm = False,
                context = context,
                feedback = feedback)

            # 6D 
            bandList.append(outRas["OUTPUT"])
 
            # 6E Check for cancelation
            if feedback.isCanceled():
                return {}

        # 6F stacking
        parametersStack = {
            "INPUT": bandList,
            "PCT": False,
            "SEPARATE": True,
            "NODATA_INPUT": None,
            "NODATA_OUTPUT": None,
            "OPTIONS":"",
            "EXTRA":"",
            "DATA_TYPE": 5,
            "OUTPUT": stackOut}

        # 6G
        outStack = processing.run(
            'gdal:merge', 
            parametersStack,
            is_child_algorithm = False,
            context = context,
            feedback = feedback)
            
        # 6H Check for cancelation
        if feedback.isCanceled():
            return {}
            
        return {self.OUTPUT: outStack["OUTPUT"]}
