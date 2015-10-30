from arcpy import da, Array, Point, Polyline, Polygon, AddField_management, CreateFeatureclass_management
import math


def rotacionar_poligono(polygon, anchor_point, ang, proj_geo):
    array = Array()
    anchor_x = anchor_point.X
    anchor_y = anchor_point.Y
    for part in polygon:
        for point in part:
            x = point.X - anchor_x
            y = point.Y - anchor_y
            resultx = (x * math.cos(ang)) - (y * math.sin(ang)) + anchor_x
            resulty = (x * math.sin(ang)) + (y * math.cos(ang)) + anchor_y
            array.add(Point(resultx, resulty))
    result_polygon = Polygon(array, proj_geo)
    del array
    return result_polygon



def ret_envolvente(polygon, proj_geo):
    array = Array()
    array.add(polygon.extent.lowerLeft)
    array.add(polygon.extent.lowerRight)
    array.add(polygon.extent.upperRight)
    array.add(polygon.extent.upperLeft)
    array.add(polygon.extent.lowerLeft)
    result_polygon = Polygon(array, proj_geo)
    del array
    return result_polygon

def calc_linha_ret(li_pla1, li_pla2, distancia, proj_geo, proj_plana):
    array = Array()
    ponto1 = li_pla1.positionAlongLine(distancia).projectAs(proj_geo)
    ponto2 = li_pla2.positionAlongLine(distancia).projectAs(proj_geo)
    pt_label1 = ponto1.labelPoint
    pt_label2 = ponto2.labelPoint
    array.add(pt_label1)
    array.add(pt_label2)
    linha_ret = Polyline(array, proj_geo)
    del array
    return linha_ret

def bases_larguras(polygon, proj_geo):
    array1 = Array()
    array2 = Array()
    array3 = Array()
    array4 = Array()
    point1 = None
    point2 = None
    point3 = None
    point4 = None
    for part in polygon:
        point1 = part[0]
        point2 = part[1]
        point3 = part[2]
        point4 = part[3]
    array1.add(point1); array1.add(point2)
    array2.add(point2); array2.add(point3)
    array3.add(point4); array3.add(point3)
    array4.add(point1); array4.add(point4)
    li1 = Polyline(array1, proj_geo)
    li2 = Polyline(array2, proj_geo)
    li3 = Polyline(array3, proj_geo)
    li4 = Polyline(array4, proj_geo)
    if li1.length > li2.length:
        lista_base = [li1, li3]
        lista_largura = [li2, li4]
    else:
        lista_base = [li2, li4]
        lista_largura = [li1, li3]
    del array1
    del array2
    del array3
    del array4
    return lista_base, lista_largura

def func_melhor_angulo(inter_ini, inter_fim, delta, point_centr, poly, projecao_geo):
    angulo = inter_ini
    dict_area_ang = {}
    while angulo <= inter_fim:
        if angulo < 0:
            angulo = 0
        if angulo == 0:
            retangulo = ret_envolvente(poly, projecao_geo)
        else:
            poly_rot = rotacionar_poligono(poly, point_centr, angulo, projecao_geo)
            retangulo = ret_envolvente(poly_rot, projecao_geo)
        area_ret = retangulo.area
        dict_area_ang[area_ret] = angulo
        angulo += delta
    melhor_ang = dict_area_ang[min(dict_area_ang)]
    del dict_area_ang
    return melhor_ang

def dimensao_fractal(perimetro, area):
    frac = (2*math.log(0.25*perimetro))/(math.log(area))
    return frac

if __name__ == '__main__':
    diretorio = "C:\Users\DYEDEN\PycharmProjects\APP_AUTOMATICO\ENTRADA\MASSA_DAGUA.shp"
    diretorio_saida = "C:\Users\DYEDEN\PycharmProjects\APP_AUTOMATICO\ENTRADA"


    projecao_geo = 'GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",' \
                                       '6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],' \
                                       'UNIT["Degree",0.0174532925199433]]'

    projecao_plana = 'PROJCS["SIRGAS_2000_Lambert_Conformal_Conic_PA",GEOGCS["GCS_SIRGAS_2000",' \
                                    'DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],' \
                                    'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],' \
                                    'PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",0.0],' \
                                    'PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-52.5],' \
                                    'PARAMETER["Standard_Parallel_1",-0.5],' \
                                    'PARAMETER["Standard_Parallel_2",-6.833333333333333],PARAMETER' \
                                    '["Latitude_Of_Origin",-3.666667],UNIT["Meter",1.0]]'


    CreateFeatureclass_management(diretorio_saida, "RETANGULOS_MI.shp", "POLYGON", "", "", "",
                          projecao_geo)

    cursor_insert_ret = da.InsertCursor(diretorio_saida + "\RETANGULOS_MI.shp", ['Id', 'SHAPE@'])

    with da.UpdateCursor(diretorio, ["OID@", "SHAPE@", "area_m2", "perim_m", "frac", "comp", "ret"]) as cursor:
        for row in cursor:
            try:

                frac_p = dimensao_fractal(row[3], row[2])
                comp_p = row[3]/(math.sqrt(row[2]))
                row[4] = frac_p
                row[5] = comp_p
                point_centroid = row[1].centroid
                delta = math.pi/36
                melhor_ang = func_melhor_angulo(0, math.pi/2, delta, point_centroid, row[1], projecao_geo)

                inter_fim = melhor_ang + delta
                inter_ini = melhor_ang - delta
                delta2 = delta/10
                melhor_ang = func_melhor_angulo(inter_ini, inter_fim, delta2, point_centroid, row[1], projecao_geo)

                poly_rot = rotacionar_poligono(row[1], point_centroid, melhor_ang, projecao_geo)
                retangulo = ret_envolvente(poly_rot, projecao_geo)
                bases_larguras(retangulo)
                ret_rot = rotacionar_poligono(retangulo, point_centroid, - melhor_ang, projecao_geo)
                area_ret_rot = ret_rot.projectAs(projecao_plana).area

                ret_p = row[2]/area_ret_rot
                row[6] = ret_p
                cursor.updateRow(row)
                cursor_insert_ret.insertRow((row[0], ret_rot))
            except:
                cursor.updateRow(row)

    del cursor
    del cursor_insert_ret