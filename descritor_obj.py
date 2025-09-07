import os

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
        display_file.objetos.clear()
        vertices_globais = []
        nome = None
        tipo = "wireframe"
        with open(nome_arquivo) as f:
            for line in f:
                if line.startswith("o "):
                    nome = line.strip().split(maxsplit=1)[1]
                elif line.startswith("v "):
                    _, x, y, _ = line.strip().split()
                    vertices_globais.append((float(x), float(y)))
                elif line.startswith("l "):
                    idxs = [int(i)-1 for i in line.strip().split()[1:]]
                    coords = [vertices_globais[i] for i in idxs]
                    tipo = "reta" if len(coords) == 2 else "wireframe"
                    display_file.adicionar_from_obj(nome, coords, tipo=tipo)
        return os.path.abspath(nome_arquivo)