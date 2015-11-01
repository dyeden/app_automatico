import numpy as np
from scipy.spatial import Voronoi
import arcpy
import shapely.geometry
import shapely.ops
from shapely.wkt import loads
import shapely.prepared
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
    # import time
    # ini = time.time()

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
    # fim = time.time()
    # print "tempo tota1: ", fim-ini

    del cursor
    return polyline_final

def voronoi_pontos_shapely(lista_pontos, poligono, linha_borda, projecao_geo, dir_saida, fid):
    "calcula as linhas de voronoi interna com uma lista de pontos"

    poligono_shapely = loads(poligono.WKT)
    points = np.array(lista_pontos)
    vor = Voronoi(points)
    lines = [
        shapely.geometry.LineString(vor.vertices[line])
        for line in vor.ridge_vertices
        if -1 not in line
    ]

    Id = 0
    import time
    ini = time.time()
    prepared_polygon = shapely.prepared.prep(poligono_shapely)
    hits = filter(prepared_polygon.contains, lines)
    line_union = shapely.ops.unary_union(hits)
    line_merge = shapely.ops.linemerge(line_union)
    fim = time.time()
    print "tempo tota1: ", fim-ini
    polyline_final = arcpy.FromWKT(line_merge.wkt, arcpy.SpatialReference(4674))
    return polyline_final

def voronoi_linhas_soltas(lista_pontos, li_pontos_extent, linha_part):
    "retorna as linha de voronoi sem se intersectarem"
    linha_shapely = loads(linha_part.WKT)
    prepared_linha_part = shapely.prepared.prep(linha_shapely)
    total_index = len(lista_pontos)
    lista_linhas = []
    lista_linhas_final = []
    lista_linha_todas = []
    for Id in xrange(total_index-1):
        ponto1 = lista_pontos[Id]
        ponto2 = lista_pontos[Id+1]
        lista_4 = [ponto1, ponto2]
        lista_4 = lista_4 + li_pontos_extent
        points = np.array(lista_4)
        vor = Voronoi(points)
        lines = [
            shapely.geometry.LineString(vor.vertices[line])
            for line in vor.ridge_vertices
            if -1 not in line
        ]
        lista_linha_todas = lista_linha_todas + lines
        hits = filter(prepared_linha_part.intersects, lines)
        lines_union_f = shapely.ops.unary_union(hits)
        try:
            polyline = arcpy.FromWKT(lines_union_f.wkt, arcpy.SpatialReference(4674))
        except:
            print lines_union_f.wkt
            continue
        lista_linhas_final.append(polyline)
        lista_linhas = lista_linhas + hits
    line_union = shapely.ops.unary_union(lista_linhas)
    linhas_todas = shapely.ops.unary_union(lista_linha_todas)
    polyline_final = arcpy.FromWKT(line_union.wkt, arcpy.SpatialReference(4674))
    polyline_todas = arcpy.FromWKT(linhas_todas.wkt, arcpy.SpatialReference(4674))
    return lista_linhas_final, polyline_final


def limpar_linha(linha_central, projecao_geo, projecao_plana):
    def proximidade_pontos(x1,y1,x2,y2, delta = 0.00001):
        proxi_x = None
        proxi_y = None
        if x1 > x2:
            deltax = x1 - x2
        else:
            deltax = x2 - x1

        if deltax <= delta:
            proxi_x = True
        else:
            proxi_x = False

        if y1 > y2:
            deltay = y1 - y2
        else:
            deltay = y2 - y1

        if deltay <= delta:
            proxi_y = True
        else:
            proxi_y = False

        if proxi_x and proxi_y:
            return True
        else:
            return False
    linha_resultado = None
    dictLinhas = {}
    Id = 0
    id_pt = 0
    # separar as partes da linha central e identificar o primeiro e ultimo ponto
    for part in linha_central.getPart():
        idFirst = id_pt
        id_pt += 1
        idLast = id_pt
        id_pt += 1
        linha = arcpy.Polyline(part, projecao_geo)
        first_point = arcpy.PointGeometry(linha.firstPoint, projecao_geo)
        last_point = arcpy.PointGeometry(linha.lastPoint, projecao_geo)
        dictLinhas[Id] = {
                            "linha":linha, "first":first_point, "last":last_point,
                            "firstIn":False, "lastIn":False,
                            "idFirst":idFirst,  "idLast":idLast,
                            "Xfirst":first_point.labelPoint.X,  "Yfirst":first_point.labelPoint.Y,
                            "Xlast":last_point.labelPoint.X,  "Ylast":last_point.labelPoint.Y,
                            "listaFirst":[], "listaLast":[] #lista ids dos pontos que nao intersectam
                          }
        Id += 1

    # identificar quais pontas estao soltas
    Ids_descartar = []
    dictLinhasCopy = dictLinhas.copy()
    for id_1 in dictLinhas:
        first_1 = dictLinhas[id_1]["first"]
        last_1 = dictLinhas[id_1]["last"]
        id_1_first = dictLinhas[id_1]["idFirst"]
        id_1_last = dictLinhas[id_1]["idLast"]

        for id_2 in dictLinhasCopy:

            if id_1 != id_2:

                id_2_first = dictLinhas[id_2]["idFirst"]
                id_2_last = dictLinhas[id_2]["idLast"]

                first_2 = dictLinhas[id_2]["first"]
                last_2 = dictLinhas[id_2]["last"]

                if id_1_first not in dictLinhas[id_2]["listaFirst"] or id_2_first not in  dictLinhas[id_1]["listaFirst"]:
                    if not first_1.disjoint(first_2):
                        dictLinhas[id_1]["firstIn"] = True
                        dictLinhas[id_2]["firstIn"] = True
                    else:
                        dictLinhas[id_1]["listaFirst"].append(id_2_first)
                        dictLinhas[id_2]["listaFirst"].append(id_1_first)

                if id_1_first not in dictLinhas[id_2]["listaLast"] or id_2_last not in  dictLinhas[id_1]["listaFirst"]:
                    if not first_1.disjoint(last_2):
                        dictLinhas[id_1]["firstIn"] = True
                        dictLinhas[id_2]["lastIn"] = True
                    else:
                        dictLinhas[id_1]["listaFirst"].append(id_2_last)
                        dictLinhas[id_2]["listaLast"].append(id_1_first)

                if id_1_last not in dictLinhas[id_2]["listaFirst"] or id_2_first not in  dictLinhas[id_1]["listaLast"]:
                    if not last_1.disjoint(first_2):
                        dictLinhas[id_1]["lastIn"] = True
                        dictLinhas[id_2]["firstIn"] = True
                    else:
                        dictLinhas[id_1]["listaLast"].append(id_2_first)
                        dictLinhas[id_2]["listaFirst"].append(id_1_last)

                if id_1_last not in dictLinhas[id_2]["listaLast"] or id_2_last not in  dictLinhas[id_1]["listaLast"]:
                    if not last_1.disjoint(last_2):
                        dictLinhas[id_1]["lastIn"] = True
                        dictLinhas[id_2]["lastIn"] = True
                    else:
                        dictLinhas[id_1]["listaLast"].append(id_2_last)
                        dictLinhas[id_2]["listaLast"].append(id_1_last)

    #descartar as partes desnecessarias
    for Id in dictLinhas:
        if not (dictLinhas[Id]["firstIn"] and dictLinhas[Id]["lastIn"]):
            if dictLinhas[Id]["firstIn"] or dictLinhas[Id]["lastIn"]:
                largura_linha = dictLinhas[Id]["linha"].projectAs(projecao_plana).length
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
                    if nParts > 1:
                        Ids_descartar.append(Id)

    for Id in dictLinhas:
        if Id not in Ids_descartar:
            linha = dictLinhas[Id]['linha']
            if linha_resultado:
                linha_resultado = linha_resultado.union(linha)
            else:
                linha_resultado = linha

    return linha_resultado













