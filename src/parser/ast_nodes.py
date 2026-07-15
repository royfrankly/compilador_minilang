import ply.yacc as yacc
# Importamos la lista de tokens del analizador léxico (requisito de PLY)
from src.lexer.lexer import tokens
# Importamos nuestras clases de nodos AST
from src.parser.ast_nodes import *

# Precedencia de operadores para resolver ambigüedades matemáticas (Criterio 9)
# Los operadores más abajo tienen mayor precedencia (se evalúan primero)
precedence = (
    ('left', 'OP_Y', 'OP_O'),
    ('left', 'OP_IGUALDAD', 'OP_DIFERENTE', 'OP_MAYOR', 'OP_MENOR'),
    ('left', 'OP_SUMA', 'OP_RESTA'),
    ('left', 'OP_MULT', 'OP_DIV'),
)

# Regla principal: Un programa empieza con INICIO, tiene instrucciones y termina con FIN
def p_programa(p):
    '''programa : INICIO lista_instrucciones FIN'''
    p[0] = Programa(p[2])

# Una lista de instrucciones puede ser una o varias instrucciones seguidas
def p_lista_instrucciones(p):
    '''lista_instrucciones : lista_instrucciones instruccion
                           | instruccion'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]] # Agrega la nueva instrucción a la lista
    else:
        p[0] = [p[1]]        # Inicia una nueva lista

# Una instrucción puede ser una declaración, asignación, ciclo, condicional o E/S
def p_instruccion(p):
    '''instruccion : declaracion
                   | asignacion
                   | condicional
                   | ciclo
                   | lectura
                   | escritura'''
    p[0] = p[1]

# Regla para declarar variables: (ej. ENTERO x;)
def p_declaracion(p):
    '''declaracion : tipo_dato ID PUNTO_COMA'''
    p[0] = Declaracion(p[1], p[2])

def p_tipo_dato(p):
    '''tipo_dato : ENTERO
                 | REAL
                 | CADENA
                 | BOOLEANO'''
    p[0] = p[1]

# Regla para asignación: (ej. x = 5 + y;)
def p_asignacion(p):
    '''asignacion : ID OP_ASIG expresion PUNTO_COMA'''
    p[0] = Asignacion(p[1], p[3])

# Regla para operaciones matemáticas y lógicas
def p_expresion_operacion(p):
    '''expresion : expresion OP_SUMA expresion
                 | expresion OP_RESTA expresion
                 | expresion OP_MULT expresion
                 | expresion OP_DIV expresion
                 | expresion OP_MAYOR expresion
                 | expresion OP_MENOR expresion
                 | expresion OP_IGUALDAD expresion
                 | expresion OP_DIFERENTE expresion
                 | expresion OP_Y expresion
                 | expresion OP_O expresion'''
    p[0] = OperacionBinaria(p[1], p[2], p[3])

# Expresiones entre paréntesis para alterar precedencia
def p_expresion_agrupacion(p):
    '''expresion : PAR_IZQ expresion PAR_DER'''
    p[0] = p[2]

# Valores literales y variables que pueden ser parte de una expresión
def p_expresion_valores(p):
    '''expresion : NUM_ENTERO
                 | NUM_REAL
                 | CADENA_LITERAL
                 | VERDADERO
                 | FALSO'''
    p[0] = Numero(p[1]) # Agrupamos todos bajo "Numero" o valor crudo

def p_expresion_id(p):
    '''expresion : ID'''
    p[0] = Identificador(p[1])

# Regla para la condición SI...SINO
def p_condicional(p):
    '''condicional : SI PAR_IZQ expresion PAR_DER lista_instrucciones FIN_SI
                   | SI PAR_IZQ expresion PAR_DER lista_instrucciones SINO lista_instrucciones FIN_SI'''
    if len(p) == 7: # Sin bloque SINO
        p[0] = CondicionalSi(p[3], p[5])
    else:           # Con bloque SINO
        p[0] = CondicionalSi(p[3], p[5], p[7])

# Regla para el ciclo MIENTRAS
def p_ciclo(p):
    '''ciclo : MIENTRAS PAR_IZQ expresion PAR_DER lista_instrucciones FIN_MIENTRAS'''
    p[0] = CicloMientras(p[3], p[5])

# Reglas para Entrada y Salida
def p_lectura(p):
    '''lectura : LEER ID PUNTO_COMA'''
    p[0] = Leer(p[2])

def p_escritura(p):
    '''escritura : ESCRIBIR expresion PUNTO_COMA'''
    p[0] = Escribir(p[2])

# Función para manejar errores de sintaxis
def p_error(p):
    if p:
        print(f"Error Sintáctico: Token inesperado '{p.value}' cerca de la línea {p.lineno}")
    else:
        print("Error Sintáctico: Fin de archivo inesperado")

# Instanciación del parser
def obtener_parser():
    return yacc.yacc()