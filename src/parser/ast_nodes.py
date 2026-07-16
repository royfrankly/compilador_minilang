class NodoAST:
    pass

class Programa(NodoAST):
    def __init__(self, instrucciones, linea="Desconocida"):
        self.instrucciones = instrucciones
        self.linea = linea

class Declaracion(NodoAST):
    def __init__(self, tipo_dato, id_variable, linea="Desconocida"):
        self.tipo_dato = tipo_dato
        self.id_variable = id_variable
        self.linea = linea

class Asignacion(NodoAST):
    def __init__(self, id_variable, expresion, linea="Desconocida"):
        self.id_variable = id_variable
        self.expresion = expresion
        self.linea = linea

class OperacionBinaria(NodoAST):
    def __init__(self, izquierda, operador, derecha, linea="Desconocida"):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha
        self.linea = linea

class Numero(NodoAST):
    def __init__(self, valor, linea="Desconocida"):
        self.valor = valor
        self.linea = linea

class Identificador(NodoAST):
    def __init__(self, nombre, linea="Desconocida"):
        self.nombre = nombre
        self.linea = linea

class CondicionalSi(NodoAST):
    def __init__(self, condicion, bloque_si, bloque_sino=None, linea="Desconocida"):
        self.condicion = condicion
        self.bloque_si = bloque_si
        self.bloque_sino = bloque_sino
        self.linea = linea

class CicloMientras(NodoAST):
    def __init__(self, condicion, bloque, linea="Desconocida"):
        self.condicion = condicion
        self.bloque = bloque
        self.linea = linea

class Leer(NodoAST):
    def __init__(self, id_variable, linea="Desconocida"):
        self.id_variable = id_variable
        self.linea = linea

class Escribir(NodoAST):
    def __init__(self, expresion, linea="Desconocida"):
        self.expresion = expresion
        self.linea = linea
