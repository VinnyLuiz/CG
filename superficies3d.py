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

# Matriz B-Spline (base)
MBS = (1.0/6.0) * np.array([
    [-1.0,  3.0, -3.0, 1.0],
    [ 3.0, -6.0,  3.0, 0.0],
    [-3.0,  0.0,  3.0, 0.0],
    [ 1.0,  4.0,  1.0, 0.0]
])

def _E_matrix(h):
    h2 = h * h
    h3 = h2 * h
    return np.array([
        [0.0,    0.0,   0.0, 1.0],
        [h3,     h2,    h,   0.0],
        [6*h3,   2*h2,  0.0, 0.0],
        [6*h3,   0.0,   0.0, 0.0]
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
        if len(self.p_calculados) < 1:
            return
        cor = "blue" if self.selecionado else "black"
        for patch_amostrado in self.p_calculados:
            for linha in patch_amostrado:
                for i in range(len(linha) - 1):
                    x0, y0 = linha[i].x_scn, linha[i].y_scn
                    x1, y1 = linha[i+1].x_scn, linha[i+1].y_scn
                    if metodo_clipping == "Cohen-Sutherland":
                        check_clipping = clip_reta_CS(x0, y0, x1, y1)
                    else:
                        check_clipping = clip_reta_NLN(x0, y0, x1, y1)
                    if check_clipping is not None:
                        x0_clipped, y0_clipped, x1_clipped, y1_clipped = check_clipping
                        x0_vp, y0_vp = viewport.scn_para_viewport(x0_clipped, y0_clipped)
                        x1_vp, y1_vp = viewport.scn_para_viewport(x1_clipped, y1_clipped)
                        canvas.create_line(x0_vp, y0_vp, x1_vp, y1_vp, fill=cor, width=1)

            if patch_amostrado and len(patch_amostrado[0]) > 1:
                ncols = len(patch_amostrado[0])
                for c in range(ncols):
                    for r in range(len(patch_amostrado) - 1):
                        p0 = patch_amostrado[r][c]
                        p1 = patch_amostrado[r+1][c]
                        x0, y0 = p0.x_scn, p0.y_scn
                        x1, y1 = p1.x_scn, p1.y_scn
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
        def ponto_to_str(p):
            try:
                return f"({p.x:.6f},{p.y:.6f},{p.z:.6f})"
            except Exception:
                try:
                    x, y, z = p
                    return f"({float(x):.6f},{float(y):.6f},{float(z):.6f})"
                except Exception:
                    return "(0.0,0.0,0.0)"

        lm = getattr(self, "lista_matrizes", None)
        if not lm:
            return ""
        matrices = []
        try:
            first = lm[0]
            if isinstance(first, (list, tuple)) and len(first) > 0 and hasattr(first[0], "x"):
                matrices = [lm]
            elif isinstance(first, (list, tuple)) and isinstance(first[0], (list, tuple)):
                matrices = lm
            else:
                matrices = [lm]
        except Exception:
            matrices = [lm]

        todas_as_linhas = []
        for matriz in matrices:
            for linha in matriz:
                if not isinstance(linha, (list, tuple)):
                    todas_as_linhas.append(ponto_to_str(linha))
                    continue
                pontos_serializados = [ponto_to_str(p) for p in linha]
                linha_serializada = ",".join(pontos_serializados)
                todas_as_linhas.append(linha_serializada)
        return ";".join(todas_as_linhas)

def _gerar_patch_forward_diffs_por_slide(Cx, Cy, Cz, n_t, n_s):

    delta_s = 1.0 / max(1, (n_s))
    delta_t = 1.0 / max(1, (n_t))

    Es = _E_matrix(delta_s)
    Et = _E_matrix(delta_t)

    DDx = Es @ Cx @ Et.T
    DDy = Es @ Cy @ Et.T
    DDz = Es @ Cz @ Et.T

    DDx = DDx.T
    DDy = DDy.T
    DDz = DDz.T

    E_u = _E_matrix(delta_t)

    patch_amostrado = []
    for iv in range(n_s + 1):
        v = iv / max(1, n_s)
        T_v = np.array([v**3, v**2, v, 1.0])
        a_x = Cx @ T_v
        a_y = Cy @ T_v
        a_z = Cz @ T_v
        fx = E_u @ a_x
        fy = E_u @ a_y
        fz = E_u @ a_z

        x, dx, d2x, d3x = float(fx[0]), float(fx[1]), float(fx[2]), float(fx[3])
        y, dy, d2y, d3y = float(fy[0]), float(fy[1]), float(fy[2]), float(fy[3])
        z, dz, d2z, d3z = float(fz[0]), float(fz[1]), float(fz[2]), float(fz[3])

        linha_pts = []
        for iu in range(n_t + 1):
            linha_pts.append(Ponto3D(x, y, z))
            x += dx; dx += d2x; d2x += d3x
            y += dy; dy += d2y; d2y += d3y
            z += dz; dz += d2z; d2z += d3z
        patch_amostrado.append(linha_pts)

    return patch_amostrado

class SuperficieBezier3D(Superficie3D):
    def __init__(self, lista_matrizes, nome):
        super().__init__(lista_matrizes, nome)
        try:
            self.gerar_curvas_fwd()
        except Exception:
            self.p_calculados = []

    def gerar_curvas(self):
        self.p_calculados = []
        n_t = max(1, int(self.n_t))
        n_s = max(1, int(self.n_s))
        for G in self.lista_matrizes:
            for t in np.linspace(0, 1, n_t + 1):
                T = np.array([t**3, t**2, t, 1])
                curva_pts = []
                for s in np.linspace(0,1, n_s + 1):
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
        self.p_calculados = []
        n_t = max(1, int(self.n_t))
        n_s = max(1, int(self.n_s))

        for G in self.lista_matrizes:
            n_rows = len(G)
            n_cols = len(G[0]) if n_rows>0 else 0
            for i in range(0, n_rows - 3):
                for j in range(0, n_cols - 3):
                    Gx = np.array([[G[i+u][j+v].x for v in range(4)] for u in range(4)])
                    Gy = np.array([[G[i+u][j+v].y for v in range(4)] for u in range(4)])
                    Gz = np.array([[G[i+u][j+v].z for v in range(4)] for u in range(4)])
                    Cx = MB @ Gx @ MB.T
                    Cy = MB @ Gy @ MB.T
                    Cz = MB @ Gz @ MB.T
                    patch_amostrado = _gerar_patch_forward_diffs_por_slide(Cx, Cy, Cz, n_t, n_s)
                    self.p_calculados.append(patch_amostrado)

class SuperficieBSpline3D(Superficie3D):
    def __init__(self, matriz_pontos, nome="BSpline", n_t=20, n_s=20):
        super().__init__(matriz_pontos, nome)
        # Normaliza matriz_pontos em self.G como lista de linhas de Ponto3D
        self.G = []
        for row in matriz_pontos:
            linha_pts = []
            for p in row:
                if isinstance(p, Ponto3D):
                    linha_pts.append(p)
                else:
                    x, y, z = p
                    linha_pts.append(Ponto3D(x, y, z))
            self.G.append(linha_pts)
        self.n_rows = len(self.G)
        self.n_cols = len(self.G[0]) if self.n_rows>0 else 0
        if self.n_rows < 4 or self.n_cols < 4:
            # permite criação, mas futuras tentativas de subdividir em patches levantarão erro
            pass
        self.n_t = int(n_t)
        self.n_s = int(n_s)
        self.p_calculados = []
        self.patches = []
        try:
            self._subdividir_em_patches()
            self.gerar_curvas_fwd()
        except Exception:
            self.p_calculados = []

    def _subdividir_em_patches(self):
        self.patches = []
        for i in range(self.n_rows - 3):
            for j in range(self.n_cols - 3):
                patch = []
                for r in range(4):
                    linha = []
                    for c in range(4):
                        linha.append(self.G[i + r][j + c])
                    patch.append(linha)
                self.patches.append(patch)

    def gerar_curvas_fwd(self):
        """Gera amostragem via forward differences por patch (B-Spline)."""
        self.p_calculados = []
        n_t = max(1, int(self.n_t))
        n_s = max(1, int(self.n_s))

        # garante patches
        if not getattr(self, "patches", None):
            self._subdividir_em_patches()

        for patch in self.patches:
            Gx = np.array([[patch[r][c].x for c in range(4)] for r in range(4)])
            Gy = np.array([[patch[r][c].y for c in range(4)] for r in range(4)])
            Gz = np.array([[patch[r][c].z for c in range(4)] for r in range(4)])
            Cx = MBS @ Gx @ MBS.T
            Cy = MBS @ Gy @ MBS.T
            Cz = MBS @ Gz @ MBS.T
            patch_amostrado = _gerar_patch_forward_diffs_por_slide(Cx, Cy, Cz, n_t, n_s)
            self.p_calculados.append(patch_amostrado)