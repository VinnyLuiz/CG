import numpy as np
from clipping import clip_reta_CS, clip_reta_NLN
from objetos_3d import Ponto3D

# Matriz Bezier
MB = np.array([
    [-1,  3, -3, 1],
    [ 3, -6,  3, 0],
    [-3,  3,  0, 0],
    [ 1,  0,  0, 0]
], dtype=float)

# Matriz B-Spline
MBS = (1/6) * np.array([
[-1, 3, -3, 1],
[3, -6, 3, 0],
[-3, 0, 3, 0],
[1, 4, 1, 0]
], dtype=float)

class Superficie3D:
    def __init__(self, lista_matrizes, nome):
        self.nome = nome
        self.lista_matrizes = lista_matrizes
        self.p_calculados = []
        self.n_s = 20
        self.n_t = 20
        self.tipoS = "Bezier"
        self.selecionado = False
        
    def desenhar(self, canvas, window, viewport, metodo_clipping):
        if len(self.p_calculados) < 2:
            return
        cor = "blue" if self.selecionado else "black"
        num_matrizes_originais = len(self.lista_matrizes)
        
        if num_matrizes_originais > 1:
            linhas_por_matriz = len(self.p_calculados) // num_matrizes_originais
            
            for mat_idx in range(num_matrizes_originais):
                start_idx = mat_idx * linhas_por_matriz
                end_idx = start_idx + linhas_por_matriz
                
                if end_idx > len(self.p_calculados):
                    end_idx = len(self.p_calculados)
                    
                matriz_atual = self.p_calculados[start_idx:end_idx]
                
                # Desenha linhas HORIZONTAIS
                for linha in matriz_atual:
                    for i in range(len(linha) - 1):
                        x0, y0 = linha[i].x_scn, linha[i].y_scn
                        x1, y1 = linha[i + 1].x_scn, linha[i + 1].y_scn
                        if metodo_clipping == "Cohen-Sutherland":
                            check_clipping = clip_reta_CS(x0, y0, x1, y1)
                        else:
                            check_clipping = clip_reta_NLN(x0, y0, x1, y1)
                        if check_clipping is not None:
                            x0_clipped, y0_clipped, x1_clipped, y1_clipped = check_clipping
                            x0_vp, y0_vp = viewport.scn_para_viewport(x0_clipped, y0_clipped)
                            x1_vp, y1_vp = viewport.scn_para_viewport(x1_clipped, y1_clipped)
                            canvas.create_line(x0_vp, y0_vp, x1_vp, y1_vp, fill=cor, width=2)
                
                # Desenha linhas VERTICAIS
                if matriz_atual and len(matriz_atual[0]) > 1:
                    for col_idx in range(len(matriz_atual[0])):
                        for linha_idx in range(len(matriz_atual) - 1):
                            x0, y0 = matriz_atual[linha_idx][col_idx].x_scn, matriz_atual[linha_idx][col_idx].y_scn
                            x1, y1 = matriz_atual[linha_idx + 1][col_idx].x_scn, matriz_atual[linha_idx + 1][col_idx].y_scn
                            if metodo_clipping == "Cohen-Sutherland":
                                check_clipping = clip_reta_CS(x0, y0, x1, y1)
                            else:
                                check_clipping = clip_reta_NLN(x0, y0, x1, y1)
                            if check_clipping is not None:
                                x0_clip, y0_clip, x1_clip, y1_clip = check_clipping
                                x0_vp, y0_vp = viewport.scn_para_viewport(x0_clip, y0_clip)
                                x1_vp, y1_vp = viewport.scn_para_viewport(x1_clip, y1_clip)
                                canvas.create_line(x0_vp, y0_vp, x1_vp, y1_vp, fill=cor, width=1)

    def unpack_matriz(self):
        todas_as_linhas = []
        
        for matriz in self.lista_matrizes:
            for linha in matriz:
                pontos_serializados = []
                for ponto in linha:
                    ponto_str = f"({ponto.x:.2f}, {ponto.y:.2f}, {ponto.z:.2f})"
                    pontos_serializados.append(ponto_str)
                linha_serializada = ", ".join(pontos_serializados)
                todas_as_linhas.append(linha_serializada)
        return ";".join(todas_as_linhas)
                
class SuperficieBezier3D(Superficie3D):
    def __init__(self, lista_matrizes, nome):
        super().__init__(lista_matrizes, nome)
        self.gerar_curvas_fwd()
        
    def gerar_curvas(self):
        """Gera as curvas da superfície"""
        self.p_calculados = []
        n_t = self.n_t
        n_s = self.n_s
        t_values = np.linspace(0, 1, n_t + 1)
        s_values = np.linspace(0, 1, n_s + 1)

        for G in self.lista_matrizes:
            for t in t_values:
                T = np.array([t**3, t**2, t, 1])
                curva_pts = []

                for s in s_values:
                    S = np.array([s**3, s**2, s, 1])

                    Gx = np.array([[p.x for p in linha] for linha in G])
                    Gy = np.array([[p.y for p in linha] for linha in G])
                    Gz = np.array([[p.z for p in linha] for linha in G])

                    x = S @ MB @ Gx @ MB.T @ T.T
                    y = S @ MB @ Gy @ MB.T @ T.T
                    z = S @ MB @ Gz @ MB.T @ T.T

                    curva_pts.append(Ponto3D(x, y, z))

                self.p_calculados.append(curva_pts)
        
    def gerar_curvas_fwd(self):
        """Gera as curvas da superfície Bézier com forward differences em s e t."""
        self.p_calculados = []
        n_t = self.n_t
        n_s = self.n_s
        # Cada bloco 4x4 define uma superfície bicúbica
        for G in self.lista_matrizes:
            n_linhas = len(G)
            n_cols = len(G[0])
            for i in range(0, n_linhas - 3, 3):
                for j in range(0, n_cols - 3, 3):
                    # Extrai o patch 4x4
                    Gx = np.array([[G[i + u][j + v].x for v in range(4)] for u in range(4)])
                    Gy = np.array([[G[i + u][j + v].y for v in range(4)] for u in range(4)])
                    Gz = np.array([[G[i + u][j + v].z for v in range(4)] for u in range(4)])

                    # Calcula as matrizes de coeficientes
                    Cx = MB @ Gx @ MB.T
                    Cy = MB @ Gy @ MB.T
                    Cz = MB @ Gz @ MB.T

                    # Prepara forward difference em t (colunas)
                    delta = 1 / n_t
                    E = np.array([
                        [0, 0, 0, 1],
                        [delta**3, delta**2, delta, 0],
                        [6*delta**3, 2*delta**2, 0, 0],
                        [6*delta**3, 0, 0, 0]
                    ])

                    # Vetores iniciais para t = 0
                    T0 = np.array([0, 0, 0, 1])
                    DX = Cx @ T0
                    DY = Cy @ T0
                    DZ = Cz @ T0

                    # Lista de curvas para este patch
                    curvas_t = []

                    t_values = np.linspace(0, 1, n_t + 1)
                    for step_t in t_values:
                        # curva em s fixo, varrendo s via forward difference
                        delta_s = 1.0 / n_s
                        Es = np.array([
                            [0, 0, 0, 1],
                            [delta_s**3, delta_s**2, delta_s, 0],
                            [6*delta_s**3, 2*delta_s**2, 0, 0],
                            [6*delta_s**3, 0, 0, 0]
                        ])
                        Sx = Es @ Cx @ np.array([step_t**3, step_t**2, step_t, 1])
                        Sy = Es @ Cy @ np.array([step_t**3, step_t**2, step_t, 1])
                        Sz = Es @ Cz @ np.array([step_t**3, step_t**2, step_t, 1])

                        x, dx, d2x, d3x = Sx
                        y, dy, d2y, d3y = Sy
                        z, dz, d2z, d3z = Sz

                        linha = []
                        for _ in range(n_s + 1):
                            linha.append(Ponto3D(x, y, z))
                            x += dx; dx += d2x; d2x += d3x
                            y += dy; dy += d2y; d2y += d3y
                            z += dz; dz += d2z; d2z += d3z
                        curvas_t.append(linha)
                    self.p_calculados.extend(curvas_t)



class SuperficieBSpline3D(Superficie3D):
    def __init__(self, matriz_pontos, nome):
        super().__init__(matriz_pontos, nome)
        self.tipoS = "BSpline"
        self.gerar_curvas_fwd()
        
    def gerar_curvas(self):
        """Gera as curvas da superfície"""
        n_t = self.n_t
        n_s = self.n_s
        t_values = np.linspace(0, 1, n_t + 1)
        s_values = np.linspace(0, 1, n_s + 1)
        for G in self.lista_matrizes:
            for t in t_values:
                T = np.array([t**3, t**2, t, 1])
                curva_pts = []
                for s in s_values:
                    S = np.array([s**3, s**2, s, 1])

                    Gx = np.array([[p.x for p in linha] for linha in G])
                    Gy = np.array([[p.y for p in linha] for linha in G])
                    Gz = np.array([[p.z for p in linha] for linha in G])

                    x = S @ MBS @ Gx @ MBS.T @ T.T
                    y = S @ MBS @ Gy @ MBS.T @ T.T
                    z = S @ MBS @ Gz @ MBS.T @ T.T

                    curva_pts.append(Ponto3D(x, y, z))

                self.p_calculados.append(curva_pts)
            
    def gerar_curvas_fwd(self):
        """Gera uma superfície B-spline bicúbica usando Forward Differences e grids."""
        self.p_calculados = []
        n_t = self.n_t
        n_s = self.n_s

        n_linhas = len(self.G)
        n_cols = len(self.G[0])

        for G in self.lista_matrizes:
            for i in range(3, n_linhas):
                for j in range(3, n_cols):
                    # Extrai o patch 4x4 (superfície local)
                    Gx = np.array([[G[i - u][j - v].x for v in range(4)] for u in range(4)])
                    Gy = np.array([[G[i - u][j - v].y for v in range(4)] for u in range(4)])
                    Gz = np.array([[G[i - u][j - v].z for v in range(4)] for u in range(4)])

                    # Calcula os coeficientes
                    Cx = MBS @ Gx @ MBS.T
                    Cy = MBS @ Gy @ MBS.T
                    Cz = MBS @ Gz @ MBS.T

                    delta = 1 / n_t 
                    E = np.array([
                        [0, 0, 0, 1],
                        [delta**3, delta**2, delta, 0],
                        [6*delta**3, 2*delta**2, 0, 0],
                        [6*delta**3, 0, 0, 0]
                    ])

                    # Itera em t (curvas)
                    t_values = np.linspace(0, 1, n_t + 1)
                    curvas_t = []
                    for t in t_values:
                        delta_s = 1.0 / n_s
                        Es = np.array([
                            [0, 0, 0, 1],
                            [delta_s**3, delta_s**2, delta_s, 0],
                            [6*delta_s**3, 2*delta_s**2, 0, 0],
                            [6*delta_s**3, 0, 0, 0]
                        ])

                        # Vetor de parâmetro t
                        T = np.array([t**3, t**2, t, 1])

                        Sx = Es @ Cx @ T
                        Sy = Es @ Cy @ T
                        Sz = Es @ Cz @ T

                        x, dx, d2x, d3x = Sx
                        y, dy, d2y, d3y = Sy
                        z, dz, d2z, d3z = Sz

                        linha = []
                        for _ in range(n_s + 1):
                            linha.append(Ponto3D(x, y, z))
                            x += dx; dx += d2x; d2x += d3x
                            y += dy; dy += d2y; d2y += d3y
                            z += dz; dz += d2z; d2z += d3z
                        curvas_t.append(linha)
                    self.p_calculados.extend(curvas_t)