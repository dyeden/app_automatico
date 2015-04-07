from arcpy import Polyline, Point, Array
from ponto_circ_borda import PtCircBorda
projecao_plana = None
projecao_geo = None
intervalo_entre_linhas = None
poligono_ma = None
borda_linha_geo = None
borda_linha_plana = None
compri_linha_raio_x1 = None
compri_linha_raio_x2 = None
primeiro_cal_circ = True

from math import pi
def funcao_multipart(linha, ponto):
    dict_partes = {}
    if linha.isMultipart:
        for n in range(linha.partCount):
            parte = linha.getPart(n)
            linha_parte = Polyline(parte, projecao_geo)
            linha_parte_lambert = linha_parte.projectAs(projecao_plana)
            if linha_parte_lambert.length > 0.8:
                if linha_parte.disjoint(ponto):
                    dict_partes["parte" + str(n)] = {"linha_array":parte, "cruza_ponto":False, "linha_geometria":linha_parte}
                else:
                    dict_partes["parte" + str(n)] = {"linha_array":parte, "cruza_ponto":True, "linha_geometria":linha_parte}
    return dict_partes


def pontos_aolongo_linha():
    lista_pontos = []
    compri_total = borda_linha_plana.length
    compri_atual = 0
    while compri_atual < compri_total:
        ponto = borda_linha_plana.positionAlongLine(compri_atual).projectAs(projecao_geo)
        lista_pontos.append((ponto,compri_atual))
        compri_atual += 10
    return lista_pontos


def ponto_meio(ponto, dict_circulo, circ_borda):
    """funcao para gerar o ponto metade"""

    x_ptc = dict_circulo["pt_centro_circ"]["x_ptc"]
    y_ptc = dict_circulo["pt_centro_circ"]["y_ptc"]

    for parte_n in dict_circulo["partes"]:
        parte_linha = Polyline(dict_circulo["partes"][parte_n]["linha_array"], projecao_geo)
        if parte_linha.disjoint(ponto):
            pontos_inte_linha_poligono = circ_borda.intersect(parte_linha,1)
            x_pt1 = pontos_inte_linha_poligono.getPart(0).X
            y_pt1 = pontos_inte_linha_poligono.getPart(0).Y
            x_pt2 = pontos_inte_linha_poligono.getPart(1).X
            y_pt2 = pontos_inte_linha_poligono.getPart(1).Y
            x_ptm, y_ptm, x_ptm_inv, y_ptm_inv = PtCircBorda(x_ptc,y_ptc,x_pt1, y_pt1, x_pt2, y_pt2).ponto_circ_borda()
    return x_ptm, y_ptm, x_ptm_inv, y_ptm_inv

def ponto_extremidade(self):
    pontos_inte_linha_ma_buffer_borda = self.buffer_poligono_borda.intersect(self.linha_ma_sirgas,1)
    self.pt1_x = pontos_inte_linha_ma_buffer_borda.getPart(0).X
    self.pt1_y = pontos_inte_linha_ma_buffer_borda.getPart(0).Y
    self.pt2_x = pontos_inte_linha_ma_buffer_borda.getPart(1).X
    self.pt2_y = pontos_inte_linha_ma_buffer_borda.getPart(1).Y
    angulo_rad = PtCircBorda(self.x_b,self.y_b).eq_ang_entre_vetores(self.pt1_x,self.pt1_y,self.pt2_x,self.pt2_y)
    return angulo_rad

def aferir_circulo(dict_circ_desc,raio):
    teste_validacao = False
    if dict_circ_desc["tipo_circulo"] == "meio":
        linha_largura = dict_circ_desc["linha_largura"]
        linha_circulo = dict_circ_desc["linha_circulo"]
        compri_linha_largura = linha_largura.projectAs(projecao_plana).length
        compri_linha_circulo = linha_circulo.projectAs(projecao_plana).length
        porc_raio_largura = (compri_linha_largura/compri_linha_circulo)*100
        if 75 < porc_raio_largura < 85:
            teste_validaco = True
        elif dict_circ_desc["primeiro_teste"]:
            primeiro_cal_circ = False

            raio = compri_linha_largura/0.8
            compri_linha_raio_x1 = compri_linha_largura/1.1
            compri_linha_raio_x2 = compri_linha_largura/0.5


        else:
            if porc_raio_largura <= 80:
                compri_linha_raio_x2 = raio
            else:
                compri_linha_raio_x1 = raio
            raio = (compri_linha_raio_x1 + compri_linha_raio_x2)/2
    elif dict_circ_desc["tipo_circulo"] == "extremidade":
        angulo_rad = dict_circ_desc["angulo_rad"]
        if angulo_rad <= (5*pi)/6:
            teste_validacao = True
    return teste_validacao, raio


def calc_circ_borda(ponto, raio):
    """criar buffer a partir de um ponto"""
    ponto_buffer_plana = ponto.projectAs(projecao_plana).buffer(raio)
    circ_borda = ponto_buffer_plana.projectAs(projecao_geo)
    return circ_borda

def calc_linhas_largura(dict_circ_desc, ponto):
    """criar linhas de largura"""
    if dict_circ_desc["tipo_circulo"] == "meio":
        linha_nao_intersecta_ponto = None
        point_circ = Point()
        point_circ.X = dict_circ_desc["pt_medios_circ"]["x_ptm"]
        point_circ.Y = dict_circ_desc["pt_medios_circ"]["y_ptm"]
        array = Array([point_circ, ponto.getPart(0)])
        linha_circulo = Polyline(array, projecao_geo)
        for parte_linha in dict_circ_desc["partes"]:
            if not dict_circ_desc["partes"][parte_linha]["cruza_ponto"]:
                linha_nao_intersecta_ponto = dict_circ_desc["partes"][parte_linha]["linha_geometria"]
        if linha_circulo.disjoint(linha_nao_intersecta_ponto):
            array.removeAll()
            point_circ = Point()
            point_circ.X = dict_circ_desc["pt_medios_circ"]["x_ptm_inv"]
            point_circ.Y = dict_circ_desc["pt_medios_circ"]["y_ptm_inv"]
            array = Array([point_circ, ponto.getPart(0)])
            linha_circulo = Polyline(array, projecao_geo)
            linha_largura = linha_circulo.intersect(poligono_ma, 2)
            array.removeAll()
        else:
            linha_largura = linha_circulo.intersect(poligono_ma, 2)
            array.removeAll()
        return linha_largura, linha_circulo

def circulo_de_borda_filtro(ponto, circ_borda, raio, dict_circulo, n_extremidades):
    """filtrar tipo de circulo"""
    tipo_circulo = dict_circulo["tipo_circulo"]
    angulo_rad = None
    pontos_medios = None
    if dict_circulo["partes"]:

        if dict_circulo["partes"].__len__() == 2:
            x_ptm, y_ptm, x_ptm_inv, y_ptm_inv = ponto_meio(ponto, dict_circulo, circ_borda)
            tipo_circulo = "meio"
            pontos_medios = {"x_ptm": x_ptm, "y_ptm": y_ptm, "x_ptm_inv":x_ptm_inv, "y_ptm_inv":y_ptm_inv}

        else:
            raio += 10

    elif tipo_circulo == "extremidade":
        # noinspection PyArgumentList
        angulo_rad = ponto_extremidade()

    else:
        raio += raio*2
        n_extremidades += 1
        if n_extremidades >= 3:
            if n_extremidades == 3:
                raio /= pow(2, 3)
            tipo_circulo = "extremidade"

    return tipo_circulo, angulo_rad, raio, pontos_medios


def calc_tipo_circ_borda(ponto, raio, dict_poligono_descricao, dict_circ_desc):
    """tipo de buffer"""
    x_ptc = ponto.getPart().X
    y_ptc = ponto.getPart().Y
    circ_borda = calc_circ_borda(ponto, raio)
    linha_buffer_inter = circ_borda.intersect(borda_linha_geo, 2)
    dict_circ_desc["partes"] =  funcao_multipart(linha_buffer_inter, ponto)
    tipo_circulo, angulo_rad, raio, pontos_medios = \
        circulo_de_borda_filtro(ponto, circ_borda, raio, dict_circ_desc,
        dict_poligono_descricao["n_extremidades"])
    dict_circ_desc["tipo_circulo"] = tipo_circulo
    dict_circ_desc["pt_medios_circ"] = pontos_medios
    dict_circ_desc["angulo_rad"] = angulo_rad
    linha_largura, linha_circulo = calc_linhas_largura(dict_circ_desc, ponto)
    dict_circ_desc["linha_largura"] = linha_largura
    dict_circ_desc["primeiro_teste"] = primeiro_cal_circ
    dict_circ_desc["linha_circulo"] = linha_circulo
    return dict_circ_desc

