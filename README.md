# MiniLang Compiler IDE

MiniLang Compiler IDE es un compilador didáctico para un lenguaje de programación simple, diseñado para enseñanza e ingeniería de compiladores. El proyecto ofrece una interfaz gráfica de usuario (Tkinter) y un pipeline completo de compilación en Python, desde el análisis léxico hasta la generación de código en C++.

## Características

- Análisis Léxico (Tokenización) con PLY
- Análisis Sintáctico con PLY y construcción de un AST
- Análisis Semántico con Tabla de Símbolos y validación de tipos
- Generación de Código Intermedio en forma de cuádruplos
- Optimización mediante plegado de constantes
- Generación de código final en C++ compatible con `iostream`
- Interfaz gráfica para editar y compilar código MiniLang

## Requisitos Previos

- Python 3.x
- Biblioteca `ply`

## Instalación y Ejecución

```bash
cd c:\Users\ASUS\Desktop\clones\compilador_minilang
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run_gui.py
```

También puedes compilar un archivo directamente desde terminal:

```bash
python main.py tests/prueba_correcta.txt
```

## Estructura del Proyecto

```
compilador_minilang/
├─ main.py
├─ run_gui.py
├─ requirements.txt
├─ src/
│  ├─ lexer/
│  │  └─ lexer.py
│  ├─ parser/
│  │  ├─ ast_nodes.py
│  │  └─ parser.py
│  ├─ semantic/
│  │  ├─ semantic.py
│  │  └─ symbol_table.py
│  ├─ intermediate/
│  │  ├─ quad_gen.py
│  │  └─ optimizer.py
│  ├─ codegen/
│  │  └─ cpp_gen.py
│  └─ ui/
│     └─ app_window.py
└─ tests/
```

### Carpetas principales

- `src/lexer`: contiene el módulo de tokenización de MiniLang.
- `src/parser`: define la gramática del lenguaje y construye el AST.
- `src/semantic`: implementa la validación semántica, la Tabla de Símbolos y la comprobación de tipos.
- `src/intermediate`: genera cuádruplos (código intermedio) y aplica optimización de constantes.
- `src/codegen`: traduce los cuádruplos optimizados a código C++.
- `src/ui`: implementa la interfaz gráfica de usuario con Tkinter.
- `tests`: incluye casos de prueba de compilación.
