class Objeto3D:
    def __init__(self, segmentos, nome="objeto3d"):
        self.segmentos = segmentos
        self.nome = nome

    def transformar(self, matriz):
        for seg in self.segmentos:
            for p in seg:
                p.transformar(matriz)

    def translacao(self, dx, dy, dz):
        T = np.eye(4)
        T[:3, 3] = [dx, dy, dz]
        self.transformar(T)

    def escala(self, sx, sy, sz):
        S = np.diag([sx, sy, sz, 1])
        self.transformar(S)

    def rotacao_x(self, ang_deg):
        for seg in self.segmentos:
            for p in seg:
                p.rotacao_x(ang_deg)

    def rotacao_y(self, ang_deg):
        for seg in self.segmentos:
            for p in seg:
                p.rotacao_y(ang_deg)

    def rotacao_z(self, ang_deg):
        for seg in self.segmentos:
            for p in seg:
                p.rotacao_z(ang_deg)
