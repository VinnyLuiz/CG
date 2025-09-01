from tkinter import *
from tkinter import ttk

class PopupTransformacao(Toplevel):
    def __init__(self, master, objeto):
        super().__init__(master)
        self.title("Transformar objeto")
        self.objeto = objeto
        self.result = None

        # Dropdown de tipo de transformação
        ttk.Label(self, text="Transformação:").grid(row=0, column=0)
        self.combo = ttk.Combobox(self, values=["Translação", "Escala", "Rotação"], state="readonly")
        self.combo.grid(row=0, column=1)
        self.combo.current(0)
        self.combo.bind("<<ComboboxSelected>>", self.atualizar_campos)

        # Labels e Entradas para os parâmetros
        self.labels = []
        self.entries = []

        # Inicializa campos para translação
        self.parametros = {
            "Translação": [("dx", 0), ("dy", 0)],
            "Escala": [("sx", 1), ("sy", 1), ("Centro X", ""), ("Centro Y", "")],
            "Rotação": [("Ângulo (graus)", 0), ("Centro X", ""), ("Centro Y", "")]
        }
        self.atualizar_campos()  # Mostra campos iniciais

        ttk.Button(self, text="Aplicar", command=self.aplicar).grid(row=10, column=1, pady=10)

    def atualizar_campos(self, event=None):
        # Remove campos antigos
        for label in self.labels:
            label.grid_forget()
        for entry in self.entries:
            entry.grid_forget()
        self.labels = []
        self.entries = []

        tipo = self.combo.get()
        params = self.parametros[tipo]
        for i, (lbl, default) in enumerate(params):
            label = ttk.Label(self, text=lbl + ":")
            label.grid(row=i+1, column=0)
            entry = ttk.Entry(self)
            entry.grid(row=i+1, column=1)
            if default != "":
                entry.insert(0, str(default))
            self.labels.append(label)
            self.entries.append(entry)

    def aplicar(self):
        tipo = self.combo.get()
        valores = []
        for entry in self.entries:
            val = entry.get()
            try:
                val = float(val)
            except ValueError:
                val = None
            valores.append(val)
        self.result = (tipo, valores)
        self.destroy()