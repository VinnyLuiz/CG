import os
from objetos import *
from objetos_3d import *
from superficies3d import SuperficieBezier3D, SuperficieBSpline3D

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
            return f"Ponto;{obj.nome};{obj.x};{obj.y}"
        elif obj.__class__.__name__ == "Reta":
            return f"Reta;{obj.nome};{obj.ponto0.x};{obj.ponto0.y};{obj.ponto1.x};{obj.ponto1.y}"
        elif obj.__class__.__name__ == "Wireframe":
            coords = ";".join([f"{p.x};{p.y}" for p in obj.lista_pontos])
            return f"Wireframe;{obj.nome};{obj.preencher};{obj.cor_preenchimento};{coords}"
        elif obj.__class__.__name__ == "Curva2D":
            coords = ";".join([f"{p.x};{p.y}" for p in obj.pontos])
            return f"Curva2D;{obj.nome};{coords}"
        elif obj.__class__.__name__ == "BSpline":
            coords = ";".join([f"{p.x};{p.y}" for p in obj.pontos])
            return f"BSpline;{obj.nome};{coords}"
        elif obj.__class__.__name__ == "Objeto3D":
            pontos_str = ";".join([f"{p.x};{p.y};{p.z}" for p in obj.pontos])
            arestas_str = ";".join([f"{i};{j}" for i, j in obj.arestas])
            tam_pontos = len(obj.pontos)
            tam_arestas = len(obj.arestas)
            return f"Objeto3D;{obj.nome};{tam_pontos};{tam_arestas};{pontos_str};{arestas_str}"
        elif obj.__class__.__bases__[0].__name__ == "Superficie3D":
            str_matriz = obj.unpack_matriz()
            if obj.tipoS == "Bezier":
                return f"SuperficieBezier3D;{obj.nome};{str_matriz}"
            else:
                return f"SuperficieBSpline3D;{obj.nome};{str_matriz}"
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
            _, nome,  preencher, cor_preenchimento, *coords,= partes
            pontos = []
            for i in range(0, len(coords), 2):
                x, y = coords[i], coords[i+1]
                pontos.append(Ponto(float(x), float(y), f"{nome}_p{i//2}"))
            preencher = preencher.lower() == 'true'
            return Wireframe(pontos, nome, preencher, cor_preenchimento)
        
        elif tipo == "Curva2D":
            if len(partes) < 4:
                return None
            _, nome, *coords = partes
            pontos = []
            for i in range(0, len(coords), 2):
                x, y = coords[i], coords[i+1]
                pontos.append(Ponto(float(x), float(y), f"{nome}_p{i//2}"))
            return Curva2D(pontos, nome)
            
        elif tipo == "BSpline":
            if len(partes) < 4:
                return None
            _, nome, *coords = partes
            pontos = []
            for i in range(0, len(coords), 2):
                x, y = coords[i], coords[i+1]
                pontos.append(Ponto(float(x), float(y), f"{nome}_p{i//2}"))
            return BSpline(pontos, nome)

        elif tipo == "Objeto3D":
            if len(partes) < 4:
                print(f"[WARN] Objeto3D incompleto na linha: {linha}")
                return None
            _, nome, tam_pontos, tam_arestas = partes[0], partes[1], int(partes[2]) * 3, int(partes[3]) * 2
            partes = partes[4::]
            pontos_str_list = list(map(float, partes[:tam_pontos]))
            arestas_str_list = [int(x) for x in partes[tam_pontos:] if x.strip() != ""]

            pontos = []
            for i in range(0, len(pontos_str_list), 3):
                x, y, z = pontos_str_list[i], pontos_str_list[i+1], pontos_str_list[i+2]
                pontos.append(Ponto3D(x, y, z))
            arestas = []
            for i in range(0, len(arestas_str_list), 2):
                p0 = arestas_str_list[i]
                p1 = arestas_str_list[i + 1]
                arestas.append((p0, p1))
            if pontos and arestas:
                return Objeto3D(pontos, arestas, nome)
            else:
                print(f"[WARN] Objeto3D '{nome}' sem pontos ou arestas válidas.")
                return None
        
        elif tipo == "SuperficieBezier3D" or tipo == "SuperficieBSpline3D":
            partes = linha.split(";", 2)
            _, nome, string_coordenadas = partes[0], partes[1], partes[2]
            linhas_str = string_coordenadas.split(';')
            nro_mats = len(linhas_str) // 4
            lista_matrizes = []
            for i in range(nro_mats):
                mat = []
                bloco_linhas = linhas_str[i*4: (i*4)+4]
                for linha_str in bloco_linhas:
                    linha_str = linha_str.strip()
                    if not linha_str:
                        continue
                        
                    # Divide os pontos da linha
                    pontos_str = linha_str.split('),')
                    linha_pontos = []
                    
                    for ponto_str in pontos_str:
                        ponto_str = ponto_str.strip()
                        # Corrige a formatação se necessário
                        if ponto_str and not ponto_str.endswith(')'):
                            ponto_str += ')'
                        if ponto_str:
                            # Remove parênteses e divide os valores
                            coord_str = ponto_str.replace('(', '').replace(')', '')
                            valores = coord_str.split(',')
                            
                            if len(valores) == 3:
                                x = float(valores[0].strip())
                                y = float(valores[1].strip())
                                z = float(valores[2].strip())
                                linha_pontos.append(Ponto3D(x, y, z))
                    if linha_pontos:
                        mat.append(linha_pontos)
                lista_matrizes.append(mat)
            return SuperficieBezier3D(lista_matrizes, nome) if tipo == "SuperficieBezier3D" else SuperficieBSpline3D(lista_matrizes, nome)
            

        else:
            print(f"[WARN] Tipo de objeto desconhecido: {linha}")
            return None
         
    def adicionar_from_obj(self, nome, coords, tipo=None):
        """Adiciona um objeto vindo do importador OBJ"""
        if tipo == "reta" and len(coords) == 2:
            obj = Reta(Ponto(*coords[0]), Ponto(*coords[1]), nome=nome)
        elif tipo == "wireframe" and len(coords) >= 2:
            pontos = [Ponto(*c) for c in coords]
            obj = Wireframe(pontos, nome=nome)
        elif tipo == "ponto" or (len(coords) == 1):
            obj = Ponto(coords[0][0], coords[0][1], nome=nome)
        else:
            print(f"[WARN] Tipo '{tipo}' ou coords inválidos para {nome}")
            return
        self.objetos.append(obj)  

    def atualizar_scn(self, window, window3D):
        for obj in self.objetos:
            if isinstance(obj, Ponto):
                obj.x_scn, obj.y_scn = window.mundo_para_scn(obj.x, obj.y)
            elif isinstance(obj, Reta):
                obj.ponto0.x_scn, obj.ponto0.y_scn = window.mundo_para_scn(obj.ponto0.x, obj.ponto0.y)
                obj.ponto1.x_scn, obj.ponto1.y_scn = window.mundo_para_scn(obj.ponto1.x, obj.ponto1.y)
            elif isinstance(obj, Wireframe):
                for p in obj.lista_pontos:
                    p.x_scn, p.y_scn = window.mundo_para_scn(p.x, p.y)
            elif isinstance(obj, Curva2D):
                for p in obj.p_curvas:
                    p.x_scn, p.y_scn = window.mundo_para_scn(p.x, p.y)
            elif isinstance(obj, BSpline):
                for p in obj.p_bspline:
                    p.x_scn, p.y_scn = window.mundo_para_scn(p.x, p.y)
            elif isinstance(obj, Ponto3D):
                x_view, y_view = window3D.mundo_para_view(obj)
                obj.x_scn, obj.y_scn = window.mundo_para_scn(x_view, y_view)
            elif isinstance(obj, Objeto3D):
                for p in obj.pontos:
                    x_pp, y_pp, z_pp = window3D.mundo_para_view(p)
                    p.x_scn, p.y_scn = window.mundo_para_scn(x_pp, y_pp)
            elif isinstance(obj, SuperficieBezier3D) or isinstance(obj, SuperficieBSpline3D):
                for linha in obj.p_calculados:
                    for p in linha:
                        x_pp, y_pp, z_pp = window3D.mundo_para_view(p)
                        p.x_scn, p.y_scn = window.mundo_para_scn(x_pp, y_pp)
