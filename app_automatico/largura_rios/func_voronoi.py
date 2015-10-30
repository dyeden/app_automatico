import numpy as np
from scipy.spatial import Voronoi
import arcpy
import shapely.geometry
import shapely.ops
from shapely.wkt import loads
dir_ma = "C:\Users\DYEDEN\PycharmProjects\APP_AUTOMATICO\ENTRADA\MASSA_DAGUA.shp"

def voronoi_pontos(lista_pontos, poligono, linha_borda, projecao_geo, dir_saida, fid):
    "calcula as linhas de voronoi interna com uma lista de pontos"

    dirLinhaVoronoi = dir_saida + "/RESIDUOS/linha_voronoi_" + str(fid) +".shp"
    dirLinhaDissolvido = dir_saida + "/RESIDUOS/linha_voronoi_dissolvido_" + str(fid) +".shp"

    arcpy.CreateFeatureclass_management(dir_saida + "/RESIDUOS", "linha_voronoi_" + str(fid) +".shp" , "POLYLINE", "", "", "",
                          projecao_geo)

    cursor_insert = arcpy.da.InsertCursor(dirLinhaVoronoi, ['Id', 'SHAPE@'])


    poligono_shapely = loads(poligono.WKT)
    points = np.array(lista_pontos)
    vor = Voronoi(points)
    lines = [
        shapely.geometry.LineString(vor.vertices[line])
        for line in vor.ridge_vertices
        if -1 not in line
    ]

    Id = 0
    polyline_final = None
    for line in lines:
        if poligono_shapely.contains(line):
            line_arcpy = arcpy.FromWKT(line.wkt, arcpy.SpatialReference(4674))
            cursor_insert.insertRow((Id, line_arcpy))
            Id += 1
    del cursor_insert
    arcpy.Dissolve_management(dirLinhaVoronoi,dirLinhaDissolvido)
    with arcpy.da.SearchCursor(dirLinhaDissolvido, ["SHAPE@"]) as cursor:
        for row in cursor:
            polyline_final = row[0]
    del cursor
    return polyline_final

def limpar_linha(linha_central, projecao_geo, projecao_plana):
    linha_resultado = None
    dictLinhas = {}
    Id = 0
    for part in linha_central.getPart():
        linha = arcpy.Polyline(part)
        first_point = arcpy.PointGeometry(linha.firstPoint)
        last_point = arcpy.PointGeometry(linha.lastPoint)
        dictLinhas[Id] = {"linha":linha, "first":first_point, "last":last_point, "firstIn":False, "lastIn":False}
        Id += 1

    Ids_descartar = []
    dictLinhasCopy = dictLinhas.copy()
    for id_1 in dictLinhas:
        first_1 = dictLinhas[id_1]["first"]
        last_1 = dictLinhas[id_1]["last"]
        for id_2 in dictLinhasCopy:
            if id_2 != id_1:
                first_2 = dictLinhas[id_2]["first"]
                last_2 = dictLinhas[id_2]["last"]
                if not first_1.disjoint(first_2):
                    dictLinhas[id_1]["firstIn"] = True
                    dictLinhas[id_2]["firstIn"] = True

                if not first_1.disjoint(last_2):
                    dictLinhas[id_1]["firstIn"] = True
                    dictLinhas[id_2]["lastIn"] = True

                if not last_1.disjoint(first_2):
                    dictLinhas[id_1]["lastIn"] = True
                    dictLinhas[id_2]["firstIn"] = True

                if not last_1.disjoint(last_2):
                    dictLinhas[id_1]["lastIn"] = True
                    dictLinhas[id_2]["lastIn"] = True

    for Id in dictLinhas:
        if not (dictLinhas[Id]["firstIn"] and dictLinhas[Id]["lastIn"]):
            if dictLinhas[Id]["firstIn"] or dictLinhas[Id]["lastIn"]:
                largura_linha = dictLinhas[Id]["linha"].projecAs(projecao_plana).length
                if largura_linha < 2:
                    Ids_descartar.append(Id)
                else:
                    ponto_fim = None
                    if not dictLinhas[Id]["firstIn"]:
                        ponto_fim =  dictLinhas[Id]["first"]
                    else:
                        ponto_fim =  dictLinhas[Id]["last"]
                    polyCirculoPlano = ponto_fim.projectAs(projecao_plana).buffer(50)
                    polyCirculo = polyCirculoPlano.projectAs(projecao_geo)
                    interCircLinha = polyCirculo.intersect(linha_central, 2)
                    nParts = interCircLinha.partCount
                    if nParts > 0:
                        Ids_descartar.append(Id)

    for Id in dictLinhas:
        if Id not in Ids_descartar:
            linha = dictLinhas[Id]['linha']
            if linha_resultado:
                linha_resultado = linha_resultado.union(linha)
            else:
                linha_resultado = linha

    return linha_resultado













