projecao_plana = None
projecao_geo = None
intervalo_entre_linhas = None
poligono_ma = None
borda_linha_geo = None
borda_linha_plana = None
from func_circulo import CircVetores
from arcpy import Point, PointGeometry, Polyline, Polygon, Array
import numpy


def bool_interseccao_entre_linhas(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])
    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       return False

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    l1_minX = min(line1[0][0], line1[1][0])
    l1_maxX = max(line1[0][0], line1[1][0])
    l2_minX = min(line2[0][0], line2[1][0])
    l2_maxX = max(line2[0][0], line2[1][0])
    l1_minY = min(line1[0][1], line1[1][1])
    l1_maxY = max(line1[0][1], line1[1][1])
    l2_minY = min(line2[0][1], line2[1][1])
    l2_maxY = max(line2[0][1], line2[1][1])

    if l1_minX <= x <= l1_maxX and l2_minX <= x <= l2_maxX:
        if l1_minY <= y <= l1_maxY and l2_minY <= y <= l2_maxY:
            return True
        else:
            return False
    else:
        return False


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

def criar_poligono_app(linha_app, linha_app_frente):
    array = Array()
    l1_firstX = linha_app.firstPoint.X
    l1_firstY = linha_app.firstPoint.Y
    l1_lastX = linha_app.lastPoint.X
    l1_lastY = linha_app.lastPoint.Y
    l2_firstX = linha_app_frente.firstPoint.X
    l2_firstY = linha_app_frente.firstPoint.Y
    l2_lastX = linha_app_frente.lastPoint.X
    l2_lastY = linha_app_frente.lastPoint.Y

    array.add(linha_app.firstPoint)
    array.add(linha_app.lastPoint)
    if bool_interseccao_entre_linhas(((l1_lastX,l1_lastY),(l2_lastX,l2_lastY)),((l1_firstX,l1_firstY),(l2_firstX,l2_firstY))):
        array.add(linha_app_frente.firstPoint)
        array.add(linha_app_frente.lastPoint)
    else:
        array.add(linha_app_frente.lastPoint)
        array.add(linha_app_frente.firstPoint)
    array.add(linha_app.firstPoint)
    polygon = Polygon(array, projecao_geo)
    array.removeAll()
    del array
    polygon = polygon.buffer(0.000000001)
    return polygon

def criar_poligono_app_hull(linha_app, linha_app_frente):
    linha_union = linha_app.union(linha_app_frente)
    polygon = linha_union.convexHull()
    polygon = polygon.buffer(0.000000001)
    return polygon


