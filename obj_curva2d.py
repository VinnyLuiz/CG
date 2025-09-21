from tkinter import Canvas
from tranformacoes import Window, Viewport
from clipping import clip_point_scn

class Curva2D:
    def __init__(self, lista_pontos, nome="curva2d"):
        self.lista_pontos = lista_pontos  # lista de objetos Ponto
        self.nome = nome
        self.selecionado = False
        self.step = 0.02  # resolução da curva - deixe ajustável se quiser

    def bezier_blend(self, t, pontos):
        """Blending function para Bézier de grau n-1"""
        from math import comb
        n = len(pontos) - 1
        x = 0
        y = 0
        for i, p in enumerate(pontos):
            bern = comb(n, i) * (t ** i) * ((1-t) ** (n-i))
            x += bern * p.x
            y += bern * p.y
        return x, y

    def gerar_pontos_curva(self):
        """Gera pontos da curva como segmentos Bézier de 4 em 4, com continuidade G(0)"""
        pts = self.lista_pontos
        segmentos = []
        if len(pts) < 4: return segmentos
        # Gera curvas com continuidade G(0): pega cada bloco de 4 pontos, avança 3 para ter a continuidade no último ponto
        for i in range(0, len(pts) - 3, 3):
            curva_pts = []
            for t in [j * self.step for j in range(int(1/self.step)+1)]:
                x, y = self.bezier_blend(t, pts[i:i+4])
                curva_pts.append((x, y))
            segmentos.append(curva_pts)
        return segmentos

    def desenhar(self, canvas: Canvas, window: Window, viewport: Viewport):
        segmentos = self.gerar_pontos_curva()
        cor = "blue" if self.selecionado else "black"
        for curva_pts in segmentos:
            # desenha como linhas entre pontos válidos (clipping por ponto em SCN!)
            last = None
            for x, y in curva_pts:
                x_scn, y_scn = window.mundo_para_scn(x, y)
                if clip_point_scn(x_scn, y_scn):
                    x_vp, y_vp = viewport.scn_para_viewport(x_scn, y_scn)
                    if last:
                        canvas.create_line(last[0], last[1], x_vp, y_vp, fill=cor, width=2)
                    last = (x_vp, y_vp)
                else:
                    last = None  # quebra a linha se o ponto está fora da window