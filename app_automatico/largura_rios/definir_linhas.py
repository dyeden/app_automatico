from func_linhas import *
class DefinirLinhas():
    def __init__(self):
        self.poligono = None
        self.dict_poligono_descricao =   {
            "tipo": None,
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
        pontos_aolongo_linha(self.borda_poligono, self.intervalo_entre_linhas, self.projecao_plana, self.projecao_geo)


    def tipo_poligono(self):
        "descreve qual o tipo de poligono"
        self.dict_poligono_descricao["tipo"] = "rio_simples"

    def iniciar(self):
        print "iniciar o script"
        self.tipo_poligono()
        print self.dict_poligono_descricao
        if self.dict_poligono_descricao["tipo"] == "rio_simples":
            self.dissecar_poligono()

        return self.dict_poligono_descricao
