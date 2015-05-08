import arcpy
import func_app

class AppRio():
    def __init__(self):
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
    def registrar_poligonos_app(self, poligono, id_linha, id_linha_frente):
        self.dict_app_poligonos[id_linha] = poligono
    def analisar_linhas(self):
        for id_linha in self.dict_poligono_descricao["metadados"]["linhas"]:
            try:
                linha = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["linha_largura"]
                id_frente = self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["id_frente"]
                linha_frente = self.dict_poligono_descricao["metadados"]["linhas"][id_frente]["linha_largura"]
                poligono = func_app.criar_poligono_app(linha, linha_frente)
                self.registrar_poligonos_app(poligono, id_linha, id_frente)
            except:
                pass
    def registrar_variaveis_func_app(self):
        func_app.projecao_plana = self.projecao_plana
        func_app.projecao_geo = self.projecao_geo
    def iniciar_codigo(self):
        self.registrar_variaveis_func_app()
        self.analisar_linhas()
        return self.dict_app_poligonos