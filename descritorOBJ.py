import os
from objetos_3d import Objeto3D, Ponto3D
from superficies3d import SuperficieBezier3D, SuperficieBSpline3D

class DescritorOBJ:
    @staticmethod
    def exportar(display_file, nome_arquivo="mundo.obj"):
        with open(nome_arquivo, "w") as f:
            global_vert_idx = 1
            for obj in display_file.objetos:
                # escreve cabeçalho do objeto
                if obj.__class__.__name__ in ("SuperficieBezier3D", "SuperficieBSpline3D"):
                    f.write(f"o {obj.__class__.__name__}_{obj.nome}\n")
                else:
                    f.write(f"o {obj.nome}\n")

                # casos por tipo
                if obj.__class__.__name__ == "Ponto":
                    f.write(f"v {obj.x} {obj.y} 0.0\n")
                    global_vert_idx += 1

                elif obj.__class__.__name__ == "Reta":
                    f.write(f"v {obj.ponto0.x} {obj.ponto0.y} 0.0\n")
                    f.write(f"v {obj.ponto1.x} {obj.ponto1.y} 0.0\n")
                    f.write(f"l {global_vert_idx} {global_vert_idx+1}\n")
                    global_vert_idx += 2

                elif obj.__class__.__name__ == "Wireframe":
                    idxs = []
                    for p in obj.lista_pontos:
                        f.write(f"v {p.x} {p.y} 0.0\n")
                        idxs.append(global_vert_idx)
                        global_vert_idx += 1
                    if len(idxs) >= 2:
                        f.write("l " + " ".join(map(str, idxs)) + f" {idxs[0]}\n")

                elif obj.__class__.__name__ == "Objeto3D":
                    primeiro_idx_obj = global_vert_idx
                    for p in obj.pontos:
                        f.write(f"v {p.x} {p.y} {p.z}\n")
                        global_vert_idx += 1
                    for i, j in obj.arestas:
                        idx_i = primeiro_idx_obj + i
                        idx_j = primeiro_idx_obj + j
                        f.write(f"l {idx_i} {idx_j}\n")

                elif obj.__class__.__name__ in ("SuperficieBezier3D", "SuperficieBSpline3D"):
                    for G in getattr(obj, "lista_matrizes", []):
                        for linha in G:
                            for p in linha:
                                f.write(f"v {p.x:.6f} {p.y:.6f} {p.z:.6f}\n")
                                global_vert_idx += 1

                else:
                    if hasattr(obj, "pontos"):
                        for p in obj.pontos:
                            try:
                                f.write(f"v {p.x} {p.y} {getattr(p,'z',0.0)}\n")
                                global_vert_idx += 1
                            except Exception:
                                pass
        return os.path.abspath(nome_arquivo)

    @staticmethod
    def importar(display_file, nome_arquivo="mundo.obj"):
        global_vertices = []
        blocks = []
        current = {"name": None, "vertex_indices": [], "arestas_global": []}
        blocks.append(current)

        try:
            with open(nome_arquivo, "r", encoding="utf-8") as fh:
                for raw in fh:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("o ") or line.startswith("g "):
                        name = line.split(maxsplit=1)[1].strip()
                        current = {"name": name, "vertex_indices": [], "arestas_global": []}
                        blocks.append(current)
                    elif line.startswith("v "):
                        parts = line.split()
                        if len(parts) >= 4:
                            x_s, y_s, z_s = parts[1], parts[2], parts[3]
                        elif len(parts) == 3:
                            x_s, y_s = parts[1], parts[2]
                            z_s = "0"
                        else:
                            continue
                        try:
                            vx = float(x_s); vy = float(y_s); vz = float(z_s)
                        except Exception:
                            continue
                        idx_global = len(global_vertices)
                        global_vertices.append((vx, vy, vz))
                        current["vertex_indices"].append(idx_global)
                    elif line.startswith("l "):
                        parts = line.split()[1:]
                        try:
                            idxs_global = [int(p) - 1 for p in parts]
                            for i in range(len(idxs_global) - 1):
                                a = idxs_global[i]; b = idxs_global[i+1]
                                current["arestas_global"].append((a, b))
                        except Exception:
                            continue
                    elif line.startswith("f "):
                        parts = line.split()[1:]
                        try:
                            idxs_global = [int(p.split("/")[0]) - 1 for p in parts]
                            for i in range(len(idxs_global)):
                                a = idxs_global[i]; b = idxs_global[(i+1) % len(idxs_global)]
                                current["arestas_global"].append((a, b))
                        except Exception:
                            continue
                    else:
                        continue
        except FileNotFoundError:
            raise

        def garantir_nome_unico(base_nome):
            if not base_nome:
                base_nome = "importado"
            nome_final = base_nome
            k = 1
            existentes = {obj.nome for obj in display_file.objetos}
            while nome_final in existentes:
                nome_final = f"{base_nome}_{k}"
                k += 1
            return nome_final

        objetos_criados = 0

        for blk in blocks:
            nome_bloco = blk["name"] or "importado"
            v_idxs = blk["vertex_indices"]
            arestas_global = blk["arestas_global"]

            # Cria Objeto3D quando houver arestas
            if arestas_global:
                usados = []
                for (a, b) in arestas_global:
                    if a not in usados:
                        usados.append(a)
                    if b not in usados:
                        usados.append(b)
                if not usados and v_idxs:
                    usados = list(v_idxs)

                mapa = {}
                pontos_locais = []
                for local_idx, gidx in enumerate(usados):
                    mapa[gidx] = local_idx
                    x, y, z = global_vertices[gidx]
                    pontos_locais.append(Ponto3D(x, y, z))

                arestas_locais = []
                for (a, b) in arestas_global:
                    if a in mapa and b in mapa:
                        arestas_locais.append((mapa[a], mapa[b]))
                    else:
                        pass

                nome_final = garantir_nome_unico(nome_bloco)
                try:
                    obj3d = Objeto3D(pontos_locais, arestas_locais, nome_final)
                    display_file.adicionar(obj3d)
                    objetos_criados += 1
                except Exception:
                    pass
                continue

            if v_idxs and (("Superficie" in nome_bloco) or (len(v_idxs) >= 16 and (len(v_idxs) % 16 == 0))):
                verts = [global_vertices[g] for g in v_idxs]
                nro_patches = len(verts) // 16
                patches = []
                for p_i in range(nro_patches):
                    block_pts = verts[p_i*16:(p_i+1)*16]
                    patch = []
                    for r in range(4):
                        linha = []
                        for c in range(4):
                            x, y, z = block_pts[r*4 + c]
                            linha.append(Ponto3D(x, y, z))
                        patch.append(linha)
                    patches.append(patch)

                nome_base = nome_bloco.replace("SuperficieBezier3D_", "").replace("SuperficieBSpline3D_", "")
                tipo_bezier = "Bezier" in (nome_bloco or "")

                def criar_surf_com_ponto3d_variantes(patches):
                    Cls = SuperficieBezier3D if tipo_bezier else SuperficieBSpline3D

                    try:
                        surf = Cls(patches, nome_base)
                        return surf
                    except Exception:
                        pass

                    try:
                        grid = []
                        for r in range(4):
                            row = []
                            for pch in patches:
                                for pt in pch[r]:
                                    row.append(pt)
                            grid.append(row)
                        surf = Cls(grid, nome_base)
                        return surf
                    except Exception:
                        pass

                    try:
                        grid_v = []
                        for pch in patches:
                            for row in pch:
                                grid_v.append(list(row))
                        surf = Cls(grid_v, nome_base)
                        return surf
                    except Exception:
                        pass

                    raise RuntimeError("Construtor de superfície rejeitou as variantes Ponto3D")

                try:
                    surf = criar_surf_com_ponto3d_variantes(patches)
                except Exception as e:
                    print(f"[OBJ] Falha ao criar Superficie '{nome_bloco}': {e}")
                    sample = []
                    for pch in patches[:min(4, len(patches))]:
                        for r in pch:
                            for p in r[:min(4, len(r))]:
                                sample.append((p.x, p.y, p.z))
                                if len(sample) >= 12:
                                    break
                            if len(sample) >= 12:
                                break
                        if len(sample) >= 12:
                            break
                    print(f"[OBJ] Exemplo de pontos (primeiros {len(sample)}): {sample}")
                    continue

                try:
                    if hasattr(display_file, "_ensure_surface_controlnet"):
                        display_file._ensure_surface_controlnet(surf)
                except Exception:
                    pass

                nome_para_adicionar = garantir_nome_unico(nome_base)
                surf.nome = nome_para_adicionar
                try:
                    display_file.adicionar(surf)
                    objetos_criados += 1
                except Exception:
                    try:
                        novo_nome = garantir_nome_unico(nome_base)
                        surf.nome = novo_nome
                        display_file.adicionar(surf)
                        objetos_criados += 1
                    except Exception:
                        print(f"[OBJ] Erro ao adicionar Superficie final '{nome_base}'")
                        continue

                continue

            if v_idxs:
                pontos = [Ponto3D(*global_vertices[g]) for g in v_idxs]
                nome_final = garantir_nome_unico(nome_bloco)
                try:
                    obj3d = Objeto3D(pontos, [], nome_final)
                    display_file.adicionar(obj3d)
                    objetos_criados += 1
                except Exception:
                    pass
                continue

            continue

        print(f"[OBJ] Total de objetos importados: {objetos_criados}")
        return os.path.abspath(nome_arquivo)