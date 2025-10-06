import numpy as np


def projecao_paralela_ortogonal(pontos3d, VRP, VPN, VUP):

    # 1. Translade VRP para a origem
    T = np.eye(4)
    T[:3, 3] = -np.array([VRP.x, VRP.y, VRP.z])

    # 2. Determine ângulos de VPN (normal)
    vpn = VPN / np.linalg.norm(VPN)
    vup = VUP / np.linalg.norm(VUP)
    z = vpn
    x = np.cross(vup, vpn)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)

    # 3. Rotacionar mundo para alinhar VPN ao eixo Z
    R = np.eye(4)
    R[:3, :3] = np.vstack([x, y, z])

    # 4. Projete ignorando Z
    matriz_proj = np.eye(4)
    matriz_proj[2, 2] = 0  # z <- 0

    # 5. Pipeline única matriz:
    M = matriz_proj @ R @ T

    # 6. Aplique M a cada ponto
    pontos2d = []
    for p in pontos3d:
        vec = np.array([p.x, p.y, p.z, 1])
        vec2d = M @ vec
        pontos2d.append((vec2d[0], vec2d[1]))  # ignore Z

    return pontos2d