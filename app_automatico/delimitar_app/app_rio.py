import arcpy
class AppRio():
    def __init__(self):
        self.diretorio_saida = None
        self.dict_poligono_descricao = None
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
    def analisar_linhas(self):
        for linha in self.dict_poligono_descricao["metadados"]["linhas"]:
            pass
    def iniciar_codigo(self):
        self.analisar_linhas()