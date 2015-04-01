from arcpy import Polyline
projecao_plana = None
projecao_geo = None
intervalo_entre_linhas = None
poligono = None
borda_linha_geo = None
borda_linha_plana = None

def funcao_multipart(linha, ponto):
    list_partes = []
    dict_partes = {}
    if linha.isMultipart:

        for n in range(linha.partCount):
            parte = linha.getPart(n)
            linha_parte = Polyline(parte, projecao_geo)
            linha_parte_lambert = linha_parte.projectAs(projecao_plana)
            if linha_parte_lambert.length > 0.8:
                list_partes.append(parte)
                if linha_parte.disjoint(ponto):
                    dict_partes["parte" + str(n)] = {"linha_array":parte, "cruza_ponto":False, "linha_geometria":linha_parte}
                else:
                    dict_partes["parte" + str(n)] = {"linha_array":parte, "cruza_ponto":True, "linha_geometria":linha_parte}
    return list_partes




def pontos_aolongo_linha():
    lista_pontos = []
    compri_total = borda_linha_plana.length
    compri_atual = 0
    while compri_atual < compri_total:
        ponto = borda_linha_plana.positionAlongLine(compri_atual).projectAs(projecao_geo)
        lista_pontos.append((ponto,compri_atual))
        compri_atual += 10
    return lista_pontos

def calc_ponto_buffer(ponto, raio):
    "criar buffer a partir de um ponto"
    ponto_buffer_plana = ponto.projectAs(projecao_plana).buffer(raio)
    ponto_buffer_geo = ponto_buffer_plana.projectAs(projecao_geo)
    return ponto_buffer_geo

def circulo_de_borda_filtro(ponto, circ_borda, raio):
    "filtrar tipo de circulo"
    linha_buffer_inter = circ_borda.intersect(borda_poligono, 2)
    list_partes =  funcao_multipart(linha_buffer_inter)
    tipo_circulo = None
    if list_partes:
        if list_partes.__len__() == 2:
            ptc_x, ptc_y = ponto_meio(list_partes,ponto)
            tipo_circulo = "meio"
            dict_circulo = {"ptc_x": ptc_x, "ptc_y": ptc_y}
        else:
            raio += 10
    elif tipo_circulo == "extremidade":
        angulo_rad = ponto_extremidade()
        dict_circulo["angulo_rad"] = angulo_rad
    else:
        self.raio += self.raio*2
        self.contador_raio_extremidade += 1
        if self.contador_raio_extremidade >= 3:
            if self.contador_raio_extremidade == 3:
                self.raio = self.raio/pow(2,3)
            self.tipo_circulo = "extremidade"
    return self.tipo_circulo, dict_circulo


def calc_tipo_ponto_buffer(ponto, raio, borda_poligono, projecao_plana, projecao_geo):
    "tipo de buffer"
    x_ptc = ponto.getPart().X
    y_ptc = ponto.getPart().Y
    validar_pt_buffer = False
    while validar_pt_buffer == False:
        circ_borda = calc_ponto_buffer(ponto, raio, projecao_plana, projecao_geo)

        dict_circ_desc ={
            "partes":{},
            "tipo":None

        }

        validar_pt_buffer = True


