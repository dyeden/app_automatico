__author__ = 'DYEDEN'
import time
tempo = time.clock()

from arcpy import Array , SelectLayerByLocation_management, MakeFeatureLayer_management, da, SelectLayerByAttribute_management, CopyFeatures_management, AddField_management, \
        Point, Polyline, Polygon, Describe, Extent, SpatialReference, CreateFeatureclass_management, Exists, Dissolve_management, Delete_management, env, ListFields
from math import sqrt
from os import path, mkdir
from shutil import rmtree
from sys import argv
env.outputMFlag = "Disabled"
env.outputZFlag = "Disabled"

class DefinirLargura():
    def __init__(self):
        diretorio = path.dirname(path.dirname(argv[0]))
        self.diretorio_saida = diretorio + "/SAIDA"
        self.diretorio_entrada = diretorio + "/ENTRADA"
        self.spatial_geo_sirgas_2000 = 'GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
        self.spatial_proj_lambert = 'PROJCS["SIRGAS_2000_Lambert_Conformal_Conic_PA",GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-52.5],PARAMETER["Standard_Parallel_1",-0.5],PARAMETER["Standard_Parallel_2",-6.833333333333333],PARAMETER["Latitude_Of_Origin",-3.666667],UNIT["Meter",1.0]]'
        self.raio = 50
        self.primeiro_teste_circ = True
        self.raio_pr = self.raio
        self.compri_linha_largura_x1 = self.raio_pr*0.75
        self.compri_linha_largura_x2 = self.raio_pr*0.85
        self.dict_partes = {}

    def funcao_multipart(self, linha, ponto):
        list_partes = []
        if linha.isMultipart:
            for n in range(linha.partCount):
                parte = linha.getPart(n)
                linha_parte = Polyline(parte,self.spatial_geo_sirgas_2000)
                list_partes.append(parte)
                if linha_parte.disjoint(ponto):
                    self.dict_partes["parte" + str(n)] = {"linha_array":parte, "cruza_ponto":False, "linha_geometria":linha_parte}
                else:
                    self.dict_partes["parte" + str(n)] = {"linha_array":parte, "cruza_ponto":True, "linha_geometria":linha_parte}
        print self.dict_partes
        return list_partes
    def validar_circulo(self,tipo_circulo, dict_descricao):
        teste_validacao = False
        if tipo_circulo == "meio":
            linha_largura = dict_descricao["linha_largura"]
            linha_circulo = dict_descricao["linha_circulo"]
            compri_linha_largura = linha_largura.projectAs(self.spatial_proj_lambert).length
            compri_linha_circulo = linha_circulo.projectAs(self.spatial_proj_lambert).length
            porc_raio_largura = (compri_linha_largura/compri_linha_circulo)*100
            print compri_linha_largura, "compri_linha_largura", compri_linha_circulo, "compri_linha_circulo", porc_raio_largura, "porc_raio_largura"
            if 75 < porc_raio_largura < 85:
                teste_validacao = True
            else:
                if porc_raio_largura <= 80:
                    self.compri_linha_raio_x2 = self.raio
                else:
                    self.compri_linha_raio_x1 = self.raio
                print self.compri_linha_raio_x1, "self.compri_linha_raio_x1", self.compri_linha_raio_x2, "self.compri_linha_raio_x2"
                self.raio = (self.compri_linha_raio_x1 + self.compri_linha_raio_x2)/2
            print teste_validacao
        return teste_validacao



    def ponto_meio(self, list_partes, ponto):
        self.buffer_poligono_borda
        self.x_b
        self.y_b
        self.ptc_x = None
        self.ptc_y = None
        print "ponto_meio"
        for parte in list_partes:
            parte_linha = Polyline(parte, self.spatial_geo_sirgas_2000)
            if parte_linha.disjoint(ponto):
                pontos_inte_linha_poligono = self.buffer_poligono_borda.intersect(parte_linha,1)
                self.pt1_x = pontos_inte_linha_poligono.getPart(0).X
                self.pt1_y = pontos_inte_linha_poligono.getPart(0).Y
                self.pt2_x = pontos_inte_linha_poligono.getPart(1).X
                self.pt2_y = pontos_inte_linha_poligono.getPart(1).Y
                self.ptc_x, self.ptc_y, self.ptc_x_inv, self.ptc_y_inv = PtCircBorda(self.x_b,self.y_b,self.pt1_x,self.pt1_y,self.pt2_x,self.pt2_y).ponto_circ_borda()
        return self.ptc_x, self.ptc_y


    def circulo_de_borda_filtro(self, linha_buffer_inter, ponto):
        list_partes = self.funcao_multipart(linha_buffer_inter, ponto)

        tipo_circulo = None
        dict_circulo = {}
        if list_partes:
            if list_partes.__len__() == 2:
                ptc_x, ptc_y = self.ponto_meio(list_partes,ponto)
                tipo_circulo = "meio"
                dict_circulo = {"ptc_x": ptc_x, "ptc_y": ptc_y}
        else:
            contador_raio = 0
            while contador_raio < 3:
                self.raio += 10
                buffer_ponto_borda = ponto.projectAs(self.spatial_proj_lambert).buffer(self.raio).projectAs(self.spatial_geo_sirgas_2000)
                contador_raio += 1
            tipo_circulo = "extremidade"
            # if contador_raio == 3:
        return tipo_circulo, dict_circulo


    def ponto_buffer(self,ponto):
        self.x_b = ponto.getPart().X
        self.y_b = ponto.getPart().Y
        teste_validacao = False
        dict_descricao = {}
        loops_validacao = 0
        while teste_validacao == False:
            self.buffer_poligono_borda = ponto.projectAs(self.spatial_proj_lambert).buffer(self.raio).projectAs(self.spatial_geo_sirgas_2000)
            dict_descricao = {}
            linha_buffer_inter = self.buffer_poligono_borda.intersect(self.linha_ma_sirgas,2)
            tipo_circulo, dict_circulo = self.circulo_de_borda_filtro(linha_buffer_inter, ponto)
            if tipo_circulo == "meio":
                dict_descricao["tipo"] = "meio"
                dict_descricao["ptc_x"] = dict_circulo["ptc_x"]
                dict_descricao["ptc_y"] = dict_circulo["ptc_y"]
                linha_largura, linha_circulo = self.linha_de_largura(dict_descricao, ponto)
                dict_descricao["linha_largura"] = linha_largura
                dict_descricao["linha_circulo"] = linha_circulo
            teste_validacao = self.validar_circulo(tipo_circulo, dict_descricao)
            CopyFeatures_management(linha_largura, self.diretorio_saida + "/linha_largura" + str(loops_validacao) + ".shp")
            CopyFeatures_management(linha_circulo, self.diretorio_saida + "/linha_circulo" + str(loops_validacao) + ".shp")
            CopyFeatures_management(self.buffer_poligono_borda, self.diretorio_saida + "/buffer_poligono_borda" + str(loops_validacao) + ".shp")
            loops_validacao += 1
        return dict_descricao

    def linha_de_largura(self, dict_descricao, ponto):
        if dict_descricao["tipo"] == "meio":
            linha_nao_intersecta_ponto = None
            point_circ = Point()
            point_circ.X = dict_descricao["ptc_x"]
            point_circ.Y = dict_descricao["ptc_y"]
            array = Array([point_circ, ponto.getPart(0)])
            linha_circulo = Polyline(array,self.spatial_geo_sirgas_2000)
            for parte_linha in self.dict_partes:
                if self.dict_partes[parte_linha]["cruza_ponto"] == False:
                    linha_nao_intersecta_ponto = self.dict_partes[parte_linha]["linha_geometria"]


            if linha_circulo.disjoint(linha_nao_intersecta_ponto):
                array.removeAll()
                point_circ = Point()
                point_circ.X = self.ptc_x_inv
                point_circ.Y = self.ptc_y_inv
                array = Array([point_circ, ponto.getPart(0)])
                linha_circulo = Polyline(array,self.spatial_geo_sirgas_2000)
                linha_largura = linha_circulo.intersect(self.poligono_ma_geo, 2)
                array.removeAll()
            else:
                linha_largura = linha_circulo.intersect(self.poligono_ma_geo, 2)
                array.removeAll()

            return linha_largura, linha_circulo


    def pontos_aolongo_linha(self):
        self.linha_ma_sirgas = self.poligono_ma_geo.boundary()
        linha_lambert = self.linha_ma_sirgas.projectAs(self.spatial_proj_lambert)
        compri_total = linha_lambert.length
        compri_linha_largura = self.raio*0.8
        distancia_pt0 = 0
        list_pts = []
        while distancia_pt0 < compri_total:
            bool_extremid_poligono = False
            compri_ok = False
            self.compri_linha_raio_x1 = compri_linha_largura/1.1
            self.compri_linha_raio_x2 = compri_linha_largura/0.5
            while compri_ok == False:
                self.distancia_pt0 = distancia_pt0
                ponto = linha_lambert.positionAlongLine(distancia_pt0).projectAs(self.spatial_geo_sirgas_2000)
                self.ponto_5m = ponto.projectAs(self.spatial_proj_lambert).buffer(5).projectAs(self.spatial_geo_sirgas_2000)
                dict_descricao = self.ponto_buffer(ponto)
                CopyFeatures_management(dict_descricao["linha_largura"], self.diretorio_saida + "/linha_largura_pt" + str(distancia_pt0) + ".shp")

                print dict_descricao
                break
            break

    def selecionar_poligono(self, layer_massa_dagua):
        with da.SearchCursor(layer_massa_dagua,["OID@","SHAPE@"],"FID = 35") as cursor:
            for row in cursor:
                self.poligono_ma_geo = row[1].projectAs(SpatialReference(4674))
                self.pontos_aolongo_linha()
                print row[0]
        del cursor
    def iniciar_codigo(self):
        if path.exists(self.diretorio_saida):
            rmtree(self.diretorio_saida)
        mkdir(self.diretorio_saida)
        MakeFeatureLayer_management(self.diretorio_entrada + "/MASSA_DAGUA_BRASIL_NOVO.shp", "MASSA_DAGUA")
        self.selecionar_poligono("MASSA_DAGUA")

class PtCircBorda(object):
    def __init__(self, x0, y0, pt1_x, pt1_y, pt2_x, pt2_y):
        self.x0 = x0; self.y0 = y0
        self.pt1_x = pt1_x; self.pt1_y = pt1_y; self.pt2_x = pt2_x; self.pt2_y = pt2_y
    def pt_medio(self):
        ptm_x = (self.pt1_x + self.pt2_x)/2
        ptm_y = (self.pt1_y + self.pt2_y)/2
        return ptm_x, ptm_y

    def distancia_dois_pontos(self, ponto1_x, ponto1_y, ponto2_x, ponto2_y):
        delta_x = (ponto2_x - ponto1_x)
        delta_y = (ponto2_y - ponto1_y)
        distancia = sqrt(delta_x*delta_x + delta_y*delta_y)
        return distancia

    def ponto_circ_borda(self):
        self.x1, self.y1 = self.pt_medio()
        #distancia entre ponto medio
        delt_x1 = self.x1 - self.x0
        delt_y1 = self.y1 - self.y0
        h1 = sqrt(delt_x1*delt_x1 + delt_y1*delt_y1)
        ##################
        raio = self.distancia_dois_pontos(self.x0, self.y0, self.pt1_x, self.pt1_y)
        h2 = raio
        delt_x2 = (delt_x1*h2)/h1
        delt_y2 = (delt_y1*h2)/h1
        self.ptc_x = self.x0 + delt_x2
        self.ptc_y = self.y0 + delt_y2
        self.ptc_x_inv = self.x0 - delt_x2
        self.ptc_y_inv = self.y0 - delt_y2

        return self.ptc_x, self.ptc_y, self.ptc_x_inv, self.ptc_y_inv



if __name__ == '__main__':
    DefinirLargura().iniciar_codigo()
tempo =  time.clock() - tempo

print tempo