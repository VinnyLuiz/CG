import os
from objetos_3d import Objeto3D, Ponto3D

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
    
    def importar(display_file, nome_arquivo="mundo.obj"):
        # Remove só os Objeto3D para não apagar os 2D (opcional)
        display_file.objetos = [obj for obj in display_file.objetos if obj.__class__.__name__ != "Objeto3D"]

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
        print(f"[OBJ] Total de objetos 3D importados: {len([o for o in display_file.objetos if o.__class__.__name__ == 'Objeto3D'])}")
        return os.path.abspath(nome_arquivo)