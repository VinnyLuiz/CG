import os
from objetos_3d import Objeto3D, Ponto3D, SuperficieBezier

class DescritorOBJ:
    def exportar(display_file, nome_arquivo="mundo.obj"):
        with open(nome_arquivo, "w") as f:
            vert_idx = 1
            for obj in display_file.objetos:
                f.write(f"o {obj.nome}\n")
                idxs = []
                # Ponto
                if obj.__class__.__name__ == "Ponto":
                    f.write(f"v {obj.x} {obj.y} 0.0\n")
                    # Para ponto, não precisa de linha
                    vert_idx += 1
                # Reta
                elif obj.__class__.__name__ == "Reta":
                    f.write(f"v {obj.ponto0.x} {obj.ponto0.y} 0.0\n")
                    f.write(f"v {obj.ponto1.x} {obj.ponto1.y} 0.0\n")
                    f.write(f"l {vert_idx} {vert_idx+1}\n")
                    vert_idx += 2
                # Wireframe
                elif obj.__class__.__name__ == "Wireframe":
                    for p in obj.lista_pontos:
                        f.write(f"v {p.x} {p.y} 0.0\n")
                        idxs.append(vert_idx)
                        vert_idx += 1
                    if len(idxs) >= 2:
                        # fecha o wireframe se for polígono
                        f.write("l " + " ".join(map(str, idxs)) + f" {idxs[0]}\n")
        return os.path.abspath(nome_arquivo)
    
    @staticmethod
    def importar(display_file, nome_arquivo="mundo.obj"):
        display_file.objetos = [obj for obj in display_file.objetos
                                if obj.__class__.__name__ not in ("Objeto3D", "SuperficieBezier")]

        objects = []
        current = {"name": None, "vertices": [], "arestas": []}
        objects.append(current)

        try:
            with open(nome_arquivo, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("o ") or line.startswith("g "):
                        name = line.split(maxsplit=1)[1].strip()
                        current = {"name": name, "vertices": [], "arestas": []}
                        objects.append(current)
                    elif line.startswith("v "):
                        parts = line.split()
                        if len(parts) >= 4:
                            x, y, z = parts[1], parts[2], parts[3]
                        elif len(parts) == 3:
                            x, y = parts[1], parts[2]
                            z = "0"
                        else:
                            print(f"[OBJ] vértice inválido ignorado: {line}")
                            continue
                        try:
                            current["vertices"].append((float(x), float(y), float(z)))
                        except Exception as e:
                            print(f"[OBJ] falha ao parsear vértice '{line}': {e}")
                    elif line.startswith("l "):
                        parts = line.split()[1:]
                        try:
                            idxs = [int(p) - 1 for p in parts]
                            for i in range(len(idxs) - 1):
                                current["arestas"].append((idxs[i], idxs[i+1]))
                        except Exception as e:
                            print(f"[OBJ] falha ao ler linha (l): {line} -> {e}")
                    elif line.startswith("f "):
                        parts = line.split()[1:]
                        try:
                            idxs = [int(p.split("/")[0]) - 1 for p in parts]
                            for i in range(len(idxs)):
                                current["arestas"].append((idxs[i], idxs[(i+1) % len(idxs)]))
                        except Exception as e:
                            print(f"[OBJ] falha ao ler face (f): {line} -> {e}")
                    else:
                        continue
        except FileNotFoundError:
            raise

        def garantir_nome_unico(base_nome):
            if not base_nome:
                base_nome = "importado"
            nome_final = base_nome
            k = 1
            nomes_existentes = {obj.nome for obj in display_file.objetos}
            while nome_final in nomes_existentes:
                nome_final = f"{base_nome}_{k}"
                k += 1
            return nome_final

        objetos_criados = 0

        for blk in objects:
            n_vertices = len(blk["vertices"])
            n_arestas = len(blk["arestas"])
            nome_bloco = blk["name"] or "importado"
            # se tem arestas e vértices suficientes -> Objeto3D
            if n_arestas > 0 and n_vertices > 0:
                pts = [Ponto3D(*v) for v in blk["vertices"]]
                nome = garantir_nome_unico(nome_bloco)
                obj3d = Objeto3D(pts, blk["arestas"], nome)
                try:
                    display_file.adicionar(obj3d)
                    print(f"[OBJ] Importado Objeto3D: {nome} ({len(pts)} pts, {len(blk['arestas'])} arestas)")
                    objetos_criados += 1
                except Exception as e:
                    print(f"[OBJ] erro ao adicionar Objeto3D {nome}: {e}")
            # se não tem arestas mas tem vértices múltiplos de 16 -> SuperficieBezier
            elif n_arestas == 0 and n_vertices >= 16 and (n_vertices % 16) == 0:
                patches = []
                for i in range(0, n_vertices, 16):
                    block = blk["vertices"][i:i+16]
                    patches.append([Ponto3D(*v) for v in block])
                nome = garantir_nome_unico(nome_bloco)
                try:
                    surf = SuperficieBezier(patches, nome)
                    display_file.adicionar(surf)
                    print(f"[OBJ] Importado SuperficieBezier: {nome} ({len(patches)} patches)")
                    objetos_criados += 1
                except Exception as e:
                    print(f"[OBJ] erro ao adicionar SuperficieBezier {nome}: {e}")
            # blocos pequenos ou inválidos
            elif n_vertices > 0:
                print(f"[OBJ] Bloco '{nome_bloco}' tem {n_vertices} vértices e {n_arestas} arestas — não convertido.")
            else:
                continue

        # combinar todos os vértices do arquivo em sequência
        if objetos_criados == 0:
            all_vertices = []
            for blk in objects:
                all_vertices.extend(blk["vertices"])
            if len(all_vertices) >= 16 and (len(all_vertices) % 16) == 0:
                patches = []
                for i in range(0, len(all_vertices), 16):
                    block = all_vertices[i:i+16]
                    patches.append([Ponto3D(*v) for v in block])
                nome = garantir_nome_unico(os.path.splitext(os.path.basename(nome_arquivo))[0] or "Superficie")
                try:
                    surf = SuperficieBezier(patches, nome)
                    display_file.adicionar(surf)
                    print(f"[OBJ] Importado SuperficieBezier combinado: {nome} ({len(patches)} patches)")
                    objetos_criados += 1
                except Exception as e:
                    print(f"[OBJ] erro ao adicionar SuperficieBezier combinado {nome}: {e}")
            else:
                print("[OBJ] Não foi possível detectar patches de 16 vértices. Nenhuma superfície importada.")
        return os.path.abspath(nome_arquivo)