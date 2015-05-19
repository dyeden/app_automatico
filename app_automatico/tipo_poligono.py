import arcpy
class TipoPoligono():
    def __init__(self):
        self.poligono_ma = None
        self.diretorio_saida = None
        self.projecao_plana = None
        self.projecao_geo = None
    def analisar_lago(self):
        pass
    def analisar_poligono(self):
        x_max = self.poligono_ma.extent.XMax
        x_min = self.poligono_ma.extent.XMin
        y_max = self.poligono_ma.extent.YMax
        y_min = self.poligono_ma.extent.YMin
        relacao_arestas = min(x_max-x_min, y_max-y_min)/max(x_max-x_min,y_max-y_min)
        if relacao_arestas > 0.8:
            self.analisar_lago()
        print type(self.poligono_ma.extent)

    def iniciar_codigo(self):

        return self.analisar_poligono()