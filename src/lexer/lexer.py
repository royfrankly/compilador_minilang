import ply.lex as lex

class ErrorLexicoMiniLang(Exception):
    pass

# Diccionario de palabras reservadas (Case-sensitive / Mayúsculas obligatorias en MiniLang)
reservadas = {
    'INICIO': 'INICIO',
    'FIN': 'FIN',
    'ENTERO': 'ENTERO',
    'REAL': 'REAL',
    'CADENA': 'CADENA',
    'BOOLEANO': 'BOOLEANO',
    'SI': 'SI',
    'SINO': 'SINO',
    'FIN_SI': 'FIN_SI',
    'MIENTRAS': 'MIENTRAS',
    'FIN_MIENTRAS': 'FIN_MIENTRAS',
    'LEER': 'LEER',
    'ESCRIBIR': 'ESCRIBIR',
    'VERDADERO': 'VERDADERO',
    'FALSO': 'FALSO'
}

# Lista principal de tokens exigidos por la especificación léxica
tokens = [
    # Identificadores y literales
    'ID',
    'NUM_ENTERO',
    'NUM_REAL',
    'CADENA_LITERAL',
    
    # Operadores aritméticos
    'OP_SUMA',
    'OP_RESTA',
    'OP_MULT',
    'OP_DIV',
    
    # Operadores relacionales y lógicos
    'OP_ASIG',
    'OP_IGUALDAD',
    'OP_DIFERENTE',
    'OP_MAYOR',
    'OP_MENOR',
    'OP_Y',
    'OP_O',
    'OP_NO',
    
    # Delimitadores y signos
    'PAR_IZQ',
    'PAR_DER',
    'PUNTO_COMA',
] + list(reservadas.values())


# Expresiones regulares simples para operadores y delimitadores
t_OP_SUMA      = r'\+'
t_OP_RESTA     = r'-'
t_OP_MULT      = r'\*'
t_OP_DIV       = r'/'
t_OP_ASIG      = r'='
t_OP_IGUALDAD  = r'=='
t_OP_DIFERENTE = r'!='
t_OP_MAYOR     = r'>'
t_OP_MENOR     = r'<'
t_OP_Y         = r'Y'
t_OP_O         = r'O'
t_OP_NO        = r'NO'
t_PAR_IZQ      = r'\('
t_PAR_DER      = r'\)'
t_PUNTO_COMA   = r';'


# Expresión regular para números reales (debe ir antes de enteros para no ser devorada)
def t_NUM_REAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

# Expresión regular para números enteros
def t_NUM_ENTERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Expresión regular para cadenas de texto entre comillas dobles
def t_CADENA_LITERAL(t):
    r'\"([^\\\n]|(\\.))*?\"'
    # Remover las comillas de los extremos para almacenar solo el valor
    t.value = t.value[1:-1]
    return t

# Expresión para identificar variables (IDs) y verificar si son palabras reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # Si el ID coincide con una palabra reservada, cambia su tipo de token
    t.type = reservadas.get(t.value, 'ID')
    return t


# Regla para rastrear los números de línea (muy útil para reportar errores en la rúbrica)
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignorar espacios en blanco, tabulaciones y saltos de carro
t_ignore = ' \t\r'

# Manejo de comentarios de una sola línea (tipo // )
def t_comments(t):
    r'//.*'
    pass # Ignoramos el comentario por completo para que no sea un token

# Función para gestionar los errores léxicos
def t_error(t):
    # Lanzamos el error exacto con el carácter que causó el problema
    mensaje = f"❌ Error Léxico en la línea {t.lexer.lineno}.\n"
    mensaje += f"   ➤ Carácter ilegal o no reconocido: '{t.value[0]}'\n"
    mensaje += "   💡 Sugerencia: Elimina este carácter, no pertenece a la sintaxis de MiniLang."
    
    raise ErrorLexicoMiniLang(mensaje)

# Función principal para instanciar y obtener el lexer
def obtener_lexer():
    return lex.lex()