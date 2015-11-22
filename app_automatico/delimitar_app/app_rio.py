import arcpy
import func_app

class AppRio():
    def __init__(self):
        self.id_poligono_app = 0
        self.diretorio_saida = None
        self.dict_poligono_descricao = None
        self.dict_app_poligonos = {}
        self.projecao_plana = None
        self.projecao_geo = None

    def registrar_poligonos_app(self, poligono, id_linha_1, id_linha_2):
        self.dict_app_poligonos[self.id_poligono_app] = {
            "poligono":poligono,
            "id_linha_1":id_linha_1,
            "id_linha_2":id_linha_2
        }
        self.id_poligono_app += 1

    def largura_app(self, linha):
        compri_linha = linha.projectAs(self.projecao_plana).length
        compri_app = None
        if compri_linha < 10:
            compri_app = 30
        elif compri_linha >= 10 and compri_linha < 50:
            compri_app = 50
        elif compri_linha >= 50 and compri_linha < 200:
            compri_app = 100
        elif compri_linha >= 200 and compri_linha < 600:
            compri_app = 200
        else:
            compri_app = 600
        return compri_app

    def analisar_linhas(self):

        for id_linha in self.dict_poligono_descricao["metadados"]["linhas"]:
            "para cada linha de largura do rio e criada uma linha de app"
            linha = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["linha_largura"]
            if linha:
                linha_app = func_app.criar_linha_largura_app(linha, self.largura_app(linha))
                self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["linha_app"] = linha_app

        for id_linha in self.dict_poligono_descricao["metadados"]["linhas"]:
            linha = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["linha_largura"]
            id_frente = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["id_frente"]

            if linha == None or id_frente == None:
                if self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["tipo"] == 'extremidade':
                    "determina uma app para as extremidades"

                    if self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["subtipo"] == 'ponta':
                        id_atras = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["id_atras"]
                        poligono_ponta = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]['poligono_ponta']
                        poligono = poligono_ponta.projectAs(self.projecao_plana).buffer(30).projectAs(self.projecao_geo)
                        self.registrar_poligonos_app(poligono, id_linha, id_atras)

            elif self.dict_poligono_descricao["metadados"]["linhas"][id_frente]["linha_largura"] == None:
                pass

            else:
                "cria a app usando as linhas de app"
                linha_app = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["linha_app"]
                linha_app_frente = self.dict_poligono_descricao["metadados"]["linhas"][id_frente]["linha_app"]
                poligono = func_app.criar_poligono_app(linha_app, linha_app_frente)
                self.registrar_poligonos_app(poligono, id_linha, id_frente)
                if id_linha == 0:
                    id_atras = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["id_atras"]
                    if id_atras:
                        linha_app_atras = self.dict_poligono_descricao["metadados"]["linhas"][id_atras]["linha_app"]
                        poligono = func_app.criar_poligono_app(linha_app, linha_app_atras)
                        self.registrar_poligonos_app(poligono, id_linha, id_atras)

    def analisar_linhas_voronoi(self):
        for id_linha in self.dict_poligono_descricao["metadados"]["linhas"]:
            id_frente = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["id_frente"]
            if id_frente is not None:
                linha1 = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["linha_largura"]
                linha2 = self.dict_poligono_descricao["metadados"]["linhas"][id_frente]["linha_largura"]
                linha_app1 = func_app.criar_linha_largura_app(linha1, self.largura_app(linha1))
                linha_app2 = func_app.criar_linha_largura_app(linha2, self.largura_app(linha2))
                poligono = func_app.criar_poligono_app_hull(linha_app2, linha_app1)
                self.registrar_poligonos_app(poligono, id_frente, id_linha)

    def registrar_variaveis_func_app(self):
        func_app.projecao_plana = self.projecao_plana
        func_app.projecao_geo = self.projecao_geo

    def iniciar_codigo(self):
        self.registrar_variaveis_func_app()
        if  self.dict_poligono_descricao["metodo"] == "voronoi":
            self.analisar_linhas_voronoi()
        else:
            self.analisar_linhas()
        return self.dict_app_poligonos, self.dict_poligono_descricao