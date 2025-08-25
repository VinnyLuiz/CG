from tkinter import *
from tkinter import ttk
from popup import Popup
from displayFile import DisplayFile
from tranformacoes import Window, Viewport


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
        self.update_idletasks()  # garante que dimensões estão corretas
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


    # Criação de Layout
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

        # Botões de navegação
        frame_botoes_movimento = ttk.Frame(labelFrame_window)
        frame_botoes_movimento.grid(column=0, row=1, padx=(8, 0), pady=(0, 8))
        ttk.Button(frame_botoes_movimento, text="↑", width=2, command=self.pan_up).grid(column=1, row=1)
        ttk.Button(frame_botoes_movimento, text="↓", width=2, command=self.pan_down).grid(column=1, row=2)
        ttk.Button(frame_botoes_movimento, text="←", width=2, command=self.pan_left).grid(column=0, row=1, rowspan=2, sticky="E")
        ttk.Button(frame_botoes_movimento, text="→", width=2, command=self.pan_right).grid(column=2, row=1, rowspan=2, sticky="W")

        # Botões de zoom
        frame_botoes_zoom = ttk.Frame(labelFrame_window)
        frame_botoes_zoom.grid(column=1, row=1, padx=(15, 0), pady=(0, 8))
        ttk.Button(frame_botoes_zoom, text="+", width=2, command=self.zoom_in).grid(column=0, row=0, pady=5)
        ttk.Button(frame_botoes_zoom, text="-", width=2, command=self.zoom_out).grid(column=0, row=1, pady=5)

    def _criar_canvas(self):
        canva_frame = ttk.Frame(self)
        canva_frame.grid(column=1, row=0, sticky="nsew")
        canva_frame.columnconfigure(0, weight=1)
        canva_frame.rowconfigure(1, weight=1)

        self.canvas = Canvas(canva_frame, bg="white")
        self.canvas.grid(column=0, row=1, columnspan=2, sticky="nsew", padx=(0, 10), pady=(20, 0))

        # clique direito desseleciona
        self.canvas.bind("<Button-3>", self.desselecionar_objeto)

    def _criar_status_bar(self):
        self.text = StringVar()
        transcript_label = ttk.Label(self, textvariable=self.text, relief="sunken")
        transcript_label.grid(column=1, row=1, sticky="nsew", padx=(0, 10), pady=10)


    # Funções de Objetos
    def redesenhar(self):
        self.canvas.delete("all")
        self.listbox_objetos.delete(0, END)

        # Viewport border (Não utilizado por enquanto)
        self.canvas.create_rectangle(0, 0, self.max_w_viewport, self.max_h_viewport, outline="red")
        self.canvas.create_text(5, 10, text="Viewport", anchor="w")

        # Deseleciona todos
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


    # Funções de Navegação
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
        """Move a window na direção especificada por porcentagem da largura/altura"""
        try:
            passo_percent = float(self.entry_passo.get()) if self.entry_passo.get() else 10
        except ValueError:
            passo_percent = 10  # Valor padrão se não for número válido

        # Converte os percentuais em unidades do mundo
        passo_x = (dx_percent * passo_percent / 100) * self.window.largura
        passo_y = (dy_percent * passo_percent / 100) * self.window.altura

        # Move a window
        self.window.xw_min += passo_x
        self.window.xw_max += passo_x
        self.window.yw_min += passo_y
        self.window.yw_max += passo_y

        # Mantém largura/altura consistentes
        self.window.largura = self.window.xw_max - self.window.xw_min
        self.window.altura = self.window.yw_max - self.window.yw_min

        self.redesenhar()


    # Wrappers para cada direção
    def pan_up(self):
        self.pan(dy_percent=1)

    def pan_down(self):
        self.pan(dy_percent=-1)

    def pan_left(self):
        self.pan(dx_percent=-1)

    def pan_right(self):
        self.pan(dx_percent=1)





if __name__ == "__main__":
    app = App()
    app.mainloop()
