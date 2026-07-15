import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import os

from src.lexer.lexer import obtener_lexer
from src.parser.parser import obtener_parser
from src.semantic.semantic import SemanticAnalyzer
from src.intermediate.quad_gen import QuadrupleGenerator
from src.intermediate.optimizer import Optimizer
from src.codegen.cpp_gen import CppGenerator

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
        self.editor = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, font=("Courier New", 12))
        self.editor.pack(fill=tk.BOTH, expand=True, pady=5)
        
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

    def limpiar_ui(self):
        self.consola.delete(1.0, tk.END)
        self.txt_codigo_final.delete(1.0, tk.END)
        for row in self.tree_simbolos.get_children():
            self.tree_simbolos.delete(row)
        for row in self.tree_quads.get_children():
            self.tree_quads.delete(row)

    def compilar(self):
        self.limpiar_ui()
        codigo_fuente = self.editor.get(1.0, tk.END).strip()
        if not codigo_fuente:
            self.log("Error: No hay código para compilar.")
            return

        self.log("--- Iniciando Compilación ---")

        # 1. Lexer y Parser
        lexer = obtener_lexer()
        parser = obtener_parser()
        lexer.lineno = 1
        
        try:
            ast = parser.parse(codigo_fuente, lexer=lexer)
        except Exception as e:
            self.log(f"Error Fatal durante Análisis Sintáctico.")
            return

        if not ast:
            self.log("Proceso abortado por errores sintácticos (Revisar consola del sistema).")
            return
        
        self.log("[OK] Análisis Léxico y Sintáctico.")

        # 2. Análisis Semántico
        semantic = SemanticAnalyzer()
        if not semantic.analyze(ast):
            self.log("Errores Semánticos Encontrados:")
            for err in semantic.errores:
                self.log("  -> " + err)
            self.log("Proceso abortado.")
            return
        
        self.log("[OK] Análisis Semántico.")
        
        # Mostrar Tabla de Símbolos
        simbolos = semantic.symbol_table.get_all()
        for nombre, info in simbolos.items():
            self.tree_simbolos.insert("", tk.END, values=(nombre, info['tipo'], info['linea']))

        # 3. Código Intermedio
        quad_gen = QuadrupleGenerator()
        cuadruplos = quad_gen.generate(ast)
        self.log(f"[OK] Código Intermedio generado ({len(cuadruplos)} cuádruplos).")

        # 4. Optimización
        optimizer = Optimizer()
        optimizados = optimizer.optimize(cuadruplos)
        self.log(f"[OK] Optimización aplicada.")

        # Mostrar Cuádruplos
        for q in optimizados:
            self.tree_quads.insert("", tk.END, values=(q.operador, q.arg1, q.arg2, q.resultado))

        # 5. Código Final
        cpp_gen = CppGenerator()
        codigo_cpp = cpp_gen.generate(optimizados, semantic.symbol_table)
        self.txt_codigo_final.insert(tk.END, codigo_cpp)
        self.log("[OK] Código C++ Generado con éxito.")
        
        # Cambiar a la pestaña de C++ para mostrar el resultado
        self.notebook.select(self.tab_final)