import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from objetos import *
from objetos_3d import *
from displayFile import DisplayFile
from tranformacoes import matriz_translacao, matriz_escalonamento, matriz_rotacao, aplicar_matriz, centro_geom
from transformacao3D import matriz_escalonamento_3d, centro_geom_3d
from superficies3d import SuperficieBezier3D, SuperficieBSpline3D
import re


class Popup(tk.Toplevel):
    def __init__(self, master, display_file: DisplayFile):
        super().__init__(master)
        self.geometry("500x500+300+100")
        self.title("Incluir Objeto")
        self.aba_atual = 0
        self.display_file = display_file

        # Comando para validar a entrada de coordenadas
        self.vcmd = (self.register(self.validar_entry_numerica), "%P")

        # Nome
        tk.Label(self, text="Nome").pack(anchor="w", padx=10, pady=5)
        self.nome_entry = tk.Entry(self)
        self.nome_entry.pack(fill="x", padx=10)

        # Notebook (abas)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(padx=10, pady=10, fill="both", expand=0)
        self.notebook.bind("<<NotebookTabChanged>>", self.mudar_aba)

        # Aba Ponto
        frame_ponto = ttk.Frame(self.notebook)
        self.notebook.add(frame_ponto, text="Ponto")
        tk.Label(frame_ponto, text="x:").grid(row=0, column=0)
        self.x_ponto = tk.Entry(frame_ponto, width=5, validate="key", validatecommand=self.vcmd)
        self.x_ponto.grid(row=0, column=1, padx=(0, 10))
        tk.Label(frame_ponto, text="y:").grid(row=0, column=2)
        self.y_ponto = tk.Entry(frame_ponto, width=5, validate="key", validatecommand=self.vcmd)
        self.y_ponto.grid(row=0, column=3, padx=(0, 10))

        # Aba Reta
        frame_reta = ttk.Frame(self.notebook)
        self.notebook.add(frame_reta, text="Reta")
        tk.Label(frame_reta, text="x0:").grid(row=0, column=0)
        self.x0_reta = tk.Entry(frame_reta, width=4, validate="key", validatecommand=self.vcmd)
        self.x0_reta.grid(row=0, column=1)
        tk.Label(frame_reta, text="y0:").grid(row=0, column=2)
        self.y0_reta = tk.Entry(frame_reta, width=4, validate="key", validatecommand=self.vcmd)
        self.y0_reta.grid(row=0, column=3)
        tk.Label(frame_reta, text="x1:").grid(row=1, column=0)
        self.x1_reta = tk.Entry(frame_reta, width=4, validate="key", validatecommand=self.vcmd)
        self.x1_reta.grid(row=1, column=1)
        tk.Label(frame_reta, text="y1:").grid(row=1, column=2)
        self.y1_reta = tk.Entry(frame_reta, width=4, validate="key", validatecommand=self.vcmd)
        self.y1_reta.grid(row=1, column=3)

        # Aba Wireframe
        frame_wireframe = ttk.Frame(self.notebook)
        self.lista_entry = []
        self.notebook.add(frame_wireframe, text="Wireframe")
        self.pontos_frame = tk.Frame(frame_wireframe)
        self.pontos_frame.pack(pady=5)
        btn_add_ponto = tk.Button(frame_wireframe, text="+ Adicionar ponto", command=self.adicionar_entry)
        btn_add_ponto.pack()

        # Checkbutton de preenchimento
        self.preencher_var = tk.BooleanVar(value=False)
        self.check_preencher = ttk.Checkbutton(frame_wireframe, text="Preencher", variable=self.preencher_var)
        self.check_preencher.pack(anchor="center", padx=10, pady=5)

        # Color picker
        self.cor_preenchimento = "#000000" # Cor inicial
        self.label_cor = tk.Label(frame_wireframe, text="Cor: #000000", bg=self.cor_preenchimento, fg="white", relief="solid")
        self.label_cor.pack(anchor="center", padx=10, pady=5)
        ttk.Button(frame_wireframe, text="Escolher Cor", command=self.escolher_cor).pack(anchor="center", padx=10, pady=5)

        # Aba Curva2D
        frame_curva = ttk.Frame(self.notebook)
        self.notebook.add(frame_curva, text="Curva2D")
        tk.Label(frame_curva, text="Pontos: (x1, y1), (x2, y2), ...").grid(column=0, row=0)
        self.curva_entry = ttk.Entry(frame_curva)
        self.curva_entry.grid(column=1, row=0)

        # Aba BSpline 
        frame_bspline = ttk.Frame(self.notebook)
        self.notebook.add(frame_bspline, text="BSpline")
        tk.Label(frame_bspline, text="Pontos: (x1, y1), (x2, y2), ...").grid(column=0, row=0)
        self.bspline_entry = ttk.Entry(frame_bspline)
        self.bspline_entry.grid(column=1, row=0)
        
        # Aba Objeto3D
        frame_obj3D = ttk.Frame(self.notebook)
        self.notebook.add(frame_obj3D, text="Objeto3D")
        tk.Label(frame_obj3D, text="Pontos: (x1, y1, z1), (x2, y2, z2), ...").grid(column=0, row=0)
        self.pontos3d_entry = ttk.Entry(frame_obj3D)
        self.pontos3d_entry.grid(column=1, row=0)
        tk.Label(frame_obj3D, text="Arestas:").grid(column=0, row=1)
        self.arestas_entry = ttk.Entry(frame_obj3D)
        self.arestas_entry.grid(column=1, row=1)
        tk.Label(frame_obj3D, text="Entrada das arestas utiliza o indice dos pontos").grid(column=0, row=2, columnspan=2)
        tk.Label(frame_obj3D, text="Ex: (0, 1), (0, 2), ...").grid(column=0, row=3, columnspan=2)
        
        # Aba Superficie3D
        frame_sprf3D = ttk.Frame(self.notebook)
        self.notebook.add(frame_sprf3D, text="Superficie3D")
        tk.Label(frame_sprf3D, text="Pontos de Controle separado em ';' por linha:").grid(column=0, row=0, padx=30)
        tk.Label(frame_sprf3D, text="ex: (x_11, y_11, z_11), (x_12, y_12, z_12), ...; (x_21, y_21, z_21)").grid(column=0, row=1, padx=30)
        self.suprf3d_entry = ttk.Entry(frame_sprf3D)
        self.suprf3d_entry.grid(column=0, row=2, sticky="we", padx=30)
        self.tipo_sprf3d = tk.StringVar(frame_sprf3D, value="Bezier")
        opcoes = ["Bezier", "B-Spline"]
        self.dropdown = ttk.OptionMenu(
            frame_sprf3D,
            self.tipo_sprf3d,
            "Bezier",
            *opcoes,
        )
        self.dropdown.grid(pady=10) 


        # Botões
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Adicionar", command=self.adicionar_objeto).pack(side="left", padx=5)


    def mudar_aba(self, event):
        self.aba_atual = self.notebook.index(self.notebook.select())
        
    def adicionar_objeto(self):
        try:
            nome = self.nome_entry.get()
            
            # Gera um nome genérico caso deixe em branco
            if not nome:
                nome = self.gerar_nome_gen()
                self.nome_entry.delete(0, tk.END)
                self.nome_entry.insert(0, nome)
            
            # Verifica se o nome já existe no displayFile
            if self.display_file.nome_existe(nome):
                messagebox.showerror("Erro", f"Já existe um objeto com o nome '{nome}'")
                return
            

            match self.aba_atual:
                case 0: # Ponto
                    x = float(self.x_ponto.get())
                    y = float(self.y_ponto.get())
                    ponto = Ponto(x, y, self.nome_entry.get())
                    self.display_file.adicionar(ponto)
                
                case 1: # Reta
                    x = float(self.x0_reta.get())
                    y = float(self.y0_reta.get())
                    ponto0 = Ponto(x, y, "ponto0")
                    x = float(self.x1_reta.get())
                    y = float(self.y1_reta.get())
                    ponto1 = Ponto(x, y, "ponto1")
                    reta = Reta(ponto0, ponto1, self.nome_entry.get())
                    self.display_file.adicionar(reta)

                case 2: # Wireframe
                    pontos = []
                    for i, (entry_x, entry_y) in enumerate(self.lista_entry):
                        x = float(entry_x.get())
                        y = float(entry_y.get())
                        pontos.append(Ponto(float(x), float(y), f"p{i}"))

                    preencher = self.preencher_var.get()
                    cor_preenchimento = self.cor_preenchimento

                    if pontos:  # só cria se tiver pontos válidos
                        wireframe = Wireframe(pontos, self.nome_entry.get(), preencher=preencher, cor_preenchimento=cor_preenchimento)
                        self.display_file.adicionar(wireframe)

                case 3: # Curva2D
                    s = self.curva_entry.get().strip()
                    if not s:
                        raise ValueError("Lista de pontos vazia")
                    coords = self._parse_pontos(s)
                    if not coords:
                        raise ValueError("Não foi possível interpretar os pontos")
                    if len(coords) < 4:
                        messagebox.showerror("Erro", "Mínimo de 4 pontos são necessários.")
                        return
                    pontos = [Ponto(float(x), float(y), f"{nome}_p{i}") for i, (x, y) in enumerate(coords)]
                    curva = BSpline(pontos, nome)
                    self.display_file.adicionar(curva)

                case 4: # BSpline
                    s = self.bspline_entry.get().strip()
                    if not s:
                        raise ValueError("Lista de pontos vazia")
                    coords = self._parse_pontos(s)
                    if not coords:
                        raise ValueError("Não foi possível interpretar os pontos")
                    pontos = [Ponto(float(x), float(y), f"{nome}_p{i}") for i, (x, y) in enumerate(coords)]
                    curva = BSpline(pontos, nome)
                    self.display_file.adicionar(curva)
                    
                case 5: # Objeto3D
                    # Parse Pontos
                    s_pontos = self.pontos3d_entry.get().strip()
                    if not s_pontos:
                        raise ValueError("Lista de pontos vazia")
                    coords_pontos = self._parse_pontos_3D(s_pontos)
                    if not coords_pontos:
                        raise ValueError("Não foi possível interpretar os pontos")
                    # Parse Arestas
                    s_arestas = self.arestas_entry.get().strip()
                    if not s_arestas:
                        raise ValueError("Lista de aresta vazia")
                    arestas = self._parse_arestas(s_arestas)
                    if not arestas:
                        raise ValueError("Não foi possível interpretar as arestas")

                    pontos = [Ponto3D(float(x), float(y), float(z)) for x, y, z in coords_pontos]
                    n = len(coords_pontos)
                    for i, j in arestas:
                        if not (0 <= i < n and 0 <= j < n):
                            raise ValueError("Arestas com índices inválidos")
                    
                    obj3d = Objeto3D(pontos, arestas, nome)
                    self.display_file.adicionar(obj3d)
                
                case 6: # Superficie3d
                    s_matriz_pontos = self._parse_matriz(self.suprf3d_entry.get())
                    tipo_sprf = self.tipo_sprf3d.get().capitalize()
                    matriz_pontos = []
                    for linha in s_matriz_pontos:
                        linha_pontos = []
                        for ponto in linha:
                            x, y, z = ponto
                            linha_pontos.append(Ponto3D(x,y,z)) 
                        matriz_pontos.append(linha_pontos)
                        
                    if tipo_sprf == "Bezier":
                        sprf_3d = SuperficieBezier3D(matriz_pontos, nome)
                    else:
                        sprf_3d = SuperficieBSpline3D(matriz_pontos, nome)
                    self.display_file.adicionar(sprf_3d)
                    

            self.destroy()
        except ValueError as e:
            if "Já existe" in str(e):
                messagebox.showerror("Nome duplicado", str(e))
            else:
                messagebox.showerror("Coordenada Inválida", "Por favor insira coordenadas válidas")
        
    def adicionar_entry(self):
        """Adiciona uma linha nova de entradas X e Y para o wireframe"""
        row = len(self.lista_entry)
        lbl = tk.Label(self.pontos_frame, text=f"Ponto{row}:")
        lbl.grid(row=row, column=0, padx=5, pady=2)

        entry_x = tk.Entry(self.pontos_frame, width=4, validate="key", validatecommand=self.vcmd)
        entry_y = tk.Entry(self.pontos_frame, width=4, validate="key", validatecommand=self.vcmd)
        entry_x.grid(row=row, column=1)
        entry_y.grid(row=row, column=2)
        self.lista_entry.append((entry_x, entry_y))

    def validar_entry_numerica(self, texto):
        """Permite apenas digitar números nas coordenadas"""
        if texto =="-" or texto == "":
            return True
        try:
            float(texto)   # tenta converter
            return True
        except ValueError:
            return False
        
    def gerar_nome_gen(self):
        """Gera um nome generico baseado no tipo e quantidade"""
        tipo = ""
        tipoS = None
        match self.aba_atual:
            case 0: tipo = "Ponto"
            case 1: tipo = "Reta"
            case 2: tipo = "Wireframe"
            case 3: tipo = "Curva2D"
            case 4: tipo = "BSpline"
            case 5: tipo = "Objeto3D"
            case 6: tipo = "Superficie3D"; tipoS = self.tipo_sprf3d.get()
        
        # Conta quantos objetos deste tipo já existem
        count = sum(1 for obj in self.display_file.objetos if obj.nome.startswith(tipo))
        return f"{tipo}_{count + 1}" if tipoS is None else f"{tipoS}_{count + 1}" 
    
    def escolher_cor(self):
        """Abre o color picker e atualiza a cor de preenchimento"""
        cor_selecionada = colorchooser.askcolor(title="Escolha a cor de preenchimento")
        if cor_selecionada:
            self.cor_preenchimento = cor_selecionada[1] # Pega o valor hexadecimal
            self.label_cor.config(text=f"Cor de Preenchimento: {self.cor_preenchimento}", bg=self.cor_preenchimento, fg="white" if cor_selecionada[0][0] + cor_selecionada[0][1] + cor_selecionada[0][2] < 382.5 else "black")

    def _parse_pontos(self, s: str):
        pattern = r'(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)'
        matches = re.findall(pattern, s)
        return matches
    
    def _parse_pontos_3D(self, s):
        s = s.strip()
        matches = re.findall(r'\(([^)]+)\)', s)
        coords = []
        for match in matches:
            try:
                valores = [float(v.strip()) for v in match.split(',') if v.strip()]
                if len(valores) != 3:
                    raise ValueError("Ponto deve ter 3 coordenadas (x, y, z).")
                coords.append(tuple(valores))
            except ValueError:
                # Se a conversão para float falhar ou o número de coords estiver errado
                raise ValueError(f"Coordenadas inválidas: '{match}'. Use números válidos.")
        return coords

    def _parse_arestas(self, s):
        """
        Interpreta a string de entrada de arestas no formato: (i, j), (k, l), ...
        Retorna uma lista de tuplas (índice_ponto1, índice_ponto2).
        """
        s = s.strip()
        
        # Regex para encontrar tuplas de 2 números (índices)
        matches = re.findall(r'\(([^)]+)\)', s)
        
        arestas = []
        for match in matches:
            try:
                # Separa os valores dentro dos parênteses por vírgula ou espaço
                indices = [int(v.strip()) for v in match.split(',') if v.strip()]
                
                if len(indices) != 2:
                    raise ValueError("Aresta deve ter 2 índices de pontos (i, j).")
                
                arestas.append(tuple(indices))
            except ValueError:
                raise ValueError(f"Índices de aresta inválidos: '{match}'. Use inteiros válidos.")
        
        return arestas
    
    def _parse_matriz(self, s):
        matriz = []
        # Divide em linhas
        linhas = s.split(';')
        for linha in linhas:
            # Encontra todas as tuplas na linha
            tuplas = re.findall(r'\([^)]+\)', linha)
            linha_coordenadas = []
            for tupla in tuplas:
                # Extrai os números da tupla
                numeros = re.findall(r'[-+]?\d*\.\d+|\d+', tupla)
                if len(numeros) == 3:
                    x, y, z = map(float, numeros)
                    linha_coordenadas.append((x, y, z))
            
            if linha_coordenadas:
                matriz.append(linha_coordenadas)
        
        return matriz
    

class PopupTransformacoes(tk.Toplevel):
    def __init__(self, parent, objeto, callback_redesenhar):
        super().__init__(parent)
        self.title(f"Transformações: {objeto.nome}")
        self.geometry("500x300")
        self.objeto = objeto
        self.is_3d = objeto.__class__.__name__ == 'Objeto3D'
        self.callback_redesenhar = callback_redesenhar

        # Tipo da transformação
        ttk.Label(self, text="Tipo:").grid(column=0, row=0, sticky="w", padx=5, pady=5)
        self.combo_tipo = ttk.Combobox(
            self, values=["Translação", "Escala", "Rotação"],
            state="readonly", width=15
        )
        self.combo_tipo.grid(column=1, row=0, padx=5, pady=5)
        self.combo_tipo.current(0)

        # Entradas
        self.label_x = ttk.Label(self, text="dx:")
        self.label_x.grid(column=0, row=1, sticky="w", padx=5, pady=5)
        self.entry_x = ttk.Entry(self, width=10)
        self.entry_x.grid(column=1, row=1, padx=5, pady=5)

        self.label_y = ttk.Label(self, text="dy:")
        self.label_y.grid(column=0, row=2, sticky="w", padx=5, pady=5)
        self.entry_y = ttk.Entry(self, width=10)
        self.entry_y.grid(column=1, row=2, padx=5, pady=5)
        
        if self.is_3d:
            self.label_z = ttk.Label(self, text="dz:")
            self.label_z.grid(column=0, row=3, sticky="w", padx=5, pady=5)
            self.entry_z = ttk.Entry(self, width=10)
            self.entry_z.grid(column=1, row=3, padx=5, pady=5)
            

        self.label_angulo = ttk.Label(self, text="Ângulo (graus):")
        self.label_angulo.grid(column=0, row=3, sticky="w", padx=5, pady=5)
        self.entry_angulo = ttk.Entry(self, width=10)
        self.entry_angulo.grid(column=1, row=3, padx=5, pady=5)

        # Centro Arbitrário
        self.label_cx = ttk.Label(self, text="Centro X (Arbitrário):")
        self.label_cx.grid(column=0, row=4, sticky="w", padx=5, pady=5)
        self.entry_cx = ttk.Entry(self, width=10)
        self.entry_cx.grid(column=1, row=4, padx=5, pady=5)

        self.label_cy = ttk.Label(self, text="Centro Y (Arbitrário):")
        self.label_cy.grid(column=0, row=5, sticky="w", padx=5, pady=5)
        self.entry_cy = ttk.Entry(self, width=10)
        self.entry_cy.grid(column=1, row=5, padx=5, pady=5)
        
        if self.is_3d:
            self.label_cz = ttk.Label(self, text="Centro Z (Arbitrário):")
            self.label_cz.grid(column=0, row=6, sticky="w", padx=5, pady=5)
            self.entry_cz = ttk.Entry(self, width=10)
            self.entry_cz.grid(column=1, row=6, padx=5, pady=5)
            

        # Centro de rotação (aparece só em Rotação)
        self.label_radio = ttk.Label(self, text="Centro da Rotação:")
        self.centro_rotacao_var = tk.StringVar(value="objeto")
        self.radio_objeto = ttk.Radiobutton(self, text="Objeto", variable=self.centro_rotacao_var, value="objeto")
        self.radio_mundo = ttk.Radiobutton(self, text="Mundo", variable=self.centro_rotacao_var, value="mundo")
        self.radio_arbitrario = ttk.Radiobutton(self, text="Arbitrário", variable=self.centro_rotacao_var, value="arbitrario")
        if self.is_3d:
            self.eixo_var = tk.StringVar(value="x")
            self.eixo_rotacao_label = ttk.Label(self, text="Eixo de rotação: ")
            self.eixo_frame = ttk.Frame(self)
            self.radio_eixo_x = ttk.Radiobutton(self.eixo_frame, text="X", variable=self.eixo_var, value="x")
            self.radio_eixo_y = ttk.Radiobutton(self.eixo_frame, text="Y", variable=self.eixo_var, value="y")
            self.radio_eixo_z= ttk.Radiobutton(self.eixo_frame, text="Z", variable=self.eixo_var, value="z")

        # Botão aplicar
        ttk.Button(self, text="Aplicar transformação", command=self.aplicar).grid(column=0, row=9, columnspan=4, pady=10)

        # Ajusta inputs dinamicamente
        self.combo_tipo.bind("<<ComboboxSelected>>", self._atualizar_inputs)
        self._atualizar_inputs()

    def _atualizar_inputs(self, event=None):
        tipo = self.combo_tipo.get()

        if tipo == "Translação":
            self.label_x.config(text="dx:")
            self.label_y.config(text="dy:")
            self.label_x.grid(); self.entry_x.grid()
            self.label_y.grid(); self.entry_y.grid()
            if self.is_3d:
                self.label_z.config(text="dz:")
                self.label_z.grid(); self.entry_z.grid()
                self.label_cz.grid_remove(); self.entry_cz.grid_remove()
                self.eixo_rotacao_label.grid_remove()
                self.radio_eixo_x.grid_remove()
                self.radio_eixo_y.grid_remove()
                self.radio_eixo_z.grid_remove()
                self.eixo_frame.grid_remove()


            # Esconde ângulo e centro
            self.label_angulo.grid_remove(); self.entry_angulo.grid_remove()
            self.label_cx.grid_remove(); self.entry_cx.grid_remove()
            self.label_cy.grid_remove(); self.entry_cy.grid_remove()
            self.label_radio.grid_remove()
            self.radio_objeto.grid_remove()
            self.radio_mundo.grid_remove()
            self.radio_arbitrario.grid_remove()

        elif tipo == "Escala":
            self.label_x.config(text="sx:")
            self.label_y.config(text="sy:")
            self.label_x.grid(); self.entry_x.grid()
            self.label_y.grid(); self.entry_y.grid()
            if self.is_3d:
                self.label_z.config(text="sz:")
                self.label_z.grid(); self.entry_z.grid()
                self.label_cz.grid_remove(); self.entry_cz.grid_remove()
                self.eixo_rotacao_label.grid_remove()
                self.radio_eixo_x.grid_remove()
                self.radio_eixo_y.grid_remove()
                self.radio_eixo_z.grid_remove()
                self.eixo_frame.grid_remove()
            # Esconde ângulo e centro
            self.label_angulo.grid_remove(); self.entry_angulo.grid_remove()
            self.label_cx.grid_remove(); self.entry_cx.grid_remove()
            self.label_cy.grid_remove(); self.entry_cy.grid_remove()
            self.label_radio.grid_remove()
            self.radio_objeto.grid_remove()
            self.radio_mundo.grid_remove()
            self.radio_arbitrario.grid_remove()

        elif tipo == "Rotação":
            self.label_x.grid_remove(); self.entry_x.grid_remove()
            self.label_y.grid_remove(); self.entry_y.grid_remove()

            self.label_angulo.grid(); self.entry_angulo.grid()
            self.label_cx.grid(); self.entry_cx.grid()
            self.label_cy.grid(); self.entry_cy.grid()
            if self.is_3d:
                self.label_cz.grid(); self.entry_cz.grid()
                self.eixo_rotacao_label.grid(column=0, row=8, sticky="w", padx=5, pady=5)
                self.eixo_frame.grid(column=1, row=8)
                self.radio_eixo_x.grid(column=1, row=0, sticky="w", padx=5, pady=5)
                self.radio_eixo_y.grid(column=2, row=0, sticky="w", padx=5, pady=5)
                self.radio_eixo_z.grid(column=3, row=0, sticky="w", padx=5, pady=5)
                self.label_radio.grid(column=0, row=7, sticky="w", padx=5, pady=5)
                self.radio_objeto.grid(column=1, row=7, sticky="w")
                self.radio_mundo.grid(column=2, row=7, sticky="w")
                self.radio_arbitrario.grid(column=3, row=7, sticky="w")
            else:
                self.label_radio.grid(column=0, row=6, sticky="w", padx=5, pady=5)
                self.radio_objeto.grid(column=1, row=6, sticky="w")
                self.radio_mundo.grid(column=2, row=6, sticky="w")
                self.radio_arbitrario.grid(column=3, row=6, sticky="w")

    def aplicar(self):
        tipo = self.combo_tipo.get()
        obj = self.objeto
        tipo3d = self.is_3d

        if tipo == "Translação":
            dx = float(self.entry_x.get() or 0)
            dy = float(self.entry_y.get() or 0)
            if not tipo3d:
                matriz = matriz_translacao(dx, dy)
                aplicar_matriz(obj, matriz)
            else:
                dz = float(self.entry_z.get() or 0)
                obj.transladar(dx, dy, dz)

        elif tipo == "Escala":
            sx = float(self.entry_x.get() or 1)
            sy = float(self.entry_y.get() or 1)
            if not tipo3d:
                cx, cy = centro_geom(obj)
                matriz = matriz_escalonamento(sx, sy, cx, cy)
                aplicar_matriz(obj, matriz)
            else:
                sz = float(self.entry_z.get() or 1)
                cx, cy, cz = centro_geom_3d(obj)
                matriz = matriz_escalonamento_3d(sx, sy, sz, cx, cy, cz)
                obj.aplicar_matriz(matriz)

        elif tipo == "Rotação":
            angulo = float(self.entry_angulo.get() or 0)
            centro_tipo = self.centro_rotacao_var.get()
            if tipo3d:
                eixo = self.eixo_var.get()
            if centro_tipo == "objeto":
                if tipo3d:
                    obj.rotacionar_em_torno_objeto(eixo, angulo)
                else:
                    cx, cy = centro_geom(obj)
                    matriz = matriz_rotacao(angulo, cx, cy)

            elif centro_tipo == "mundo":
                if tipo3d:
                    if eixo == "x":
                        obj.rotacionar_x(angulo)
                    if eixo == "y":
                        obj.rotacionar_y(angulo)
                    if eixo == "z":
                        obj.rotacionar_z(angulo)
                else:
                    matriz = matriz_rotacao(angulo, 0, 0)

            elif centro_tipo == "arbitrario":
                if tipo3d:
                    cx = float(self.entry_cx.get() or 0)
                    cy = float(self.entry_cy.get() or 0)
                    cz = float(self.entry_cz.get() or 0)
                    obj.rotacionar_em_torno_ponto(eixo, angulo, cx, cy, cz)
                else:
                    cx = float(self.entry_cx.get() or 0)
                    cy = float(self.entry_cy.get() or 0)
                    matriz = (
                        matriz_translacao(cx, cy) @
                        matriz_rotacao(angulo, 0, 0) @
                        matriz_translacao(-cx, -cy)
                    )
            if not tipo3d:
                aplicar_matriz(obj, matriz)

        self.callback_redesenhar()
        self.destroy()