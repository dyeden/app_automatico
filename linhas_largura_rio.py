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

class DefinirLargura():

    def __init__(self):
        diretorio = path.dirname(path.dirname(argv[0]))
        self.diretorio_saida = diretorio + "/SAIDA"
        self.diretorio_entrada = diretorio + "/ENTRADA"
        self.spatial_geo_sirgas_2000 = 'GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
        self.spatial_proj_lambert = 'PROJCS["SIRGAS_2000_Lambert_Conformal_Conic_PA",GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-52.5],PARAMETER["Standard_Parallel_1",-0.5],PARAMETER["Standard_Parallel_2",-6.833333333333333],PARAMETER["Latitude_Of_Origin",-3.666667],UNIT["Meter",1.0]]'
        self.raio = 50
        self.primeiro_teste_circ = True
        self.ponto = None
        self.compri_linha_largura_x1 = self.raio*0.75
        self.compri_linha_largura_x2 = self.raio*0.85
        self.dict_partes = {}

    def funcao_multipart(self, linha, ponto):
        list_partes = []
        if linha.isMultipart:
            for n in range(linha.partCount):
                parte = linha.getPart(n)
                linha_parte = Polyline(parte,self.spatial_geo_sirgas_2000)
                linha_parte_lambert = linha_parte.projectAs(self.spatial_proj_lambert)
                if linha_parte_lambert.length > 0.8:
                    list_partes.append(parte)
                    if linha_parte.disjoint(ponto):
                        self.dict_partes["parte" + str(n)] = {"linha_array":parte, "cruza_ponto":False, "linha_geometria":linha_parte}
                    else:
                        self.dict_partes["parte" + str(n)] = {"linha_array":parte, "cruza_ponto":True, "linha_geometria":linha_parte}
        return list_partes

    def validar_circulo(self,tipo_circulo, dict_descricao):
        teste_validacao = False
        if dict_descricao:
            if tipo_circulo == "meio":
                linha_largura = dict_descricao["linha_largura"]
                linha_circulo = dict_descricao["linha_circulo"]
                compri_linha_largura = linha_largura.projectAs(self.spatial_proj_lambert).length
                compri_linha_circulo = linha_circulo.projectAs(self.spatial_proj_lambert).length
                porc_raio_largura = (compri_linha_largura/compri_linha_circulo)*100
                #print compri_linha_largura, "compri_linha_largura", compri_linha_circulo, "compri_linha_circulo", porc_raio_largura, "porc_raio_largura"
                if 75 < porc_raio_largura < 85:
                    teste_validacao = True
                elif self.primeiro_teste_circ:
                    self.primeiro_teste_circ = False
                    self.raio = compri_linha_largura/0.8
                    self.compri_linha_largura_x1 = self.raio*0.75
                    self.compri_linha_largura_x2 = self.raio*0.85
                else:
                    if porc_raio_largura <= 80:
                        self.compri_linha_raio_x2 = self.raio
                    else:
                        self.compri_linha_raio_x1 = self.raio
                    print self.compri_linha_raio_x1, "self.compri_linha_raio_x1", self.compri_linha_raio_x2, "self.compri_linha_raio_x2"
                    self.raio = (self.compri_linha_raio_x1 + self.compri_linha_raio_x2)/2
            elif tipo_circulo == "extremidade":
                angulo_rad = dict_descricao["angulo_rad"]
                if angulo_rad <= (5*pi)/6:
                    teste_validacao = True
        return teste_validacao

    def ponto_meio(self, list_partes, ponto):
        self.ptc_x = None
        self.ptc_y = None
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

    def ponto_extremidade(self):
        pontos_inte_linha_ma_buffer_borda = self.buffer_poligono_borda.intersect(self.linha_ma_sirgas,1)
        self.pt1_x = pontos_inte_linha_ma_buffer_borda.getPart(0).X
        self.pt1_y = pontos_inte_linha_ma_buffer_borda.getPart(0).Y
        self.pt2_x = pontos_inte_linha_ma_buffer_borda.getPart(1).X
        self.pt2_y = pontos_inte_linha_ma_buffer_borda.getPart(1).Y
        angulo_rad = PtCircBorda(self.x_b,self.y_b).eq_ang_entre_vetores(self.pt1_x,self.pt1_y,self.pt2_x,self.pt2_y)
        return angulo_rad

    def circulo_de_borda_filtro(self, linha_buffer_inter, ponto):
        list_partes = self.funcao_multipart(linha_buffer_inter, ponto)
        dict_circulo = {}
        if list_partes:
            if list_partes.__len__() == 2:
                ptc_x, ptc_y = self.ponto_meio(list_partes,ponto)
                self.tipo_circulo = "meio"
                dict_circulo = {"ptc_x": ptc_x, "ptc_y": ptc_y}
            else:
                self.raio += 10
        elif self.tipo_circulo == "extremidade":
            angulo_rad = self.ponto_extremidade()
            dict_circulo["angulo_rad"] = angulo_rad
        else:
            self.raio += 10
            self.contador_raio_extremidade += 1
            if self.contador_raio_extremidade >= 3:
                if self.contador_raio_extremidade == 3:
                    self.raio = self.raio - 30
                self.tipo_circulo = "extremidade"
        return self.tipo_circulo, dict_circulo

    def ponto_buffer(self,ponto):
        self.x_b = ponto.getPart().X
        self.y_b = ponto.getPart().Y
        teste_validacao = False
        dict_descricao = {}
        loops_validacao = 0
        self.contador_raio_extremidade = 0
        self.tipo_circulo = None
        while teste_validacao == False:
            self.buffer_poligono_borda = ponto.projectAs(self.spatial_proj_lambert).buffer(self.raio).projectAs(self.spatial_geo_sirgas_2000)
            self.dict_partes = {}
            dict_descricao = {}
            linha_buffer_inter = self.buffer_poligono_borda.intersect(self.linha_ma_sirgas,2)
            self.tipo_circulo, dict_circulo = self.circulo_de_borda_filtro(linha_buffer_inter, ponto)
            if dict_circulo:
                if self.tipo_circulo == "meio":
                    dict_descricao["tipo"] = "meio"
                    dict_descricao["ptc_x"] = dict_circulo["ptc_x"]
                    dict_descricao["ptc_y"] = dict_circulo["ptc_y"]
                    linha_largura, linha_circulo = self.linha_de_largura(dict_descricao, ponto)
                    dict_descricao["linha_largura"] = linha_largura
                    dict_descricao["linha_circulo"] = linha_circulo
                elif self.tipo_circulo == "extremidade":
                    dict_descricao["tipo"] = "extremidade"
                    dict_descricao["angulo_rad"] = dict_circulo["angulo_rad"]
            teste_validacao = self.validar_circulo(self.tipo_circulo, dict_descricao)
            loops_validacao += 1
            # except:
            #     CopyFeatures_management(self.buffer_poligono_borda, self.diretorio_saida + "/" + "buffer_poligono_borda" + "_" + str(loops_validacao)  + "_" + str(self.distancia_pt_inicial) + ".shp")
            #     CopyFeatures_management(ponto, self.diretorio_saida + "/" + "ponto" + "_" + str(loops_validacao) + "_" + str(self.distancia_pt_inicial) + ".shp")
            #     CopyFeatures_management(self.linha_ma_sirgas, self.diretorio_saida + "/" + "linha_ma_sirgas" + "_" + str(loops_validacao) + str(self.distancia_pt_inicial) + ".shp")
            #     print teste_validacao
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
        self.distancia_pt_inicial = 0
        self.distancia_lado_oposto_inicial_pt = None
        self.identificador_extremidade = False
        controlador_poligono = ControlePoligono()
        while self.distancia_pt_inicial < compri_total:
            print "self.distancia_pt_inicial", self.distancia_pt_inicial
            self.primeiro_teste_circ = True
            self.compri_linha_raio_x1 = compri_linha_largura/1.1
            self.compri_linha_raio_x2 = compri_linha_largura/0.5
            ponto = linha_lambert.positionAlongLine(self.distancia_pt_inicial).projectAs(self.spatial_geo_sirgas_2000)
            self.ponto = ponto
            self.ponto_5m = ponto.projectAs(self.spatial_proj_lambert).buffer(5).projectAs(self.spatial_geo_sirgas_2000)
            dict_descricao = self.ponto_buffer(ponto)
            if self.tipo_circulo == "meio":
                self.identificador_extremidade = False
                CopyFeatures_management(dict_descricao["linha_largura"], self.diretorio_saida + "/linha_largura" + str(self.distancia_pt_inicial) + ".shp")
                self.distancia_pt_inicial += 30
                if self.distancia_pt_inicial == 0:
                    controlador_poligono.ponto_0_tipo == "meio"
                    controlador_poligono.ponto_oposto_0_distancia

            elif self.tipo_circulo == "extremidade":
                if self.identificador_extremidade == False:
                    self.identificador_extremidade = True
                    controlador_poligono.contador_n_extremidades += 1
                self.distancia_pt_inicial += 30


    def selecionar_poligono(self, layer_massa_dagua):
        with da.SearchCursor(layer_massa_dagua,["OID@","SHAPE@"],"FID = 35") as cursor:
            for row in cursor:
                self.poligono_ma_geo = row[1].projectAs(SpatialReference(4674))
                self.pontos_aolongo_linha()
        del cursor

    def iniciar_codigo(self):
        if path.exists(self.diretorio_saida):
            rmtree(self.diretorio_saida)
        mkdir(self.diretorio_saida)
        MakeFeatureLayer_management(self.diretorio_entrada + "/MASSA_DAGUA.shp", "MASSA_DAGUA")
        self.selecionar_poligono("MASSA_DAGUA")

class ControlePoligono():
    def __init__(self):
        self.contador_n_extremidades = 0
        self.ponto_0_tipo = None
        self.ponto_oposto_0_distancia = None

    def mudar_distancia(self):
        if self.ponto_0_tipo == "meio":
            if self.contador_n_extremidades == 1:
                return self.ponto_oposto_0_distancia
        return False

    def finalizar_poligono(self):
        if self.contador_n_extremidades == 2:
            return True
        return False

class PtCircBorda(object):
    def __init__(self, x0, y0, pt1_x = None, pt1_y = None, pt2_x = None, pt2_y = None):
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

    def eq_circ_achar_x(self,y, raio):
        a = self.x0
        b = self.y0
        x = a + sqrt(pow(raio,2) - pow(y - b, 2))
        return x

    def eq_circ_achar_y(self,x, raio):
        a = self.x0
        b = self.y0
        y = b + sqrt(pow(raio,2) - pow(x - a, 2))
        return y

    def eq_circ_achar_raio(self, x, y):
        a = self.x0
        b = self.y0
        raio =  sqrt(pow((x-a),2) + pow((y-b),2))
        return raio

    def converter_pontos_para_vetores_circ(self, ponto_x, ponto_y):
        vetor_x = ponto_x - self.x0
        vetor_y = ponto_y - self.y0
        return vetor_x, vetor_y

    def converter_vetores_circ_para_pontos(self, vetor_x, vetor_y):
        ponto_x = vetor_x + self.x0
        ponto_y = vetor_y + self.y0
        return ponto_x, ponto_y

    def eq_ang_entre_vetores(self, ponto1_x, ponto1_y, ponto2_x, ponto2_y):
        vetor_pt1_x, vetor_pt1_y = self.converter_pontos_para_vetores_circ(ponto1_x, ponto1_y)
        vetor_pt2_x, vetor_pt2_y = self.converter_pontos_para_vetores_circ(ponto2_x, ponto2_y)
        ## produto escalar ###
        produto_esc = vetor_pt1_x*vetor_pt2_x + vetor_pt1_y*vetor_pt2_y
        ## magnitude dos vetores ###
        magnitude_vetor_pt1 = sqrt(pow(vetor_pt1_x,2) + pow(vetor_pt1_y,2))
        magnitude_vetor_pt2 = sqrt(pow(vetor_pt2_x,2) + pow(vetor_pt2_y,2))
        angulo_rad = acos(produto_esc/(magnitude_vetor_pt1*magnitude_vetor_pt2))
        return angulo_rad

    def retorna_ponto_atraves_angulo(self, ang_rad, raio):
        vetor_x = cos(ang_rad)*raio
        vetor_y = sin(ang_rad)*raio
        ponto_x, ponto_y = self.converter_vetores_circ_para_pontos( vetor_x, vetor_y)
        return ponto_x, ponto_y

    def retorna_angulo_atraves_ponto(self, ponto_x, ponto_y):
        vetor_x, vetor_y = self.converter_pontos_para_vetores_circ(ponto_x, ponto_y)
        if vetor_x == 0:
            angulo = pi/2
        else:
            angulo = abs(atan(vetor_y/vetor_x))
        if vetor_x >= 0 and vetor_y >= 0:
            "QI"
            pass
        elif vetor_x < 0 and vetor_y > 0:
            "QII"
            angulo = pi - angulo
        elif vetor_x <= 0 and vetor_y < 0:
            "QIII"
            angulo = pi + angulo
        elif vetor_x > 0 and vetor_y < 0:
            "QIV"
            angulo = 2*pi - angulo
        return angulo

    def retorna_pontos_metade_entre_vetores(self, ponto1_x, ponto1_y, ponto2_x, ponto2_y, raio):
        angulo_pt1 = self.retorna_angulo_atraves_ponto(ponto1_x, ponto1_y)
        angulo_pt2 = self.retorna_angulo_atraves_ponto(ponto2_x, ponto2_y)
        menor_ang_vetores = self.eq_ang_entre_vetores(ponto1_x, ponto1_y, ponto2_x, ponto2_y)
        if angulo_pt1 <= angulo_pt2:
            if (angulo_pt2 - angulo_pt1) > pi:
                angulo_metade = angulo_pt2 + menor_ang_vetores/2
            else:
                angulo_metade = angulo_pt1 + menor_ang_vetores/2
        else:
            if (angulo_pt1 - angulo_pt2) > pi:
                angulo_metade = angulo_pt1 + menor_ang_vetores/2
            else:
                angulo_metade = angulo_pt2 + menor_ang_vetores/2

        if angulo_metade < pi:
            angulo_metade_inv = pi + angulo_metade
        else:
            angulo_metade_inv = angulo_metade - pi

        pt_x_metade, pt_y_metade = self.retorna_ponto_atraves_angulo(angulo_metade, raio)
        pt_x_metade_inv, pt_y_metade_inv = self.retorna_ponto_atraves_angulo(angulo_metade_inv, raio)
        return pt_x_metade, pt_y_metade, pt_x_metade_inv, pt_y_metade_inv

    def ponto_circ_borda(self):
        raio = self.eq_circ_achar_raio(self.pt1_x, self.pt1_y)
        self.ptc_x, self.ptc_y, self.ptc_x_inv, self.ptc_y_inv = self.retorna_pontos_metade_entre_vetores(self.pt1_x,  self.pt1_y, self.pt2_x, self.pt2_y, raio)
        return self.ptc_x, self.ptc_y, self.ptc_x_inv, self.ptc_y_inv

if __name__ == '__main__':
    DefinirLargura().iniciar_codigo()
tempo =  time.clock() - tempo

print tempo