from shapely import speedups
speedups.enable()
import numpy as np
from scipy.spatial import Voronoi
import arcpy
import shapely.geometry
import shapely.ops
from shapely.wkt import loads
import shapely.prepared
import itertools



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
    import time
    ini_total = time.time()
    poligono_shapely = loads(poligono.WKT)
    points = np.array(lista_pontos)
    vor = Voronoi(points)
    lines = [
        shapely.geometry.LineString(vor.vertices[line])
        for line in vor.ridge_vertices
        if -1 not in line
    ]

    Id = 0

    ini = time.time()
    prepared_polygon = shapely.prepared.prep(poligono_shapely)
    hits = filter(prepared_polygon.contains, lines)
    line_union = shapely.ops.unary_union(hits)
    line_merge = shapely.ops.linemerge(line_union)
    fim = time.time()
    print "tempo tota1: ", fim-ini_total
    print "tempo union: ", fim-ini
    polyline_final = arcpy.FromWKT(line_merge.wkt, arcpy.SpatialReference(4674))
    return polyline_final

def gerar_linhas_largura(poligono, lista_pontos, li_pontos_extent, linha_part, projecao_geo):
    "retorna linhas entre par de pontos"
    spatialReference4674 = arcpy.SpatialReference(4674)
    linha_shapely = linha_part

    lista_linhas = []
    lista_linhas_final = []
    circvetores = PtCircBorda()
    diametroExtent = circvetores.distancia_dois_pontos(
        li_pontos_extent[0][0],li_pontos_extent[0][1],
        li_pontos_extent[1][0],li_pontos_extent[1][1],
    )
    if len(lista_pontos) <= 2:
        lista_pontos = [
            linha_part.coords[0],
            [linha_part.centroid.x,linha_part.centroid.y],
            linha_part.coords[-1],
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
        ponto_m = shapely.geometry.Point([ptm_x, ptm_y])
        linha_largura = line_shapely.intersection(poligono)

        if linha_largura._is_empty:
            continue
        try:
            if linha_largura.type != "LineString":
                bufferM = ponto_m.buffer(0.000005)
                prepared_bufferM = shapely.prepared.prep(bufferM)
                hits = filter(prepared_bufferM.intersects, linha_largura)
                linha_largura = hits[0]
            polyline = arcpy.FromWKT(linha_largura.wkt, spatialReference4674)
        except:
            continue


        lista_linhas_final.append(polyline)
        lista_linhas.append(linha_largura)
    line_union = shapely.ops.unary_union(lista_linhas)
    polyline_final = arcpy.FromWKT(line_union.wkt,spatialReference4674)
    return lista_linhas_final, polyline_final

def cortar_conexoes(poligono, linhas, pontos, raio = 0.005):


    linhas = loads(linhas.WKT)
    poligono = loads(poligono.WKT)
    lista_polysCortar = []
    if pontos.type == "Point":
        lista_pontos = [pontos]
    else:
        lista_pontos = pontos
    for ponto in lista_pontos:
        circulo = ponto.buffer(0.0001)
        polyConex = circulo.intersection(linhas).buffer(0.000005)
        bordaCirculo = circulo.boundary
        circunDividida = bordaCirculo.difference(polyConex)
        linhas_merge = shapely.ops.linemerge(circunDividida)
        lista_linhas = list(linhas_merge)
        funcCirculoBorda = PtCircBorda(ponto.x, ponto.y)
        lista_linhasm = []
        for linha_part in lista_linhas:
            pt1x = linha_part.coords[0][0]
            pt1y = linha_part.coords[0][1]
            pt2x = linha_part.coords[-1][0]
            pt2y = linha_part.coords[-1][1]

            ptx_m, pty_m, ptx_inv, pty_inv = funcCirculoBorda.retorna_pontos_metade_entre_vetores(
              pt1x, pt1y, pt2x, pt2y, raio
            )
            linha_metade = shapely.geometry.LineString([[ponto.x, ponto.y], [ptx_m, pty_m]])
            linham_poly_final= None
            linham_poly = linha_metade.intersection(poligono)
            if linham_poly.type != "LineString":
                for linham in list(linham_poly):
                    if linham.intersects(circulo):
                        linham_poly_final = linham
            else:
                linham_poly_final = linham_poly
            lista_linhasm.append(linham_poly_final)
            pass
        linhasm_unidas = shapely.ops.unary_union(lista_linhasm)
        polyCortador = linhasm_unidas.buffer(0.000005)
        lista_polysCortar.append(polyCortador)
    polyCortarUnido = shapely.ops.unary_union(lista_polysCortar)
    poligonos_separados = poligono.difference(polyCortarUnido)
    return poligonos_separados

def PontosInterFim(linhas):
    lines = list(loads(linhas.WKT))
    endpts = [(shapely.geometry.Point(list(line.coords)[0]), shapely.geometry.Point(list(line.coords)[-1])) for line  in lines]
    endpts = [pt for sublist in endpts  for pt in sublist]
    inters = []
    for line1,line2 in  itertools.combinations(lines, 2):
      if  line1.intersects(line2):
        inter = line1.intersection(line2)
        if "Point" == inter.type:
            inters.append(inter)

    point_todos = shapely.ops.unary_union(endpts)
    point_inter = shapely.ops.unary_union(inters)
    point_fim = point_todos.difference(point_inter)
    return point_todos, point_inter, point_fim

def indetiLinePoly(poligonos, linhas):
    linhas = loads(linhas.WKT)
    listaLinhaPoligono = []

    if poligonos.type == "Polygon":
        lista_poligonos = [poligonos]
    else:
        lista_poligonos = list(poligonos)
    for poligono in lista_poligonos:
        prepared_poligono = shapely.prepared.prep(poligono)
        hits = filter(prepared_poligono.intersects, linhas)
        try:
            linha_part = hits[0]
        except:
            continue
        listaLinhaPoligono.append([linha_part, poligono])
    return listaLinhaPoligono

def limpar_linha_CircBorda(pontos_fim, linhas, poligono, linha_borda, projecao_plana, raio = 0.0009):
    spatialReference4674 = arcpy.SpatialReference(4674)
    PontosLinhas_descartar = []
    linhas_descartar = []
    linhas = loads(linhas.WKT)
    poligono = loads(poligono.WKT)
    linha_borda = loads(linha_borda.WKT)

    for ponto in pontos_fim:
        prepared_ponto = shapely.prepared.prep(ponto)
        hits = filter(prepared_ponto.intersects, linhas)

        linha = hits[0]
        linhaarcpy = arcpy.FromWKT(linha.wkt, spatialReference4674)
        largura = linhaarcpy.projectAs(projecao_plana).length
        try:
            if largura < 13:
                linhas_descartar.append(linha)
                PontosLinhas_descartar.append(linha.centroid)
            elif largura < 110:
                polyCirc = ponto.buffer(raio)
                linhaPartBorda = linha_borda.intersection(polyCirc)
                if  linhaPartBorda.type == 'LineString':
                    ptCentroid = linhaPartBorda.centroid
                    CircCentroid = ptCentroid.buffer(0.0003)
                    polyInter = linha_borda.intersection(CircCentroid).buffer(0.000005)
                    BoundaryCirc = CircCentroid.boundary
                    linhas_circ = BoundaryCirc.difference(polyInter)
                    linhas_circ = shapely.ops.linemerge(linhas_circ)
                    li_linhas_circ = list(linhas_circ)
                    if len(li_linhas_circ) == 2:
                        linha1 = li_linhas_circ[0]
                        linha2 = li_linhas_circ[1]
                        if linha1.length > linha2.length:
                            linhaMaior = linha1
                            linhaMenor= linha2
                        else:
                            linhaMaior = linha2
                            linhaMenor = linha1

                        totalLength = linhaMenor.length + linhaMaior.length
                        if (linhaMenor.length/totalLength) > 0.4:
                            linhas_descartar.append(linha)
                            PontosLinhas_descartar.append(linha.centroid)
        except:
            print "erro limpar_linha_CircBorda  ", "ponto", ponto.wkt

    # PontosDescartarUnion = shapely.ops.unary_union(PontosLinhas_descartar)
    # prepared_pontos = shapely.prepared.prep(PontosDescartarUnion)
    #
    # hits = filter(prepared_pontos.disjoint, linhas)
    # linhas_resultado = shapely.ops.unary_union(hits)
    # linhas_resultado = shapely.ops.linemerge(linhas_resultado)

    LinhasDescartarUnion = shapely.ops.unary_union(linhas_descartar)
    linhas_resultado = linhas.difference(LinhasDescartarUnion)
    linhas_resultado = shapely.ops.linemerge(linhas_resultado)
    poligonos_linha = list(shapely.ops.polygonize(linhas_resultado))

    liTodasLinhasNovas = []
    linhas_descartar = []
    for poly in poligonos_linha:
        if poligono.contains(poly):
            poly_arcpy = arcpy.FromWKT(poly.wkt, spatialReference4674)
            area = poly_arcpy.projectAs(projecao_plana).area
            if area < 250:
                boundarydescartar = poly.boundary
                linhas_descartar.append(boundarydescartar)
                centroidPoly = poly.centroid
                poly_boundary = poly.buffer(0.000005).boundary
                prepared_boundary = shapely.prepared.prep(poly_boundary)
                hits = filter(prepared_boundary.intersects, linhas_resultado)
                for resultlinha in hits:
                    linhas_descartar.append(resultlinha)
                    pt_ini = shapely.geometry.Point(resultlinha.coords[0])
                    pt_fim = shapely.geometry.Point(resultlinha.coords[-1])
                    liLinhaNova = []
                    if pt_ini.intersects(poly):
                        liLinhaNova.append(centroidPoly.coords[0])
                        for coord in resultlinha.coords:
                            liLinhaNova.append(coord)
                    else:
                        for coord in resultlinha.coords:
                            liLinhaNova.append(coord)
                        liLinhaNova.append(centroidPoly.coords[0])
                    linha_nova = shapely.geometry.LineString(liLinhaNova)
                    liTodasLinhasNovas.append(linha_nova)
    if liTodasLinhasNovas:
        linhasNovas = shapely.ops.unary_union(liTodasLinhasNovas)
        LinhasDescartarUnion = shapely.ops.unary_union(linhas_descartar)
        linhas_resultado = linhas_resultado.difference(LinhasDescartarUnion)
        linhas_resultado = linhas_resultado.union(linhasNovas)
        linhas_resultado = shapely.ops.linemerge(linhas_resultado)
    linhas_resultado = arcpy.FromWKT(linhas_resultado.wkt, spatialReference4674)
    return linhas_resultado

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

