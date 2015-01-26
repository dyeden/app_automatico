__author__ = 'DYEDEN'

from arcpy import Polyline, da, Point, Array, CopyFeatures_management, PointGeometry
from math import sqrt, acos, pi
from os import path, mkdir
from shutil import rmtree

spatial_geo_sirgas_2000 = 'GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
spatial_proj_lambert = 'PROJCS["SIRGAS_2000_Lambert_Conformal_Conic_PA",GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-52.5],PARAMETER["Standard_Parallel_1",-0.5],PARAMETER["Standard_Parallel_2",-6.833333333333333],PARAMETER["Latitude_Of_Origin",-3.666667],UNIT["Meter",1.0]]'

saida = "LARGURA_LINHA"
if path.exists(saida):
    rmtree(saida)
mkdir(saida)

class LarguraRio(object):
    def __init__(self, poligono_ma, faixa_compri):
        self.poligono_ma = poligono_ma
        self.faixa_compri = faixa_compri
        self.raio = 30
        self.raio_pr = self.raio
        self.compri_linha_largura_x1 = self.raio_pr*0.75
        self.compri_linha_largura_x2 = self.raio_pr*0.85
    def conversao(self):
        self.poligono_ma_sirgas = self.poligono_ma.projectAs(spatial_geo_sirgas_2000)
        self.linha_ma_sirgas = self.poligono_ma_sirgas.boundary()
    def ponto_buffer(self,ponto):
        buffer_ponto = ponto.projectAs(spatial_proj_lambert).buffer(self.raio).projectAs(spatial_geo_sirgas_2000)

        self.x0 = ponto.getPart().X
        self.y0 = ponto.getPart().Y

        linha_buffer_inter = buffer_ponto.intersect(self.linha_ma_sirgas,2)
        ponto_buffer_inter = buffer_ponto.intersect(self.linha_ma_sirgas,1)
        contador_pt_buffer = 0

        bool_extremid_poligono = False
        while linha_buffer_inter.isMultipart != True:
            print self.raio, "raio", contador_pt_buffer, "contador_pt_buffer"
            # CopyFeatures_management(buffer_ponto,saida + "/buffer_ponto" + str(self.raio) + ".shp")
            # CopyFeatures_management(linha_buffer_inter,saida + "/linha_buffer_inter" + str(self.raio) + ".shp")
            # CopyFeatures_management(ponto_buffer_inter,saida + "/ponto_buffer_inter" + str(self.raio) + ".shp")
            self.raio += 10
            buffer_ponto = ponto.projectAs(spatial_proj_lambert).buffer(self.raio).projectAs(spatial_geo_sirgas_2000)
            linha_buffer_inter = buffer_ponto.intersect(self.linha_ma_sirgas,2)
            ponto_buffer_inter = buffer_ponto.intersect(self.linha_ma_sirgas,1)
            self.raio_pr = self.raio



            if contador_pt_buffer == 3:
                self.raio = self.raio - 30
                buffer_ponto = ponto.projectAs(spatial_proj_lambert).buffer(self.raio).projectAs(spatial_geo_sirgas_2000)
                self.x0 = ponto.getPart().X
                self.y0 = ponto.getPart().Y
                linha_buffer_inter = buffer_ponto.intersect(self.linha_ma_sirgas,2)

                if linha_buffer_inter.isMultipart == False:

                    vetor_pt1_x =  ponto_buffer_inter.getPart(0).X - self.x0
                    vetor_pt1_y =  ponto_buffer_inter.getPart(0).Y - self.y0
                    vetor_pt2_x =  ponto_buffer_inter.getPart(1).X - self.x0
                    vetor_pt2_y =  ponto_buffer_inter.getPart(1).Y - self.y0
                    prod_escalar = vetor_pt1_x*vetor_pt2_x + vetor_pt1_y*vetor_pt2_y
                    manig_pt1 = sqrt(pow(vetor_pt1_x,2) + pow(vetor_pt1_y,2))
                    manig_pt2 = sqrt(pow(vetor_pt2_x,2) + pow(vetor_pt2_y,2))
                    ang_radianos = acos(prod_escalar/(manig_pt1*manig_pt2))
                    ang_graus = ang_radianos*(180/pi)
                    if ang_graus < 45:
                        bool_extremid_poligono = True
                        CopyFeatures_management(buffer_ponto,saida + "/buffer_ponto_extremidade" + str(self.distancia_pt0) + ".shp")
                        return None, None, bool_extremid_poligono
                        break
            contador_pt_buffer += 1

        # CopyFeatures_management(buffer_ponto,saida + "/buffer_ponto.shp")
        if linha_buffer_inter.isMultipart:
            n_part_linha = linha_buffer_inter.partCount
            for n in xrange(n_part_linha):
                part_array = linha_buffer_inter.getPart(n)
                part_linha = Polyline(part_array, spatial_geo_sirgas_2000)
                if part_linha.disjoint(ponto):
                    ponto_inter_linha = buffer_ponto.intersect(part_linha,1)
                    self.pt1_x = ponto_inter_linha.getPart(0).X
                    self.pt1_y = ponto_inter_linha.getPart(0).Y
                    self.pt2_x = ponto_inter_linha.getPart(1).X
                    self.pt2_y = ponto_inter_linha.getPart(1).Y
                    ptc_x, ptc_y = PtCircBorda(self.x0,self.y0,self.pt1_x,self.pt1_y,self.pt2_x,self.pt2_y).ponto_circ_borda()
                    # CopyFeatures_management(buffer_ponto,saida + "/buffer_ponto" + str(self.distancia_pt0) + ".shp")
                    return ptc_x, ptc_y, bool_extremid_poligono

    def linha_largura_fc(self, ptc_x, ptc_y, ponto):
        point_circ = Point()
        point_circ.X = ptc_x
        point_circ.Y = ptc_y
        array = Array([point_circ, ponto.getPart(0)])
        linha_circulo = Polyline(array,spatial_geo_sirgas_2000)
        linha_largura = linha_circulo.intersect(self.poligono_ma_sirgas, 2)
        array.removeAll()
        return linha_largura, linha_circulo


    def pontos_aolongo_linha(self):
        self.conversao()
        linha_lambert = self.linha_ma_sirgas.projectAs(spatial_proj_lambert)
        compri_total = linha_lambert.length
        distancia_pt0 = 0
        list_pts = []
        porc_raio_largura = 0

        compri_linha_largura = self.raio*0.8
        while distancia_pt0 < compri_total:
            compri_ok = False
            bool_extremid_poligono = False
            self.compri_linha_raio_x1 = compri_linha_largura/1.1
            self.compri_linha_raio_x2 = compri_linha_largura/0.5
            # # if distancia_pt0 < 3330 or distancia_pt0 > 4200:
            # distancia_pt0 += 30
            # #     continue

            while compri_ok == False:
                print distancia_pt0
                self.distancia_pt0 = distancia_pt0
                ponto = linha_lambert.positionAlongLine(distancia_pt0).projectAs(spatial_geo_sirgas_2000)
                ptc_x, ptc_y, bool_extremid_poligono = self.ponto_buffer(ponto)
                if bool_extremid_poligono:
                    compri_ok = True
                else:
                    list_pts.append((ptc_x, ptc_y))
                    linha_largura, linha_circulo = self.linha_largura_fc(ptc_x,ptc_y,ponto)
                    compri_linha_largura = linha_largura.projectAs(spatial_proj_lambert).length
                    compri_linha_circulo = linha_circulo.projectAs(spatial_proj_lambert).length
                    porc_raio_largura = (compri_linha_largura/compri_linha_circulo)*100

                    print compri_linha_largura, compri_linha_circulo, porc_raio_largura
                    print self.raio, 'raio', self.raio_pr, "raio_pr"
                    if 75 < porc_raio_largura < 85:
                        compri_ok = True
                    else:
                        if porc_raio_largura <= 80:
                            self.compri_linha_raio_x2 = self.raio
                        else:
                            self.compri_linha_raio_x1 = self.raio
                        print self.compri_linha_raio_x1, "self.compri_linha_raio_x1", self.compri_linha_raio_x2, "self.compri_linha_raio_x2"
                        self.raio = (self.compri_linha_raio_x1 + self.compri_linha_raio_x2)/2
                        if self.raio > self.raio_pr:
                            self.raio_pr = self.raio
            if bool_extremid_poligono == False:
                CopyFeatures_management(linha_largura,saida + "/linha_largura_pt" + str(distancia_pt0) + ".shp")
            distancia_pt0 += 30
        return list_pts
    def __repr__(self):
        return str(self.pontos_aolongo_linha())

class PtCircBorda(object):
    def __init__(self, x0, y0, pt1_x, pt1_y, pt2_x, pt2_y):
        self.x0 = x0; self.y0 = y0
        self.pt1_x = pt1_x; self.pt1_y = pt1_y; self.pt2_x = pt2_x; self.pt2_y = pt2_y
    def pt_medio(self):
        ptm_x = (self.pt1_x + self.pt2_x)/2
        ptm_y = (self.pt1_y + self.pt2_y)/2
        return ptm_x, ptm_y
    def ponto_circ_borda(self):
        self.x1, self.y1 = self.pt_medio()


        delt_x1 = self.x1 - self.x0
        delt_y1 = self.y1 - self.y0
        h1 = sqrt(delt_x1*delt_x1 + delt_y1*delt_y1)

        delt_xr = self.pt1_x - self.x0
        delt_yr = self.pt1_y - self.y0
        h2 = sqrt(delt_xr*delt_xr + delt_yr*delt_yr)


        delt_x2 = (delt_x1*h2)/h1
        delt_y2 = (delt_y1*h2)/h1
        self.ptc_x = self.x0 + delt_x2
        self.ptc_y = self.y0 + delt_y2
        return self.ptc_x, self.ptc_y


if __name__ == '__main__':
    layer_ma = "ENTRADA/MASSA_DAGUA_BRASIL_NOVO.shp"
    with da.SearchCursor(layer_ma,["OID@","SHAPE@"],"FID = 35") as cursor:
        for row in cursor:
            print row[0]
            print LarguraRio(row[1],100)
            # print lista
    del cursor