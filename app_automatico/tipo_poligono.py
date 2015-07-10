import arcpy
class TipoPoligono():
    def __init__(self):
        self.poligono_ma = None
        self.diretorio_saida = None
        self.projecao_plana = None
        self.projecao_geo = None

    def analisar_lago(self, poligono, n_li = 10):
        x_max = poligono.extent.XMax
        x_min = poligono.extent.XMin
        y_max = poligono.extent.YMax
        y_min = poligono.extent.YMin
        x_cent = poligono.centroid.X
        y_cent = poligono.centroid.Y
        array = arcpy.Array()
        array.add(arcpy.Point(x_min,y_min))
        array.add(arcpy.Point(x_min,y_max))
        array.add(arcpy.Point(x_max,y_max))
        array.add(arcpy.Point(x_max,y_min))
        array.add(arcpy.Point(x_min,y_min))
        linha_envelope = arcpy.Polyline(array, self.projecao_geo)
        del array
        len_li_envelope = linha_envelope.length
        n_inter = len_li_envelope/n_li
        len_li = 0
        while len_li < len_li_envelope:
            ponto_env = linha_envelope.positionAlongLine(len_li)
            array = arcpy.Array()
            array.add(arcpy.Point(ponto_env.firstPoint.X, ponto_env.firstPoint.Y))
            array.add(arcpy.Point(x_cent,y_cent))
            linha_cent_env = arcpy.Polyline(array, self.projecao_geo)
            del array
            ponto_inter = linha_cent_env.intersect(poligono, 1)
            if ponto_inter.partCount > 1:
                return "rio"
            len_li += n_inter
        return "lago"

    def analisar_poligono(self):
        tipo = None
        x_max = self.poligono_ma.extent.XMax
        x_min = self.poligono_ma.extent.XMin
        y_max = self.poligono_ma.extent.YMax
        y_min = self.poligono_ma.extent.YMin
        relacao_arestas = min(x_max-x_min, y_max-y_min)/max(x_max-x_min,y_max-y_min)
        if relacao_arestas > 0.8:
            tipo = self.analisar_lago(self.poligono_ma)
        else:
            tipo = "rio"
        return tipo

    def iniciar_codigo(self):

        return self.analisar_poligono()