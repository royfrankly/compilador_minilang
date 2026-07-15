
class NodoAST:
    pass

class Programa(NodoAST):
    def __init__(self, instrucciones):
        self.instrucciones = instrucciones

class Declaracion(NodoAST):
    def __init__(self, tipo_dato, id_variable):
        self.tipo_dato = tipo_dato
        self.id_variable = id_variable

class Asignacion(NodoAST):
    def __init__(self, id_variable, expresion):
        self.id_variable = id_variable
        self.expresion = expresion

class OperacionBinaria(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

class Numero(NodoAST):
    def __init__(self, valor):
        self.valor = valor

class Identificador(NodoAST):
    def __init__(self, nombre):
        self.nombre = nombre

class CondicionalSi(NodoAST):
    def __init__(self, condicion, bloque_si, bloque_sino=None):
        self.condicion = condicion
        self.bloque_si = bloque_si
        self.bloque_sino = bloque_sino

class CicloMientras(NodoAST):
    def __init__(self, condicion, bloque):
        self.condicion = condicion
        self.bloque = bloque

class Leer(NodoAST):
    def __init__(self, id_variable):
        self.id_variable = id_variable

class Escribir(NodoAST):
    def __init__(self, expresion):
        self.expresion = expresion