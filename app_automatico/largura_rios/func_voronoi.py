import numpy as np
from scipy.spatial import Voronoi
import arcpy
import shapely.geometry
import shapely.ops
from shapely.wkt import loads
import shapely.prepared



from ponto_circ_borda import PtCircBorda


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

def voronoi_linhas_soltas(lista_pontos, li_pontos_extent, linha_part, projecao_geo):
    "retorna as linha de voronoi sem se intersectarem"
    spatialReference4674 = arcpy.SpatialReference(4674)
    linha_shapely = loads(linha_part.WKT)


    lista_linhas = []
    lista_linhas_final = []
    lista_linha_todas = []
    circvetores = PtCircBorda()
    diametroExtent = circvetores.distancia_dois_pontos(
        li_pontos_extent[0][0],li_pontos_extent[0][1],
        li_pontos_extent[1][0],li_pontos_extent[1][1],
    )
    if len(lista_pontos) < 2:
        lista_pontos = [
            [linha_part.lastPoint.X,linha_part.lastPoint.Y],
            [linha_part.firstPoint.X,linha_part.firstPoint.Y],

        ]
    total_index = len(lista_pontos)
    for Id in xrange(total_index-1):
        ponto1 = lista_pontos[Id]
        ponto2 = lista_pontos[Id+1]
        ptm_x = (ponto1[0] + ponto2[0])/2
        ptm_y = (ponto1[1] + ponto2[1])/2
        circvetores = PtCircBorda(ptm_x, ptm_y)
        ptx_m, pty_m, ptx_inv, pty_inv = \
        circvetores.retorna_pontos_metade_entre_vetores(ponto1[0], ponto1[1],ponto2[0], ponto2[1], diametroExtent)

        line_shapely = shapely.geometry.LineString([[ptx_m, pty_m], [ptx_inv, pty_inv]])
        # lista_4 = [ponto1, ponto2]
        # lista_4 = lista_4 + li_pontos_extent
        # points = np.array(lista_4)
        # vor = Voronoi(points)
        # lines = [
        #     shapely.geometry.LineString(vor.vertices[line])
        #     for line in vor.ridge_vertices
        #     if -1 not in line
        # ]
        # lista_linha_todas = lista_linha_todas + lines
        # hits = filter(prepared_linha_part.intersects, lines)
        # lines_union_f = shapely.ops.unary_union(hits)


        polyline = arcpy.FromWKT(line_shapely.wkt, spatialReference4674)

        lista_linhas_final.append(polyline)
        lista_linhas.append(line_shapely)
    line_union = shapely.ops.unary_union(lista_linhas)
    try:
        polyline_final = arcpy.FromWKT(line_union.wkt,spatialReference4674)
    except:
        print line_union.wkt
        pass
    return lista_linhas_final, polyline_final

def identificar_pontas_conex(linha_central, projecao_geo):
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
                    # if not first_1.disjoint(first_2):
                    if proximidade_pontos(dictLinhas[id_1]["Xfirst"], dictLinhas[id_1]["Yfirst"], dictLinhas[id_2]["Xfirst"], dictLinhas[id_2]["Yfirst"]):
                        dictLinhas[id_1]["firstIn"] = True
                        dictLinhas[id_2]["firstIn"] = True
                    else:
                        dictLinhas[id_1]["listaFirst"].append(id_2_first)
                        dictLinhas[id_2]["listaFirst"].append(id_1_first)

                if id_1_first not in dictLinhas[id_2]["listaLast"] or id_2_last not in  dictLinhas[id_1]["listaFirst"]:
                    # if not first_1.disjoint(last_2):
                    if proximidade_pontos(dictLinhas[id_1]["Xfirst"], dictLinhas[id_1]["Yfirst"], dictLinhas[id_2]["Xlast"], dictLinhas[id_2]["Ylast"]):
                        dictLinhas[id_1]["firstIn"] = True
                        dictLinhas[id_2]["lastIn"] = True
                    else:
                        dictLinhas[id_1]["listaFirst"].append(id_2_last)
                        dictLinhas[id_2]["listaLast"].append(id_1_first)

                if id_1_last not in dictLinhas[id_2]["listaFirst"] or id_2_first not in  dictLinhas[id_1]["listaLast"]:
                    # if not last_1.disjoint(first_2):
                    if proximidade_pontos(dictLinhas[id_1]["Xlast"], dictLinhas[id_1]["Ylast"], dictLinhas[id_2]["Xfirst"], dictLinhas[id_2]["Yfirst"]):

                        dictLinhas[id_1]["lastIn"] = True
                        dictLinhas[id_2]["firstIn"] = True
                    else:
                        dictLinhas[id_1]["listaLast"].append(id_2_first)
                        dictLinhas[id_2]["listaFirst"].append(id_1_last)

                if id_1_last not in dictLinhas[id_2]["listaLast"] or id_2_last not in  dictLinhas[id_1]["listaLast"]:
                    # if not last_1.disjoint(last_2):
                    if proximidade_pontos(dictLinhas[id_1]["Xlast"], dictLinhas[id_1]["Ylast"], dictLinhas[id_2]["Xlast"], dictLinhas[id_2]["Ylast"]):
                        dictLinhas[id_1]["lastIn"] = True
                        dictLinhas[id_2]["lastIn"] = True
                    else:
                        dictLinhas[id_1]["listaLast"].append(id_2_last)
                        dictLinhas[id_2]["listaLast"].append(id_1_last)

    return dictLinhas

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
                    # if not first_1.disjoint(first_2):
                    if proximidade_pontos(dictLinhas[id_1]["Xfirst"], dictLinhas[id_1]["Yfirst"], dictLinhas[id_2]["Xfirst"], dictLinhas[id_2]["Yfirst"]):
                        dictLinhas[id_1]["firstIn"] = True
                        dictLinhas[id_2]["firstIn"] = True
                    else:
                        dictLinhas[id_1]["listaFirst"].append(id_2_first)
                        dictLinhas[id_2]["listaFirst"].append(id_1_first)

                if id_1_first not in dictLinhas[id_2]["listaLast"] or id_2_last not in  dictLinhas[id_1]["listaFirst"]:
                    # if not first_1.disjoint(last_2):
                    if proximidade_pontos(dictLinhas[id_1]["Xfirst"], dictLinhas[id_1]["Yfirst"], dictLinhas[id_2]["Xlast"], dictLinhas[id_2]["Ylast"]):
                        dictLinhas[id_1]["firstIn"] = True
                        dictLinhas[id_2]["lastIn"] = True
                    else:
                        dictLinhas[id_1]["listaFirst"].append(id_2_last)
                        dictLinhas[id_2]["listaLast"].append(id_1_first)

                if id_1_last not in dictLinhas[id_2]["listaFirst"] or id_2_first not in  dictLinhas[id_1]["listaLast"]:
                    # if not last_1.disjoint(first_2):
                    if proximidade_pontos(dictLinhas[id_1]["Xlast"], dictLinhas[id_1]["Ylast"], dictLinhas[id_2]["Xfirst"], dictLinhas[id_2]["Yfirst"]):

                        dictLinhas[id_1]["lastIn"] = True
                        dictLinhas[id_2]["firstIn"] = True
                    else:
                        dictLinhas[id_1]["listaLast"].append(id_2_first)
                        dictLinhas[id_2]["listaFirst"].append(id_1_last)

                if id_1_last not in dictLinhas[id_2]["listaLast"] or id_2_last not in  dictLinhas[id_1]["listaLast"]:
                    # if not last_1.disjoint(last_2):
                    if proximidade_pontos(dictLinhas[id_1]["Xlast"], dictLinhas[id_1]["Ylast"], dictLinhas[id_2]["Xlast"], dictLinhas[id_2]["Ylast"]):
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













