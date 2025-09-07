import math
import numpy as np

class Window:
    """Classe que gerencia os coordenadas de uma Window (sistema do mundo)"""
    def __init__(self, xw_min, yw_min, xw_max, yw_max, angle=0):
        self.xw_min = xw_min
        self.yw_min = yw_min
        self.xw_max = xw_max
        self.yw_max = yw_max
        self.largura = xw_max - xw_min
        self.altura = yw_max - yw_min
        self.angle = angle
    
    def set_angle(self, angle):
        self.angle = angle


class Viewport:
    def __init__(self, xvp_min, yvp_min, xvp_max, yvp_max):
        self.xvp_min = xvp_min
        self.yvp_min = yvp_min
        self.xvp_max = xvp_max
        self.yvp_max = yvp_max
        self.largura = xvp_max - xvp_min
        self.altura = yvp_max - yvp_min

    def mundo_para_scn(self, window, x_w, y_w):
        """Transforma coordenadas do mundo para SCN (aplica rotação da window)"""
        # Centro da window
        cx = (window.xw_min + window.xw_max) / 2
        cy = (window.yw_min + window.yw_max) / 2
        # Translada para origem (centro da window)
        dx = x_w - cx
        dy = y_w - cy
        # Rotaciona -window.angle (em rad)
        theta = -math.radians(getattr(window, "angle", 0))
        xr = dx * math.cos(theta) - dy * math.sin(theta)
        yr = dx * math.sin(theta) + dy * math.cos(theta)
        # Volta ao centro
        xr += cx
        yr += cy
        # Normaliza para SCN [0,1]
        xn = (xr - window.xw_min) / window.largura
        yn = (yr - window.yw_min) / window.altura
        return xn, yn

    def scn_para_viewport(self, xn, yn):
        """Transforma SCN para Viewport"""
        x_vp = self.xvp_min + xn * self.largura
        y_vp = self.yvp_min + (1 - yn) * self.altura  # Y invertido
        return x_vp, y_vp

    def mundo_para_viewport(self, window, x_w, y_w):
        """Transforma coordenadas do mundo para viewport (com rotação da window)"""
        xn, yn = self.mundo_para_scn(window, x_w, y_w)
        return self.scn_para_viewport(xn, yn)

    def esta_dentro_viewport(self, x_vp, y_vp):
        return (self.xvp_min <= x_vp <= self.xvp_max and 
                self.yvp_min <= y_vp <= self.yvp_max)

def matriz_translacao(dx, dy):
    return np.array([
        [1, 0, dx],
        [0, 1, dy],
        [0, 0, 1]
    ])

def matriz_escalonamento(sx, sy, cx=0, cy=0):
    # Escala em torno de um centro
    return np.dot(
        np.dot(
            matriz_translacao(-cx, -cy),
            np.array([
                [sx, 0, 0],
                [0, sy, 0],
                [0, 0, 1]
            ])
        ),
        matriz_translacao(cx, cy)
    )

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