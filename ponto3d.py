import numpy as np

class Ponto3D:
    def __init__(self, x, y, z, nome="ponto3d"):
        self.x = x
        self.y = y
        self.z = z
        self.nome = nome

    def get_coords(self):
        return np.array([self.x, self.y, self.z, 1])

    def set_coords(self, arr):
        self.x, self.y, self.z = arr[:3]

    def transformar(self, matriz):
        res = matriz @ self.get_coords()
        self.set_coords(res)

    def translacao(self, dx, dy, dz):
        T = np.eye(4)
        T[:3, 3] = [dx, dy, dz]
        self.transformar(T)

    def escala(self, sx, sy, sz):
        S = np.diag([sx, sy, sz, 1])
        self.transformar(S)

    def rotacao_x(self, ang_deg):
        ang = np.radians(ang_deg)
        R = np.eye(4)
        R[1, 1] = np.cos(ang)
        R[1, 2] = -np.sin(ang)
        R[2, 1] = np.sin(ang)
        R[2, 2] = np.cos(ang)
        self.transformar(R)

    def rotacao_y(self, ang_deg):
        ang = np.radians(ang_deg)
        R = np.eye(4)
        R[0, 0] = np.cos(ang)
        R[0, 2] = np.sin(ang)
        R[2, 0] = -np.sin(ang)
        R[2, 2] = np.cos(ang)
        self.transformar(R)

    def rotacao_z(self, ang_deg):
        ang = np.radians(ang_deg)
        R = np.eye(4)
        R[0, 0] = np.cos(ang)
        R[0, 1] = -np.sin(ang)
        R[1, 0] = np.sin(ang)
        R[1, 1] = np.cos(ang)
        self.transformar(R)

    def __repr__(self):
        return f"Ponto3D({self.x}, {self.y}, {self.z})"