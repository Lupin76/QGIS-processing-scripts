# -*- coding: utf-8 -*-

"""
***************************************************************************
    
    regularpoints.py

    Date         : December 2020
    Copyright : (C) 2020 by Giacomo Fontanelli
    Email        : giacomofontanelli76 at gmail dot com

***************************************************************************
                                                                                                                 
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or  
    (at your option) any later version.                                                         
                                                                                                                 
***************************************************************************

    This script produces a 1-0 raster mask of polygons extension
    and a net of regular points with a precise spacing

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
    QgsProcessingParameterFeatureSink,
    QgsProcessingException,
    QgsProcessing,
    QgsWkbTypes,
    QgsFields,
    QgsField,
    QgsFeature,
    QgsPointXY,
    QgsGeometry,
    QgsFeatureSink)
  
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QVariant)

from qgis import processing

import numpy as np
import gdal

# --------------------------------------------------------------------------------------------------------------------
# 2 ----- Define the algorithm as a class inheriting from QgsProcessingAlgorithm -------
# --------------------------------------------------------------------------------------------------------------------

class mioScript(QgsProcessingAlgorithm):
    
    # 2A
    INPUT = "INPUT"
    PIXEL_DIMENSION = "PIXEL_DIMENSION"
    MASK = "MASK"
    OUTPUT = "OUTPUT"
 
    # 2B
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    # 2C
    def createInstance(self):
        return mioScript()
    
    # 2D
    def name(self):
        return 'Regular point net'

    # 2E
    def displayName(self):
        return self.tr('Regular point net')

    # 2F
    def group(self):
        return self.tr('Sampling')

    # 2G
    def groupId(self):
        return 'rasteranalysis'

    # 2H
    def shortHelpString(self):
        return self.tr("This script produces a 1-0 raster mask of polygons extension and a regular points net")

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
            self.MASK,
            self.tr('Output raster')))
            
        # 3E Output shape points
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT,
            self.tr('Random points'),
            type=QgsProcessing.TypeVectorPoint))

    # --------------------------------------------------------------------------------------------------------------------
    # 4 ----------------------------------------- Import layers ----------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------------
    
    def processAlgorithm(
        self, 
        parameters, 
        context, 
        feedback):

        # 4A Input polygons 
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context)

        # 4B Distance
        pixelDim = self.parameterAsDouble(
            parameters,
            self.PIXEL_DIMENSION,
            context)
        
        # 4C Output point shapefile
        fields = QgsFields()
        fields.append(QgsField(
            "id",
            QVariant.Int,
            "",
            1,
            0))
        
        (sink, dest_id) = self.parameterAsSink(
            parameters, 
            self.OUTPUT, 
            context,
            fields, 
            QgsWkbTypes.Point, 
            source.sourceCrs())

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
        # 6 ------------------------------------ Rasterization - with GDAL ---------------------------------
        # -------------------------------------------------------------------------------------------------------------

        # 6A Retrieve border limits
        ext = source.sourceExtent()
        Xmin  = ext.xMinimum()
        Xmax = ext.xMaximum()
        Ymin  = ext.yMinimum()
        Ymax = ext.yMaximum()

        # 6B Raster number of column and row 
        nCol   = int((Xmax - Xmin) / pixelDim)
        nRow = int((Ymax - Ymin) / pixelDim)

        # 6C Parameters for rasterization
        processPar = {
            "INPUT": parameters[self.INPUT],
            "FIELD": "",
            "BURN": 1,
            "UNITS": 0,
            "WIDTH": nCol,
            "HEIGHT": nRow,
            "EXTENT": parameters[self.INPUT],
            "NODATA": "nan",
            "OPTIONS": "",
            "DATA_TYPE": 1,
            "INIT": 0,
            "INVERT": False,
            "EXTRA": "",
            "OUTPUT": parameters[self.MASK]}

        # 6D Run rasterization
        processOut = processing.run(
            "gdal:rasterize",
            processPar,
            is_child_algorithm = True,
            context = context,
            feedback = feedback)
        
        # 6E Check for cancelation
        if feedback.isCanceled():
            return {}
        
        # -------------------------------------------------------------------------------------------------------------
        # 7 ----------------------- Open in NUMPY ------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------

        # 7A open the raster in GDAL and then in numpy
        rasterGDAL = gdal.Open(processOut["OUTPUT"])
        band = rasterGDAL.GetRasterBand(1)
        tempArray = band.ReadAsArray()

        # ------------------------------------------------------------------------------------------------------------
        # 8 ---------------------- Points -------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------------------------------

        # 8A attribute table
        features = QgsFeature()
        features.initAttributes(1)
        features.setFields(fields)
        
        # 8E retrieve points
        count = 0
        id0 = 1
        pointList = np.where(tempArray == 1)

        for indexY in pointList[0]:
            indexX = pointList[1][count]

            Xcoord = (Xmin + (pixelDim/2.0)) + (pixelDim * indexX)
            Ycoord = (Ymax -  (pixelDim/2.0)) -  (pixelDim * indexY)
    
            pt = QgsPointXY(Xcoord,Ycoord)
            geom = QgsGeometry.fromPointXY(pt)
 
            # 8F create featurs
            features.setAttributes([id0])
            features.setGeometry(geom)
            sink.addFeature(features, QgsFeatureSink.FastInsert)
    
            count = count + 1
            id0 = id0 + 1
            
        return {self.OUTPUT: dest_id}
    
