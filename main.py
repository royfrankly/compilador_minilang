import os
import sys

from src.lexer.lexer import obtener_lexer
from src.parser.parser import obtener_parser
from src.semantic.semantic import SemanticAnalyzer
from src.intermediate.quad_gen import QuadrupleGenerator
from src.intermediate.optimizer import Optimizer
from src.codegen.cpp_gen import CppGenerator

def compilar_archivo(ruta_archivo):
    print(f"--- Compilando: {ruta_archivo} ---")
    
    if not os.path.exists(ruta_archivo):
        print(f"Error: No se encontró el archivo {ruta_archivo}")
        return

    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        codigo_fuente = f.read()

    # 1. Análisis Léxico y Sintáctico
    print("[1/6] Análisis Léxico y Sintáctico...")
    lexer = obtener_lexer()
    parser = obtener_parser()
    
    # Reiniciar contadores de línea por si se compilan varios archivos
    lexer.lineno = 1 
    
    ast = parser.parse(codigo_fuente, lexer=lexer)
    
    if not ast:
        print("Compilación abortada: Errores sintácticos detectados.\n")
        return

    # 2. Análisis Semántico
    print("[2/6] Análisis Semántico...")
    semantic_analyzer = SemanticAnalyzer()
    es_valido = semantic_analyzer.analyze(ast)
    
    if not es_valido:
        print("Errores Semánticos encontrados:")
        for error in semantic_analyzer.errores:
            print(f"  - {error}")
        print("Compilación abortada.\n")
        return

    # 3. Código Intermedio
    print("[3/6] Generando Código Intermedio...")
    quad_gen = QuadrupleGenerator()
    cuadruplos = quad_gen.generate(ast)
    
    # 4. Optimización
    print("[4/6] Optimizando Código Intermedio...")
    optimizer = Optimizer()
    cuadruplos_optimos = optimizer.optimize(cuadruplos)

    # 5. Generación de Código Final
    print("[5/6] Generando Código C++...")
    cpp_gen = CppGenerator()
    codigo_cpp = cpp_gen.generate(cuadruplos_optimos, semantic_analyzer.symbol_table)

    # 6. Guardar archivo final
    print("[6/6] Guardando archivo ejecutable...")
    nombre_salida = ruta_archivo.replace('.txt', '.cpp')
    with open(nombre_salida, 'w', encoding='utf-8') as f:
        f.write(codigo_cpp)
    
    print(f"¡Compilación Exitosa! Código generado en: {nombre_salida}\n")

if __name__ == '__main__':
    # Si se pasa un archivo por argumento, compilar ese
    if len(sys.argv) > 1:
        compilar_archivo(sys.argv[1])
    else:
        # Por defecto, compilar la prueba correcta
        compilar_archivo('tests/prueba_correcta.txt')