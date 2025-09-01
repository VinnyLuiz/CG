from tkinter import *
from tkinter import ttk
from popup import Popup
from displayFile import DisplayFile
from tranformacoes import Window, Viewport, matriz_translacao, matriz_escalonamento, matriz_rotacao, aplicar_matriz, centro_geom

class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor de Objetos 2D")
        self.geometry("1000x700+300+100")

        # Estado
        self.display_file = DisplayFile("objetos_salvos.txt")
        self.objeto_selecionado = None

        # Configuração grid principal
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Widgets
        self._criar_menu_contexto()
        self._criar_canvas()
        self._criar_status_bar()

        # Viewport e Window
        self.update_idletasks()
        self.max_w_viewport = self.canvas.winfo_width()
        self.max_h_viewport = self.canvas.winfo_height()
        viewport_width = self.max_w_viewport
        viewport_height = self.max_h_viewport
        centro_ret_x = viewport_width / 2
        centro_ret_y = viewport_height / 2

        self.window = Window(-centro_ret_x, -centro_ret_y, centro_ret_x, centro_ret_y)
        self.viewport = Viewport(0, 0, self.max_w_viewport, self.max_h_viewport)

        self.text.set(f"Dimensão do Viewport: {viewport_width}x{viewport_height}\n"
                      f"Centro: {centro_ret_x:.1f}x{centro_ret_y:.1f}\n\n")

        self.redesenhar()

    def _criar_menu_contexto(self):
        context_menu_frame = ttk.LabelFrame(self, text="Menu de ações", padding=20)
        context_menu_frame.grid(column=0, row=0, rowspan=2, padx=10, pady=10, sticky="ns")

        # Lista de objetos
        ttk.Label(context_menu_frame, text="Objetos").grid(column=0, row=0, sticky="w")
        self.listbox_objetos = Listbox(context_menu_frame, activestyle="underline",
                                    background="white", selectmode="single")
        self.listbox_objetos.grid(column=0, row=1)

        frame_botoes_objetos = ttk.Frame(context_menu_frame)
        frame_botoes_objetos.grid(column=0, row=2)
        ttk.Button(frame_botoes_objetos, text="Adicionar",
                command=lambda: self.adicionar_objeto(None)).grid(column=0, row=0)
        ttk.Button(frame_botoes_objetos, text="Remover",
                command=self.remover_objeto).grid(column=1, row=0)

        self.listbox_objetos.bind('<<ListboxSelect>>', self.selecionar_objeto)
        self.listbox_objetos.bind('<Button-3>', self.desselecionar_objeto)

        # Frame da window
        labelFrame_window = ttk.LabelFrame(context_menu_frame, text="Window")
        labelFrame_window.grid(column=0, row=3)

        self.entry_passo = ttk.Entry(labelFrame_window, background="white", width=5)
        self.entry_passo.grid(column=1, row=0, padx=(0, 5), pady=10)

        ttk.Label(labelFrame_window, text="Passo:").grid(column=0, row=0, padx=10)
        ttk.Label(labelFrame_window, text="%").grid(column=2, row=0)

        frame_botoes_movimento = ttk.Frame(labelFrame_window)
        frame_botoes_movimento.grid(column=0, row=1, padx=(8, 0), pady=(0, 8))
        ttk.Button(frame_botoes_movimento, text="↑", width=2, command=self.pan_up).grid(column=1, row=1)
        ttk.Button(frame_botoes_movimento, text="↓", width=2, command=self.pan_down).grid(column=1, row=2)
        ttk.Button(frame_botoes_movimento, text="←", width=2, command=self.pan_left).grid(column=0, row=1, rowspan=2, sticky="E")
        ttk.Button(frame_botoes_movimento, text="→", width=2, command=self.pan_right).grid(column=2, row=1, rowspan=2, sticky="W")

        frame_botoes_zoom = ttk.Frame(labelFrame_window)
        frame_botoes_zoom.grid(column=1, row=1, padx=(15, 0), pady=(0, 8))
        ttk.Button(frame_botoes_zoom, text="+", width=2, command=self.zoom_in).grid(column=0, row=0, pady=5)
        ttk.Button(frame_botoes_zoom, text="-", width=2, command=self.zoom_out).grid(column=0, row=1, pady=5)

        # Painel de Transformações
        labelFrame_transformacoes = ttk.LabelFrame(context_menu_frame, text="Transformações 2D")
        labelFrame_transformacoes.grid(column=0, row=4, pady=(20,0), sticky="ew")

        ttk.Label(labelFrame_transformacoes, text="Tipo:").grid(column=0, row=0, sticky="w", padx=(0,5))
        self.combo_tipo = ttk.Combobox(labelFrame_transformacoes, values=["Translação", "Escala", "Rotação"], state="readonly", width=15)
        self.combo_tipo.grid(column=1, row=0)
        self.combo_tipo.current(0)

        # Entradas para parâmetros de transformação
        self.label_x = ttk.Label(labelFrame_transformacoes, text="dx:")
        self.label_x.grid(column=0, row=1, sticky="w", padx=(0,5))
        self.entry_x = ttk.Entry(labelFrame_transformacoes, width=8)
        self.entry_x.grid(column=1, row=1)

        self.label_y = ttk.Label(labelFrame_transformacoes, text="dy:")
        self.label_y.grid(column=0, row=2, sticky="w", padx=(0,5))
        self.entry_y = ttk.Entry(labelFrame_transformacoes, width=8)
        self.entry_y.grid(column=1, row=2)

        self.label_angulo = ttk.Label(labelFrame_transformacoes, text="Ângulo (graus):")
        self.label_angulo.grid(column=0, row=3, sticky="w", padx=(0,5))
        self.entry_angulo = ttk.Entry(labelFrame_transformacoes, width=8)
        self.entry_angulo.grid(column=1, row=3)

        self.label_cx = ttk.Label(labelFrame_transformacoes, text="Centro X (Arbitrário):")
        self.label_cx.grid(column=0, row=4, sticky="w", padx=(0,5))
        self.entry_cx = ttk.Entry(labelFrame_transformacoes, width=8)
        self.entry_cx.grid(column=1, row=4)

        self.label_cy = ttk.Label(labelFrame_transformacoes, text="Centro Y (Arbitrário):")
        self.label_cy.grid(column=0, row=5, sticky="w", padx=(0,5))
        self.entry_cy = ttk.Entry(labelFrame_transformacoes, width=8)
        self.entry_cy.grid(column=1, row=5)

        # Centro da rotação
        ttk.Label(labelFrame_transformacoes, text="Centro da Rotação:").grid(column=0, row=6, sticky="w", padx=(0,5))
        self.centro_rotacao_var = StringVar(value="objeto")
        self.radio_objeto = ttk.Radiobutton(labelFrame_transformacoes, text="Objeto", variable=self.centro_rotacao_var, value="objeto")
        self.radio_objeto.grid(column=1, row=6, sticky="w")
        self.radio_mundo = ttk.Radiobutton(labelFrame_transformacoes, text="Mundo", variable=self.centro_rotacao_var, value="mundo")
        self.radio_mundo.grid(column=2, row=6, sticky="w")
        self.radio_arbitrario = ttk.Radiobutton(labelFrame_transformacoes, text="Arbitrário", variable=self.centro_rotacao_var, value="arbitrario")
        self.radio_arbitrario.grid(column=3, row=6, sticky="w")

        # Botão para aplicar transformação
        ttk.Button(labelFrame_transformacoes, text="Aplicar transformação", command=self.aplicar_transformacao_objeto).grid(column=0, row=7, columnspan=4, pady=10)

        # Ligação do evento para atualizar campos
        self.combo_tipo.bind("<<ComboboxSelected>>", self._atualizar_transformacao_inputs)

        # Chama a função para ajustar a interface ao iniciar
        self._atualizar_transformacao_inputs()
    
    def _atualizar_transformacao_inputs(self, event=None):
        tipo = self.combo_tipo.get()
        if tipo == "Translação":
            # Mostra só dx/dy
            self.label_x.config(text="dx:")
            self.label_x.grid()
            self.entry_x.grid()
            self.label_y.config(text="dy:")
            self.label_y.grid()
            self.entry_y.grid()
            self.label_angulo.grid_remove()
            self.entry_angulo.grid_remove()
            self.label_cx.grid_remove()
            self.entry_cx.grid_remove()
            self.label_cy.grid_remove()
            self.entry_cy.grid_remove()
            self.radio_objeto.grid_remove()
            self.radio_mundo.grid_remove()
            self.radio_arbitrario.grid_remove()
        elif tipo == "Escala":
            # Mostra só sx/sy e centro sempre é objeto
            self.label_x.config(text="sx:")
            self.label_x.grid()
            self.entry_x.grid()
            self.label_y.config(text="sy:")
            self.label_y.grid()
            self.entry_y.grid()
            self.label_angulo.grid_remove()
            self.entry_angulo.grid_remove()
            self.label_cx.grid_remove()
            self.entry_cx.grid_remove()
            self.label_cy.grid_remove()
            self.entry_cy.grid_remove()
            self.radio_objeto.grid_remove()
            self.radio_mundo.grid_remove()
            self.radio_arbitrario.grid_remove()
        elif tipo == "Rotação":
            # Mostra só ângulo, centro X/Y e radios
            self.label_x.grid_remove()
            self.entry_x.grid_remove()
            self.label_y.grid_remove()
            self.entry_y.grid_remove()
            self.label_angulo.grid()
            self.entry_angulo.grid()
            self.label_cx.grid()
            self.entry_cx.grid()
            self.label_cy.grid()
            self.entry_cy.grid()
            self.radio_objeto.grid()
            self.radio_mundo.grid()
            self.radio_arbitrario.grid()
    def _criar_canvas(self):
        canva_frame = ttk.Frame(self)
        canva_frame.grid(column=1, row=0, sticky="nsew")
        canva_frame.columnconfigure(0, weight=1)
        canva_frame.rowconfigure(1, weight=1)

        self.canvas = Canvas(canva_frame, bg="white")
        self.canvas.grid(column=0, row=1, columnspan=2, sticky="nsew", padx=(0, 10), pady=(20, 0))

        self.canvas.bind("<Button-3>", self.desselecionar_objeto)

    def _criar_status_bar(self):
        self.text = StringVar()
        transcript_label = ttk.Label(self, textvariable=self.text, relief="sunken")
        transcript_label.grid(column=1, row=1, sticky="nsew", padx=(0, 10), pady=10)

    def redesenhar(self):
        self.canvas.delete("all")
        self.listbox_objetos.delete(0, END)

        self.canvas.create_rectangle(0, 0, self.max_w_viewport, self.max_h_viewport, outline="red")
        self.canvas.create_text(5, 10, text="Viewport", anchor="w")

        for obj in self.display_file.objetos:
            obj.selecionado = False

        if self.objeto_selecionado:
            self.objeto_selecionado.selecionado = True

        for obj in self.display_file.objetos:
            obj.desenhar(self.canvas, self.window, self.viewport)
            self.listbox_objetos.insert(END, obj.nome)

    def adicionar_objeto(self, event):
        popup = Popup(self, display_file=self.display_file)
        self.wait_window(popup)
        self.redesenhar()

    def remover_objeto(self):
        selecao = self.listbox_objetos.curselection()
        if selecao:
            index = selecao[0]
            objeto = self.listbox_objetos.get(index)
            self.display_file.remover(objeto)
            self.listbox_objetos.delete(index)
            self.redesenhar()

    def selecionar_objeto(self, event):
        selecao = self.listbox_objetos.curselection()
        if selecao:
            index = selecao[0]
            nome_objeto = self.listbox_objetos.get(index)
            self.objeto_selecionado = self.display_file.get_objeto(nome_objeto)
            self.redesenhar()
            if index < self.listbox_objetos.size():
                self.listbox_objetos.select_set(index)

    def desselecionar_objeto(self, event=None):
        self.objeto_selecionado = None
        self.redesenhar()

    def zoom_in(self):
        self.zoom(0.8)

    def zoom_out(self):
        self.zoom(1.2)

    def zoom(self, fator):
        centro_x = (self.window.xw_min + self.window.xw_max) / 2
        centro_y = (self.window.yw_min + self.window.yw_max) / 2

        nova_largura = self.window.largura * fator
        nova_altura = self.window.altura * fator

        self.window.xw_min = centro_x - nova_largura / 2
        self.window.xw_max = centro_x + nova_largura / 2
        self.window.yw_min = centro_y - nova_altura / 2
        self.window.yw_max = centro_y + nova_altura / 2
        self.window.largura = nova_largura
        self.window.altura = nova_altura

        self.redesenhar()

    def pan(self, dx_percent=0, dy_percent=0):
        try:
            passo_percent = float(self.entry_passo.get()) if self.entry_passo.get() else 10
        except ValueError:
            passo_percent = 10

        passo_x = (dx_percent * passo_percent / 100) * self.window.largura
        passo_y = (dy_percent * passo_percent / 100) * self.window.altura

        self.window.xw_min += passo_x
        self.window.xw_max += passo_x
        self.window.yw_min += passo_y
        self.window.yw_max += passo_y

        self.window.largura = self.window.xw_max - self.window.xw_min
        self.window.altura = self.window.yw_max - self.window.yw_min

        self.redesenhar()

    def pan_up(self):
        self.pan(dy_percent=1)

    def pan_down(self):
        self.pan(dy_percent=-1)

    def pan_left(self):
        self.pan(dx_percent=-1)

    def pan_right(self):
        self.pan(dx_percent=1)


    def aplicar_transformacao_objeto(self):
        if not self.objeto_selecionado:
            return

        tipo = self.combo_tipo.get()
        obj = self.objeto_selecionado

        if tipo == "Translação":
            try:
                x_val = float(self.entry_x.get() or 0)
                y_val = float(self.entry_y.get() or 0)
            except ValueError:
                x_val, y_val = 0, 0
            matriz = matriz_translacao(x_val, y_val)
            aplicar_matriz(obj, matriz)

        elif tipo == "Escala":
            try:
                x_val = float(self.entry_x.get() or 1)
                y_val = float(self.entry_y.get() or 1)
            except ValueError:
                x_val, y_val = 1, 1
            cx, cy = centro_geom(obj)
            matriz = matriz_escalonamento(x_val, y_val, cx, cy)
            aplicar_matriz(obj, matriz)

        elif tipo == "Rotação":
            try:
                angulo = float(self.entry_angulo.get())
            except ValueError:
                angulo = 0

            centro_tipo = self.centro_rotacao_var.get()
            if centro_tipo == "objeto":
                cx, cy = centro_geom(obj)
                matriz = matriz_rotacao(angulo, cx, cy)
            elif centro_tipo == "mundo":
                cx, cy = 0, 0
                matriz = matriz_rotacao(angulo, cx, cy)
            elif centro_tipo == "arbitrario":
                try:
                    cx = float(self.entry_cx.get())
                    cy = float(self.entry_cy.get())
                except ValueError:
                    cx, cy = 0, 0
                matriz = (
                    matriz_translacao(cx, cy) @
                    matriz_rotacao(angulo, 0, 0) @
                    matriz_translacao(-cx, -cy)
                )

            aplicar_matriz(obj, matriz)
        self.redesenhar()
if __name__ == "__main__":
    app = App()
    app.mainloop()