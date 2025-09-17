from tkinter import Canvas
from tranformacoes import Window, Viewport
from clipping import clip_ponto, clip_reta_CS, clip_reta_NLN, clip_poligono

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
            centro_x = sum(xs) / len(xs)
            centro_y  = sum(ys) / len(xs)
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
            