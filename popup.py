import tkinter as tk
from tkinter import ttk, messagebox
from objetos import *
from displayFile import DisplayFile

class Popup(tk.Toplevel):
    def __init__(self, master, display_file: DisplayFile):
        super().__init__(master)
        self.geometry("400x300+300+100")
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

                    if pontos:  # só cria se tiver pontos válidos
                        wireframe = Wireframe(pontos, self.nome_entry.get())
                        self.display_file.adicionar(wireframe)
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
        match self.aba_atual:
            case 0: tipo = "Ponto"
            case 1: tipo = "Reta"
            case 2: tipo = "Wireframe"
        
        # Conta quantos objetos deste tipo já existem
        count = sum(1 for obj in self.display_file.objetos if obj.nome.startswith(tipo))
        return f"{tipo}_{count + 1}"