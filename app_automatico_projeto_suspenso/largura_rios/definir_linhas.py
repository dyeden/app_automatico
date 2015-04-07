import func_linhas
import arcpy
class DefinirLinhas():
    def __init__(self):
        self.poligono_ma = None
        self.diretorio_saida = None
        self.dict_poligono_descricao =   {
            "tipo": None,
            "subtipo":None,
            "metadados": None,
            "n_extremidades": 0

        }
        self.raio = 50
        self.dict_circ_desc = {
            "partes":None,
            "tipo_circulo":None,
            "pt_centro_circ":{"x_ptc":None,"y_ptc":None},
            "pt_medios_circ":{""},
            "pts_outros_circ":{"x_pt1":None,"y_pt1":None, "x_pt2":None,"y_pt2":None},
            "linha_largura":None,
            "linha_circulo":None,
            "loop_teste":0,
            "distancia_pt_inicio":0,
            "angulo_rad":None,
            "raio":self.raio
        }


        self.projecao_plana = None
        self.projecao_geo = None
        self.intervalo_entre_linhas = 10
        self.compri_linha_raio_x1 = None
        self.compri_linha_raio_x2 = None
        self.lista_pontos = None
        self.borda_linha_geo = None
        self.borda_linha_plana = None

    def dissecar_poligono(self):
        "gerar os pontos que percorrera as bordas do poligono, gerar borda"
        self.borda_linha_geo = self.poligono_ma.boundary()
        self.borda_linha_plana = self.borda_linha_geo.projectAs(self.projecao_plana)
        func_linhas.borda_linha_geo = self.borda_linha_geo
        func_linhas.borda_linha_plana = self.borda_linha_plana
        self.lista_pontos = \
            func_linhas.pontos_aolongo_linha()

    def tipo_poligono(self):
        "descreve qual o tipo de poligono"
        self.dict_poligono_descricao["tipo"] = "rio"

    def subtipo_rio(self):
        "definine qual o subtipo que o poligono rio pertence"
        self.dict_poligono_descricao["subtipo"] = "rio_simples"

    def montar_linhas(self):
        "montar linhas para rio"
        for ponto, distancia in self.lista_pontos:
            func_linhas.calc_tipo_ponto_buffer(
                ponto, self.raio, self.dict_poligono_descricao
            )

    def registrar_variaveis_func_linhas(self):
        "registra as variaveis necessarias para o script func_linhas"
        func_linhas.projecao_plana = self.projecao_plana
        func_linhas.projecao_geo = self.projecao_geo
        func_linhas.intervalo_entre_linhas = self.intervalo_entre_linhas
        func_linhas.poligono_ma = self.poligono_ma

    def iniciar(self):
        print "iniciar o script"
        self.registrar_variaveis_func_linhas()
        self.tipo_poligono()
        if self.dict_poligono_descricao["tipo"] == "rio":
            self.dissecar_poligono()
            self.montar_linhas()


        return self.dict_poligono_descricao
