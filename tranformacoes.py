import math
import numpy as np

class Window:
    """Classe que gerencia os coordenadas de uma Window (sistema do mundo)"""
    def __init__(self, xw_min: float, yw_min: float, xw_max: float, yw_max: float):
        self.xw_min = xw_min
        self.yw_min = yw_min
        self.xw_max = xw_max
        self.yw_max = yw_max
        self.largura = xw_max - xw_min
        self.altura = yw_max - yw_min
        self.angulo_rotacao = 0


    def rotacionar(self, angulo):
        self.angulo_rotacao = (self.angulo_rotacao + angulo) % 360

    def centro(self):
        """Retorna as coordenadas do centro da window"""
        return (self.xw_min + self.xw_max) / 2, (self.yw_min + self.yw_max) / 2
    
    def mundo_para_scn(self, x_w: float, y_w: float):
        """Retorna as coordenadas do mundo em coordenadas normalizadas"""
        centro_x, centro_y = self.centro()
        T = matriz_translacao(-centro_x, -centro_y)
        
        R = matriz_rotacao(-self.angulo_rotacao)

        S = matriz_escalonamento(2/self.largura, 2/self.altura)

        M = S @ R @ T

        coord_ponto = np.array([x_w, y_w, 1])
        coord_ponto_norm = M @ coord_ponto

        return coord_ponto_norm[0], coord_ponto_norm[1]



class Viewport:
    """Classe que gerencia os coordenadas de uma Viewport (sistema de tela)"""
    def __init__(self, xvp_min: float, yvp_min: float, xvp_max: float, yvp_max: float):
        self.xvp_min = xvp_min
        self.yvp_min = yvp_min
        self.xvp_max = xvp_max
        self.yvp_max = yvp_max
        self.largura = xvp_max - xvp_min
        self.altura = yvp_max - yvp_min

    def esta_dentro_viewport(self, x_vp: float, y_vp: float):
        """Verifica se as coordenadas estão dentro da viewport"""
        return (self.xvp_min <= x_vp <= self.xvp_max and 
                self.yvp_min <= y_vp <= self.yvp_max)
    
    def scn_para_viewport(self, x_scn, y_scn):
        """Transforma as coordenadas normalizadas para coordenadas do viewport"""
        x_vp = self.xvp_min + ((x_scn + 1) / 2.0) * self.largura
        y_vp = self.yvp_min + (1 - (y_scn + 1) / 2.0) * self.altura 
        return x_vp, y_vp

    def mundo_para_viewport(self, window, xw, yw):
        """Transforma coordenadas do mundo para coordenadas do viewport"""
        x_vp = self.xvp_min + ((xw - window.xw_min) / window.largura) * self.largura
        y_vp = self.yvp_min + (1 - (yw - window.yw_min) / window.altura) * self.altura
        return x_vp, y_vp

def matriz_translacao(dx, dy):
    return np.array([
        [1, 0, dx],
        [0, 1, dy],
        [0, 0, 1]
    ])

def matriz_escalonamento(sx, sy, cx=0, cy=0):
    S = np.array([
        [sx, 0, 0],
        [0, sy, 0],
        [0,  0, 1]
    ])
    return matriz_translacao(cx, cy) @ S @ matriz_translacao(-cx, -cy)

def matriz_rotacao(angulo_graus, cx=0, cy=0):
    rad = math.radians(angulo_graus)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    R = np.array([
        [cos_a, -sin_a, 0],
        [sin_a,  cos_a, 0],
        [0,      0,     1]
    ])
    T1 = matriz_translacao(-cx, -cy)
    T2 = matriz_translacao(cx, cy)
    return T2 @ R @ T1

def aplicar_matriz(objeto, matriz):
    # Importa Ponto apenas dentro da função para evitar importação circular
    from objetos import Ponto

    if objeto.__class__.__name__ == "Ponto":
        x, y = objeto.x, objeto.y
        p = np.array([x, y, 1])
        p_transf = np.dot(matriz, p)
        objeto.x, objeto.y = p_transf[0], p_transf[1]
    elif objeto.__class__.__name__ == "Reta":
        for ponto in [objeto.ponto0, objeto.ponto1]:
            x, y = ponto.x, ponto.y
            p = np.array([x, y, 1])
            p_transf = np.dot(matriz, p)
            ponto.x, ponto.y = p_transf[0], p_transf[1]
    elif objeto.__class__.__name__ == "Wireframe":
        novos_pontos = []
        for ponto in objeto.lista_pontos:
            x, y = ponto.x, ponto.y
            p = np.array([x, y, 1])
            p_transf = np.dot(matriz, p)
            novos_pontos.append(Ponto(p_transf[0], p_transf[1], ponto.nome))
        objeto.lista_pontos = novos_pontos
    return objeto

def centro_geom(objeto):
    # Para Wireframe
    if hasattr(objeto, "lista_pontos"):
        xs = [p.x for p in objeto.lista_pontos]
        ys = [p.y for p in objeto.lista_pontos]
        return sum(xs)/len(xs), sum(ys)/len(ys)
    # Para Reta
    elif hasattr(objeto, "ponto0") and hasattr(objeto, "ponto1"):
        xs = [objeto.ponto0.x, objeto.ponto1.x]
        ys = [objeto.ponto0.y, objeto.ponto1.y]
        return sum(xs)/2, sum(ys)/2
    # Para Ponto
    elif hasattr(objeto, "x") and hasattr(objeto, "y"):
        return objeto.x, objeto.y
    else:
        raise AttributeError("Objeto não possui pontos reconhecíveis")
    

    
