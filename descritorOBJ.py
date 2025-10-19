import os
from objetos_3d import Objeto3D, Ponto3D
from superficies3d import SuperficieBezier3D, SuperficieBSpline3D

class DescritorOBJ:
    def exportar(display_file, nome_arquivo="mundo.obj"):
        with open(nome_arquivo, "w") as f:
            for obj in display_file.objetos:
                vert_idx = 1
                if obj.__class__.__name__ == "SuperficieBezier3D" or obj.__class__.__name__ == "SuperficieBSpline3D":
                    f.write(f"o {obj.__class__.__name__}_{obj.nome}\n")
                else:
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
                # Objeto 3D
                if obj.__class__.__name__ == "Objeto3D":
                    primeiro_idx_obj = vert_idx
                    for p in obj.pontos:
                        # Ponto3D tem x, y, z
                        f.write(f"v {p.x} {p.y} {p.z}\n")
                        vert_idx += 1
                        
                    for i, j in obj.arestas:
                        idx_i = primeiro_idx_obj + i
                        idx_j = primeiro_idx_obj + j
                        f.write(f"l {idx_i} {idx_j}\n")
                
                # Superficie 3D
                if obj.__class__.__bases__[0].__name__ == "Superficie3D":
                    for G in obj.lista_matrizes:
                        for linha in G:
                            for p in linha:
                                f.write(f"v {p.x:.6f} {p.y:.6f} {p.z:.6f}\n")

        return os.path.abspath(nome_arquivo)
    
    def importar(display_file, nome_arquivo="mundo.obj"):
        display_file.objetos = [obj for obj in display_file.objetos]

        vertices_globais = []
        arestas = []
        nome = None

        with open(nome_arquivo) as f:
            for line in f:
                if line.startswith("o "):
                    # Salva o objeto anterior se houver
                    if vertices_globais and arestas:
                        pontos = [Ponto3D(*v) for v in vertices_globais]
                        obj3d = Objeto3D(pontos, arestas, nome)
                        display_file.adicionar(obj3d)
                        print(f"[OBJ] Importado Objeto3D: {nome} ({len(pontos)} pontos, {len(arestas)} arestas)")
                    # Começa novo objeto
                    nome = line.strip().split(maxsplit=1)[1]
                    vertices_globais = []
                    arestas = []
                elif line.startswith("v "):
                    try:
                        _, x, y, z = line.strip().split()
                        vertices_globais.append((float(x), float(y), float(z)))
                    except Exception as e:
                        print(f"[OBJ] Erro ao ler vértice: {line.strip()} - {e}")
                elif line.startswith("l "):
                    try:
                        idxs = [int(i)-1 for i in line.strip().split()[1:]]
                        for i in range(len(idxs)-1):
                            arestas.append((idxs[i], idxs[i+1]))
                    except Exception as e:
                        print(f"[OBJ] Erro ao ler aresta: {line.strip()} - {e}")
            # Salva o último objeto do arquivo
            if vertices_globais and arestas:
                pontos = [Ponto3D(*v) for v in vertices_globais]
                obj3d = Objeto3D(pontos, arestas, nome)
                display_file.adicionar(obj3d)
                print(f"[OBJ] Importado Objeto3D: {nome} ({len(pontos)} pontos, {len(arestas)} arestas)")
            if "Superficie" in nome:
                print(nome)
                if "SuperficieBezier" in nome:
                    nome_fmt = nome.removeprefix("SuperficieBezier3D_")
                    tipo = 0
                else:
                    nome_fmt = nome.removeprefix("SuperficieBSpline3D_")
                    tipo = 1
                nro_mat = len(vertices_globais) // 16
                print(nro_mat)
                lista_mats = []
                for mat in range(nro_mat):
                    mat = []
                    for i in range(4):
                        linha_mat = []
                        for j in range(4):
                            v = vertices_globais.pop(0)
                            ponto_3d = Ponto3D(*v)
                            linha_mat.append(ponto_3d)
                        mat.append(linha_mat)
                    lista_mats.append(mat)
                if tipo == 0:
                    suprf = SuperficieBezier3D(lista_mats, nome_fmt)
                else:
                    suprf = SuperficieBSpline3D(lista_mats, nome_fmt)
                display_file.adicionar(suprf)
                        
        print(f"[OBJ] Total de objetos 3D importados: {len([o for o in display_file.objetos if o.__class__.__name__ == 'Objeto3D'])}")
        return os.path.abspath(nome_arquivo)