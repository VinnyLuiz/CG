from tkinter import Canvas
from tranformacoes import Window, Viewport

class Ponto:
    def __init__(self, x: float, y: float, nome="ponto"):
        self.x = x
        self.y = y
        self.nome = nome
        self.size = 6
        self.selecionado = False

    def desenhar(self, canvas: Canvas, window: Window, viewport: Viewport):
        x_view, y_view = viewport.mundo_para_viewport(window, self.x, self.y)
        
        # Verifica se está dentro do viewport
        if viewport.esta_dentro_viewport(x_view, y_view):
            cor = "blue" if self.selecionado else "black"
            canvas.create_oval(x_view - self.size/2, y_view - self.size/2,
                              x_view + self.size/2, y_view + self.size/2,
                              fill=cor, outline="black", width=2)
            if self.selecionado:
                canvas.create_text(x_view, y_view - 20, text=self.nome, fill="blue")


class Reta:
    """Reta de um ponto até outro"""
    def __init__(self, ponto0: Ponto, ponto1: Ponto, nome="reta"):
        self.nome = nome
        self.ponto0 = ponto0
        self.ponto1 = ponto1
        self.selecionado = False


    def desenhar(self, canvas: Canvas, window: Window, viewport: Viewport):
        x0, y0 = viewport.mundo_para_viewport(window, self.ponto0.x, self.ponto0.y)
        x1, y1 = viewport.mundo_para_viewport(window, self.ponto1.x, self.ponto1.y)
        
        # Checa se há ao menos um ponto dentro do viewport
        if (viewport.esta_dentro_viewport(x0, y0) or 
            viewport.esta_dentro_viewport(x1, y1)):
            
            cor = "blue" if self.selecionado else "black"
            canvas.create_line(x0, y0, x1, y1, fill=cor, width=2)
            
            # Mostra nome se selecionado
            if self.selecionado:
                centro_x = (x0 + x1) / 2
                centro_y = (y0 + y1) / 2
                canvas.create_text(centro_x, centro_y - 15, text=self.nome, fill="blue")
     

class Wireframe:
    """Conjunto de pontos interligados por retas"""
    def __init__(self, lista_pontos : list[Ponto], nome="wireframe"):
        self.nome = nome
        self.lista_pontos = lista_pontos
        self.selecionado = False


    def desenhar(self, canvas: Canvas, window: Window, viewport: Viewport):
        lista_coordenadas = []
        algum_ponto_dentro = False
        
        for p in self.lista_pontos:
            x_view, y_view = viewport.mundo_para_viewport(window, p.x, p.y)
            lista_coordenadas.extend([x_view, y_view])
            if viewport.esta_dentro_viewport(x_view, y_view):
                algum_ponto_dentro = True
        
        # Só desenha se pelo menos um ponto estiver dentro do viewport
        if algum_ponto_dentro and len(self.lista_pontos) >= 2:
            cor = "blue" if self.selecionado else "black"
            canvas.create_line(*lista_coordenadas, fill=cor, width=2)
            
            if self.selecionado:
                # Calcula o centro do wireframe
                soma_x = sum(lista_coordenadas[::2])
                soma_y = sum(lista_coordenadas[1::2])
                centro_x = soma_x / len(self.lista_pontos)
                centro_y = soma_y / len(self.lista_pontos)
                canvas.create_text(centro_x, centro_y - 15, text=self.nome, fill="blue")

        elif self.lista_pontos and algum_ponto_dentro:
            # Se só tem um ponto, desenha como ponto
            self.lista_pontos[0].desenhar(canvas, window, viewport)
        