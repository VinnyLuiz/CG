from tkinter import *
from tkinter import ttk, filedialog, messagebox
from popup import Popup, PopupTransformacoes
from displayFile import DisplayFile
from tranformacoes import Window, Viewport, matriz_rotacao
from transformacao3D import Window3D
import numpy as np
from descritorOBJ import DescritorOBJ

class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor de Objetos 2D/3D")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        # Estado
        self.display_file = DisplayFile("objetos_salvos.txt")
        self.objeto_selecionado = None

        # Flags para evitar reentrada/flicker
        self._is_redesenhando = False
        self._redraw_scheduled = False

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

        self.window = Window(-x_window, -y_window, x_window, y_window)

        self.update_idletasks()
        self.max_w_viewport = max(100, self.canvas.winfo_width() - 10)
        self.max_h_viewport = max(100, self.canvas.winfo_height() - 10)
        self.viewport = Viewport(10, 10, self.max_w_viewport, self.max_h_viewport)

        # View Reference Point / camera
        VRP_inicial = [0, 0, 200]
        VPN_inicial = [0, 0, -1]
        VUP_inicial = [0, 1, 0]
        self.window3D = Window3D(VRP_inicial, VPN_inicial, VUP_inicial)

        # status text
        self.text.set(f"Dimensão do Viewport: {self.max_w_viewport}x{self.max_h_viewport}")
        # primeiro desenho
        self.schedule_redraw()

    # ---------------- UI creation ----------------
    def _criar_menu_contexto(self):
        context_menu_frame = ttk.LabelFrame(self, text="Menu de ações", padding=10)
        context_menu_frame.grid(column=0, row=0, rowspan=2, padx=10, pady=5, sticky="ns")
        context_menu_frame.rowconfigure(1, weight=1)
        context_menu_frame.columnconfigure(0, weight=1)

        # Lista de objetos
        ttk.Label(context_menu_frame, text="Objetos").grid(column=0, row=0, sticky="w")
        self.listbox_objetos = Listbox(context_menu_frame, activestyle="underline",
                                       background="white", selectmode="single")
        self.listbox_objetos.grid(column=0, row=1, sticky="nsew", padx=2, pady=2)
        self.listbox_objetos.config(height=12)

        frame_botoes_objetos = ttk.Frame(context_menu_frame)
        frame_botoes_objetos.grid(column=0, row=2, pady=(6,8), sticky="ew")
        ttk.Button(frame_botoes_objetos, text="Adicionar", command=self.adicionar_objeto).grid(column=0, row=0, padx=2)
        ttk.Button(frame_botoes_objetos, text="Transformar", command=lambda: self.transformar_objeto(None)).grid(column=1, row=0, padx=2)
        ttk.Button(frame_botoes_objetos, text="Remover", command=self.remover_objeto).grid(column=2, row=0, padx=2)

        self.listbox_objetos.bind('<<ListboxSelect>>', self.selecionar_objeto)
        self.listbox_objetos.bind('<Button-3>', self.desselecionar_objeto)
        self.listbox_objetos.bind('<Double-1>', self.transformar_objeto)

        # Frame da window (controles)
        labelFrame_window = ttk.LabelFrame(context_menu_frame, text="Window")
        labelFrame_window.grid(column=0, row=3, sticky="ew", pady=(8,6))
        labelFrame_window.columnconfigure(0, weight=1)
        labelFrame_window.columnconfigure(1, weight=1)

        ttk.Label(labelFrame_window, text="Passo:").grid(column=0, row=0, padx=6, sticky="w")
        self.entry_passo = ttk.Entry(labelFrame_window, width=6)
        self.entry_passo.grid(column=1, row=0, padx=(0, 6), sticky="e")

        ttk.Label(labelFrame_window, text="Ângulo:").grid(column=0, row=1, padx=6, sticky="w")
        self.entry_angulo_window = ttk.Entry(labelFrame_window, width=6)
        self.entry_angulo_window.grid(column=1, row=1, padx=(0, 6), pady=4, sticky="e")

        # Movement + Zoom controls
        frame_controls = ttk.Frame(labelFrame_window)
        frame_controls.grid(column=0, row=2, columnspan=2, pady=(8,0), sticky="ew")
        frame_controls.columnconfigure((0,1), weight=1)

        frame_botoes_movimento = ttk.Frame(frame_controls)
        frame_botoes_movimento.grid(column=0, row=0, sticky="w")
        ttk.Button(frame_botoes_movimento, text="↑", width=3, command=self._btn_pan_up).grid(column=1, row=0, padx=2)
        ttk.Button(frame_botoes_movimento, text="↓", width=3, command=self._btn_pan_down).grid(column=1, row=2, padx=2)
        ttk.Button(frame_botoes_movimento, text="←", width=3, command=self._btn_pan_left).grid(column=0, row=1, padx=2)
        ttk.Button(frame_botoes_movimento, text="→", width=3, command=self._btn_pan_right).grid(column=2, row=1, padx=2)
        ttk.Button(frame_botoes_movimento, text="↶", width=3, command=self._btn_rotate_left).grid(column=0, row=0, padx=2)
        ttk.Button(frame_botoes_movimento, text="↷", width=3, command=self._btn_rotate_right).grid(column=2, row=0, padx=2)

        frame_botoes_zoom = ttk.Frame(frame_controls)
        frame_botoes_zoom.grid(column=1, row=0, sticky="w", padx=(6,0))
        ttk.Button(frame_botoes_zoom, text="+", width=3, command=self._btn_zoom_in).grid(column=0, row=0, padx=2)
        ttk.Button(frame_botoes_zoom, text="-", width=3, command=self._btn_zoom_out).grid(column=0, row=1, padx=2)

        # Frame de arquivo (salvar/carregar)
        frame_arquivos = ttk.Frame(context_menu_frame)
        frame_arquivos.grid(column=0, row=7, pady=(8,6))
        ttk.Button(frame_arquivos, text="Salvar Arquivo", width=15, command=self.exportar_obj).grid(column=0, row=0, pady=4, padx=4)
        ttk.Button(frame_arquivos, text="Carregar Arquivo", width=15, command=self.importar_obj).grid(column=1, row=0, pady=4, padx=4)

        # Frame Auxiliar para clipping e projecao
        frame_aux = ttk.Frame(context_menu_frame)
        frame_aux.grid(row=8, padx=5, pady=5, sticky="ew")
        frame_aux.columnconfigure(0, weight=1)
        frame_aux.columnconfigure(1, weight=1)

        # RadioButton Clipping
        self.metodo_clipping = StringVar(value="Cohen-Sutherland")
        frame_clipping = ttk.LabelFrame(frame_aux, text="Clipping de Retas")
        frame_clipping.grid(row=0, column=0, padx=5, sticky="ew")
        ttk.Radiobutton(frame_clipping, text="Cohen-Sutherland", variable=self.metodo_clipping,
                        value="Cohen-Sutherland", command=self.schedule_redraw).pack(anchor="w", padx=6, pady=2)
        ttk.Radiobutton(frame_clipping, text="Nicholl-Lee-Nicholl", variable=self.metodo_clipping,
                        value="Nicholl-Lee-Nicholl", command=self.schedule_redraw).pack(anchor="w", padx=6, pady=2)

        # Projection frame: two subframes (proj controls and COP) to avoid layout conflicts
        self.tipo_proj = StringVar(value="Paralela")
        frame_proj = ttk.LabelFrame(frame_aux, text="Tipo de Projeção")
        frame_proj.grid(row=0, column=1, padx=5, sticky="ew")
        frame_proj.columnconfigure(0, weight=1)

        self.proj_ctrl_frame = ttk.Frame(frame_proj)
        self.proj_ctrl_frame.grid(row=0, column=0, sticky="ew", padx=6, pady=(6,0))
        self.proj_ctrl_frame.columnconfigure(0, weight=1)

        ttk.Radiobutton(self.proj_ctrl_frame, text="Paralela", variable=self.tipo_proj, value="Paralela",
                        command=self._btn_mudar_projecao).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(self.proj_ctrl_frame, text="Perspectiva", variable=self.tipo_proj, value="Perspectiva",
                        command=self._btn_mudar_projecao).grid(row=1, column=0, sticky="w")

        self.label_distancia = ttk.Label(self.proj_ctrl_frame, text="Distância: 0")
        self.slider_distancia = ttk.Scale(self.proj_ctrl_frame, from_=100, to=500, orient=HORIZONTAL, command=self.atualizar_distancia_camera)
        self.label_distancia.grid_forget()
        self.slider_distancia.grid_forget()

        self.cop_frame = ttk.Frame(frame_proj)
        self.cop_frame.grid(row=1, column=0, sticky="ew", padx=6, pady=(8,6))
        self.cop_frame.columnconfigure((1,3,5), weight=1)

        ttk.Label(self.cop_frame, text="COP").grid(row=0, column=0, sticky="w", pady=(0,6))
        inner_frame_proj = ttk.Frame(self.cop_frame)
        inner_frame_proj.grid(row=1, column=0, columnspan=6, sticky="ew")
        label_xcop = ttk.Label(inner_frame_proj, text="X:")
        label_ycop = ttk.Label(inner_frame_proj, text="Y:")
        label_zcop = ttk.Label(inner_frame_proj, text="Z:")
        self.entry_xcop = ttk.Entry(inner_frame_proj, width=6)
        self.entry_ycop = ttk.Entry(inner_frame_proj, width=6)
        self.entry_zcop = ttk.Entry(inner_frame_proj, width=6)
        label_xcop.grid(row=0, column=0); self.entry_xcop.grid(row=0, column=1, padx=2)
        label_ycop.grid(row=0, column=2); self.entry_ycop.grid(row=0, column=3, padx=2)
        label_zcop.grid(row=0, column=4); self.entry_zcop.grid(row=0, column=5, padx=2)
        ttk.Button(self.cop_frame, text="Atualizar COP", command=self._btn_atualizar_COP).grid(row=2, column=0, columnspan=6, pady=6, sticky="ew")

    def _criar_canvas(self):
        self.canvas = Canvas(self, bg="white")
        self.canvas.grid(column=1, row=0, columnspan=2, sticky="nsew", padx=(0, 10), pady=(15, 0))

    def _criar_status_bar(self):
        self.text = StringVar()
        transcript_label = Label(self, textvariable=self.text, relief="sunken", anchor="nw", height=4)
        transcript_label.grid(column=1, row=1, sticky="nsew", padx=(0, 10), pady=10)

    def redesenhar(self):
        if getattr(self, "_is_redesenhando", False):
            return
        self._is_redesenhando = True
        try:
            try:
                self.canvas.delete("all")
            except Exception:
                pass
            try:
                self.listbox_objetos.delete(0, END)
            except Exception:
                pass

            try:
                w = max(100, self.canvas.winfo_width() - 10)
                h = max(100, self.canvas.winfo_height() - 10)
                if w != getattr(self, "max_w_viewport", None) or h != getattr(self, "max_h_viewport", None):
                    self.max_w_viewport = w
                    self.max_h_viewport = h
                    try:
                        self.viewport = Viewport(10, 10, self.max_w_viewport, self.max_h_viewport)
                    except Exception:
                        pass
                self.text.set(f"Dimensão do Viewport: {self.max_w_viewport}x{self.max_h_viewport}\nObjetos: {len(self.display_file.objetos)}")
                self.canvas.create_rectangle(10, 10, self.max_w_viewport, self.max_h_viewport, outline="red")
            except Exception:
                pass

            try:
                self.display_file.atualizar_scn(self.window, self.window3D)
            except Exception as e:
                print("[ERROR] atualizar_scn falhou:", e)

            # desenha objetos e popula listbox
            for obj in self.display_file.objetos:
                try:
                    self.listbox_objetos.insert(END, obj.nome)
                except Exception:
                    pass

                try:
                    if hasattr(obj, "desenhar_perspectiva"):
                        try:
                            obj.desenhar_perspectiva(self.canvas, self.viewport,
                                                     (self.window3D.COP[0], self.window3D.COP[1], self.window3D.COP[2]),
                                                     (0,0,0),
                                                     getattr(self.window3D, "distancia", 100),
                                                     self.metodo_clipping.get())
                        except TypeError:
                            try:
                                obj.desenhar_perspectiva(self.canvas, self.viewport, self.window3D.COP, (0,0,0), getattr(self.window3D, "distancia", 100), self.metodo_clipping.get())
                            except Exception:
                                pass
                    else:
                        try:
                            obj.desenhar(self.canvas, self.window, self.viewport, self.metodo_clipping.get())
                        except TypeError:
                            obj.desenhar(self.canvas, self.window, self.viewport)
                except Exception as e:
                    print(f"[WARN] Falha ao desenhar '{getattr(obj,'nome','?')}': {e}")

            try:
                self.listbox_objetos.update_idletasks()
            except Exception:
                pass
        finally:
            self._is_redesenhando = False
            self._redraw_scheduled = False

    def schedule_redraw(self):
        if getattr(self, "_redraw_scheduled", False):
            return
        self._redraw_scheduled = True
        try:
            self.after_idle(self.redesenhar)
        except Exception:
            self.after(10, self.redesenhar)

    def _btn_zoom_in(self): self.zoom(0.8); self.schedule_redraw()
    def _btn_zoom_out(self): self.zoom(1.2); self.schedule_redraw()
    def _btn_pan_up(self): self.pan(dy_percent=1); self.schedule_redraw()
    def _btn_pan_down(self): self.pan(dy_percent=-1); self.schedule_redraw()
    def _btn_pan_left(self): self.pan(dx_percent=-1); self.schedule_redraw()
    def _btn_pan_right(self): self.pan(dx_percent=1); self.schedule_redraw()
    def _btn_rotate_left(self): self.rotate_left(); self.schedule_redraw()
    def _btn_rotate_right(self): self.rotate_right(); self.schedule_redraw()
    def _btn_mudar_projecao(self): self.mudar_projecao(); self.schedule_redraw()
    def _btn_atualizar_COP(self): self.atualizar_COP(); self.schedule_redraw()

    # ---------------- Object operations ----------------
    def adicionar_objeto(self):
        popup = Popup(self, display_file=self.display_file)
        self.wait_window(popup)
        self.schedule_redraw()

    def remover_objeto(self):
        selecao = self.listbox_objetos.curselection()
        if selecao:
            index = selecao[0]
            objeto = self.listbox_objetos.get(index)
            self.display_file.remover(objeto)
            self.schedule_redraw()

    def transformar_objeto(self, event):
        selecao = self.listbox_objetos.curselection()
        if not selecao:
            return
        index = selecao[0]
        nome_objeto = self.listbox_objetos.get(index)
        self.objeto_selecionado = self.display_file.get_objeto(nome_objeto)
        if not self.objeto_selecionado:
            return
        tempW = PopupTransformacoes(self, self.objeto_selecionado, self.schedule_redraw)
        self.wait_window(tempW)
        self.schedule_redraw()

    def selecionar_objeto(self, event):
        selecao = self.listbox_objetos.curselection()
        if selecao:
            index = selecao[0]
            nome_objeto = self.listbox_objetos.get(index)
            self.objeto_selecionado = self.display_file.get_objeto(nome_objeto)
            self.schedule_redraw()
            if index < self.listbox_objetos.size():
                self.listbox_objetos.select_set(index)

    def desselecionar_objeto(self, event=None):
        self.objeto_selecionado = None
        self.schedule_redraw()

    # ---------------- View controls (zoom, pan, rotate) ----------------
    def zoom_in(self): self.zoom(0.8); self.schedule_redraw()
    def zoom_out(self): self.zoom(1.2); self.schedule_redraw()

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

    def pan(self, dx_percent=0, dy_percent=0):
        try:
            passo_percent = float(self.entry_passo.get()) if self.entry_passo.get() else 10
        except ValueError:
            passo_percent = 10

        passo_x = (dx_percent * passo_percent / 100) * self.window.largura
        passo_y = (dy_percent * passo_percent / 100) * self.window.altura

        vup_window = np.array([passo_x, passo_y, 1])
        R = matriz_rotacao(self.window.angulo_rotacao)
        vup_mundo = R @ vup_window
        novo_x, novo_y = vup_mundo[0], vup_mundo[1]

        centro_x_atual, centro_y_atual = self.window.centro()
        novo_centro_x = centro_x_atual + novo_x
        novo_centro_y = centro_y_atual + novo_y

        self.window.xw_min = novo_centro_x - self.window.largura / 2
        self.window.xw_max = novo_centro_x + self.window.largura / 2
        self.window.yw_min = novo_centro_y - self.window.altura / 2
        self.window.yw_max = novo_centro_y + self.window.altura / 2
        self.window.largura = self.window.xw_max - self.window.xw_min
        self.window.altura = self.window.yw_max - self.window.yw_min

    def pan_up(self): self.pan(dy_percent=1); self.schedule_redraw()
    def pan_down(self): self.pan(dy_percent=-1); self.schedule_redraw()
    def pan_left(self): self.pan(dx_percent=-1); self.schedule_redraw()
    def pan_right(self): self.pan(dx_percent=1); self.schedule_redraw()

    def rotate_left(self):
        try:
            angulo_graus = float(self.entry_angulo_window.get()) if self.entry_angulo_window.get() else 10
        except ValueError:
            angulo_graus = 10
        self.window.rotacionar(angulo_graus)

    def rotate_right(self):
        try:
            angulo_graus = float(self.entry_angulo_window.get()) if self.entry_angulo_window.get() else 10
        except ValueError:
            angulo_graus = 10
        self.window.rotacionar(-angulo_graus)

    def _btn_rotate_left(self): self.rotate_left(); self.schedule_redraw()
    def _btn_rotate_right(self): self.rotate_right(); self.schedule_redraw()

    # ---------------- Import / Export ----------------
    def importar_obj(self):
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo OBJ para importar",
            filetypes=[("OBJ Files", "*.obj"), ("Todos os arquivos", "*.*")]
        )
        if not caminho_arquivo:
            return
        try:
            caminho = DescritorOBJ.importar(self.display_file, nome_arquivo=caminho_arquivo)
        except Exception as e:
            messagebox.showerror("Erro na importação", f"Falha ao importar: {e}")
            print("[ERROR] DescritorOBJ.importar levantou exceção:", e)
            return

        try:
            for o in self.display_file.objetos:
                if o.__class__.__name__.startswith("Superficie"):
                    surf = o
                    try:
                        if hasattr(surf, "n_t"):
                            surf.n_t = max(8, getattr(surf, "n_t", 12))
                        if hasattr(surf, "n_s"):
                            surf.n_s = max(8, getattr(surf, "n_s", 12))
                        if hasattr(surf, "gerar_curvas_fwd"):
                            surf.gerar_curvas_fwd()
                    except Exception as e:
                        print("[WARN] Falha ao gerar p_calculados da superfície:", e)
                    pts = []
                    if getattr(surf, "lista_matrizes", None):
                        for patch in surf.lista_matrizes:
                            for row in patch:
                                for p in row:
                                    pts.append(p)
                    elif getattr(surf, "p_calculados", None):
                        def _iter(objc):
                            if objc is None:
                                return
                            if isinstance(objc, (list, tuple)):
                                for sub in objc:
                                    yield from _iter(sub)
                            else:
                                if hasattr(objc, "x") and hasattr(objc, "y") and hasattr(objc, "z"):
                                    yield objc
                        for p in _iter(surf.p_calculados):
                            pts.append(p)
                    if pts:
                        xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
                        cx, cy, cz = sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs)
                        span = max(max(xs)-min(xs), max(ys)-min(ys), 1.0)
                        offset_z = max(10.0, span * 1.5)
                        try:
                            self.window3D.COP[0] = cx
                            self.window3D.COP[1] = cy
                            self.window3D.COP[2] = cz + offset_z
                            if hasattr(self.window3D, "distancia"):
                                self.window3D.distancia = max(1.0, offset_z * 1.0)
                        except Exception as e:
                            print("[WARN] Não foi possível atualizar window3D.COP automaticamente:", e)
                    break
        except Exception as e:
            print("[WARN] Falha no pós-import auto-center:", e)

        self.schedule_redraw()
        messagebox.showinfo(
            "Importação realizada",
            f"Arquivo OBJ importado com sucesso!\nCaminho: {caminho}"
        )

    def exportar_obj(self):
        try:
            caminho = DescritorOBJ.exportar(self.display_file)
            messagebox.showinfo("Exportação realizada",
                f"Arquivo OBJ exportado com sucesso!\nCaminho: {caminho}")
        except Exception as e:
            messagebox.showerror("Erro na exportação", f"Falha ao exportar: {e}")
            print("[ERROR] exportar_obj failed:", e)

    def mudar_projecao(self):
        tipo = self.tipo_proj.get().lower()
        if tipo == "perspectiva":
            try:
                self.label_distancia.grid(row=2, column=0, sticky="w", pady=(6,0))
                self.slider_distancia.grid(row=3, column=0, sticky="ew", pady=(2,6))
                self.label_distancia.lift()
                self.slider_distancia.lift()
            except Exception:
                pass
        else:
            try:
                self.label_distancia.grid_forget()
                self.slider_distancia.grid_forget()
            except Exception:
                pass

        try:
            self.window3D.mudar_projecao(tipo)
        except Exception:
            pass
        self.schedule_redraw()

    def atualizar_distancia_camera(self, valor):
        try:
            distancia = float(valor)
            self.window3D.distancia = distancia
            self.label_distancia.config(text=f"Distância: {distancia:.0f}")
            self.schedule_redraw()
        except Exception:
            pass

    def atualizar_COP(self):
        try:
            x = float(self.entry_xcop.get()) if self.entry_xcop.get() != "" else 0.0
            y = float(self.entry_ycop.get()) if self.entry_ycop.get() != "" else 0.0
            z = float(self.entry_zcop.get()) if self.entry_zcop.get() != "" else 0.0
            self.window3D.COP[0] = x
            self.window3D.COP[1] = y
            self.window3D.COP[2] = z
            self.schedule_redraw()
        except Exception as e:
            messagebox.showerror("Erro COP", f"Valor inválido: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()