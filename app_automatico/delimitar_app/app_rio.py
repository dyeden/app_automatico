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

    def salvar_linhas(self):
        fid_n = 5
        diretorio_linhas = self.diretorio_saida + "/LINHAS/LINHAS_FID_" + str(fid_n) + ".shp"
        arcpy.CreateFeatureclass_management(self.diretorio_saida + "/LINHAS", "LINHAS_FID_" + str(fid_n) + ".shp", "POLYLINE", "", "", "",
                              self.projecao_geo)
        arcpy.AddField_management(diretorio_linhas,"largura_m","Double")
        cursor_insert = arcpy.da.InsertCursor(diretorio_linhas, ['Id', 'SHAPE@', "largura_m"])
        n = 0
        for linha in  self.dict_poligono_descricao["metadados"]["linhas"]:
            linha_largura_poly = self.dict_linhas_completo[n]["linha_largura"]
            comprimento = linha_largura_poly.projectAs(self.projecao_plana).length
            cursor_insert.insertRow((n, linha_largura_poly, comprimento))
            n += 1
        del cursor_insert

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
        elif compri_app <= 10 and compri_app < 50:
            compri_app = 50
        elif compri_app <= 50 and compri_app < 200:
            compri_app = 100
        return compri_app

    def analisar_linhas(self):
        for id_linha in self.dict_poligono_descricao["metadados"]["linhas"]:
            print id_linha

            linha = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["linha_largura"]
            id_frente = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["id_frente"]
            if linha:
                linha_app = func_app.criar_linha_largura_app(linha, self.largura_app(linha))
                self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["linha_app"] = linha_app
            if linha == None or id_frente == None:
                if self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["tipo"] == 'extremidade':
                    if self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["subtipo"] == 'ponta':
                        pass

            elif self.dict_poligono_descricao["metadados"]["linhas"][id_frente]["linha_largura"] == None:
                pass

            else:
                linha_frente = self.dict_poligono_descricao["metadados"]["linhas"][id_frente]["linha_largura"]
                linha_app_frente = func_app.criar_linha_largura_app(linha_frente, self.largura_app(linha_frente))
                poligono = func_app.criar_poligono_app(linha_app, linha_app_frente)
                self.registrar_poligonos_app(poligono, id_linha, id_frente)
                if id_linha == 0:
                    id_atras = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["id_atras"]
                    if id_atras:
                        linha_atras = self.dict_poligono_descricao["metadados"]["linhas"][id_atras]["linha_largura"]
                        linha_app_atras = func_app.criar_linha_largura_app(linha_atras, self.largura_app(linha_atras))
                        poligono = func_app.criar_poligono_app(linha_app, linha_app_atras)
                        self.registrar_poligonos_app(poligono, id_linha, id_atras)

    def registrar_variaveis_func_app(self):
        func_app.projecao_plana = self.projecao_plana
        func_app.projecao_geo = self.projecao_geo

    def iniciar_codigo(self):
        self.registrar_variaveis_func_app()
        self.analisar_linhas()
        return self.dict_app_poligonos