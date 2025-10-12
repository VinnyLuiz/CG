from transformacao3D import *
from clipping import clip_reta_CS, clip_reta_NLN

# Objetos
class Ponto3D:
    def __init__(self, x, y, z, nome=None):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.x_scn = 0
        self.y_scn = 0
        self.z_scn = 0
        self.nome = nome or f"P({x},{y},{z})"

    def aplicar_matriz(self, matriz):
        p = np.array([self.x, self.y, self.z, 1])
        p_t = matriz @ p
        self.x, self.y, self.z = p_t[0], p_t[1], p_t[2]

    def __repr__(self):
        return f"Ponto3D({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

class Objeto3D:
    """Modelo de Arame em 3D (Wireframe 3D)"""
    def __init__(self, pontos, arestas, nome="objeto3D"):
        self.nome = nome
        self.pontos = pontos
        # Arestas é uma lista de tuplas com quais os pontos de conectam. ex: (p0, p1)
        self.arestas = arestas
        self.selecionado = False

    def aplicar_matriz(self, matriz):
        for p in self.pontos:
            p.aplicar_matriz(matriz)

    # Operações básicas
    def transladar(self, dx, dy, dz):
        self.aplicar_matriz(matriz_translacao_3d(dx, dy, dz))

    def escalar(self, sx, sy, sz, cx=0, cy=0, cz=0):
        self.aplicar_matriz(matriz_escalonamento_3d(sx, sy, sz, cx, cy, cz))

    def rotacionar_x(self, angulo):
        self.aplicar_matriz(matriz_rotacao_x(angulo))

    def rotacionar_y(self, angulo):
        self.aplicar_matriz(matriz_rotacao_y(angulo))

    def rotacionar_z(self, angulo):
        self.aplicar_matriz(matriz_rotacao_z(angulo))

    def rotacionar_arbitrario(self, p1, p2, angulo):
        self.aplicar_matriz(matriz_rotacao_arbitraria(p1, p2, angulo))
        
    # Projeção
    def projetar(self, window3D):
        lista_p_proj = []
        for p in self.pontos:
            p_view = window3D.mundo_para_view(p)
            p_proj = proj_ortogonal(p_view)
            lista_p_proj.append((p_proj[0], p_proj[1]))
        return lista_p_proj
    
    def desenhar(self, canvas, window, viewport, modo_clipping):
        # Itera sobre as arestas (conexões entre pontos)
        for idx_p0, idx_p1 in self.arestas:
            p0 = self.pontos[idx_p0]
            p1 = self.pontos[idx_p1]
            match modo_clipping:
                case "Cohen-Sutherland":
                    check_clipping = clip_reta_CS(p0.x_scn, p0.y_scn, p1.x_scn, p1.y_scn)
                case "Nicholl-Lee-Nicholl":
                    check_clipping = clip_reta_NLN(p0.x_scn, p0.y_scn, p1.x_scn, p1.y_scn)
            if check_clipping is not None:
                x0, y0, x1, y1 = check_clipping 
                # Mapeamento para Viewport (Tela)
                x_vp0, y_vp0 = viewport.scn_para_viewport(x0, y0)
                x_vp1, y_vp1 = viewport.scn_para_viewport(x1, y1)
                
                # Desenho final
                cor = "blue" if self.selecionado else "black"
                canvas.create_line(x_vp0, y_vp0, x_vp1, y_vp1, fill=cor, width=2)
    
    def projetar_perspectiva(self, COP, look_at, d_proj):
        pontos = [(p.x, p.y, p.z) for p in self.pontos]
        cx, cy, cz = COP
        pontos = [(x-cx, y-cy, z-cz) for (x, y, z) in pontos]
        vpn = (look_at[0]-cx, look_at[1]-cy, look_at[2]-cz)
        vx, vy, vz = vpn
        theta = np.arctan2(vx, vz)
        Ry = np.array([
            [np.cos(-theta), 0, np.sin(-theta)],
            [0, 1, 0],
            [-np.sin(-theta), 0, np.cos(-theta)]
        ])
        pontos_rot = [Ry @ np.array([x, y, z]) for x, y, z in pontos]
        vpn_rot = Ry @ np.array([vx, vy, vz])
        phi = np.arctan2(vpn_rot[1], vpn_rot[2])
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(phi), -np.sin(phi)],
            [0, np.sin(phi), np.cos(phi)]
        ])
        pontos_final = [Rx @ p for p in pontos_rot]
        lista_p_proj = []
        for pt in pontos_final:
            x, y, z = pt
            if z <= 0: continue  # evita divisão por zero e pontos atrás do plano
            x_proj = x * d_proj / z
            y_proj = y * d_proj / z
            lista_p_proj.append((x_proj, y_proj))
        return lista_p_proj
    def desenhar_perspectiva(self, canvas, viewport, COP, look_at, d_proj, modo_clipping):
        pontos_proj = self.projetar_perspectiva(COP, look_at, d_proj)
        # Itera sobre as arestas (conexões entre pontos)
        for idx_p0, idx_p1 in self.arestas:
            if idx_p0 >= len(pontos_proj) or idx_p1 >= len(pontos_proj):
                continue
            x0, y0 = pontos_proj[idx_p0]
            x1, y1 = pontos_proj[idx_p1]
            match modo_clipping:
                case "Cohen-Sutherland":
                    check_clipping = clip_reta_CS(x0, y0, x1, y1)
                case "Nicholl-Lee-Nicholl":
                    check_clipping = clip_reta_NLN(x0, y0, x1, y1)
                case _:
                    check_clipping = (x0, y0, x1, y1)
            if check_clipping is not None:
                x0c, y0c, x1c, y1c = check_clipping 
                # Mapeamento para Viewport (Tela)
                x_vp0, y_vp0 = viewport.scn_para_viewport(x0c, y0c)
                x_vp1, y_vp1 = viewport.scn_para_viewport(x1c, y1c)
                cor = "red" if self.selecionado else "black"
                canvas.create_line(x_vp0, y_vp0, x_vp1, y_vp1, fill=cor, width=2)


        







