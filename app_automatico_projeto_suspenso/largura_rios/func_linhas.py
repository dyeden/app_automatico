from arcpy import Polyline, Point, Array
from ponto_circ_borda import PtCircBorda
projecao_plana = None
projecao_geo = None
intervalo_entre_linhas = None
poligono = None
borda_linha_geo = None
borda_linha_plana = None

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


def ponto_meio(list_partes, ponto, dict_circulo, circ_borda):
    "funcao para gerar o "

    x_ptc = dict_circulo["pt_centro_circ"]["x_ptc"]
    y_ptc = dict_circulo["pt_centro_circ"]["y_ptc"]
    for parte in list_partes:
        parte_linha = Polyline(parte, projecao_geo)
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

def calc_circ_borda(ponto, raio):
    "criar buffer a partir de um ponto"
    ponto_buffer_plana = ponto.projectAs(projecao_plana).buffer(raio)
    circ_borda = ponto_buffer_plana.projectAs(projecao_geo)
    return circ_borda

def calc_linhas_largura(dict_circ_desc, ponto):
    "criar linhas de largura"
    if dict_circ_desc["tipo_circulo"] == "meio":
        linha_nao_intersecta_ponto = None
        point_circ = Point()
        point_circ.X = dict_circ_desc["pt_medios_circ"]["x_ptm"]
        point_circ.Y = dict_circ_desc["pt_medios_circ"]["y_ptm"]
        array = Array([point_circ, ponto.getPart(0)])
        linha_circulo = Polyline(array, projecao_geo)
        for parte_linha in dict_circ_desc["partes"]:
            if dict_circ_desc["partes"][parte_linha]["cruza_ponto"] == False:
                linha_nao_intersecta_ponto = dict_circ_desc["partes"][parte_linha]["linha_geometria"]
        if linha_circulo.disjoint(linha_nao_intersecta_ponto):
            array.removeAll()
            point_circ = Point()
            point_circ.X = dict_circ_desc["pt_medios_circ"]["x_ptm_inv"]
            point_circ.Y = dict_circ_desc["pt_medios_circ"]["y_ptm_inv"]
            array = Array([point_circ, ponto.getPart(0)])
            linha_circulo = Polyline(array, projecao_geo)
            linha_largura = linha_circulo.intersect(borda_linha_geo, 2)
            array.removeAll()
        else:
            linha_largura = linha_circulo.intersect(borda_linha_geo, 2)
            array.removeAll()
        return linha_largura, linha_circulo

def circulo_de_borda_filtro(ponto, circ_borda, raio, dict_circulo, n_extremidades):
    "filtrar tipo de circulo"
    linha_buffer_inter = circ_borda.intersect(borda_linha_geo, 2)
    dict_partes =  funcao_multipart(linha_buffer_inter, ponto)
    tipo_circulo = dict_circulo["tipo_circulo"]
    angulo_rad = None
    pontos_medios = None
    if list_partes:

        if list_partes.__len__() == 2:
            x_ptm, y_ptm, x_ptm_inv, y_ptm_inv = ponto_meio(list_partes, ponto, dict_circulo, circ_borda)
            tipo_circulo = "meio"
            pontos_medios = {"x_ptm": x_ptm, "y_ptm": y_ptm, "x_ptm_inv":x_ptm_inv, "y_ptm_inv":y_ptm_inv}

        else:
            raio += 10

    elif tipo_circulo == "extremidade":
        angulo_rad = ponto_extremidade()

    else:
        raio += raio*2
        n_extremidades += 1
        if n_extremidades >= 3:
            if n_extremidades == 3:
                raio = raio/pow(2,3)
            tipo_circulo = "extremidade"

    return tipo_circulo, angulo_rad, raio, pontos_medios, list_partes


def calc_tipo_ponto_buffer(ponto, raio, dict_poligono_descricao):
    "tipo de buffer"
    x_ptc = ponto.getPart().X
    y_ptc = ponto.getPart().Y
    validar_pt_buffer = False
    dict_circ_desc ={
    "partes":None,
    "tipo_circulo":None,
    "pt_centro_circ":{"x_ptc":x_ptc,"y_ptc":y_ptc},
    "pt_medios_circ":{""},
    "pts_outros_circ":{"x_pt1":None,"y_pt1":None, "x_pt2":None,"y_pt2":None}
    }
    while validar_pt_buffer == False:
        circ_borda = calc_circ_borda(ponto, raio)
        tipo_circulo, angulo_rad, raio, pontos_medios, list_partes = \
            circulo_de_borda_filtro(ponto, circ_borda, raio, dict_circ_desc,
            dict_poligono_descricao["n_extremidades"])
        dict_circ_desc["partes"] = list_partes
        dict_circ_desc["tipo_circulo"] = tipo_circulo
        dict_circ_desc["pt_medios_circ"] = pontos_medios
        linha_largura, linha_circulo = calc_linhas_largura(dict_circ_desc, ponto)

        validar_pt_buffer = True


