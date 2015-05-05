projecao_plana = None
projecao_geo = None
intervalo_entre_linhas = None
poligono_ma = None
borda_linha_geo = None
borda_linha_plana = None
from func_circulo import CircVetores
from arcpy import PointGeometry
def criar_linha_largura_app(linha):
    compri_linha = linha.projectAs(projecao_plana).length
    largura_app = 50
    x_1_c = linha.firstPoint.X
    y_1_c = linha.firstPoint.Y
    x_2_c = linha.lastPoint.X
    y_2_c = linha.lastPoint.Y
    pt1_geometry = PointGeometry(linha.firstPoint, projecao_geo)
    pt2_geometry = PointGeometry(linha.lastPoint, projecao_geo)
    circ_poly_1 = pt1_geometry.projectAs(projecao_plana).buffer(largura_app).projectAs(projecao_geo).boundary()
    x_1_nocirc = circ_poly_1.firstPoint.X
    y_1_nocirc = circ_poly_1.firstPoint.Y
    obj_circ = CircVetores(x_1_c,y_1_c)
    raio = obj_circ.eq_circ_achar_raio(x_1_nocirc,y_1_nocirc)
    angulo_rad = obj_circ.retorna_angulo_atraves_ponto(x_2_c,y_2_c)
    x_1_final, y_1_final = obj_circ.retorna_ponto_de_angulo_inverso(angulo_rad, raio)
    del obj_circ

    circ_poly_2 = pt2_geometry.projectAs(projecao_plana).buffer(largura_app).projectAs(projecao_geo).boundary()
    x_2_nocirc = circ_poly_2.firstPoint.X
    y_2_nocirc = circ_poly_2.firstPoint.Y
    obj_circ = CircVetores(x_2_c,y_2_c)
    raio = obj_circ.eq_circ_achar_raio(x_2_nocirc,y_2_nocirc)
    angulo_rad = obj_circ.retorna_angulo_atraves_ponto(x_1_c,y_1_c)
    x_2_final, y_2_final = obj_circ.retorna_ponto_de_angulo_inverso(angulo_rad, raio)
    del obj_circ
    #TODO finalizar a funcao



def criar_poligono_app(linha, linha_frente):
    compri_linha = linha.projectAs(projecao_plana).length
    compri_linha_frente = linha_frente.projectAs(projecao_plana).length
    criar_linha_largura_app(linha)
    # compri_app_linha = identificar_largura_app(compri_linha)
    # compri_app_linha_frente = identificar_largura_app(compri_linha_frente)
    # circ_linha =
