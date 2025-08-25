class Window:
    """Classe que gerencia os coordenadas de uma Window (sistema do mundo)"""
    def __init__(self, xw_min: float, yw_min: float, xw_max: float, yw_max: float):
        self.xw_min = xw_min
        self.yw_min = yw_min
        self.xw_max = xw_max
        self.yw_max = yw_max
        self.largura = xw_max - xw_min
        self.altura = yw_max - yw_min

class Viewport:
    """Classe que gerencia os coordenadas de uma Viewport (sistema de tela)"""
    def __init__(self, xvp_min: float, yvp_min: float, xvp_max: float, yvp_max: float):
        self.xvp_min = xvp_min
        self.yvp_min = yvp_min
        self.xvp_max = xvp_max
        self.yvp_max = yvp_max
        self.largura = xvp_max - xvp_min
        self.altura = yvp_max - yvp_min

    def mundo_para_viewport(self, window: Window, x_w: float, y_w: float):
        """Transforma coordenadas do mundo diretamente para viewport em um único passo"""
        x_vp = self.xvp_min + ((x_w - window.xw_min) / window.largura) * self.largura
        y_vp = self.yvp_min + (1 - (y_w - window.yw_min) / window.altura) * self.altura
        return x_vp, y_vp

    def viewport_para_mundo(self, window: Window, x_vp: float, y_vp: float):
        """Transforma coordenadas da viewport para coordenadas do mundo"""
        x_w = window.xw_min + ((x_vp - self.xvp_min) / self.largura) * window.largura
        y_w = window.yw_min + (1 - (y_vp - self.yvp_min) / self.altura) * window.altura
        return x_w, y_w

    def esta_dentro_viewport(self, x_vp: float, y_vp: float):
        """Verifica se as coordenadas estão dentro da viewport"""
        return (self.xvp_min <= x_vp <= self.xvp_max and 
                self.yvp_min <= y_vp <= self.yvp_max)