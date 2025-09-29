from tkinter import Canvas
from tranformacoes import Window, Viewport
from clipping import clip_ponto, clip_reta_CS, clip_reta_NLN, clip_poligono
import numpy as np

class Ponto:
    def __init__(self, x: float, y: float, nome="ponto"):
        self.x = x
        self.y = y
        self.x_scn = 0
        self.y_scn = 0
        self.nome = nome
        self.size = 2
        self.selecionado = False

    def desenhar(self, canvas: Canvas, window: Window, viewport: Viewport):
        # Verifica se está dentro da janela
        if clip_ponto(self.x_scn, self.y_scn):
            x_vp, y_vp = viewport.scn_para_viewport(self.x_scn, self.y_scn)
            cor = "blue" if self.selecionado else "black"
            canvas.create_oval(x_vp - self.size, y_vp - self.size,
                              x_vp + self.size, y_vp + self.size,
                              fill=cor, outline="black", width=2)
            if self.selecionado:
                canvas.create_text(x_vp, y_vp - 20, text=self.nome, fill="blue")


class Reta:
    """Reta de um ponto até outro"""
    def __init__(self, ponto0: Ponto, ponto1: Ponto, nome="reta"):
        self.nome = nome
        self.ponto0 = ponto0
        self.ponto1 = ponto1
        self.selecionado = False


    def desenhar(self, canvas: Canvas, window: Window, viewport: Viewport, modo_clipping):
        match modo_clipping:
            case "Cohen-Sutherland":
                check_clipping = clip_reta_CS(self.ponto0.x_scn, self.ponto0.y_scn, self.ponto1.x_scn, self.ponto1.y_scn)
            case "Nicholl-Lee-Nicholl":
                check_clipping = clip_reta_NLN(self.ponto0.x_scn, self.ponto0.y_scn, self.ponto1.x_scn, self.ponto1.y_scn)
        if check_clipping is not None:
            x0, y0, x1, y1 = check_clipping
            x0, y0 = viewport.scn_para_viewport(x0, y0)
            x1, y1 = viewport.scn_para_viewport(x1, y1)
            cor = "blue" if self.selecionado else "black"
            canvas.create_line(x0, y0, x1, y1, fill=cor, width=2)
            # Mostra nome se selecionado
            if self.selecionado:
                centro_x = (x0 + x1) / 2
                centro_y = (y0 + y1) / 2
                canvas.create_text(centro_x, centro_y - 15, text=self.nome, fill="blue")
     

class Wireframe:
    """Conjunto de pontos interligados por retas"""
    def __init__(self, lista_pontos : list[Ponto], nome="wireframe", preencher=False, cor_preenchimento='black'):
        self.nome = nome
        self.lista_pontos = lista_pontos
        self.selecionado = False
        self.preencher = preencher
        self.cor_preenchimento = cor_preenchimento 


    def desenhar(self, canvas: Canvas, window: Window, viewport: Viewport):
        coordenadas_scn = [(p.x_scn, p.y_scn) for p in self.lista_pontos]

        coordenadas_clippadas = clip_poligono(coordenadas_scn)
        if not coordenadas_clippadas:
            return
        coordenadas_vp = [viewport.scn_para_viewport(x, y) for (x, y) in coordenadas_clippadas]
        cor = "blue" if self.selecionado else "black"
        if self.preencher:
            self.preencher_(canvas, coordenadas_vp)
        else:
            canvas.create_line(*coordenadas_vp, fill=cor, width=2)
        if self.selecionado:
            # Calcula o centro do wireframe
            xs = [p[0] for p in coordenadas_vp]
            ys = [p[1] for p in coordenadas_vp]
            centro_x = sum(xs) / len(coordenadas_vp)
            centro_y  = sum(ys) / len(coordenadas_vp)
            canvas.create_text(centro_x, centro_y, text=self.nome, fill="blue")

    def preencher_(self, canvas: Canvas, coordenadas_vp):
        if len(coordenadas_vp) < 3:
            return

        ys = [p[1] for p in coordenadas_vp]
        y_min = int(min(ys))
        y_max = int(max(ys))

        # Varredura por linha
        for y in range(y_min, y_max + 1):
            intersections = []
            for i in range(len(coordenadas_vp)):
                p1 = coordenadas_vp[i]
                p2 = coordenadas_vp[(i + 1) % len(coordenadas_vp)]

                y1, y2 = p1[1], p2[1]
                x1, x2 = p1[0], p2[0]

                # Verifica se a linha Y está entre os pontos
                if min(y1, y2) <= y < max(y1, y2):
                    # Calcula a intersecção X
                    # Evita divisão por zero para linhas horizontais
                    if (y2 - y1) != 0:
                        x_intersec = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                        intersections.append(x_intersec)

            intersections.sort()

            # Desenha linhas entre os pontos de intersecção em pares
            for i in range(0, len(intersections), 2):
                if i + 1 < len(intersections):
                    x_start = int(intersections[i])
                    x_end = int(intersections[i+1])
                    canvas.create_line(x_start, y, x_end, y, fill=self.cor_preenchimento)
            
class Curva2D:
    """Curva 2D usando o método de Bezier"""
    def __init__(self, lista_pontos: list, nome):
        self.nome = nome
        self.pontos = lista_pontos
        self.p_curvas = []
        self.selecionado = False
        self.calcular_pontos_curva()

    def calcular_pontos_curva(self, k=500):
        passo = 1/k
        for i in range(0, len(self.pontos) - 1, 3):
            if i+3 >= len(self.pontos):
                break
            P1, P2, P3, P4 = self.pontos[i:i+4]
            for t in np.arange(0, 1 + passo, passo):
                T = [t**3, t**2, t, 1]
                x_t = P1.x * (-3*T[0] + 3*T[1] - 3*T[2] + T[3]) + P2.x * (3*T[0] - 6*T[1] + 3*T[2]) + P3.x * (-3*T[0]+ 3*T[1]) + P4.x *(T[0])
                y_t = P1.y * (-3*T[0] + 3*T[1] - 3*T[2] + T[3]) + P2.y * (3*T[0] - 6*T[1] + 3*T[2]) + P3.y * (-3*T[0]+ 3*T[1]) + P4.y *(T[0])
                self.p_curvas.append(Ponto(x_t, y_t))
        
    def desenhar(self, canvas: Canvas, window: Window, viewport: Viewport):
        if len(self.p_curvas) < 2:
            return
        p_clipados = []
        cor = "blue" if self.selecionado else "black"
        for p in self.p_curvas:
            if clip_ponto(p.x_scn, p.y_scn):
                p_clipados.append(p)
        
        for i in range(len(p_clipados) - 1):
            p1 = p_clipados[i]
            p2 = p_clipados[i + 1]
            x1_vp, y1_vp = viewport.scn_para_viewport(p1.x_scn, p1.y_scn)
            x2_vp, y2_vp = viewport.scn_para_viewport(p2.x_scn, p2.y_scn)
            canvas.create_line(x1_vp, y1_vp, x2_vp, y2_vp, fill=cor, width=2)
            if self.selecionado and p1 == p_clipados[len(p_clipados)//2]:
                canvas.create_text(x1_vp, y1_vp + 15, text=self.nome)

class BSpline:
    def __init__(self,lista_pontos, nome):
        self.nome = nome
        self.pontos = lista_pontos
        self.p_bspline = []
        self.selecionado = False
        pass
    
    def calcular_pontos_curva(self, n=100):
        MBS = (1/6) * np.array([
            [-1, 3, -3, 1],
            [3, -6, 3, 0],
            [-3, 0, 3, 0],
            [1, 4, 1, 0]
        ])


        m = len(self.pontos)
        for i in range(3, m):
            P0 = self.pontos[i - 3]
            P1 = self.pontos[i - 2]
            P2 = self.pontos[i - 1]
            P3 = self.pontos[i]
            CX = MBS @ np.array([P0[0],P1[0],P2[0],P3[0]])
            CY = MBS @ np.array([P0[1],P1[1],P2[1],P3[1]])
            delta = 1.0/n
            E = np.array([
                [0, 0, 0, 1],
                [delta**3, delta**2, delta, 0],
                [6*delta**3, 2*delta**2, 0, 0],
                [6*delta**3, 0, 0, 0]
            ])
            DX = E @ CX
            DY = E @ CY
            x, dx, d2x, d3x = DX
            y, dy, d2y, d3y = DY
            for i in range(n + 1):
                self.p_bspline.append(Ponto(x, y))
                x += dx; dx += d2x; d2x += d3x
                y += dy; dy += d2y; d2y += d3y

    def desenhar(self, canvas: Canvas, window: Window, viewport: Viewport):
        if len(self.p_curvas) < 2:
            return
        p_clipados = []
        cor = "blue" if self.selecionado else "black"
        for p in self.p_curvas:
            if clip_ponto(p.x_scn, p.y_scn):
                p_clipados.append(p)
        
        for i in range(len(p_clipados) - 1):
            p1 = p_clipados[i]
            p2 = p_clipados[i + 1]
            x1_vp, y1_vp = viewport.scn_para_viewport(p1.x_scn, p1.y_scn)
            x2_vp, y2_vp = viewport.scn_para_viewport(p2.x_scn, p2.y_scn)
            canvas.create_line(x1_vp, y1_vp, x2_vp, y2_vp, fill=cor, width=2)
            if self.selecionado and p1 == p_clipados[len(p_clipados)//2]:
                canvas.create_text(x1_vp, y1_vp + 15, text=self.nome)




