# -*- coding: utf-8 -*-

#******************************************************************************
#
# TauDEM SEXTANTE Provider
# ---------------------------------------------------------
# A suite of Digital Elevation Model (DEM) tools for the extraction and
# analysis of hydrologic information from topography as represented by
# a DEM of vector layer.
#
# Copyright (C) 2012 Alexander Bruy (alexander.bruy@gmail.com)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/licenses/>. You can also obtain it by writing
# to the Free Software Foundation, 51 Franklin Street, Suite 500 Boston,
# MA 02110-1335 USA.
#
#******************************************************************************

import os

from PyQt4.QtGui import *

from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.core.SextanteLog import SextanteLog
from sextante.core.SextanteUtils import SextanteUtils
from sextante.core.SextanteConfig import SextanteConfig
from sextante.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException

from sextante.parameters.ParameterRaster import ParameterRaster
from sextante.parameters.ParameterNumber import ParameterNumber

from sextante.outputs.OutputRaster import OutputRaster

from sextante_taudem.TauDEMUtils import TauDEMUtils

class PeukerDouglas(GeoAlgorithm):
    ELEVATION_GRID = "ELEVATION_GRID"
    CENTER_WEIGHT = "CENTER_WEIGHT"
    SIDE_WEIGHT = "SIDE_WEIGHT"
    DIAGONAL_WEIGHT = "DIAGONAL_WEIGHT"

    STREAM_SOURCE_GRID = "STREAM_SOURCE_GRID"

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/icons/taudem.png")

    def defineCharacteristics(self):
        self.name = "Peuker Douglas"
        self.cmdName = "peukerdouglas"
        self.group = "Stream Network Analysis tools"

        self.addParameter(ParameterRaster(self.ELEVATION_GRID, "Elevation Grid", False))
        self.addParameter(ParameterNumber(self.CENTER_WEIGHT, "Center Smoothing Weight", 0, None, 0.4))
        self.addParameter(ParameterNumber(self.SIDE_WEIGHT, "Side Smoothing Weight", 0, None, 0.1))
        self.addParameter(ParameterNumber(self.DIAGONAL_WEIGHT, "Diagonal Smoothing Weight", 0, None, 0.05))

        self.addOutput(OutputRaster(self.STREAM_SOURCE_GRID, "Stream Source Grid"))

    def processAlgorithm(self, progress):
        commands = []
        commands.append(os.path.join(TauDEMUtils.mpiexecPath(), "mpiexec"))

        processNum = SextanteConfig.getSetting(TauDEMUtils.MPI_PROCESSES)
        if processNum <= 0:
          raise GeoAlgorithmExecutionException("Wrong number of MPI processes used.\nPlease set correct number before running TauDEM algorithms.")

        commands.append("-n")
        commands.append(str(processNum))
        commands.append(os.path.join(TauDEMUtils.taudemPath(), self.cmdName))
        commands.append("-fel")
        commands.append(self.getParameterValue(self.ELEVATION_GRID))
        commands.append("-par")
        commands.append(str(self.getParameterValue(self.CENTER_WEIGHT)))
        commands.append(str(self.getParameterValue(self.SIDE_WEIGHT)))
        commands.append(str(self.getParameterValue(self.DIAGONAL_WEIGHT)))
        commands.append("-ss")
        commands.append(self.getOutputValue(self.STREAM_SOURCE_GRID))

        loglines = []
        loglines.append("TauDEM execution command")
        for line in commands:
            loglines.append(line)
        SextanteLog.addToLog(SextanteLog.LOG_INFO, loglines)

        TauDEMUtils.executeTauDEM(commands, progress)

    def helpFile(self):
        return os.path.join(os.path.dirname(__file__), "help", self.cmdName + ".html")
