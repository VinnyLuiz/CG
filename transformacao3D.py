import numpy as np
import math

# Window
class Window3D:
    def __init__(self, vrp, vpn, vup):
        self.vrp = np.array(vrp, dtype=float)
        self.vpn = np.array(vpn, dtype=float)
        self.vup = np.array(vup, dtype=float)
        self.tipo_proj = "paralela"
        self.distancia = 100
        self.COP = np.array([0, 0, 0], dtype=float)

    def mudar_projecao(self, perspectiva: str):
        self.tipo_proj = perspectiva.lower()

    def atualizar_mat_view(self):
        # 1. Leva para a origem
        T = matriz_translacao_3d(-self.vrp[0], -self.vrp[1], -self.vrp[2])

        # 2. Decompor VPN
        n = self.vpn / np.linalg.norm(self.vpn)

        # 3. Rotacionar o Mundo em torno de X e Y
        u = np.cross(self.vup, n)
        u /= np.linalg.norm(u)
        v = np.cross(n, u)

        R = np.array([
            [u[0], u[1], u[2], 0],
            [v[0], v[1], v[2], 0],
            [n[0], n[1], n[2], 0],
            [0,    0,    0,    1]
        ])
        
        return R @ T


    def aplicar_projecao(self, p_view):
        """
        Aplica a matriz de projeção 3D (Perspectiva ou Paralela).
        p_view é o ponto já transformado para SCV: (xv, yv, zv, 1).
        Retorna o ponto homogêneo transformado (x', y', z', h).
        """
        if self.tipo_proj == "perspectiva":
            # 1. Aplica M_PROJ
            M_PROJ = matriz_projecao_perspectiva(self.distancia)
            p_proj = M_PROJ @ p_view
            
            # 2. Divisão em Perspectiva (Dehomogeneização)
            # O quarto elemento (w ou h) é p_proj[3].
            h = p_proj[3]
            if abs(h) < 1e-6: # Evita divisão por zero (ponto no COP)
                h = 1.0 

            # Transforma (x', y', z', h) para (x_pp, y_pp, z_pp, 1)
            x_pp = p_proj[0] / h
            y_pp = p_proj[1] / h
            # O z_pp é usado para Z-Buffer/Clipping de profundidade
            z_pp = p_proj[2] / h
            
            return x_pp, y_pp, z_pp
            
        else: # Projeção Paralela (Ortogonal)
            # No SCV, a projeção já é dada por X e Y (descartando Z)
            return p_view[0], p_view[1], p_view[2]


    def mundo_para_view(self, p):
        M_VIEW = self.atualizar_mat_view()
        P_SCM_hom = np.array([p.x, p.y, p.z, 1])
        P_SCV_hom = M_VIEW @ P_SCM_hom
        
        x_v, y_v, z_v = P_SCV_hom[0], P_SCV_hom[1], P_SCV_hom[2]
        
        if self.tipo_proj == "perspectiva":
            cx, cy, cz = self.COP
            
            M_T_COP = matriz_translacao_3d(-cx, -cy, -cz)
            P_SCV_CENTRO_COP = M_T_COP @ P_SCV_hom
            
            M_PROJ = matriz_projecao_perspectiva(self.distancia)
            P_PROJ_hom = M_PROJ @ P_SCV_CENTRO_COP
            
            h = P_PROJ_hom[3]
            
            if h <= 1e-6:
                return 99999, 99999, z_v 

            x_pp_centro = P_PROJ_hom[0] / h
            y_pp_centro = P_PROJ_hom[1] / h
            
            x_pp = x_pp_centro + cx
            y_pp = y_pp_centro + cy
            
            return x_pp, y_pp, z_v
            
        return x_v, y_v, z_v



# Projeção
def proj_ortogonal(pov):
    x, y, z = pov
    return np.array([x, y, 0])

def matriz_projecao_perspectiva(d):
    """Cria a matriz de projeção em perspectiva com distância d do plano de projeção."""
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 1/d, 0]
    ], dtype=float)

# Matrizes
def matriz_translacao_3d(dx, dy, dz):
    """Cria uma matriz de translação 3D."""
    return np.array([
        [1, 0, 0, dx],
        [0, 1, 0, dy],
        [0, 0, 1, dz],
        [0, 0, 0, 1]
    ], dtype=float)

def matriz_escalonamento_3d(sx, sy, sz, cx=0, cy=0, cz=0):
    """Cria uma matriz de escala 3D em torno de um ponto (cx, cy, cz)."""
    T1 = matriz_translacao_3d(-cx, -cy, -cz)
    T2 = matriz_translacao_3d(cx, cy, cz)
    S = np.array([
        [sx, 0,  0,  0],
        [0, sy,  0,  0],
        [0,  0, sz,  0],
        [0,  0,  0,  1]
    ], dtype=float)
    return T2 @ S @ T1

def matriz_rotacao_x(angulo):
    """Rotação em torno do eixo X."""
    rad = math.radians(angulo)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return np.array([
        [1, 0,      0,     0],
        [0, cos_a, sin_a, 0],
        [0, -sin_a,  cos_a, 0],
        [0, 0,      0,     1]
    ], dtype=float)

def matriz_rotacao_y(angulo):
    """Rotação em torno do eixo Y."""
    rad = math.radians(angulo)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return np.array([
        [cos_a,  0, -sin_a, 0],
        [0,      1, 0,     0],
        [sin_a, 0, cos_a, 0],
        [0,      0, 0,     1]
    ], dtype=float)

def matriz_rotacao_z(angulo):
    """Rotação em torno do eixo Z."""
    rad = math.radians(angulo)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return np.array([
        [cos_a, sin_a, 0, 0],
        [-sin_a,  cos_a, 0, 0],
        [0,      0,     1, 0],
        [0,      0,     0, 1]
    ], dtype=float)

def matriz_rotacao_arbitraria(p1, p2, angulo):
    # 1. Translação para origem
    T1 = matriz_translacao_3d(-p1.x, -p1.y, -p1.z)
    
    # 2. Calcular deltas e ângulos
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    dz = p2.z - p1.z
    
    theta_x = math.atan2(dy, dz)
    theta_z = -math.atan2(dx, math.sqrt(dy**2 + dz**2))
    
    # 3. Matrizes de rotação
    Rx = matriz_rotacao_x(math.degrees(theta_x))
    Rz = matriz_rotacao_z(math.degrees(theta_z))
    Ry = matriz_rotacao_y(angulo)
    
    # 4. Montagem final
    M = (
        matriz_translacao_3d(p1.x, p1.y, p1.z) @
        Rz.T @ Rx.T @ Ry @ Rx @ Rz @
        T1
    )
    return M

def centro_geom_3d(objeto):
    n = len(objeto.pontos)
    if n == 0:
        return (0, 0, 0)
    cx = sum(p.x for p in objeto.pontos) / n
    cy = sum(p.y for p in objeto.pontos) / n
    cz = sum(p.z for p in objeto.pontos) / n
    return (cx, cy, cz)

