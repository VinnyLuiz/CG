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
        self.aplicar_matriz(matriz_translacao_3d(-dx, -dy, -dz))

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
        
    def rotacionar_em_torno_objeto(self, eixo, angulo):
        cx, cy, cz = centro_geom_3d(self)
        
        if eixo == 'x':
            R = matriz_rotacao_x(angulo)
        elif eixo == 'y':
            R = matriz_rotacao_y(angulo)
        elif eixo == 'z':
            R = matriz_rotacao_z(angulo)
        else:
            raise ValueError("Eixo inválido, use 'x', 'y' ou 'z'")

        M = matriz_translacao_3d(cx, cy, cz) @ R @ matriz_translacao_3d(-cx, -cy, -cz)
        self.aplicar_matriz(M)

    def rotacionar_em_torno_ponto(self, eixo, angulo, px, py, pz):
        if eixo == 'x':
            R = matriz_rotacao_x(angulo)
        elif eixo == 'y':
            R = matriz_rotacao_y(angulo)
        elif eixo == 'z':
            R = matriz_rotacao_z(angulo)
        else:
            raise ValueError("Eixo inválido")

        M = matriz_translacao_3d(px, py, pz) @ R @ matriz_translacao_3d(-px, -py, -pz)
        self.aplicar_matriz(M)

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


        







