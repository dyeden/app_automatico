from math import sqrt, acos, sin, cos, pi, atan
class CircVetores(object):
    def __init__(self, x0 = None, y0= None, pt1_x = None, pt1_y = None, pt2_x = None, pt2_y = None):
        self.x0 = x0; self.y0 = y0
        self.pt1_x = pt1_x; self.pt1_y = pt1_y; self.pt2_x = pt2_x; self.pt2_y = pt2_y

    def pt_medio(self):
        ptm_x = (self.pt1_x + self.pt2_x)/2
        ptm_y = (self.pt1_y + self.pt2_y)/2
        return ptm_x, ptm_y

    def distancia_dois_pontos(self, ponto1_x, ponto1_y, ponto2_x, ponto2_y):
        delta_x = (ponto2_x - ponto1_x)
        delta_y = (ponto2_y - ponto1_y)
        distancia = sqrt(delta_x*delta_x + delta_y*delta_y)
        return distancia

    def eq_circ_achar_x(self,y, raio):
        a = self.x0
        b = self.y0
        x = a + sqrt(pow(raio,2) - pow(y - b, 2))
        return x

    def eq_circ_achar_y(self,x, raio):
        a = self.x0
        b = self.y0
        y = b + sqrt(pow(raio,2) - pow(x - a, 2))
        return y

    def eq_circ_achar_raio(self, x, y):
        a = self.x0
        b = self.y0
        raio =  sqrt(pow((x-a),2) + pow((y-b),2))
        return raio

    def converter_pontos_para_vetores_circ(self, ponto_x, ponto_y):
        vetor_x = ponto_x - self.x0
        vetor_y = ponto_y - self.y0
        return vetor_x, vetor_y

    def converter_vetores_circ_para_pontos(self, vetor_x, vetor_y):
        ponto_x = vetor_x + self.x0
        ponto_y = vetor_y + self.y0
        return ponto_x, ponto_y

    def eq_ang_entre_vetores(self, ponto1_x, ponto1_y, ponto2_x, ponto2_y):
        vetor_pt1_x, vetor_pt1_y = self.converter_pontos_para_vetores_circ(ponto1_x, ponto1_y)
        vetor_pt2_x, vetor_pt2_y = self.converter_pontos_para_vetores_circ(ponto2_x, ponto2_y)
        produto_esc = vetor_pt1_x*vetor_pt2_x + vetor_pt1_y*vetor_pt2_y
        magnitude_vetor_pt1 = sqrt(pow(vetor_pt1_x,2) + pow(vetor_pt1_y,2))
        magnitude_vetor_pt2 = sqrt(pow(vetor_pt2_x,2) + pow(vetor_pt2_y,2))
        angulo_rad = acos(produto_esc/(magnitude_vetor_pt1*magnitude_vetor_pt2))
        return angulo_rad

    def retorna_ponto_atraves_angulo(self, ang_rad, raio):
        vetor_x = cos(ang_rad)*raio
        vetor_y = sin(ang_rad)*raio
        ponto_x, ponto_y = self.converter_vetores_circ_para_pontos( vetor_x, vetor_y)
        return ponto_x, ponto_y

    def retorna_angulo_atraves_ponto(self, ponto_x, ponto_y):
        vetor_x, vetor_y = self.converter_pontos_para_vetores_circ(ponto_x, ponto_y)
        if vetor_x == 0:
            angulo = pi/2
        else:
            angulo = abs(atan(vetor_y/vetor_x))
        if vetor_x >= 0 and vetor_y >= 0:
            "QI"
            pass
        elif vetor_x < 0 and vetor_y > 0:
            "QII"
            angulo = pi - angulo
        elif vetor_x <= 0 and vetor_y < 0:
            "QIII"
            angulo = pi + angulo
        elif vetor_x > 0 and vetor_y < 0:
            "QIV"
            angulo = 2*pi - angulo
        return angulo

    def retorna_ponto_de_angulo_inverso(self, ang_rad, raio):
        ang_inverso = None
        if ang_rad < pi:
            ang_inverso = ang_rad + pi
        else:
            ang_inverso = ang_rad - pi
        x , y = self.retorna_ponto_atraves_angulo(ang_inverso, raio)
        return x, y

    def retorna_pontos_metade_entre_vetores(self, ponto1_x, ponto1_y, ponto2_x, ponto2_y, raio):
        angulo_pt1 = self.retorna_angulo_atraves_ponto(ponto1_x, ponto1_y)
        angulo_pt2 = self.retorna_angulo_atraves_ponto(ponto2_x, ponto2_y)
        menor_ang_vetores = self.eq_ang_entre_vetores(ponto1_x, ponto1_y, ponto2_x, ponto2_y)
        if angulo_pt1 <= angulo_pt2:
            if (angulo_pt2 - angulo_pt1) > pi:
                angulo_metade = angulo_pt2 + menor_ang_vetores/2
            else:
                angulo_metade = angulo_pt1 + menor_ang_vetores/2
        else:
            if (angulo_pt1 - angulo_pt2) > pi:
                angulo_metade = angulo_pt1 + menor_ang_vetores/2
            else:
                angulo_metade = angulo_pt2 + menor_ang_vetores/2

        if angulo_metade < pi:
            angulo_metade_inv = pi + angulo_metade
        else:
            angulo_metade_inv = angulo_metade - pi

        pt_x_metade, pt_y_metade = self.retorna_ponto_atraves_angulo(angulo_metade, raio)
        pt_x_metade_inv, pt_y_metade_inv = self.retorna_ponto_atraves_angulo(angulo_metade_inv, raio)
        return pt_x_metade, pt_y_metade, pt_x_metade_inv, pt_y_metade_inv

    def ponto_circ_borda(self):
        raio = self.eq_circ_achar_raio(self.pt1_x, self.pt1_y)
        self.ptc_x, self.ptc_y, self.ptc_x_inv, self.ptc_y_inv = self.retorna_pontos_metade_entre_vetores(self.pt1_x,  self.pt1_y, self.pt2_x, self.pt2_y, raio)
        return self.ptc_x, self.ptc_y, self.ptc_x_inv, self.ptc_y_inv
