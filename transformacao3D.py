import numpy as np
import math

# Window
class Window3D:
    def __init__(self, vrp, vpn, vup):
        self.vrp = np.array(vrp, dtype=float)
        self.vpn = np.array(vpn, dtype=float)
        self.vup = np.array(vup, dtype=float)

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

    def mundo_para_view(self, p):
        M = self.atualizar_mat_view()
        P = np.array([p.x, p.y, p.z, 1])
        p_view = M @ P
        return p_view[0], p_view[1]

def proj_ortogonal(pov):
    x, y, z = pov
    return np.array([x, y, 0])

# Matrizes
def matriz_translacao_3d(dx, dy, dz):
    """Cria uma matriz de translação 3D."""
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [dx, dy, dz, 1]
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
