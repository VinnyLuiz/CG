from tkinter import Canvas
from tranformacoes import Window, Viewport
from clipping import (
    clip_point_scn,
    sutherland_hodgman_scn,
    cohen_sutherland_clip_scn,
    liang_barsky_clip_scn,
)

class Ponto:
    def __init__(self, x: float, y: float, nome="ponto"):
        self.x = x
        self.y = y
        self.nome = nome
        self.size = 6
        self.selecionado = False

    def desenhar(self, canvas: Canvas, window: Window, viewport: Viewport):
        # Calcula SCN, faz o clipping em SCN
        x_scn, y_scn = window.mundo_para_scn(self.x, self.y)
        if not clip_point_scn(x_scn, y_scn):
            return  # Fora da window (SCN)

        x_vp, y_vp = viewport.scn_para_viewport(x_scn, y_scn)
        cor = "blue" if self.selecionado else "black"
        canvas.create_oval(
            x_vp - self.size / 2, y_vp - self.size / 2,
            x_vp + self.size / 2, y_vp + self.size / 2,
            fill=cor, outline="black", width=2
        )
        if self.selecionado:
            canvas.create_text(x_vp, y_vp - 20, text=self.nome, fill="blue")

class Reta:
    """Reta de um ponto até outro"""
    def __init__(self, ponto0: Ponto, ponto1: Ponto, nome="reta"):
        self.nome = nome
        self.ponto0 = ponto0
        self.ponto1 = ponto1
        self.selecionado = False

    def desenhar(self, canvas: Canvas, window: Window, viewport: Viewport, clipping_method="cohen-sutherland"):
        # Transforme os pontos para SCN
        x0_scn, y0_scn = window.mundo_para_scn(self.ponto0.x, self.ponto0.y)
        x1_scn, y1_scn = window.mundo_para_scn(self.ponto1.x, self.ponto1.y)

        # Faça o clipping em SCN
        if clipping_method == "liang-barsky":
            clipped = liang_barsky_clip_scn(x0_scn, y0_scn, x1_scn, y1_scn)
        else:
            clipped = cohen_sutherland_clip_scn(x0_scn, y0_scn, x1_scn, y1_scn)

        if clipped:
            x0c, y0c, x1c, y1c = clipped

            x0_vp, y0_vp = viewport.scn_para_viewport(x0c, y0c)
            x1_vp, y1_vp = viewport.scn_para_viewport(x1c, y1c)

            cor = "blue" if self.selecionado else "black"
            canvas.create_line(x0_vp, y0_vp, x1_vp, y1_vp, fill=cor, width=2)

            if self.selecionado:
                centro_x = (x0_vp + x1_vp) / 2
                centro_y = (y0_vp + y1_vp) / 2
                canvas.create_text(centro_x, centro_y - 15, text=self.nome, fill="blue")

class Wireframe:
    """Conjunto de pontos interligados por retas"""
    def __init__(self, lista_pontos : list, nome="wireframe", preenchido=False):
        self.nome = nome
        self.lista_pontos = lista_pontos
        self.selecionado = False
        self.preenchido = preenchido  # True para polígono preenchido

    def desenhar(self, canvas: Canvas, window: Window, viewport: Viewport):
        pontos_scn = [window.mundo_para_scn(p.x, p.y) for p in self.lista_pontos]
        if len(pontos_scn) < 2:
            # Só tem um ponto, desenha como ponto
            x_scn, y_scn = pontos_scn[0]
            if not clip_point_scn(x_scn, y_scn):
                return
            x_vp, y_vp = viewport.scn_para_viewport(x_scn, y_scn)
            cor = "blue" if self.selecionado else "black"
            canvas.create_oval(
                x_vp - 3, y_vp - 3, x_vp + 3, y_vp + 3,
                fill=cor, outline="black", width=2
            )
            return

        # Clipping do wireframe no SCN
        pontos_clipados = sutherland_hodgman_scn(pontos_scn)

        if len(pontos_clipados) >= 2:
            coords_vp = []
            for x_scn, y_scn in pontos_clipados:
                x_vp, y_vp = viewport.scn_para_viewport(x_scn, y_scn)
                coords_vp.extend([x_vp, y_vp])

            cor = "blue" if self.selecionado else "black"

            if self.preenchido:
                canvas.create_polygon(*coords_vp, fill="lightblue", outline=cor, width=2)
            else:
                canvas.create_line(*coords_vp, fill=cor, width=2)

            if self.selecionado:
                centro_x = sum(coords_vp[::2]) / len(pontos_clipados)
                centro_y = sum(coords_vp[1::2]) / len(pontos_clipados)
                canvas.create_text(centro_x, centro_y - 15, text=self.nome, fill="blue")

class BSpline2D:
    def __init__(self, lista_pontos, nome="b-spline"):
        if not nome:
            nome = "B-Spline"
        self.lista_pontos = lista_pontos  # lista de objetos Ponto
        self.nome = nome
        self.selecionado = False
        self.step = 0.02  # resolução da curva

    def _fd_matrix(self, delta_t):
        """Matriz de Forward Differences para B-Spline cúbica uniform"""
        dt = delta_t
        dt2 = dt*dt
        dt3 = dt*dt*dt
        return [
            [0,       0,      0,   1],
            [dt3,     dt2,    dt,  0],
            [6*dt3,   2*dt2,  0,   0],
            [6*dt3,   0,      0,   0]
        ]

    def _bspline_basis_matrix(self):
        """Matriz base B-Spline cúbica"""
        return [
            [-1/6,  3/6, -3/6, 1/6],
            [ 3/6, -6/6,  3/6, 0  ],
            [-3/6, 0,     3/6, 0  ],
            [ 1/6, 4/6,  1/6, 0  ]
        ]

    def _mult_matrix_vec(self, m, v):
        return [sum(m[i][j]*v[j] for j in range(4)) for i in range(4)]

    def gerar_pontos_bspline(self):
        """Gera a curva usando forward differences para cada segmento de 4 pontos"""
        pts = self.lista_pontos
        if len(pts) < 4: return []
        k = int(1/self.step)
        pontos_da_curva = []
        M_bspline = self._bspline_basis_matrix()
        dt = self.step
        FD = self._fd_matrix(dt)

        for i in range(len(pts)-3):
            Gx = [pts[i].x, pts[i+1].x, pts[i+2].x, pts[i+3].x]
            Gy = [pts[i].y, pts[i+1].y, pts[i+2].y, pts[i+3].y]
            Cx = self._mult_matrix_vec(M_bspline, Gx)
            Cy = self._mult_matrix_vec(M_bspline, Gy)
            Dx = self._mult_matrix_vec(FD, Cx)
            Dy = self._mult_matrix_vec(FD, Cy)
            # Forward Differences
            x, dx, d2x, d3x = Dx
            y, dy, d2y, d3y = Dy
            curva_segmento = []
            for _ in range(k+1):
                curva_segmento.append((x, y))
                x += dx; dx += d2x; d2x += d3x
                y += dy; dy += d2y; d2y += d3y
            pontos_da_curva.append(curva_segmento)
        return pontos_da_curva

    def desenhar(self, canvas: Canvas, window: Window, viewport: Viewport):
        segmentos = self.gerar_pontos_bspline()
        cor = "blue" if self.selecionado else "black"
        for curva_pts in segmentos:
            last = None
            for x, y in curva_pts:
                x_scn, y_scn = window.mundo_para_scn(x, y)
                if clip_point_scn(x_scn, y_scn):
                    x_vp, y_vp = viewport.scn_para_viewport(x_scn, y_scn)
                    if last:
                        canvas.create_line(last[0], last[1], x_vp, y_vp, fill=cor, width=2)
                    last = (x_vp, y_vp)
                else:
                    last = None  # quebra a linha se sair da window
