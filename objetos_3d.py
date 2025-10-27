class Ponto3D:
    def __init__(self, x=0.0, y=0.0, z=0.0, nome=None):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.nome = nome
        # coordenadas na SCN (após projeção)
        self.x_scn = 0.0
        self.y_scn = 0.0

    def __repr__(self):
        return f"Ponto3D({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

class Objeto3D:
    def __init__(self, pontos=None, arestas=None, nome="Objeto3D"):
        self.pontos = pontos if pontos is not None else []
        self.arestas = arestas if arestas is not None else []
        self.nome = nome
        self.selecionado = False

    def desenhar(self, canvas, window, viewport, metodo_clipping=None):
        """
        Desenha as arestas projetadas assumindo que cada ponto já tem x_scn,y_scn.
        Se não houver arestas, não desenha.
        """
        cor = "red" if self.selecionado else "black"
        for (i, j) in self.arestas:
            try:
                p0 = self.pontos[i]
                p1 = self.pontos[j]
                x0, y0 = p0.x_scn, p0.y_scn
                x1, y1 = p1.x_scn, p1.y_scn
                # converte SCN -> viewport
                try:
                    x0_vp, y0_vp = viewport.scn_para_viewport(x0, y0)
                    x1_vp, y1_vp = viewport.scn_para_viewport(x1, y1)
                    canvas.create_line(x0_vp, y0_vp, x1_vp, y1_vp, fill=cor, width=1)
                except Exception:
                    # se conversão falhar, tenta desenhar sem transformação (fallback)
                    canvas.create_line(x0, y0, x1, y1, fill=cor, width=1)
            except Exception:
                continue

    def __repr__(self):
        return f"<Objeto3D {self.nome} pts={len(self.pontos)} edges={len(self.arestas)}>"