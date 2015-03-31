from func_linhas import *
class DefinirLinhas():
    def __init__(self):
        self.poligono = None
        self.dict_poligono_descricao =   {
            "tipo": None,
            "subtipo":None,
            "metadados": None

        }
        self.projecao_plana = None
        self.projecao_geo = None
        self.raio = 50
        self.intervalo_entre_linhas = 10
        self.lista_pontos = None
        self.borda_poligono = None

    def dissecar_poligono(self):
        "gerar os pontos que percorrera as bordas do poligono, gerar borda"
        self.borda_poligono = self.poligono.boundary()
        self.lista_pontos = \
            pontos_aolongo_linha(self.borda_poligono, self.intervalo_entre_linhas, self.projecao_plana, self.projecao_geo)


    def tipo_poligono(self):
        "descreve qual o tipo de poligono"
        self.dict_poligono_descricao["tipo"] = "rio"

    def subtipo_rio(self):
        "definine qual o subtipo que o poligono rio pertence"
        self.dict_poligono_descricao["subtipo"] = "rio_simples"

    def montar_linhas(self):
        "montar linhas para rio"
        for ponto, distancia in self.lista_pontos:
            calc_tipo_ponto_buffer(
                ponto, self.raio, self.borda_poligono, self.projecao_plana, self.projecao_geo
            )



    def iniciar(self):
        print "iniciar o script"
        self.tipo_poligono()
        if self.dict_poligono_descricao["tipo"] == "rio":
            self.dissecar_poligono()
            self.montar_linhas()

        return self.dict_poligono_descricao
