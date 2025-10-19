import os
from objetos import *
from objetos_3d import *

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
        """Adiciona um objeto, removendo o anterior se o nome já existe"""
        self.objetos = [obj for obj in self.objetos if obj.nome != objeto.nome]
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
            pontos_str = ";".join([f"{p.x},{p.y},{p.z}" for p in obj.pontos])
            arestas_str = ";".join([f"{i},{j}" for i, j in obj.arestas])
            return f"Objeto3D;{obj.nome};{pontos_str};{arestas_str}"
        elif obj.__class__.__name__ == "SuperficieBezier":
            patches_repr = []
            for patch in obj.patches:
                pts = "|".join([f"{p.x},{p.y},{p.z}" for p in patch])
                patches_repr.append(pts)
            patches_joined = ";".join(patches_repr)
            return f"SuperficieBezier;{obj.nome};{patches_joined}"
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
            _, nome, *resto = partes
            pontos_str_list = resto[0]
            arestas_str_list = resto[1] if len(resto) > 1 else ""
            pontos = []
            p_coords_str = pontos_str_list.split(';') if pontos_str_list else []
            for p_str in p_coords_str:
                try:
                    x, y, z = map(float, p_str.split(','))
                    pontos.append(Ponto3D(x, y, z))
                except ValueError:
                    print(f"[WARN] Ponto 3D inválido em {nome}: {p_str}")
                    continue
            arestas = []
            a_coords_str = arestas_str_list.split(';') if arestas_str_list else []
            for a_str in a_coords_str:
                try:
                    i, j = map(int, a_str.split(','))
                    arestas.append((i, j))
                except ValueError:
                    print(f"[WARN] Aresta inválida em {nome}: {a_str}")
                    continue
            if pontos and arestas:
                return Objeto3D(pontos, arestas, nome)
            else:
                print(f"[WARN] Objeto3D '{nome}' sem pontos ou arestas válidas.")
                return None

        elif tipo == "SuperficieBezier":
            if len(partes) < 3:
                print(f"[WARN] SuperficieBezier incompleta na linha: {linha}")
                return None
            _, nome, *patches_str = partes
            patches = []
            for patch_str in patches_str:
                pt_strs = [s for s in patch_str.split("|") if s.strip()]
                if len(pt_strs) != 16:
                    print(f"[WARN] Patch com {len(pt_strs)} pontos em {nome}, esperado 16. Ignorando patch.")
                    continue
                patch = []
                for p_str in pt_strs:
                    try:
                        x, y, z = map(float, p_str.split(','))
                        patch.append(Ponto3D(x, y, z))
                    except Exception as e:
                        print(f"[WARN] Falha ao parsear ponto da superfície {nome}: {p_str} -> {e}")
                if len(patch) == 16:
                    patches.append(patch)
            if patches:
                return SuperficieBezier(patches, nome)
            else:
                print(f"[WARN] SuperficieBezier '{nome}' sem patches válidos.")
                return None

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
                    x_view, y_view = window3D.mundo_para_view(p)
                    p.x_scn, p.y_scn = window.mundo_para_scn(x_view, y_view)

    def atualizar_perspectiva(self, window, viewport, COP, look_at, d_proj):
        for obj in self.objetos:
            if isinstance(obj, Objeto3D):
                pontos_proj = obj.projetar_perspectiva(COP, look_at, d_proj)
                # Atualiza os x_scn/y_scn dos pontos para desenho e clipping
                for i, p in enumerate(obj.pontos):
                    if i < len(pontos_proj):
                        x_proj, y_proj = pontos_proj[i]
                        p.x_scn, p.y_scn = x_proj, y_proj

