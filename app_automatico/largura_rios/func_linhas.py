import arcpy
def pontos_aolongo_linha(linha_borda, intervalo, projecao_plana, projecao_geo):
    linha_plana = linha_borda.projectAs(projecao_plana)
    lista_pontos = []
    compri_total = linha_plana.length
    compri_atual = 0
    while compri_atual < compri_total:
        print compri_atual
        ponto = linha_plana.positionAlongLine(compri_atual).projectAs(projecao_geo)
        lista_pontos.append((ponto,compri_atual))
        compri_atual += 10
    return lista_pontos

