mport os
import re
from objetos import *
from objetos_3d import *
from superficies3d import SuperficieBezier3D, SuperficieBSpline3D, Superficie3D

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
        print(f"[DEBUG] Carregando arquivo de objetos: {self.arquivo}")
        with open(self.arquivo, "r", encoding="utf-8") as f:
            linhas = f.readlines()
        print(f"[DEBUG] {len(linhas)} linhas lidas do arquivo.")
        for idx, linha in enumerate(linhas, start=1):
            linha = linha.strip()
            if not linha:
                continue
            print(f"[DEBUG] Linha {idx}: {linha[:200]}")
            obj = self.desserializar_objeto(linha)
            print(f"[DEBUG] desserializar_objeto -> {obj}")
            if obj:
                try:
                    self.objetos.append(obj)
                    print(f"[DEBUG] Adicionado {getattr(obj,'nome',str(obj))} ({obj.__class__.__name__})")
                except Exception as e:
                    print(f"[ERROR] Falha ao adicionar objeto lido: {e}")

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
            try:
                str_matriz = obj.unpack_matriz()
            except Exception:
                lm = getattr(obj, "lista_matrizes", None)
                if not lm:
                    str_matriz = ""
                else:
                    linhas_all = []
                    try:
                        # lm pode ser lista de patches ou matriz única
                        if isinstance(lm[0][0], (int, float)):
                            for bloco in lm:
                                linhas_all.append(",".join([f"({float(x):.6f},{float(y):.6f},{float(z):.6f})" for (x,y,z) in bloco]))
                        else:
                            if isinstance(lm[0][0], (list, tuple)) and hasattr(lm[0][0][0], "x"):
                                for patch in lm:
                                    for row in patch:
                                        linhas_all.append(",".join([f"({p.x:.6f},{p.y:.6f},{p.z:.6f})" for p in row]))
                            elif isinstance(lm[0], (list, tuple)) and hasattr(lm[0][0], "x"):
                                for row in lm:
                                    linhas_all.append(",".join([f"({p.x:.6f},{p.y:.6f},{p.z:.6f})" for p in row]))
                            else:
                                def _iter_collect(obj):
                                    if obj is None:
                                        return
                                    if hasattr(obj, "x") and hasattr(obj, "y") and hasattr(obj, "z"):
                                        yield obj
                                    elif isinstance(obj, (list, tuple)):
                                        for sub in obj:
                                            yield from _iter_collect(sub)
                                pts = list(_iter_collect(lm))
                                for i in range(0, len(pts), 4):
                                    chunk = pts[i:i+4]
                                    linhas_all.append(",".join([f"({p.x:.6f},{p.y:.6f},{p.z:.6f})" for p in chunk]))
                        str_matriz = ";".join(linhas_all)
                    except Exception:
                        str_matriz = ""
            if getattr(obj, "tipoS", "BSpline") == "Bezier":
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
            try:
                _, nome, x, y = partes
                return Ponto(float(x), float(y), nome)
            except Exception:
                print(f"[WARN] Falha ao desserializar Ponto: {linha}")
                return None

        elif tipo == "Reta":
            try:
                _, nome, x0, y0, x1, y1 = partes
                p0 = Ponto(float(x0), float(y0), f"{nome}_p0")
                p1 = Ponto(float(x1), float(y1), f"{nome}_p1")
                return Reta(p0, p1, nome)
            except Exception:
                print(f"[WARN] Falha ao desserializar Reta: {linha}")
                return None

        elif tipo == "Wireframe":
            try:
                _, nome,  preencher, cor_preenchimento, *coords,= partes
                pontos = []
                for i in range(0, len(coords), 2):
                    x, y = coords[i], coords[i+1]
                    pontos.append(Ponto(float(x), float(y), f"{nome}_p{i//2}"))
                preencher = preencher.lower() == 'true'
                return Wireframe(pontos, nome, preencher, cor_preenchimento)
            except Exception:
                print(f"[WARN] Falha ao desserializar Wireframe: {linha}")
                return None

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
            try:
                if len(partes) >= 4:
                    n_pts = int(partes[2])
                    n_arestas = int(partes[3])
                    rem = partes[4:]
                    rem = [r for r in rem if r.strip() != ""]
                    expected_nums = n_pts * 3 + n_arestas * 2
                    if len(rem) < expected_nums:
                        print(f"[WARN] Esperado {expected_nums} valores para pontos+arestas, mas encontrei {len(rem)}. Tentando usar o que existe.")
                    pontos = []
                    cnt_pts_vals = min(len(rem), n_pts * 3)
                    for i in range(0, cnt_pts_vals, 3):
                        try:
                            x = float(rem[i]); y = float(rem[i+1]); z = float(rem[i+2])
                            pontos.append(Ponto3D(x, y, z))
                        except Exception as e:
                            print(f"[WARN] Falha ao parsear ponto no Objeto3D '{partes[1]}': {e}")
                            break
                    arestas = []
                    start_edges = cnt_pts_vals
                    end_edges = min(len(rem), cnt_pts_vals + n_arestas * 2)
                    for i in range(start_edges, end_edges, 2):
                        try:
                            p0 = int(rem[i])
                            p1 = int(rem[i+1])
                            arestas.append((p0, p1))
                        except Exception as e:
                            print(f"[WARN] Falha ao parsear aresta no Objeto3D '{partes[1]}': {e}")
                            break

                    if pontos:
                        n = len(pontos)
                        if arestas:
                            max_idx = max(max(a, b) for (a, b) in arestas)
                            min_idx = min(min(a, b) for (a, b) in arestas)
                            # hipótese 1: arestas estão 1-based (ex.: 1..n) -> converte
                            if min_idx >= 1 and max_idx >= n:
                                converted = [(a-1, b-1) for (a, b) in arestas]
                                if all(0 <= a < n and 0 <= b < n for (a, b) in converted):
                                    arestas = converted
                                    print(f"[INFO] Arestas de '{partes[1]}' convertidas de 1-based para 0-based.")
                            valid_arestas = []
                            invalid_count = 0
                            for (a, b) in arestas:
                                if 0 <= a < n and 0 <= b < n:
                                    valid_arestas.append((a, b))
                                else:
                                    invalid_count += 1
                            if invalid_count:
                                print(f"[WARN] {invalid_count} arestas inválidas removidas de '{partes[1]}'.")
                            arestas = valid_arestas

                        return Objeto3D(pontos, arestas, partes[1])
                    else:
                        print(f"[WARN] Objeto3D '{partes[1]}' sem pontos válidos (formato com contadores).")
                        return None
                else:
                    raise ValueError("Formato esperado com contadores ausente")
            except Exception:
                try:
                    rest = linha.split(";", 2)[2]  # tudo após o segundo ';'
                except Exception:
                    print(f"[WARN] Não foi possível isolar o conteúdo de Objeto3D: {linha}")
                    return None

                num_re = re.compile(r'[-+]?\d*\.\d+(?:[eE][-+]?\d+)?|[-+]?\d+')
                nums = num_re.findall(rest)
                if not nums:
                    print(f"[WARN] Nenhum número encontrado para Objeto3D '{partes[1]}'. Linha: {linha}")
                    return None
                nums_f = [float(n) for n in nums]

                if len(nums_f) >= 3 and (len(nums_f) % 3) == 0:
                    pontos = []
                    for i in range(0, len(nums_f), 3):
                        x, y, z = nums_f[i], nums_f[i+1], nums_f[i+2]
                        pontos.append(Ponto3D(x, y, z))
                    print(f"[INFO] Objeto3D '{partes[1]}' importado com {len(pontos)} pontos (sem arestas).")
                    return Objeto3D(pontos, [], partes[1])

                tokens = [t.strip() for t in rest.split(";") if t.strip()]
                pontos = []
                arestas = []
                for tok in tokens:
                    if "," in tok:
                        parts_comma = [s.strip() for s in tok.split(",") if s.strip() != ""]
                        if len(parts_comma) == 3:
                            try:
                                x = float(parts_comma[0]); y = float(parts_comma[1]); z = float(parts_comma[2])
                                pontos.append(Ponto3D(x, y, z))
                                continue
                            except:
                                pass
                        elif len(parts_comma) == 2:
                            try:
                                p0 = int(parts_comma[0]); p1 = int(parts_comma[1])
                                arestas.append((p0, p1))
                                continue
                            except:
                                pass
                if pontos:
                    n = len(pontos)
                    if arestas:
                        if all(i >= 1 for a,b in arestas for i in (a,b)):
                            converted = [(a-1, b-1) for (a,b) in arestas]
                            if all(0 <= a < n and 0 <= b < n for (a,b) in converted):
                                arestas = converted
                                print(f"[INFO] Arestas convertidas de 1-based para 0-based (fallback) para '{partes[1]}'")
                    valid_arestas = []
                    invalid_count = 0
                    for (a,b) in arestas:
                        if 0 <= a < n and 0 <= b < n:
                            valid_arestas.append((a,b))
                        else:
                            invalid_count += 1
                    if invalid_count:
                        print(f"[WARN] {invalid_count} arestas inválidas removidas (fallback) de '{partes[1]}'.")
                    arestas = valid_arestas

                    print(f"[INFO] Objeto3D '{partes[1]}' importado via fallback com {len(pontos)} pontos e {len(arestas)} arestas.")
                    return Objeto3D(pontos, arestas, partes[1])
                else:
                    print(f"[WARN] Não foi possível parsear Objeto3D '{partes[1]}' a partir da linha: {linha}")
                    return None
        elif tipo.startswith("SuperficieBezier") or tipo.startswith("SuperficieBSpline") or tipo == "SuperficieBezier" or tipo == "SuperficieBSpline":
            partes2 = linha.split(";", 2)
            if len(partes2) < 3:
                print(f"[WARN] Linha de superfície inválida: {linha}")
                return None
            _, nome, string_coordenadas = partes2[0], partes2[1], partes2[2]
            lista_matrizes = []

            if '|' in string_coordenadas:
                patches_str = [p.strip() for p in string_coordenadas.split(';') if p.strip()]
                for patch_str in patches_str:
                    ponto_tokens = [pt.strip() for pt in patch_str.split('|') if pt.strip()]
                    if len(ponto_tokens) != 16:
                        print(f"[WARN] Patch com {len(ponto_tokens)} pontos em {nome}; esperado 16. Ignorando patch.")
                        continue
                    patch = []
                    for i in range(0, 16, 4):
                        linha_pts = []
                        for j in range(4):
                            tok = ponto_tokens[i + j]
                            coords = [c.strip() for c in tok.replace('(', '').replace(')', '').split(',') if c.strip()]
                            if len(coords) != 3:
                                linha_pts = []
                                break
                            x, y, z = float(coords[0]), float(coords[1]), float(coords[2])
                            linha_pts.append(Ponto3D(x, y, z))
                        if len(linha_pts) != 4:
                            patch = []
                            break
                        patch.append(linha_pts)
                    if patch:
                        lista_matrizes.append(patch)
            else:
                linhas_str = [l.strip() for l in string_coordenadas.split(';') if l.strip()]
                if len(linhas_str) % 4 != 0:
                    print(f"[WARN] Número de linhas de superfície não múltiplo de 4 em {nome}: {len(linhas_str)}")
                for i in range(0, len(linhas_str), 4):
                    bloco = linhas_str[i:i+4]
                    if len(bloco) < 4:
                        print(f"[WARN] Bloco de superfície incompleto em {nome}, pulando.")
                        continue
                    mat = []
                    ok = True
                    for linha_str in bloco:
                        pts_tokens = [p.strip() for p in linha_str.split('),') if p.strip()]
                        linha_pts = []
                        for tok in pts_tokens:
                            s = tok.strip()
                            if not s.endswith(')'):
                                s = s + ')'
                            s = s.replace('(', '').replace(')', '')
                            coords = [c.strip() for c in s.split(',') if c.strip()]
                            if len(coords) != 3:
                                ok = False
                                break
                            linha_pts.append(Ponto3D(float(coords[0]), float(coords[1]), float(coords[2])))
                        if not ok or len(linha_pts) == 0:
                            ok = False
                            break
                        mat.append(linha_pts)
                    if ok and len(mat) == 4:
                        lista_matrizes.append(mat)
                    else:
                        print(f"[WARN] Falha ao parsear bloco como 4x4 em {nome}; bloco ignorado.")
            if not lista_matrizes:
                print(f"[WARN] Superfície '{nome}' sem patches válidos.")
                return None
            if "Bezier" in tipo:
                return SuperficieBezier3D(lista_matrizes, nome)
            else:
                return SuperficieBSpline3D(lista_matrizes, nome)

        else:
            print(f"[WARN] Tipo de objeto desconhecido: {linha}")
            return None

    def _ensure_surface_controlnet(self, surf):
        if getattr(surf, "p_calculados", None):
            return

        if getattr(surf, "lista_matrizes", None):
            patches = []
            for G in surf.lista_matrizes:
                try:
                    patch_rows = []
                    for row in G:
                        linha = []
                        for p in row:
                            if hasattr(p, "x") and hasattr(p, "y") and hasattr(p, "z"):
                                linha.append(p)
                        if linha:
                            patch_rows.append(linha)
                    if patch_rows:
                        patches.append(patch_rows)
                except Exception:
                    continue
            if patches:
                surf.p_calculados = patches
                return
        surf.p_calculados = []

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

    def _iterar_pontos_em_pcalculados(self, p_calculados):
        if p_calculados is None:
            return
        def _rec(obj):
            if obj is None:
                return
            if isinstance(obj, Ponto3D):
                yield obj
            elif isinstance(obj, (list, tuple)):
                for sub in obj:
                    yield from _rec(sub)
            else:
                if hasattr(obj, "x") and hasattr(obj, "y") and hasattr(obj, "z"):
                    yield obj
        yield from _rec(p_calculados)

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
                if hasattr(obj, "p_calculados") and obj.p_calculados:
                    for p in self._iterar_pontos_em_pcalculados(obj.p_calculados):
                        try:
                            x_pp, y_pp, z_pp = window3D.mundo_para_view(p)
                            p.x_scn, p.y_scn = window.mundo_para_scn(x_pp, y_pp)
                        except Exception:
                            continue
                else:
                    if hasattr(obj, "gerar_curvas_fwd"):
                        try:
                            obj.gerar_curvas_fwd()
                            if hasattr(obj, "p_calculados") and obj.p_calculados:
                                for p in self._iterar_pontos_em_pcalculados(obj.p_calculados):
                                    try:
                                        x_pp, y_pp, z_pp = window3D.mundo_para_view(p)
                                        p.x_scn, p.y_scn = window.mundo_para_scn(x_pp, y_pp)
                                    except Exception:
                                        continue
                        except Exception:
                            pass