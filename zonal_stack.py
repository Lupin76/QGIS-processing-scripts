# -*- coding: utf-8 -*-

"""
***************************************************************************
    
    StackZonalStatistics.py
    
    Date                 : January 2021
    Copyright         : (C) 2021 by Giacomo Fontanelli
    Email                : giacomofontanelli76 at gmail.com
    
***************************************************************************
                                                                                                                   
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
                                                                                                                   
***************************************************************************

    This script run zonal statistics 
    for each layer of a multi band raster

***************************************************************************   
"""

# --------------------------------------------------------------------------------------------------------------------
# 0 -----------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------

__author__      = 'Giacomo Fontanelli'
__date__         = 'December 2020'
__copyright__ = '(C) 2020, Giacomo Fontanelli'

# --------------------------------------------------------------------------------------------------------------------
# 1 -----------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------

from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterString,
    QgsProcessingParameterEnum,
    QgsProcessingOutputVectorLayer,
    QgsProcessingException)

from qgis import processing

# --------------------------------------------------------------------------------------------------------------------
# 2 ----- Define the algorithm as a class inheriting from QgsProcessingAlgorithm -------
# --------------------------------------------------------------------------------------------------------------------

class ZonalStatisticsStack(QgsProcessingAlgorithm):

    # 2A 
    STACK        = 'STACK'              # stack                   - INPUT_RASTER
    POLYGONS = 'POLYGONS'      # polygons             - INPUT_VECTOR
    PREFIX        = 'PREFIX'            # column_prefix     - COLUMN_PREFIX
    STAT           = 'STAT'                # stat                     - STATISTICS

    # 2B
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
        
    # 2C
    def createInstance(self):
        return ZonalStatisticsStack()
        
    # 2D
    def name(self):
        return 'Zonal stat for stacks'
        
    # 2E
    def displayName(self):
        return self.tr('Zonal stat for stacks')
        
    # 2F
    def group(self):
        return self.tr('Sampling')

    # 2G
    def groupId(self):
        return 'rasteranalysis'

    # 2H
    def shortHelpString(self):
        return self.tr("This script perform statistics on multilayer stacks")
    
    # --------------------------------------------------------------------------------------------------------------------
    # 3 ---------- Define the parameters of the processing framework -----------------------------
    # --------------------------------------------------------------------------------------------------------------------
    
    def initAlgorithm(self, config=None):
    
        # 3A Input vector polygon
        self.addParameter(QgsProcessingParameterVectorLayer(
            name = self.POLYGONS,
            description = self.tr('Vector layer containing polygons'),
            types = [QgsProcessing.TypeVectorPolygon],
            defaultValue = None,
            optional = False))
    
        # 3B Input stack polygon
        self.addParameter(QgsProcessingParameterRasterLayer(
            name = self.STACK,
            description = self.tr('Stack'),
            defaultValue = None,
            optional = False))
    
        # 3C Input band prefix
        self.addParameter(QgsProcessingParameterString(
            name = self.PREFIX,
            description = self.tr('Output column prefix'),
            defaultValue = 'b_',
            optional = False))

        # 3D select statistics 
        self.addParameter(QgsProcessingParameterEnum(
            name = self.STAT,
            description = self.tr('Statistics to calculate'),
            options = [self.tr("Number = 0"),
                            self.tr("Sum = 1"),
                            self.tr("Mean = 2"),
                            self.tr("Median = 3"),
                            self.tr("Dev std = 5"),
                            self.tr("Minimum = 6"),
                            self.tr("Maximum = 7"),
                            self.tr("Range = 8"),
                            self.tr("Minority = 9"),
                            self.tr("Majourity = 10"),
                            self.tr("Variety = 11"), 
                            self.tr("Variance = 12")],
            allowMultiple=True, 
            defaultValue=[2],
            optional = False))

    # --------------------------------------------------------------------------------------------------------------------
    # 4 ----------------------------------------- Import layers ----------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------------

    def processAlgorithm(
        self,
        parameters,
        context,
        feedback):
        
        # 4A Input polygons
        polygons = self.parameterAsSource(
            parameters,
            self.POLYGONS,
            context)
        
        # 4B Input stack
        stack = self.parameterAsRasterLayer(
            parameters, 
            self.STACK, 
            context)

        # 4C Input prefix for each column of sampling
        columnPrefix = self.parameterAsString(
            parameters, 
            self.PREFIX, 
            context)
        
        # 4D Select statistical index
        stat = self.parameterAsEnums(
            parameters, 
            self.STAT, 
            context)
            
        # -------------------------------------------------------------------------------------------------------------
        # 5 ------------------------------------- Check -----------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        
        # 5A If source was not found, throw an exception
        if polygons is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, POLYGONS))
   
        # 5B Check for cancelation
        if feedback.isCanceled():
            return {}
            
        # --------------------------------------------------------------------------------------------------------------------
        # 6 ----------------------------------------- Execution ----------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------------
       
        # 6A retrieve band number
        nBands = stack.bandCount()
        listBands = range(1, (nBands+1))
        
        # 6B
        for iBand in listBands:
            processPar = {
                "INPUT_RASTER": parameters[self.STACK],
                "RASTER_BAND": iBand, 
                "INPUT_VECTOR": parameters[self.POLYGONS],
                "COLUMN_PREFIX": 'b_', 
                "STATISTICS": parameters[self.STAT]}
            
            # 6C
            processOut = processing.run(
                'qgis:zonalstatistics', 
                processPar,
                is_child_algorithm = False,
                context = context,
                feedback = feedback)
                
            # 6D Check for cancelation
            if feedback.isCanceled():
                return {}
        
        return {self.POLYGONS: processOut["INPUT_VECTOR"]}

