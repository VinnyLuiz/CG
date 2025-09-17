from tkinter import *
from tkinter import ttk, filedialog, messagebox
from popup import Popup, PopupTransformacoes
from displayFile import DisplayFile
from tranformacoes import Window, Viewport, matriz_rotacao
import numpy as np
from descritorOBJ import DescritorOBJ

class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor de Objetos 2D")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

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
        x_window = 500
        y_window = 500

        self.text.set(f"Dimensão do Viewport: {self.canvas.winfo_width()}x{self.canvas.winfo_height()}")
        self.window = Window(-x_window, -y_window, x_window, y_window)

        self.update_idletasks()
        self.max_w_viewport = self.canvas.winfo_width() - 10
        self.max_h_viewport = self.canvas.winfo_height() - 10
        self.viewport = Viewport(10, 10, self.max_w_viewport, self.max_h_viewport)


        self.redesenhar()

    # Criação do Layout
    def _criar_menu_contexto(self):
        context_menu_frame = ttk.LabelFrame(self, text="Menu de ações", padding=20)
        context_menu_frame.grid(column=0, row=0, rowspan=2, padx=10, pady=10, sticky="ns")

        # Lista de objetos
        ttk.Label(context_menu_frame, text="Objetos").grid(column=0, row=0)
        self.listbox_objetos = Listbox(context_menu_frame, activestyle="underline",
                                    background="white", selectmode="single")
        self.listbox_objetos.grid(column=0, row=1)

        frame_botoes_objetos = ttk.Frame(context_menu_frame)
        frame_botoes_objetos.grid(column=0, row=2)
        ttk.Button(frame_botoes_objetos, text="Adicionar",
                command=self.adicionar_objeto).grid(column=0, row=0)
        ttk.Button(frame_botoes_objetos, text="Remover",
                command=self.remover_objeto).grid(column=2, row=0)
        ttk.Button(frame_botoes_objetos, text="Transformar",
                command=lambda: self.transformar_objeto(None)).grid(column=1, row=0)

        self.listbox_objetos.bind('<<ListboxSelect>>', self.selecionar_objeto)
        self.listbox_objetos.bind('<Button-3>', self.desselecionar_objeto)
        self.listbox_objetos.bind('<Double-1>', self.transformar_objeto)


        # Frame da window
        labelFrame_window = ttk.LabelFrame(context_menu_frame, text="Window")
        labelFrame_window.grid(column=0, row=3)

        self.entry_passo = ttk.Entry(labelFrame_window, background="white", width=5)
        self.entry_passo.grid(column=1, row=0, padx=(0, 5), pady=10)

        self.entry_angulo_window = ttk.Entry(labelFrame_window, background="white", width=5)
        self.entry_angulo_window.grid(column=1, row=1, padx=(0, 5), pady=10)

        ttk.Label(labelFrame_window, text="Passo:").grid(column=0, row=0, padx=10)
        ttk.Label(labelFrame_window, text="Ângulo:").grid(column=0, row=1, padx=10)
        
        # Frame de arquivo
        ttk.Button(context_menu_frame, text="Salvar Arquivo", width=15, command=self.exportar_obj).grid(column=0, row=5, pady=5)
        ttk.Button(context_menu_frame, text="Carregar Arquivo", width=15, command=self.importar_obj).grid(column=0, row=6)

        # Botões de Movimento
        frame_botoes_movimento = ttk.Frame(labelFrame_window)
        frame_botoes_movimento.grid(column=0, row=2, padx=(8, 0), pady=(0, 8))
        ttk.Button(frame_botoes_movimento, text="↑", width=2, command=self.pan_up).grid(column=1, row=1)
        ttk.Button(frame_botoes_movimento, text="↓", width=2, command=self.pan_down).grid(column=1, row=3)
        ttk.Button(frame_botoes_movimento, text="←", width=2, command=self.pan_left).grid(column=0, row=3, rowspan=2, sticky="E")
        ttk.Button(frame_botoes_movimento, text="→", width=2, command=self.pan_right).grid(column=2, row=3, rowspan=2, sticky="W")
        ttk.Button(frame_botoes_movimento, text="↶", width=2, command=self.rotate_left).grid(column=0, row=1, sticky="E")
        ttk.Button(frame_botoes_movimento, text="↷", width=2, command=self.rotate_right).grid(column=2, row=1, sticky="W")

        # Botões de Zoom
        frame_botoes_zoom = ttk.Frame(labelFrame_window)
        frame_botoes_zoom.grid(column=1, row=2, padx=(15, 0), pady=(0, 8))
        ttk.Button(frame_botoes_zoom, text="+", width=2, command=self.zoom_in).grid(column=0, row=0, padx=(0, 5), pady=5)
        ttk.Button(frame_botoes_zoom, text="-", width=2, command=self.zoom_out).grid(column=0, row=1, padx=(0, 5), pady=5)

        # RadioButton Clipping
        self.metodo_clipping = StringVar(value="Cohen-Sutherland")
        frame_clipping = ttk.LabelFrame(context_menu_frame, text="Clipping de Retas")
        frame_clipping.grid(row=4, padx=5, pady=5)

        ttk.Radiobutton(
            frame_clipping,
            text="Cohen-Sutherland",
            variable=self.metodo_clipping,
            value="Cohen-Sutherland",
            command=self.redesenhar
        ).pack(anchor="w", padx=10, pady=2)

        ttk.Radiobutton(
            frame_clipping,
            text="Nicholl-Lee-Nicholl",
            variable=self.metodo_clipping,
            value="Nicholl-Lee-Nicholl",
            command=self.redesenhar
        ).pack(anchor="w", padx=10, pady=2)


    def _criar_canvas(self):
        self.canvas = Canvas(self, bg="white")
        self.canvas.grid(column=1, row=0, columnspan=2, sticky="nsew", padx=(0, 10), pady=(20, 0))

    def _criar_status_bar(self):
        self.text = StringVar()
        transcript_label = Label(self, textvariable=self.text, relief="sunken", anchor="nw", height=4)
        transcript_label.grid(column=1, row=1, sticky="nsew", padx=(0, 10), pady=10)

    def redesenhar(self):
        self.canvas.delete("all")
        self.listbox_objetos.delete(0, END)

        self.text.set(f"Dimensão do Viewport: {self.max_w_viewport}x{self.max_h_viewport}")
        self.canvas.create_rectangle(10, 10, self.max_w_viewport, self.max_h_viewport, outline="red")

        self.display_file.atualizar_scn(self.window)
        for obj in self.display_file.objetos:
            obj.selecionado = False

        if self.objeto_selecionado:
            self.objeto_selecionado.selecionado = True

        for obj in self.display_file.objetos:
            if obj.__class__.__name__== "Reta":
                obj.desenhar(self.canvas, self.window, self.viewport, self.metodo_clipping.get())
            else:    
                obj.desenhar(self.canvas, self.window, self.viewport)
            self.listbox_objetos.insert(END, obj.nome)

    def adicionar_objeto(self):
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

    def transformar_objeto(self, event):
        selecao = self.listbox_objetos.curselection()
        if not selecao:
            return
        index = selecao[0]
        nome_objeto = self.listbox_objetos.get(index)
        self.objeto_selecionado = self.display_file.get_objeto(nome_objeto)
        if not self.objeto_selecionado:
            return
        tempW = PopupTransformacoes(self, self.objeto_selecionado, self.redesenhar)
        self.wait_window(tempW)
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

        # Agora aplicamos a matriz de rotação para alinhar o vup com o mundo
        vup_window = np.array([passo_x, passo_y, 1])
        R = matriz_rotacao(self.window.angulo_rotacao)
        vup_mundo = R @ vup_window

        novo_x, novo_y = vup_mundo[0], vup_mundo[1]

        # Get current window center
        centro_x_atual, centro_y_atual = self.window.centro()

        # Calculate new window center
        novo_centro_x = centro_x_atual + novo_x
        novo_centro_y = centro_y_atual + novo_y

        # Update window boundaries based on new center
        self.window.xw_min = novo_centro_x - self.window.largura / 2
        self.window.xw_max = novo_centro_x + self.window.largura / 2
        self.window.yw_min = novo_centro_y - self.window.altura / 2
        self.window.yw_max = novo_centro_y + self.window.altura / 2
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

    def rotate_left(self):
        try:
            angulo_graus = float(self.entry_angulo_window.get()) if self.entry_angulo_window.get() else 10
        except ValueError:
            angulo_graus = 10
            
        self.window.rotacionar(angulo_graus)
        self.redesenhar()
        
    def rotate_right(self):
        try:
            angulo_graus = float(self.entry_angulo_window.get()) if self.entry_angulo_window.get() else 10
        except ValueError:
            angulo_graus = 10
            
        self.window.rotacionar(-angulo_graus)
        self.redesenhar()

    def importar_obj(self):
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo OBJ para importar",
            filetypes=[("OBJ Files", "*.obj"), ("Todos os arquivos", "*.*")]
        )
        if not caminho_arquivo:
            return
        caminho = DescritorOBJ.importar(self.display_file, nome_arquivo=caminho_arquivo)
        self.redesenhar()
        messagebox.showinfo(
            "Importação realizada",
            f"Arquivo OBJ importado com sucesso!\nCaminho: {caminho}"
        )

    def exportar_obj(self):
        caminho = DescritorOBJ.exportar(self.display_file)
        messagebox.showinfo("Exportação realizada",
            f"Arquivo OBJ exportado com sucesso!\nCaminho: {caminho}")
        
    def abrir_popup_transformacoes(self):
            selecao = self.listbox_objetos.curselection()
    


if __name__ == "__main__":
    app = App()
    app.mainloop()