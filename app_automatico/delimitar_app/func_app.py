projecao_plana = None
projecao_geo = None
intervalo_entre_linhas = None
poligono_ma = None
borda_linha_geo = None
borda_linha_plana = None
from func_circulo import CircVetores
from arcpy import Point, PointGeometry, Polyline, Polygon, Array
def definir_largura_app(linha):
    compri_linha = linha.projectAs(projecao_plana).length
    compri_app = None
    if compri_linha < 10:
        compri_app = 30
    elif compri_app <= 10 and compri_app < 50:
        compri_app = 50
    elif compri_app <= 50 and compri_app < 200:
        compri_app = 100
    return compri_app

def criar_linha_largura_app(linha, largura_app):
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
    point1_final = Point()
    point1_final.X = x_1_final
    point1_final.Y = y_1_final
    point2_final = Point()
    point2_final.X = x_2_final
    point2_final.Y = y_2_final
    array = Array([point1_final, point2_final])
    linha_app = Polyline(array, projecao_geo)
    del array
    return linha_app

def criar_poligono_app(linha, linha_frente):
    linha_app = criar_linha_largura_app(linha, definir_largura_app(linha))
    linha_app_frente =  criar_linha_largura_app(linha_frente, definir_largura_app(linha_frente))
    array = Array()
    array.add(linha_app.firstPoint)
    array.add(linha_app.lastPoint)
    array.add(linha_app_frente.lastPoint)
    array.add(linha_app_frente.firstPoint)
    array.add(linha_app.firstPoint)
    polygon = Polygon(array, projecao_geo)
    array.removeAll()
    del array
    return polygon

