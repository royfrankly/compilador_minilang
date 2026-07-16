import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import os

from src.lexer.lexer import obtener_lexer
from src.parser.parser import obtener_parser
from src.semantic.semantic import SemanticAnalyzer
from src.intermediate.quad_gen import QuadrupleGenerator
from src.intermediate.optimizer import Optimizer
from src.codegen.cpp_gen import CppGenerator

class NumerosDeLinea(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.editor = None

    def conectar(self, editor):
        self.editor = editor

    def redibujar(self, *args):
        if not self.editor: return
        self.delete("all")
        i = self.editor.index("@0,0")
        while True:
            dline = self.editor.dlineinfo(i)
            if dline is None: 
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            # Alineación y fuente estilo VS Code
            self.create_text(30, y, anchor="ne", text=linenum, font=("Consolas", 11), fill="#888888")
            i = self.editor.index("%s+1line" % i)

class CompiladorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniLang Compiler IDE")
        self.root.geometry("1200x800")
        
        self.setup_ui()

    def setup_ui(self):
        # Frame Principal
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Izquierda: Editor de Código
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Editor de Código (MiniLang):").pack(anchor=tk.W)
        
        # --- NUEVA CAJA DEL EDITOR (Números + Editor) ---
        caja_editor = ttk.Frame(left_frame)
        caja_editor.pack(fill=tk.BOTH, expand=True, pady=5)

        # Panel de números (Izquierda)
        self.numeros = NumerosDeLinea(caja_editor, width=35, bg='#f3f3f3', highlightthickness=0)
        self.numeros.pack(side=tk.LEFT, fill=tk.Y)

        # Editor de texto (Derecha)
        self.editor = scrolledtext.ScrolledText(caja_editor, wrap=tk.WORD, font=("Consolas", 11), undo=True)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Conectar números con el editor
        self.numeros.conectar(self.editor)

        # Eventos para actualizar los números automáticamente
        eventos = ["<KeyRelease>", "<MouseWheel>", "<Configure>", "<Return>", "<BackSpace>", "<B1-Motion>"]
        for evento in eventos:
            self.editor.bind(evento, self.numeros.redibujar)
        # -----------------------------------------------
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Cargar Archivo", command=self.cargar_archivo).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Compilar", command=self.compilar).pack(side=tk.LEFT, padx=5)

        # Derecha: Pestañas de resultados
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Pestañas
        self.tab_consola = ttk.Frame(self.notebook)
        self.tab_simbolos = ttk.Frame(self.notebook)
        self.tab_intermedio = ttk.Frame(self.notebook)
        self.tab_final = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_consola, text="Consola de Salida")
        self.notebook.add(self.tab_simbolos, text="Tabla de Símbolos")
        self.notebook.add(self.tab_intermedio, text="Código Intermedio")
        self.notebook.add(self.tab_final, text="Código Final (C++)")

        # Contenido Consola
        self.consola = scrolledtext.ScrolledText(self.tab_consola, bg="black", fg="white", font=("Consolas", 11))
        self.consola.pack(fill=tk.BOTH, expand=True)

        # Contenido Tabla Símbolos
        cols_simbolos = ("Nombre", "Tipo", "Línea")
        self.tree_simbolos = ttk.Treeview(self.tab_simbolos, columns=cols_simbolos, show="headings")
        for col in cols_simbolos:
            self.tree_simbolos.heading(col, text=col)
        self.tree_simbolos.pack(fill=tk.BOTH, expand=True)

        # Contenido Código Intermedio
        cols_quads = ("Operador", "Arg1", "Arg2", "Resultado")
        self.tree_quads = ttk.Treeview(self.tab_intermedio, columns=cols_quads, show="headings")
        for col in cols_quads:
            self.tree_quads.heading(col, text=col)
        self.tree_quads.pack(fill=tk.BOTH, expand=True)

        # Contenido Código Final
        self.txt_codigo_final = scrolledtext.ScrolledText(self.tab_final, font=("Courier New", 12))
        self.txt_codigo_final.pack(fill=tk.BOTH, expand=True)

    def log(self, mensaje):
        self.consola.insert(tk.END, mensaje + "\n")
        self.consola.see(tk.END)

    def cargar_archivo(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filepath:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.editor.delete(1.0, tk.END)
                self.editor.insert(tk.END, f.read())
            self.log(f"Archivo cargado: {filepath}")
            # Forzamos el redibujado de los números al cargar un archivo nuevo
            self.numeros.redibujar()

    def limpiar_ui(self):
        self.consola.delete(1.0, tk.END)
        self.txt_codigo_final.delete(1.0, tk.END)
        for row in self.tree_simbolos.get_children():
            self.tree_simbolos.delete(row)
        for row in self.tree_quads.get_children():
            self.tree_quads.delete(row)

    def compilar(self):
        self.limpiar_ui()
        # Forzar a la UI a limpiar la pantalla inmediatamente
        self.consola.update() 
        
        codigo_fuente = self.editor.get(1.0, tk.END).strip()
        if not codigo_fuente:
            self.log("Error: No hay código para compilar.")
            return

        self.log("--- Iniciando Compilación ---")
        self.consola.update() # Refrescar UI

        # 1. Lexer y Parser
        lexer = obtener_lexer()
        parser = obtener_parser()
        lexer.lineno = 1
        
        try:
            ast = parser.parse(codigo_fuente, lexer=lexer)
        except Exception as e:
            error_msg = str(e)
            # Detectar si es un error de programación en Python o un error del usuario en MiniLang
            if "is not defined" in error_msg or "object has no attribute" in error_msg:
                self.log("❌ Error INTERNO del Compilador (Python):")
                self.log(f"-> {error_msg}")
                self.log("💡 Sugerencia: Te falta importar una clase (ej. 'Declaracion') en parser.py.")
            else:
                # Si es un error de sintaxis que nosotros lanzamos, se mostrará bonito con su línea
                self.log("❌ Se encontró un error en el código:")
                self.log(error_msg)
            
            self.log("Proceso abortado.")
            self.consola.update() # Refrescar UI antes de salir
            return

        if not ast:
            self.log("❌ Error de Sintaxis: El compilador no pudo construir el árbol (AST).")
            self.log("Sugerencia: Revisa la estructura (¿Falta 'INICIO', 'FIN', o punto y coma?).")
            self.log("Proceso abortado.")
            self.consola.update()
            return
        
        self.log("[OK] Análisis Léxico y Sintáctico.")
        self.consola.update()

        # 2. Análisis Semántico
        semantic = SemanticAnalyzer()
        if not semantic.analyze(ast):
            self.log("❌ Errores Semánticos Encontrados:")
            for err in semantic.errores:
                self.log("  -> " + err)
            self.log("Proceso abortado.")
            self.consola.update()
            return
        
        self.log("[OK] Análisis Semántico.")
        self.consola.update()
        
        # Mostrar Tabla de Símbolos
        simbolos = semantic.symbol_table.get_all()
        for nombre, info in simbolos.items():
            self.tree_simbolos.insert("", tk.END, values=(nombre, info['tipo'], info['linea']))
        self.tree_simbolos.update() # Forzar actualización de la tabla visualmente

        # 3. Código Intermedio
        quad_gen = QuadrupleGenerator()
        cuadruplos = quad_gen.generate(ast)
        self.log(f"[OK] Código Intermedio generado ({len(cuadruplos)} cuádruplos).")
        self.consola.update()

        # 4. Optimización
        optimizer = Optimizer()
        optimizados = optimizer.optimize(cuadruplos)
        self.log(f"[OK] Optimización aplicada.")
        self.consola.update()

        # Mostrar Cuádruplos
        for q in optimizados:
            self.tree_quads.insert("", tk.END, values=(q.operador, q.arg1, q.arg2, q.resultado))
        self.tree_quads.update() # Forzar actualización visual

        # 5. Código Final
        cpp_gen = CppGenerator()
        codigo_cpp = cpp_gen.generate(optimizados, semantic.symbol_table)
        self.txt_codigo_final.insert(tk.END, codigo_cpp)
        self.log("[OK] Código C++ Generado con éxito.")
        self.txt_codigo_final.update() # Forzar actualización visual
        
        # Cambiar a la pestaña de C++ para mostrar el resultado
        self.notebook.select(self.tab_final)