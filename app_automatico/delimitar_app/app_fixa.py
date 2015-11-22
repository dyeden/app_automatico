# -*- coding: utf-8 -*-
import arcpy
import shapely.geometry
import shapely.ops
from shapely.wkt import loads
import shapely.prepared
import shapely.prepared
import itertools

class AppFixa:
    def __init__(self, diretorio=None):
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

    def pontas_extremidades(self, linhas):
        endpts = [(shapely.geometry.Point(list(line.coords)[0]), shapely.geometry.Point(list(line.coords)[-1])) for line  in linhas]
        endpts = [pt for sublist in endpts  for pt in sublist]
        inters = []
        for line1,line2 in  itertools.combinations(linhas, 2):
          if  line1.intersects(line2):
            inter = line1.intersection(line2)
            if "Point" == inter.type:
                inters.append(inter)

        point_todos = shapely.ops.unary_union(endpts)
        point_inter = shapely.ops.unary_union(inters)
        pontos_pontas = point_todos.difference(point_inter)

        PontosCorretos = []
        for ponto in list(pontos_pontas):
            buffer_ponto = ponto.buffer(0.00005)
            prepared_ponto= shapely.prepared.prep(buffer_ponto)
            hits = filter(prepared_ponto.intersects, linhas)
            if len(hits) == 1:
                PontosCorretos.append(ponto)
        pontos_pontas = shapely.ops.unary_union(PontosCorretos)

        return pontos_pontas

    def ler_linhas(self, dir_linhas_shp):
        lista_linhas = []
        for row in arcpy.da.SearchCursor(dir_linhas_shp, ["OID@", "SHAPE@"]):
            linha = loads(row[1].WKT)
            lista_linhas.append(linha)
        linhas = shapely.ops.unary_union(lista_linhas)
        linhas = shapely.ops.linemerge(linhas)
        return linhas

    def larguraAPP(self, area_ma):
        area_hectares = area_ma/10000
        if area_hectares < 5:
            largura_app = 0
        elif 5 <= area_hectares < 20:
            largura_app = 50
        else:
            largura_app = 100
        return largura_app


    def geraApp_lagosLagoas(self, dir_ma, dir_dre, dir_saida):
        arcpy.MakeFeatureLayer_management(dir_ma,"lyr_ma")
        layer_ma = "lyr_ma"
        arcpy.MakeFeatureLayer_management(dir_dre,"lyr_dre")
        layer_dre =  "lyr_dre"
        arcpy.SelectLayerByLocation_management(layer_ma, "INTERSECT", layer_dre, "", "NEW_SELECTION")
        arcpy.SelectLayerByAttribute_management(layer_ma, "SWITCH_SELECTION")

        arcpy.CreateFeatureclass_management(dir_saida, "APP_LAGOSLAGOAS.shp", "POLYGON", "", "", "",
                              self.projecao_geo)
        cursor_insert = arcpy.da.InsertCursor(dir_saida + "/APP_LAGOSLAGOAS.shp", ['Id', 'SHAPE@'])


        for row in arcpy.da.SearchCursor(layer_ma, ["OID@", "SHAPE@"]):
            fid = int(row[0])
            poly_ma = row[1]
            area_ma = poly_ma.projectAs(self.projecao_plana).area
            largura_app = self.larguraAPP(area_ma)
            poly_app = poly_ma.projectAs(self.projecao_plana).buffer(largura_app).projectAs(self.projecao_geo)
            cursor_insert.insertRow((fid, poly_app))

        del cursor_insert


    def main(self):
        dir_dre_shp = "C:\Users\DYEDEN\PycharmProjects\APP_AUTOMATICO\ENTRADA\DRENAGEM_1507953.shp"
        dir_ma_shp = "C:\Users\DYEDEN\PycharmProjects\APP_AUTOMATICO\ENTRADA\MASSA_DAGUA_1507953.shp"
        dir_saida =  "C:\Users\DYEDEN\PycharmProjects\APP_AUTOMATICO\SAIDA\APP_FIXA"
        linhas_dre = self.ler_linhas(dir_dre_shp)
        pontos_nasc = self.pontas_extremidades(linhas_dre)
        # self.geraApp_lagosLagoas(dir_ma_shp, dir_dre_shp, dir_saida)

        pass

if __name__ == '__main__':
    appfixa = AppFixa()
    appfixa.main()