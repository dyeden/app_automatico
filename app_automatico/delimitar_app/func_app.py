projecao_plana = None
projecao_geo = None
intervalo_entre_linhas = None
poligono_ma = None
borda_linha_geo = None
borda_linha_plana = None
from func_circulo import PtCircBorda

def criar_linha_largura_app(linha):
    compri_linha = linha.projectAs(projecao_plana).length
    largura_app = 50
    circ_linha_1 = linha.projectAs(projecao_plana).buffer(largura_app).projectAs(projecao_geo)


def criar_poligono_app(linha, linha_frente):
    compri_linha = linha.projectAs(projecao_plana).length
    compri_linha_frente = linha_frente.projectAs(projecao_plana).length
    compri_app_linha = identificar_largura_app(compri_linha)
    compri_app_linha_frente = identificar_largura_app(compri_linha_frente)
    circ_linha =
