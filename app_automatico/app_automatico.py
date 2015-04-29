# -*- coding: utf-8 -*-
import arcpy
from largura_rios.definir_linhas import DefinirLinhas
from delimitar_app.app_rio import AppRio
from os import path, mkdir
from sys import argv
from shutil import rmtree
arcpy.env.outputMFlag = "Disabled"
arcpy.env.outputZFlag = "Disabled"
class DefinirApp():
    def __init__(self):
        diretorio = path.dirname(path.dirname(path.dirname(argv[0])))
        self.diretorio_entrada = diretorio + "\ENTRADA\MASSA_DAGUA.shp"
        self.diretorio_saida = diretorio + "\SAIDA"
        self.dict_poligono_descricao = None
        self.spatial_geo_sirgas_2000 = 'GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",' \
                                       '6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],' \
                                       'UNIT["Degree",0.0174532925199433]]'
        self.spatial_proj_lambert = 'PROJCS["SIRGAS_2000_Lambert_Conformal_Conic_PA",GEOGCS["GCS_SIRGAS_2000",' \
                                    'DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],' \
                                    'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],' \
                                    'PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",0.0],' \
                                    'PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-52.5],' \
                                    'PARAMETER["Standard_Parallel_1",-0.5],' \
                                    'PARAMETER["Standard_Parallel_2",-6.833333333333333],PARAMETER' \
                                    '["Latitude_Of_Origin",-3.666667],UNIT["Meter",1.0]]'

    def gerar_app(self, id, poligono_ma, tipo):
        "gerar app de acordo com o tipo de dado"
        if tipo == "MASSA_DAGUA":
            obj_linhas = DefinirLinhas()
            obj_linhas.poligono_ma = poligono_ma
            obj_linhas.diretorio_saida = self.diretorio_saida
            obj_linhas.projecao_plana = self.spatial_proj_lambert
            obj_linhas.projecao_geo = self.spatial_geo_sirgas_2000
            self.dict_poligono_descricao = obj_linhas.iniciar()
            del obj_linhas

            obj_app_rio = AppRio()
            obj_app_rio.diretorio_saida =self.diretorio_saida
            obj_app_rio.dict_poligono_descricao = self.dict_poligono_descricao
            obj_app_rio.projecao_plana = self.spatial_proj_lambert
            obj_app_rio.projecao_geo = self.spatial_geo_sirgas_2000
            obj_app_rio.iniciar_codigo()

    def salvar_dados(self):
        pass

    def main(self):
        if path.exists(self.diretorio_saida):
            rmtree(self.diretorio_saida)
        mkdir(self.diretorio_saida)
        mkdir(self.diretorio_saida + "/LINHAS")
        mkdir(self.diretorio_saida + "/RESIDUOS")
        mkdir(self.diretorio_saida + "/APP")
        with arcpy.da.SearchCursor(self.diretorio_entrada + "\MASSA_DAGUA.shp", ["OID@", "SHAPE@"], "FID = 19") as cursor:
            for row in cursor:
                self.gerar_app(row[0], row[1].projectAs(self.spatial_geo_sirgas_2000), "MASSA_DAGUA")
        del cursor
if __name__ == '__main__':
    DefinirApp().main()