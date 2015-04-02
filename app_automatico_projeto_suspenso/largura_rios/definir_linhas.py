import func_linhas
class DefinirLinhas():
    def __init__(self):
        self.poligono = None
        self.dict_poligono_descricao =   {
            "tipo": None,
            "subtipo":None,
            "metadados": None,
            "n_extremidades": 0

        }
        self.projecao_plana = None
        self.projecao_geo = None
        self.raio = 50
        self.intervalo_entre_linhas = 10
        self.lista_pontos = None
        self.borda_linha_geo = None
        self.borda_linha_plana = None

    def dissecar_poligono(self):
        "gerar os pontos que percorrera as bordas do poligono, gerar borda"
        self.borda_linha_geo = self.poligono.boundary()
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
        func_linhas.poligono = self.poligono

    def iniciar(self):
        print "iniciar o script"
        self.registrar_variaveis_func_linhas()
        self.tipo_poligono()
        if self.dict_poligono_descricao["tipo"] == "rio":
            self.dissecar_poligono()
            self.montar_linhas()


        return self.dict_poligono_descricao
