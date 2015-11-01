# -*- coding: utf-8 -*-
import arcpy
from tipo_poligono import TipoPoligono
from largura_rios.definir_linhas import DefinirLinhas
from delimitar_app.app_rio import AppRio
from os import path, mkdir
from sys import argv
from shutil import rmtree
arcpy.env.outputMFlag = "Disabled"
arcpy.env.outputZFlag = "Disabled"
class DefinirApp:
    def __init__(self, maPath = None, drePath = None, ptPath = None, aprtPath = None, saiPath = None):
        diretorio = path.dirname(path.dirname(path.dirname(argv[0])))
        self.diretorio_entrada = diretorio + "\ENTRADA"
        if saiPath:
            self.diretorio_saida = saiPath
        else:
            self.diretorio_saida = diretorio + "\SAIDA"
        self.__maPath = maPath
        self.__drePath = drePath
        self.__ptPath = drePath
        self.dict_poligono_descricao = {}
        self.dict_app_poligonos  = None
        self.projecao_geo = 'GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",' \
                                       '6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],' \
                                       'UNIT["Degree",0.0174532925199433]]'
        self.projecao_plana = 'PROJCS["SIRGAS_2000_Lambert_Conformal_Conic_PA",GEOGCS["GCS_SIRGAS_2000",' \
                                    'DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],' \
                                    'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],' \
                                    'PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",0.0],' \
                                    'PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-52.5],' \
                                    'PARAMETER["Standard_Parallel_1",-0.5],' \
                                    'PARAMETER["Standard_Parallel_2",-6.833333333333333],PARAMETER' \
                                    '["Latitude_Of_Origin",-3.666667],UNIT["Meter",1.0]]'

    def gerar_app(self, fid, poligono_ma, tipo):
        "gerar app de acordo com o tipo de dado"
        if tipo == "MASSA_DAGUA":
            tipo_ma = None
            obj_tipo_poligono = TipoPoligono()
            obj_tipo_poligono.poligono_ma = poligono_ma
            obj_tipo_poligono.diretorio_saida = self.diretorio_saida
            obj_tipo_poligono.projecao_plana = self.projecao_plana
            obj_tipo_poligono.projecao_geo = self.projecao_geo
            # tipo_ma = obj_tipo_poligono.iniciar_codigo()
            del obj_tipo_poligono

            obj_linhas = DefinirLinhas()
            obj_linhas.fid = fid
            obj_linhas.poligono_ma = poligono_ma
            obj_linhas.diretorio_saida = self.diretorio_saida
            obj_linhas.projecao_plana = self.projecao_plana
            obj_linhas.projecao_geo = self.projecao_geo
            self.dict_poligono_descricao = obj_linhas.iniciar()
            del obj_linhas

            obj_app_rio = AppRio()
            obj_app_rio.diretorio_saida =self.diretorio_saida
            obj_app_rio.dict_poligono_descricao = self.dict_poligono_descricao
            obj_app_rio.projecao_plana = self.projecao_plana
            obj_app_rio.projecao_geo = self.projecao_geo
            return obj_app_rio.iniciar_codigo()

    def salvar_dados(self, dict_app_poligonos, fid):
        diretorio_app = self.diretorio_saida + "\APP\APP_" + str(fid)
        diretorio_linhas = self.diretorio_saida + "/LINHAS/LINHAS_LARGURA_FID_" + str(fid) + ".shp"
        diretorio_li_app = self.diretorio_saida + "/LINHAS/LINHAS_APP_FID_" + str(fid) + ".shp"

        arcpy.CreateFeatureclass_management(self.diretorio_saida + "/APP", "APP_" + str(fid)  + ".shp", "POLYGON", "", "", "",
                              self.projecao_geo)
        cursor_insert = arcpy.da.InsertCursor(diretorio_app + ".shp", ['Id', 'SHAPE@'])

        for id_app in dict_app_poligonos:
            cursor_insert.insertRow((id_app, dict_app_poligonos[id_app]["poligono"]))
            # arcpy.CopyFeatures_management(dict_app_poligonos[id]["poligono"],self.diretorio_saida + "\APP\APP_" + str(fid) + "_" + str(id))
        del cursor_insert

        arcpy.CreateFeatureclass_management(self.diretorio_saida + "/LINHAS", "LINHAS_LARGURA_FID_" + str(fid) + ".shp", "POLYLINE", "", "", "",
                              self.projecao_geo)
        arcpy.AddField_management(diretorio_linhas,"largura_m","Double")
        cursor_insert_li = arcpy.da.InsertCursor(diretorio_linhas, ['Id', 'SHAPE@', "largura_m"])

        arcpy.CreateFeatureclass_management(self.diretorio_saida + "/LINHAS", "LINHAS_APP_FID_" + str(fid) + ".shp", "POLYLINE", "", "", "",
                              self.projecao_geo)
        arcpy.AddField_management(diretorio_li_app,"largura_m","Double")
        cursor_insert_app = arcpy.da.InsertCursor(diretorio_li_app, ['Id', 'SHAPE@', "largura_m"])

        for id_linha in  self.dict_poligono_descricao["metadados"]["linhas"]:
            linha_largura = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["linha_largura"]
            if linha_largura:
                comprimento = linha_largura.projectAs(self.projecao_plana).length
                cursor_insert_li.insertRow((id_linha, linha_largura, comprimento))

            linha_app = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["linha_app"]
            if linha_app:
                comprimento = linha_app.projectAs(self.projecao_plana).length
                cursor_insert_app.insertRow((id_linha, linha_app, comprimento))
            id_linha += 1

        del cursor_insert_li
        del cursor_insert_app


    def main(self):
        if self.__maPath:
            dir_ma_shp = self.__maPath
        else:
            dir_ma_shp = self.diretorio_entrada + "\MASSA_DAGUA_2.shp"
        if path.exists(self.diretorio_saida):
            rmtree(self.diretorio_saida)
        mkdir(self.diretorio_saida)
        mkdir(self.diretorio_saida + "/LINHAS")
        mkdir(self.diretorio_saida + "/RESIDUOS")
        mkdir(self.diretorio_saida + "/APP")

        with arcpy.da.SearchCursor(dir_ma_shp, ["OID@", "SHAPE@"], "FID = 215") as cursor:
            for row in cursor:
                print "fid: ", row[0]
                dict_app_poligonos, self.dict_poligono_descricao = self.gerar_app(row[0], row[1].projectAs(self.projecao_geo), "MASSA_DAGUA")
                self.salvar_dados(dict_app_poligonos, row[0])
        del cursor

if __name__ == '__main__':
    DefinirApp().main()