__author__ = 'DYEDEN'
import time
tempo = time.clock()

from arcpy import Array , SelectLayerByLocation_management, MakeFeatureLayer_management, da, SelectLayerByAttribute_management, CopyFeatures_management, AddField_management, \
        Point, Polyline, Polygon, Describe, Extent, SpatialReference, CreateFeatureclass_management, Exists, Dissolve_management, Delete_management, env, ListFields
from math import sqrt, acos, degrees, sin,cos, tan, pi, atan
from os import path, mkdir
from shutil import rmtree
from sys import argv
env.outputMFlag = "Disabled"
env.outputZFlag = "Disabled"
class DefinirApp():
    def __init__(self):
        diretorio = path.dirname(path.dirname(argv[0]))
        self.spatial_geo_sirgas_2000 = 'GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
        self.spatial_proj_lambert = 'PROJCS["SIRGAS_2000_Lambert_Conformal_Conic_PA",GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-52.5],PARAMETER["Standard_Parallel_1",-0.5],PARAMETER["Standard_Parallel_2",-6.833333333333333],PARAMETER["Latitude_Of_Origin",-3.666667],UNIT["Meter",1.0]]'
