# -*- coding: utf-8 -*-

"""
***************************************************************************

    polygon mask.py

    Date         : September 2020
    Copyright : (C) 2020 by Giacomo Fontanelli
    Email        : giacomofontanelli76 at gmail dot com

***************************************************************************

   This program is free software; you can redistribute it and/or modify    
   it under the terms of the GNU General Public License as published by 
   the Free Software Foundation; either version 2 of the License, or        
   (at your option) any later version.                                                         

***************************************************************************

   This script produces a 1-0 raster mask of polygons extension

***************************************************************************
"""

# --------------------------------------------------------------------------------------------------------------------
# 0 -----------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------

__author__ = 'Giacomo Fontanelli'
__date__ = 'September 2020'
__copyright__ = '(C) 2020, Giacomo Fontanelli'

# --------------------------------------------------------------------------------------------------------------------
# 1 -----------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterDistance,
    QgsProcessingParameterRasterDestination,
    QgsProcessingException,
    QgsProcessing)
  
from qgis.PyQt.QtCore import (
    QCoreApplication)

from qgis import processing

# --------------------------------------------------------------------------------------------------------------------
# 2 ----- Define the algorithm as a class inheriting from QgsProcessingAlgorithm -------
# --------------------------------------------------------------------------------------------------------------------

class mioScript(QgsProcessingAlgorithm):
    
    # 2A
    INPUT = "INPUT"
    PIXEL_DIMENSION = "PIXEL_DIMENSION"
    OUTPUT = "OUTPUT"
 
    # 2B
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    # 2C
    def createInstance(self):
        return mioScript()
    
    # 2D
    def name(self):
        return 'Raster polygon mask'

    # 2E
    def displayName(self):
        return self.tr('Raster polygon mask')

    # 2F
    def group(self):
        return self.tr('Miscellaneous')

    # 2G
    def groupId(self):
        return 'rsscripts'

    # 2H
    def shortHelpString(self):
        return self.tr("This script produces a 1-0 raster mask of polygons extension")

    # --------------------------------------------------------------------------------------------------------------------
    # 3 ---------- Define the parameters of the processing framework -----------------------------
    # --------------------------------------------------------------------------------------------------------------------
    
    def initAlgorithm(self, config=None):

        # 3A Input vector polygon
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT,
            self.tr('Input polygon layer'),
            types=[QgsProcessing.TypeVectorPolygon]))

        # 3B Distance
        self.addParameter(QgsProcessingParameterDistance(
            self.PIXEL_DIMENSION,
            self.tr('Input point distance'),
            parentParameterName=self.INPUT,
            minValue=0.0,
            defaultValue=10.0))
            
        # 3D Output raster
        self.addParameter(QgsProcessingParameterRasterDestination(
            self.OUTPUT,
            self.tr('Output raster')))

    # --------------------------------------------------------------------------------------------------------------------
    # 4 ----------------------------------------- Import layers ----------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------------
    
    def processAlgorithm(
        self, 
        parameters, 
        context, 
        feedback):

        # 4B Input polygon 
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context)

        # 4C Distance
        pixelDim = self.parameterAsDouble(
            parameters,
            self.PIXEL_DIMENSION,
            context)

        # -------------------------------------------------------------------------------------------------------------
        # 5 ------------------------------------- Check -----------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        
        # 5A If source was not found, throw an exception
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, INPUT))
   
        # 5B Check for cancelation
        if feedback.isCanceled():
            return {}

        # -------------------------------------------------------------------------------------------------------------
        # 6 ------------------------------------ Rasterization -with GDAL ----------------------------------
        # -------------------------------------------------------------------------------------------------------------

        # 6A Retrieve border limits
        ext = source.sourceExtent()
        xmin = ext.xMinimum()
        xmax = ext.xMaximum()
        ymin = ext.yMinimum()
        ymax = ext.yMaximum()

        # 6B Raster number of column and row 
        nCol = int((xmax - xmin) / pixelDim)
        nRow = int((ymax - ymin) / pixelDim)

        # 6C Parameters for rasterization
        processPar = {
            "INPUT":parameters[self.INPUT],
            "FIELD":"",
            "BURN":1,
            "UNITS":0,
            "WIDTH":nCol,
            "HEIGHT":nRow,
            "EXTENT": parameters[self.INPUT],
            "NODATA":"nan",
            "OPTIONS":"",
            "DATA_TYPE":1,
            "INIT":0,
            "INVERT":False,
            "EXTRA":"",
            "OUTPUT": parameters[self.OUTPUT]}

        # 6D Run rasterization
        processOut = processing.run(
            "gdal:rasterize",
            processPar,
            is_child_algorithm=False,
            context=context,
            feedback=feedback)
        
        # 6E Check for cancelation
        if feedback.isCanceled():
            return {}
        
        return {self.OUTPUT: processOut["OUTPUT"]}
    
       
