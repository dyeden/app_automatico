__author__ = 'DYEDEN'
__author__ = 'DYEDEN'
# -*- coding: utf-8 -*-
import time
tempo = time.clock()

from arcpy import Array , SelectLayerByLocation_management, MakeFeatureLayer_management, da, SelectLayerByAttribute_management, CopyFeatures_management, AddField_management, \
        Point, Polygon, Describe, Extent, SpatialReference, CreateFeatureclass_management, Exists, Dissolve_management, Delete_management, env, ListFields
from os import path, mkdir
from shutil import rmtree
from sys import argv
env.outputMFlag = "Disabled"
env.outputZFlag = "Disabled"
class definir_app():
    def __init__(self):
        diretorio = path.dirname(argv[0])
        self.diretorio_saida = diretorio + "/SAIDA"
        self.diretorio_entrada = diretorio + "/ENTRADA"
        self.spatial_geo_sirgas_2000 = 'GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
        self.spatial_proj_lambert = 'PROJCS["SIRGAS_2000_Lambert_Conformal_Conic_PA",GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-52.5],PARAMETER["Standard_Parallel_1",-0.5],PARAMETER["Standard_Parallel_2",-6.833333333333333],PARAMETER["Latitude_Of_Origin",-3.666667],UNIT["Meter",1.0]]'

    def municipio_grid(self, id_municipio, layer_municipios, grid_colunas, grid_linhas):
        dict_municipio_grid = {}
        CreateFeatureclass_management(self.diretorio_saida, "municipio_grid.shp", "POLYGON", "", "", "", self.spatial_geo_sirgas_2000)
        cursor_insert_mun = da.InsertCursor(self.diretorio_saida + "/municipio_grid.shp", ['Id','SHAPE@'])
        with da.SearchCursor(layer_municipios,["SHAPE@"],"GEOCODIG_M = " + str(id_municipio)) as cursor:
            for row in cursor:
                poligono_municipio_geo = row[0].projectAs(SpatialReference(4326))
                xmin = poligono_municipio_geo.extent.XMin
                xmax = poligono_municipio_geo.extent.XMax
                ymin = poligono_municipio_geo.extent.YMin
                ymax = poligono_municipio_geo.extent.YMax
                yinter = (ymax - ymin)/grid_linhas
                xinter = (xmax - xmin)/grid_colunas
                id_grid = 0
                for y in range(grid_linhas + 1)[1:]:
                    ycoord_min = ymin + (y-1)*yinter
                    ycoord_max = ymin + y*yinter
                    for x in range(grid_colunas + 1)[1:]:
                        id_grid += 1
                        xcoord_min = xmin + (x-1)*xinter
                        xcoord_max = xmin + x*xinter
                        extent_grid = Extent(xcoord_min, ycoord_min, xcoord_max, ycoord_max)
                        poly_grid = poligono_municipio_geo.clip(extent_grid)
                        # if poly_grid.disjoint(poligono_municipio_geo):
                        #     pass
                        # else:
                        dict_municipio_grid[id_grid] = [extent_grid,poly_grid]
                        cursor_insert_mun.insertRow((id_grid,poly_grid))

        del cursor
        del cursor_insert_mun
        return dict_municipio_grid
    def largura_rios(self,layer_dre, layer_ma):
        fields_ma = [f.name for f  in ListFields(layer_ma)]
        if "largura_m" in fields_ma:
            pass
        else:
            AddField_management(layer_ma, "largura_m", "FLOAT")
        with da.UpdateCursor(layer_ma,["OID@","SHAPE@", "ma_tipo", "largura_m"]) as cursor:
            for row in cursor:
                if row[2] == "lago":
                    pass
                else:
                    poly_geo = row[1].projectAs(self.spatial_geo_sirgas_2000)

        del cursor


    def municipio_app(self, dict_mun_grid, layer_dre, layer_pt, layer_ma):
        CreateFeatureclass_management(self.diretorio_saida, "APP_SISTEMA.shp", "POLYGON", "", "", "", self.spatial_geo_sirgas_2000)
        cursor_insert_app = da.InsertCursor(self.diretorio_saida + "/APP_SISTEMA.shp", ['Id','SHAPE@'])
        CreateFeatureclass_management(self.diretorio_saida, "drenagem_grid.shp", "POLYGON", "", "", "", self.spatial_geo_sirgas_2000)
        cursor_insert_dre = da.InsertCursor(self.diretorio_saida + "/drenagem_grid.shp", ['Id','SHAPE@'])
        if layer_pt:
            CreateFeatureclass_management(self.diretorio_saida, "ponto_de_drenagem_grid.shp", "POLYGON", "", "", "", self.spatial_geo_sirgas_2000)
            cursor_insert_pt = da.InsertCursor(self.diretorio_saida + "/ponto_de_drenagem_grid.shp", ['Id','SHAPE@'])
        CreateFeatureclass_management(self.diretorio_saida, "massa_da_agua_grid.shp", "POLYGON", "", "", "", self.spatial_geo_sirgas_2000)
        cursor_insert_ma_buff = da.InsertCursor(self.diretorio_saida + "/massa_da_agua_grid.shp", ['Id','SHAPE@'])

        CreateFeatureclass_management(self.diretorio_saida, "massa_da_agua_ori_grid.shp", "POLYGON", "", "", "", self.spatial_geo_sirgas_2000)
        cursor_insert_ma = da.InsertCursor(self.diretorio_saida + "/massa_da_agua_ori_grid.shp", ['Id','SHAPE@'])

        dict_muni_grid = {}

        fields_ma = [f.name for f  in ListFields(layer_ma)]
        if "ma_tipo" in fields_ma:
            pass
        else:
            AddField_management(layer_ma, "ma_tipo", "TEXT")
            SelectLayerByLocation_management(layer_ma, 'INTERSECT', layer_dre,"","NEW_SELECTION")
            SelectLayerByLocation_management(layer_ma, "", "","","SWITCH_SELECTION")
            desc = Describe(layer_ma)
            if len(desc.FIDSet) > 0:
                with da.UpdateCursor(layer_ma,["OID@","SHAPE@","ma_tipo"]) as cursor:
                    for row in cursor:
                        row[2] = "lago"
                        cursor.updateRow(row)
                del cursor
            SelectLayerByAttribute_management(layer_ma, "CLEAR_SELECTION")


        for id_grid in dict_mun_grid:
            dict_muni_grid[id_grid] = {None:None}
            extent_grid = dict_mun_grid[id_grid][0]
            poly_grid = dict_mun_grid[id_grid][1]
            SelectLayerByLocation_management(layer_dre, 'WITHIN_A_DISTANCE', poly_grid ,"31 Meters","NEW_SELECTION")
            desc = Describe(layer_dre)
            if len(desc.FIDSet) > 0:
                with da.SearchCursor(layer_dre,["OID@","SHAPE@"]) as cursor:
                    for row in cursor:
                        buffer_geo = row[1].projectAs(self.spatial_proj_lambert).buffer(30).projectAs(self.spatial_geo_sirgas_2000)
                        if poly_grid.disjoint(buffer_geo):
                            pass
                        else:
                            cursor_insert_dre.insertRow((id_grid,buffer_geo.clip(extent_grid)))
                del cursor

            if layer_pt:
                SelectLayerByLocation_management(layer_pt, 'WITHIN_A_DISTANCE', poly_grid ,"51 Meters","NEW_SELECTION")
                desc = Describe(layer_pt)
                if len(desc.FIDSet) > 0:
                    with da.SearchCursor(layer_pt,["OID@","SHAPE@"]) as cursor:
                        for row in cursor:
                            buffer_geo = row[1].projectAs(self.spatial_proj_lambert).buffer(50).projectAs(self.spatial_geo_sirgas_2000)

                            if poly_grid.disjoint(buffer_geo):
                                pass
                            else:
                                cursor_insert_pt.insertRow((id_grid,buffer_geo.clip(extent_grid)))

                    del cursor

            SelectLayerByLocation_management(layer_ma, 'WITHIN_A_DISTANCE', poly_grid ,"101 Meters","NEW_SELECTION")
            desc = Describe(layer_ma)
            if len(desc.FIDSet) > 0:
                with da.SearchCursor(layer_ma,["OID@","SHAPE@", "ma_tipo"]) as cursor:
                    for row in cursor:
                        #CopyFeatures_management(row[1], self.diretorio_saida + "/massa_dagua_feature" + str(row[0]) + ".shp")
                        poly_geo = row[1].projectAs(self.spatial_geo_sirgas_2000)
                        if row[2] == "lago":
                            if  row[1].projectAs(self.spatial_proj_lambert).area <= 200000:
                                buffer_geo = row[1].projectAs(self.spatial_proj_lambert).buffer(50).projectAs(self.spatial_geo_sirgas_2000)
                            else:
                                buffer_geo = row[1].projectAs(self.spatial_proj_lambert).buffer(100).projectAs(self.spatial_geo_sirgas_2000)
                        else:
                            buffer_geo = row[1].projectAs(self.spatial_proj_lambert).buffer(50).projectAs(self.spatial_geo_sirgas_2000)
                        if poly_grid.disjoint(buffer_geo):
                            pass
                        else:
                            cursor_insert_ma_buff.insertRow((id_grid,buffer_geo.clip(extent_grid)))
                            if poly_grid.disjoint(poly_geo):
                                pass
                            else:
                                cursor_insert_ma.insertRow((id_grid,poly_geo.clip(extent_grid)))
                del cursor
        if layer_pt:
            Dissolve_management(self.diretorio_saida + "/ponto_de_drenagem_grid.shp", self.diretorio_saida + "/ponto_de_drenagem_dissolved.shp", ["Id"])
        Dissolve_management(self.diretorio_saida + "/drenagem_grid.shp", self.diretorio_saida + "/drenagem_dissolved.shp", ["Id"])
        Dissolve_management(self.diretorio_saida + "/massa_da_agua_grid.shp", self.diretorio_saida + "/massa_da_agua_dissolved.shp", ["Id"])
        Dissolve_management(self.diretorio_saida + "/massa_da_agua_ori_grid.shp", self.diretorio_saida + "/massa_da_agua_dissolved_ori.shp", ["Id"])


        del cursor_insert_ma
        del cursor_insert_ma_buff
        del cursor_insert_dre
        if layer_pt:
            del cursor_insert_pt


        with da.SearchCursor(self.diretorio_saida + "/drenagem_dissolved.shp",["Id","SHAPE@"]) as cursor:
            for row_dre in cursor:
                dict_muni_grid[row_dre[0]]["dre"] =  row_dre[1]
        del cursor

        if layer_pt:
            with da.SearchCursor(self.diretorio_saida + "/ponto_de_drenagem_dissolved.shp",["Id","SHAPE@"]) as cursor:
                for row_pt in cursor:
                    dict_muni_grid[row_pt[0]]["pt_dre"] =  row_pt[1]
            del cursor
        with da.SearchCursor(self.diretorio_saida + "/massa_da_agua_dissolved_ori.shp",["Id","SHAPE@"]) as cursor:
            for row_ma_ori in cursor:
                dict_muni_grid[row_ma_ori[0]]["ma_ori"] =  row_ma_ori[1]
        del cursor
        with da.SearchCursor(self.diretorio_saida + "/massa_da_agua_dissolved.shp",["Id","SHAPE@"]) as cursor:
            for row_ma in cursor:
                dict_muni_grid[row_ma[0]]["ma"] =  row_ma[1]
        del cursor
        for grid_number in dict_muni_grid:
            dict_cell = dict_muni_grid[grid_number]
            poligono_app = None
            if "ma"  in dict_cell:
                if "ma_ori"  in dict_cell:
                    ma_ma_ori = dict_cell["ma"].difference(dict_cell["ma_ori"])
                    if "pt_dre" not in dict_cell and "dre" not in dict_cell:
                        poligono_app = ma_ma_ori
                    elif "pt_dre" not in dict_cell:
                        dre_ma_ori = dict_cell["dre"].difference(dict_cell["ma_ori"])
                        poligono_app = dre_ma_ori.union(ma_ma_ori)
                    elif "dre" not in dict_cell:
                        dre_pt_dre_ma_ori = dict_cell["pt_dre"].difference(dict_cell["ma_ori"])
                        poligono_app = dre_pt_dre_ma_ori.union(ma_ma_ori)
                    else:
                        dre_ma_ori = dict_cell["dre"].difference(dict_cell["ma_ori"])
                        dre_pt_dre_ma_ori = dict_cell["pt_dre"].difference(dict_cell["ma_ori"])
                        poligono_app = dre_pt_dre_ma_ori.union(dre_ma_ori.union(ma_ma_ori))
                else:

                    if "pt_dre" not in dict_cell and "dre" not in dict_cell:
                        poligono_app = dict_cell["ma"]
                    elif "pt_dre" not in dict_cell:
                        poligono_app = dict_cell["ma"].union(dict_cell["dre"])
                    elif "dre" not in dict_cell:
                        poligono_app = dict_cell["pt_dre"].union(dict_cell["ma"])
                    else:
                        poligono_app = dict_cell["pt_dre"].union(dict_cell["ma"].union(dict_cell["dre"]))


            else:
                if "pt_dre" not in dict_cell and "dre" not in dict_cell:
                    pass
                elif "pt_dre" not in dict_cell:
                    poligono_app = dict_cell["dre"]
                elif "dre" not in dict_cell:
                    poligono_app = dict_cell["pt_dre"]
                else:
                    poligono_app = dict_cell["pt_dre"].union(dict_cell["dre"])
            if poligono_app:
                cursor_insert_app.insertRow((grid_number,poligono_app))

        del cursor_insert_app

        Delete_management(self.diretorio_saida + "/drenagem_dissolved.shp")
        Delete_management(self.diretorio_saida + "/drenagem_grid.shp")
        Delete_management(self.diretorio_saida + "/massa_da_agua_dissolved_ori.shp")
        Delete_management(self.diretorio_saida + "/massa_da_agua_dissolved.shp")
        Delete_management(self.diretorio_saida + "/massa_da_agua_grid.shp")
        Delete_management(self.diretorio_saida + "/massa_da_agua_ori_grid.shp")
        if layer_pt:
            Delete_management(self.diretorio_saida + "/ponto_de_drenagem_dissolved.shp")
            Delete_management(self.diretorio_saida + "/ponto_de_drenagem_grid.shp")
    def iniciar_layer(self, id_municipio):
        if path.exists(self.diretorio_saida):
            rmtree(self.diretorio_saida)
        mkdir(self.diretorio_saida)
        MakeFeatureLayer_management(self.diretorio_entrada + "/MUNICIPIOS_AMZ.shp", "MUNICIPIOS_AMZ")
        dict_municipio_grid = self.municipio_grid(id_municipio,"MUNICIPIOS_AMZ",grid_colunas=20,grid_linhas=20)
        MakeFeatureLayer_management(self.diretorio_entrada + "/MASSA_DAGUA.shp", "MASSA_DAGUA")
        MakeFeatureLayer_management(self.diretorio_entrada + "/DRENAGEM.shp", "DRENAGEM")
        MakeFeatureLayer_management(self.diretorio_entrada + "/PONTO_DE_DRENAGEM.shp", "PONTO_DE_DRENAGEM")
        self.municipio_app(dict_municipio_grid,"DRENAGEM","PONTO_DE_DRENAGEM","MASSA_DAGUA")

if __name__ == '__main__':
    definir_app().iniciar_layer(1504703)
tempo =  time.clock() - tempo

print tempo