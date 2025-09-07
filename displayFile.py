import os
from objetos import Ponto, Reta, Wireframe

class DisplayFile:
    def __init__(self, arquivo="objetos.txt"):
        self.objetos = []
        self.arquivo = arquivo

        # cria o arquivo se não existir
        if not os.path.exists(self.arquivo):
            open(self.arquivo, "w").close()

        # tenta carregar objetos já salvos
        self.carregar_do_arquivo()

    def get_objeto(self, nome_objeto):
        for obj in self.objetos:
            if obj.nome == nome_objeto:
                return obj

    def nome_existe(self, nome):
        """Verifica se um nome já existe na lista de objetos"""
        return any(obj.nome == nome for obj in self.objetos)

    def adicionar(self, objeto):
        """Adiciona um objeto, mas verifica se o nome já existe"""
        if self.nome_existe(objeto.nome):
            raise ValueError(f"Já existe um objeto com o nome '{objeto.nome}'")
        self.objetos.append(objeto)
        self.salvar_em_arquivo()

    def remover(self, objeto):
        """Remove um Objeto, pelo nome do objeto ou por objeto em si"""
        if type(objeto) == str:
            objeto = self.get_objeto(objeto)
        self.objetos.remove(objeto)
        self.salvar_em_arquivo()

    def salvar_em_arquivo(self):
        """Reescreve o arquivo inteiro com todos os objetos atuais"""
        with open(self.arquivo, "w", encoding="utf-8") as f:
            for obj in self.objetos:
                f.write(self.serializar_objeto(obj) + "\n")

    def carregar_do_arquivo(self):
        """Lê o arquivo e recria os objetos"""
        with open(self.arquivo, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue
                obj = self.desserializar_objeto(linha)
                if obj:
                    self.objetos.append(obj)

    def serializar_objeto(self, obj):
        """Transforma o objeto em string para salvar no arquivo"""
        if obj.__class__.__name__ == "Ponto":
            return f"Ponto;{obj.nome};{obj.x_wc};{obj.y_wc}"
        elif obj.__class__.__name__ == "Reta":
            return f"Reta;{obj.nome};{obj.ponto0.x_wc};{obj.ponto0.y_wc};{obj.ponto1.x_wc};{obj.ponto1.y_wc}"
        elif obj.__class__.__name__ == "Wireframe":
            coords = ";".join([f"{p.x_wc};{p.y_wc}" for p in obj.lista_pontos])
            return f"Wireframe;{obj.nome};{coords}"
        else:
            return f"{obj.__class__.__name__};{vars(obj)}"

    def desserializar_objeto(self, linha):
        """Recria o objeto a partir de uma string salva"""
        partes = linha.split(";")
        tipo = partes[0]

        if tipo == "Ponto":
            _, nome, x, y = partes
            return Ponto(float(x), float(y), nome)

        elif tipo == "Reta":
            _, nome, x0, y0, x1, y1 = partes
            p0 = Ponto(float(x0), float(y0), f"{nome}_p0")
            p1 = Ponto(float(x1), float(y1), f"{nome}_p1")
            return Reta(p0, p1, nome)

        elif tipo == "Wireframe":
            _, nome, *coords = partes
            pontos = []
            for i in range(0, len(coords), 2):
                x, y = coords[i], coords[i+1]
                pontos.append(Ponto(float(x), float(y), f"{nome}_p{i//2}"))
            return Wireframe(pontos, nome)

        else:
            print(f"[WARN] Tipo de objeto desconhecido: {linha}")
            return None

    def atualizar_scn(self, window):
        for obj in self.objetos:
            if isinstance(obj, Ponto):
                obj.x_scn, obj.y_scn = window.mundo_para_scn(obj.x, obj.y)
            elif isinstance(obj, Reta):
                obj.ponto0.x_scn, obj.ponto0.y_scn = window.mundo_para_scn(obj.ponto0.x, obj.ponto0.y)
                obj.ponto1.x_scn, obj.ponto1.y_scn = window.mundo_para_scn(obj.ponto1.x, obj.ponto1.y)
            elif isinstance(obj, Wireframe):
                for p in obj.lista_pontos:
                    p.x_scn, p.y_scn = window.mundo_para_scn(p.x, p.y)

