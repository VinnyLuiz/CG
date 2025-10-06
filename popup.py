import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import re

class Popup(tk.Toplevel):
    def __init__(self, master, display_file):
        super().__init__(master)
        self.geometry("420x520+300+100")
        self.title("Incluir Objeto")
        self.aba_atual = 0
        self.display_file = display_file
        self.vcmd = (self.register(self.validar_entry_numerica), "%P")

        tk.Label(self, text="Nome").pack(anchor="w", padx=10, pady=5)
        self.nome_entry = tk.Entry(self)
        self.nome_entry.pack(fill="x", padx=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(padx=10, pady=10, fill="both", expand=1)
        self.notebook.bind("<<NotebookTabChanged>>", self.mudar_aba)

        # Função para criar aba com scroll
        def make_scrollable_tab():
            frame = ttk.Frame(self.notebook)
            canvas = tk.Canvas(frame, height=330)  # altura visível
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollbar.pack(side="right", fill="y")
            canvas.configure(yscrollcommand=scrollbar.set)
            inner = tk.Frame(canvas)
            window = canvas.create_window((0, 0), window=inner, anchor="nw")
            def on_frame_configure(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
            def on_canvas_configure(event):
                canvas.itemconfig(window, width=event.width)
            inner.bind("<Configure>", on_frame_configure)
            canvas.bind("<Configure>", on_canvas_configure)
            inner.bind(
                "<Enter>", lambda e: canvas.bind_all('<MouseWheel>', lambda ev: canvas.yview_scroll(-1 * int(ev.delta / 120), "units"))
            )
            inner.bind(
                "<Leave>", lambda e: canvas.unbind_all('<MouseWheel>')
            )
            return frame, inner

        # Aba Ponto
        frame_ponto, inner_ponto = make_scrollable_tab()
        self.notebook.add(frame_ponto, text="Ponto")
        tk.Label(inner_ponto, text="x:").grid(row=0, column=0)
        self.x_ponto = tk.Entry(inner_ponto, width=7, validate="key", validatecommand=self.vcmd)
        self.x_ponto.grid(row=0, column=1, padx=(0, 10))
        tk.Label(inner_ponto, text="y:").grid(row=0, column=2)
        self.y_ponto = tk.Entry(inner_ponto, width=7, validate="key", validatecommand=self.vcmd)
        self.y_ponto.grid(row=0, column=3, padx=(0, 10))

        # Aba Reta
        frame_reta, inner_reta = make_scrollable_tab()
        self.notebook.add(frame_reta, text="Reta")
        tk.Label(inner_reta, text="x0:").grid(row=0, column=0)
        self.x0_reta = tk.Entry(inner_reta, width=6, validate="key", validatecommand=self.vcmd)
        self.x0_reta.grid(row=0, column=1)
        tk.Label(inner_reta, text="y0:").grid(row=0, column=2)
        self.y0_reta = tk.Entry(inner_reta, width=6, validate="key", validatecommand=self.vcmd)
        self.y0_reta.grid(row=0, column=3)
        tk.Label(inner_reta, text="x1:").grid(row=1, column=0)
        self.x1_reta = tk.Entry(inner_reta, width=6, validate="key", validatecommand=self.vcmd)
        self.x1_reta.grid(row=1, column=1)
        tk.Label(inner_reta, text="y1:").grid(row=1, column=2)
        self.y1_reta = tk.Entry(inner_reta, width=6, validate="key", validatecommand=self.vcmd)
        self.y1_reta.grid(row=1, column=3)

        # Aba Wireframe
        frame_wireframe, inner_wireframe = make_scrollable_tab()
        self.notebook.add(frame_wireframe, text="Wireframe")
        self.lista_entry = []
        self.pontos_frame = inner_wireframe

        def adicionar_entry():
            row = len(self.lista_entry)
            lbl = tk.Label(self.pontos_frame, text=f"Ponto{row}:")
            lbl.grid(row=row, column=0, padx=5, pady=2)
            entry_x = tk.Entry(self.pontos_frame, width=7, validate="key", validatecommand=self.vcmd)
            entry_y = tk.Entry(self.pontos_frame, width=7, validate="key", validatecommand=self.vcmd)
            entry_x.grid(row=row, column=1)
            entry_y.grid(row=row, column=2)
            self.lista_entry.append((entry_x, entry_y))
        self.adicionar_entry = adicionar_entry
        btn_add_ponto = tk.Button(frame_wireframe, text="+ Adicionar ponto", command=self.adicionar_entry)
        btn_add_ponto.pack(side="bottom", pady=6)

        self.preencher_var = tk.BooleanVar(value=False)
        self.check_preencher = ttk.Checkbutton(inner_wireframe, text="Preencher", variable=self.preencher_var)
        self.check_preencher.grid(row=100, column=0, columnspan=3, pady=5)

        self.cor_preenchimento = "#000000"
        self.label_cor = tk.Label(inner_wireframe, text="Cor: #000000", bg=self.cor_preenchimento, fg="white", relief="solid")
        self.label_cor.grid(row=101, column=0, columnspan=2, pady=5)
        ttk.Button(inner_wireframe, text="Escolher Cor", command=self.escolher_cor).grid(row=101, column=2, pady=5)

        # Aba Curva2D
        frame_curva, inner_curva = make_scrollable_tab()
        self.notebook.add(frame_curva, text="Curva2D")
        tk.Label(inner_curva, text="Pontos: (x1, y1), (x2, y2), ...").grid(column=0, row=0)
        self.curva_entry = ttk.Entry(inner_curva)
        self.curva_entry.grid(column=1, row=0)

        # Aba BSpline
        frame_bspline, inner_bspline = make_scrollable_tab()
        self.notebook.add(frame_bspline, text="BSpline")
        tk.Label(inner_bspline, text="Pontos: (x1, y1), (x2, y2), ...").grid(column=0, row=0)
        self.bspline_entry = ttk.Entry(inner_bspline)
        self.bspline_entry.grid(column=1, row=0)

        # Aba Objeto3D
        frame_obj3d, inner_obj3d = make_scrollable_tab()
        self.notebook.add(frame_obj3d, text="Objeto3D")
        self.lista_entry_pontos3d = []
        self.lista_entry_segmentos3d = []
        self.pontos3d_frame = tk.Frame(inner_obj3d)
        self.pontos3d_frame.pack(pady=5)
        btn_add_ponto3d = tk.Button(inner_obj3d, text="+ Adicionar ponto", command=self.adicionar_entry_ponto3d)
        btn_add_ponto3d.pack()
        self.adicionar_entry_ponto3d()
        tk.Label(inner_obj3d, text="Segmento (índices dos pontos, ex: 0 1):").pack()
        self.segmentos3d_frame = tk.Frame(inner_obj3d)
        self.segmentos3d_frame.pack(pady=5)
        btn_add_segmento3d = tk.Button(inner_obj3d, text="+ Adicionar segmento", command=self.adicionar_entry_segmento3d)
        btn_add_segmento3d.pack()
        self.adicionar_entry_segmento3d()

        # Botões
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Adicionar", command=self.adicionar_objeto).pack(side="left", padx=5)

    def mudar_aba(self, event):
        self.aba_atual = self.notebook.index(self.notebook.select())

    def adicionar_objeto(self):
        pass  # implemente conforme seu projeto

    def validar_entry_numerica(self, texto):
        if texto == "-" or texto == "":
            return True
        try:
            float(texto)
            return True
        except ValueError:
            return False

    def escolher_cor(self):
        cor_selecionada = colorchooser.askcolor(title="Escolha a cor de preenchimento")
        if cor_selecionada:
            self.cor_preenchimento = cor_selecionada[1]
            self.label_cor.config(text=f"Cor de Preenchimento: {self.cor_preenchimento}", bg=self.cor_preenchimento, fg="white" if sum(cor_selecionada[0][:3]) < 382.5 else "black")

    def adicionar_entry_ponto3d(self):
        row = len(self.lista_entry_pontos3d)
        lbl = tk.Label(self.pontos3d_frame, text=f"Ponto{row}:")
        lbl.grid(row=row, column=0, padx=5, pady=2)
        entry_x = tk.Entry(self.pontos3d_frame, width=4, validate="key", validatecommand=self.vcmd)
        entry_y = tk.Entry(self.pontos3d_frame, width=4, validate="key", validatecommand=self.vcmd)
        entry_z = tk.Entry(self.pontos3d_frame, width=4, validate="key", validatecommand=self.vcmd)
        entry_x.grid(row=row, column=1)
        entry_y.grid(row=row, column=2)
        entry_z.grid(row=row, column=3)
        self.lista_entry_pontos3d.append((entry_x, entry_y, entry_z))

    def adicionar_entry_segmento3d(self):
        row = len(self.lista_entry_segmentos3d)
        lbl = tk.Label(self.segmentos3d_frame, text=f"Segmento{row}:")
        lbl.grid(row=row, column=0, padx=5, pady=2)
        entry_i = tk.Entry(self.segmentos3d_frame, width=3, validate="key", validatecommand=self.vcmd)
        entry_j = tk.Entry(self.segmentos3d_frame, width=3, validate="key", validatecommand=self.vcmd)
        entry_i.grid(row=row, column=1)
        entry_j.grid(row=row, column=2)
        self.lista_entry_segmentos3d.append((entry_i, entry_j))
class PopupTransformacoes(tk.Toplevel):
    def __init__(self, parent, objeto, callback_redesenhar):
        super().__init__(parent)
        self.title(f"Transformações: {objeto.nome}")
        self.geometry("500x300")
        self.objeto = objeto
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

        # Centro de rotação (aparece só em Rotação)
        self.label_radio = ttk.Label(self, text="Centro da Rotação:")
        self.centro_rotacao_var = tk.StringVar(value="objeto")
        self.radio_objeto = ttk.Radiobutton(self, text="Objeto", variable=self.centro_rotacao_var, value="objeto")
        self.radio_mundo = ttk.Radiobutton(self, text="Mundo", variable=self.centro_rotacao_var, value="mundo")
        self.radio_arbitrario = ttk.Radiobutton(self, text="Arbitrário", variable=self.centro_rotacao_var, value="arbitrario")

        # Botão aplicar
        ttk.Button(self, text="Aplicar transformação", command=self.aplicar).grid(column=0, row=7, columnspan=4, pady=10)

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

            self.label_radio.grid(column=0, row=6, sticky="w", padx=5, pady=5)
            self.radio_objeto.grid(column=1, row=6, sticky="w")
            self.radio_mundo.grid(column=2, row=6, sticky="w")
            self.radio_arbitrario.grid(column=3, row=6, sticky="w")

    def aplicar(self):
        tipo = self.combo_tipo.get()
        obj = self.objeto

        if tipo == "Translação":
            dx = float(self.entry_x.get() or 0)
            dy = float(self.entry_y.get() or 0)
            matriz = matriz_translacao(dx, dy)
            aplicar_matriz(obj, matriz)

        elif tipo == "Escala":
            sx = float(self.entry_x.get() or 1)
            sy = float(self.entry_y.get() or 1)
            cx, cy = centro_geom(obj)
            matriz = matriz_escalonamento(sx, sy, cx, cy)
            aplicar_matriz(obj, matriz)

        elif tipo == "Rotação":
            angulo = float(self.entry_angulo.get() or 0)
            centro_tipo = self.centro_rotacao_var.get()

            if centro_tipo == "objeto":
                cx, cy = centro_geom(obj)
                matriz = matriz_rotacao(angulo, cx, cy)
            elif centro_tipo == "mundo":
                matriz = matriz_rotacao(angulo, 0, 0)
            elif centro_tipo == "arbitrario":
                cx = float(self.entry_cx.get() or 0)
                cy = float(self.entry_cy.get() or 0)
                matriz = (
                    matriz_translacao(cx, cy) @
                    matriz_rotacao(angulo, 0, 0) @
                    matriz_translacao(-cx, -cy)
                )
            aplicar_matriz(obj, matriz)

        self.callback_redesenhar()
        self.destroy()