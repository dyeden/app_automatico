import func_linhas
import func_retangulo
import arcpy
arcpy.env.outputMFlag = "Disabled"
arcpy.env.outputZFlag = "Disabled"
class DefinirLinhas():
    def __init__(self):
        self.poligono_ma = None
        self.diretorio_saida = None
        self.dict_poligono_descricao =   {
            "tipo": None,
            "subtipo":None,
            "metadados":{"linhas":{
                0:{
                    "id_linha_braco":None,
                    "id_frente":None,
                    "id_atras":None,
                    "linha_largura":None,
                    "linha_app":None,
                    "braco":None,
                    "distancia":None,
                    "tipo":None,

                }
            },
                         "bracos":{
                             0:{
                                 "pt_ini":None,
                                 "pt_ini_oposto":None,
                                 "n_extremidades":0,
                                 "ponta":None,
                                 "base":None
                             }
                         }},
            "n_extremidades": 0,
            "pt_ini":None,
            "pt_ini_borda_oposta":None,
        }
        self.raio = 50

        self.dict_circ_desc = {
            "tipo_circulo":None,
            "subtipo":None,
            "circ_borda_geo":None,
            "partes":None,
            "pt_centro_circ":{"x_ptc":None,"y_ptc":None},
            "pt_medios_circ":{""},
            "pts_outros_circ":{"x_pt1":None,"y_pt1":None, "x_pt2":None,"y_pt2":None},
            "linha_largura":None,
            "linha_circulo":None,
            "loop_validar":0,
            "distancia_pt_inicio":0,
            "compri_linha_raio_x1":0,
            "compri_linha_raio_x2":0,
            "angulo_rad":None,
            "n_loop_extremidade":0,
            "raio":self.raio,
        }


        self.projecao_plana = None
        self.projecao_geo = None
        self.intervalo_entre_linhas = 10
        self.compri_linha_raio_x1 = None
        self.compri_linha_raio_x2 = None
        self.dict_lista_pontos = None
        self.borda_linha_geo = None
        self.borda_linha_plana = None
        self.finalizar_linhas = False

    def dissecar_poligono(self):
        "gerar os pontos que percorrera as bordas do poligono, gerar borda"
        self.borda_linha_geo = self.poligono_ma.boundary()
        self.borda_linha_plana = self.borda_linha_geo.projectAs(self.projecao_plana)
        func_linhas.borda_linha_geo = self.borda_linha_geo
        func_linhas.borda_linha_plana = self.borda_linha_plana
        self.dict_lista_pontos = \
            func_linhas.pontos_aolongo_linha()

    def tipo_poligono(self):
        "descreve qual o tipo de poligono"
        self.dict_poligono_descricao["tipo"] = "rio"

    def subtipo_rio(self):
        "definine qual o subtipo que o poligono rio pertence"
        self.dict_poligono_descricao["subtipo"] = "rio_simples"

    def atualizar_poligono_descricao(self, id_linha, distancia, id_braco, id_linha_braco, ponto):
        "atualiza as informacoes conforme o progresso de leitura da borda"

        self.dict_poligono_descricao["metadados"]["linhas"][id_linha] = {
                "id_linha_braco":id_linha_braco,
                "id_frente":None,
                "id_atras":None,
                "linha_largura":self.dict_circ_desc["linha_largura"],
                "linha_app":None,
                "braco":None,
                "distancia":distancia,
                "tipo":self.dict_circ_desc["tipo_circulo"],
            }

        if self.dict_circ_desc["tipo_circulo"] == "extremidade":
            self.dict_poligono_descricao["metadados"]["bracos"][id_braco]["n_extremidades"] += 1

        if self.dict_poligono_descricao["metadados"]["bracos"][id_braco]["n_extremidades"] == 2:
            self.finalizar_linhas = True



        if id_linha_braco == 0:
            self.dict_poligono_descricao["metadados"]["bracos"][id_braco] ={
                     "id_linha_ini":None,
                     "pt_ini":None,
                     "pt_ini_oposto":None,
                     "n_extremidades":0,
                     "ponta":None,
                     "base":None,
                     "distancia_oposta":None
                 }
            ponto_oposto = func_linhas.ponto_oposto(ponto, self.dict_circ_desc)
            distancia_oposta = func_linhas.calc_distancia_oposta( self.dict_circ_desc, self.dict_lista_pontos[distancia+self.intervalo_entre_linhas])
            self.dict_poligono_descricao["metadados"]["bracos"][id_braco]["id_linha_ini"] = id_linha
            self.dict_poligono_descricao["metadados"]["bracos"][id_braco]["pt_ini"] = ponto
            self.dict_poligono_descricao["metadados"]["bracos"][id_braco]["pt_ini_oposto"] = ponto_oposto
            self.dict_poligono_descricao["metadados"]["bracos"][id_braco]["distancia_oposta"] = distancia_oposta

        if id_linha > 0:
            if self.dict_poligono_descricao["metadados"]["linhas"][id_linha - 1]["tipo"] == "extremidade":
                if self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["tipo"] == "meio":
                    id_linha_ini = self.dict_poligono_descricao["metadados"]["bracos"][id_braco]["id_linha_ini"]
                    self.dict_poligono_descricao["metadados"]["linhas"][id_linha_ini]["id_atras"] = id_linha
            else:
                self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["id_atras"] = id_linha - 1
                self.dict_poligono_descricao["metadados"]["linhas"][id_linha - 1]["id_frente"] = id_linha
        if self.dict_circ_desc["tipo_circulo"] == "extremidade":
            if self.dict_circ_desc["subtipo"] == "ponta":
                poligono_ponta = func_linhas.calc_poligono_ponta(
                    self.dict_poligono_descricao["metadados"]["linhas"][id_linha - 1]["linha_largura"],
                    self.dict_poligono_descricao["metadados"]["linhas"][id_linha - 2]["linha_largura"]
                )
                self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["poligono_ponta"] = poligono_ponta
                self.dict_poligono_descricao["metadados"]["linhas"][id_linha]["subtipo"] = "ponta"


    def montar_linhas(self):
        "montar linhas para rio"
        id_linha = 0
        id_linha_braco = 0
        id_braco = 0
        distancia = 0
        compri_total = self.dict_lista_pontos["compri_total"]
        while distancia < compri_total:
            ponto = self.dict_lista_pontos[distancia]

            print distancia

            validar_circulo = False
            self.dict_circ_desc["loop_validar"] = 0
            self.dict_circ_desc["distancia_pt_inicio"] = distancia
            while validar_circulo == False:
                self.dict_circ_desc = func_linhas.calc_tipo_circ_borda(
                    ponto, self.dict_poligono_descricao, self.dict_circ_desc
                )
                self.dict_circ_desc, validar_circulo = func_linhas.aferir_circulo(self.dict_circ_desc)
                self.dict_circ_desc["loop_validar"] += 1
            self.atualizar_poligono_descricao(id_linha, distancia, id_braco, id_linha_braco, ponto)
            if self.dict_circ_desc["tipo_circulo"] == "extremidade":
                distancia = int(self.dict_poligono_descricao["metadados"]["bracos"][id_braco]['distancia_oposta']/10)*10
                print "extremidade"
                print "parar aqui"
            if self.finalizar_linhas:
                break
            id_linha += 1
            id_linha_braco += 1
            distancia += self.intervalo_entre_linhas

    def montar_linhas_retangular(self, li_ret_base, li_ret_largura):
        lin_base_plana_1 = li_ret_base[0].projectAs(self.projecao_plana)
        lin_base_plana_2 = li_ret_base[1].projectAs(self.projecao_plana)
        compri_total = lin_base_plana_1.length
        distancia = 0

        while distancia < compri_total:
            print distancia
            distancia += self.intervalo_entre_linhas


    def direcionar_processo(self):
        area_ma = self.poligono_ma.area
        perimetro_ma = self.poligono_ma.length
        frac_p = func_retangulo.dimensao_fractal(perimetro_ma, area_ma)
        li_ret_largura = None
        li_ret_base = None
        if frac_p < 1.12:
            point_centroid = self.poligono_ma.centroid
            delta = 0.087266462
            rad_90 = 1.570796327
            melhor_ang = func_retangulo.func_melhor_angulo(0,rad_90, delta, point_centroid,
                                                           self.poligono_ma, self.projecao_geo)
            inter_fim = melhor_ang + delta
            inter_ini = melhor_ang - delta
            delta2 = delta/10
            melhor_ang = func_retangulo.func_melhor_angulo(inter_ini, inter_fim, delta2, point_centroid,
                                                           self.poligono_ma, self.projecao_geo)
            poly_rot = func_retangulo.rotacionar_poligono(self.poligono_ma, point_centroid, melhor_ang, self.projecao_geo)
            retangulo = func_retangulo.ret_envolvente(poly_rot, self.projecao_geo)
            ret_rot = func_retangulo.rotacionar_poligono(retangulo, point_centroid, - melhor_ang, self.projecao_geo)
            area_ret_rot = ret_rot.projectAs(self.projecao_plana).area
            ret_p = area_ma/area_ret_rot
            if ret_p > 0.6:
                li_ret_base, li_ret_largura = func_retangulo.bases_larguras(self.poligono_ma)
                if li_ret_largura[0].length/li_ret_base[0].length > 0.3:
                    tipo = "retangulo"
                else:
                    tipo = "circulo"
                return tipo, li_ret_base, li_ret_largura
            else:
                return "circulo", li_ret_base, li_ret_largura
        else:
            return "circulo", li_ret_base, li_ret_largura


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
            tipo, li_ret_base, li_ret_largura = self.direcionar_processo()
            if tipo == "circulo":
                self.dissecar_poligono()
                self.montar_linhas()
            elif tipo == "retangulo":
                self.montar_linhas_retangular(li_ret_base, li_ret_largura)

        return self.dict_poligono_descricao
