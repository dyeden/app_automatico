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
        diretorio = path.dirname(path.dirname(path.dirname(argv[0])))
        self.dict_poligono_tipo = None
        self.spatial_geo_sirgas_2000 = 'GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
        self.spatial_proj_lambert = 'PROJCS["SIRGAS_2000_Lambert_Conformal_Conic_PA",GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-52.5],PARAMETER["Standard_Parallel_1",-0.5],PARAMETER["Standard_Parallel_2",-6.833333333333333],PARAMETER["Latitude_Of_Origin",-3.666667],UNIT["Meter",1.0]]'
        self.diretorio_saida = diretorio + "/SAIDA"
        self.diretorio_entrada = diretorio + "/ENTRADA"
        self.FID = None

    def gerar_app_circulo_buffer(self, layer_linha_largura, diretorio_app):
        buffer_poligono_unido = None
        with da.SearchCursor(layer_linha_largura, ["OID@", "SHAPE@"]) as cursor:
            for row in cursor:
                linha_lambert =  row[1].projectAs(self.spatial_proj_lambert)
                comprimento_linha =  linha_lambert.length
                print comprimento_linha
                buffer_poligono = None
                if comprimento_linha < 10:
                    buffer_poligono =  linha_lambert.buffer(30).projectAs(self.spatial_geo_sirgas_2000)
                elif 10 <= comprimento_linha < 50:
                    buffer_poligono =  linha_lambert.buffer(50).projectAs(self.spatial_geo_sirgas_2000)
                elif 50 <= comprimento_linha < 200:
                    buffer_poligono =  linha_lambert.buffer(100).projectAs(self.spatial_geo_sirgas_2000)
                elif 200 <= comprimento_linha <= 600:
                    buffer_poligono =  linha_lambert.buffer(200).projectAs(self.spatial_geo_sirgas_2000)
                elif comprimento_linha > 600:
                    buffer_poligono =  linha_lambert.buffer(500).projectAs(self.spatial_geo_sirgas_2000)
                if buffer_poligono:
                    if buffer_poligono_unido:
                        buffer_poligono_unido = buffer_poligono_unido.union(buffer_poligono)
                    else:
                        buffer_poligono_unido = buffer_poligono
        CopyFeatures_management(buffer_poligono_unido, diretorio_app)
        del cursor

    def ler_linhas_largura(self, tipo):
        if tipo == "poligono_simples":
            self.dict_poligono_tipo[self.FID]["layer"] = MakeFeatureLayer_management(self.diretorio_saida +
                                                                                     "/LINHAS/LINHAS_FID_" + str(self.FID) + ".shp", "LINHA_LARGURA_"  + str(self.FID))

    def tipo_de_poligono(self, fid_n, shape_massa_dagua):
        import linhas_largura_rio
        linhas_de_largura_var = linhas_largura_rio.DefinirLargura()
        return linhas_de_largura_var.iniciar_codigo(fid_n, shape_massa_dagua)

    def criar_app(self, layer_massa_dagua):
        self.dict_poligono_tipo = {}
        with da.SearchCursor(layer_massa_dagua, ["OID@", "SHAPE@"]) as cursor:
            for row in cursor:
                self.FID = row[0]
                try:
                    self.dict_poligono_tipo[self.FID] = self.tipo_de_poligono(self.FID, row[1])
                    self.ler_linhas_largura(self.dict_poligono_tipo[self.FID]["tipo"])
                    diretorio_app = self.diretorio_saida + "/APP/APP_FID_" + str(self.FID) + ".shp"
                    self.gerar_app_circulo_buffer(self.dict_poligono_tipo[self.FID]["layer"], diretorio_app)
                    print self.dict_poligono_tipo
                except:
                    print self.FID, "nao_funcionou"
        del cursor

    def iniciar_codigo(self):
        if path.exists(self.diretorio_saida):
            rmtree(self.diretorio_saida)
        mkdir(self.diretorio_saida)
        mkdir(self.diretorio_saida + "/LINHAS")
        mkdir(self.diretorio_saida + "/RESIDUOS")
        mkdir(self.diretorio_saida + "/APP")
        MakeFeatureLayer_management(self.diretorio_entrada + "/MASSA_DAGUA.shp", "MASSA_DAGUA")
        self.criar_app("MASSA_DAGUA")
        # self.ler_linhas_largura()
        # for FID in self.dict_poligono_tipo:
        #     diretorio_app = self.diretorio_saida + "/APP/APP_FID_" + str(FID) + ".shp"
        #     self.gerar_app_circulo_buffer(self.dict_poligono_tipo[FID]["layer"], diretorio_app)
        # print self.dict_poligono_tipo

if __name__ == '__main__':
    DefinirApp().iniciar_codigo()

tempo =  time.clock() - tempo
print tempo, "tempo"