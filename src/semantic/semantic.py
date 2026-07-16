from src.parser.ast_nodes import *
from src.semantic.symbol_table import SymbolTable

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errores = []

    def analyze(self, nodo_ast):
        if not nodo_ast:
            return False

        try:
            self._visit(nodo_ast)
            return len(self.errores) == 0
        except Exception as e:
            self.errores.append(str(e))
            return False

    def _visit(self, nodo):
        method_name = f'visit_{type(nodo).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(nodo)

    def generic_visit(self, nodo):
        linea = getattr(nodo, 'linea', 'Desconocida')
        raise Exception(f"Error Semántico (Línea {linea}): Nodo no soportado {type(nodo).__name__}")

    def visit_Programa(self, nodo):
        for instruccion in nodo.instrucciones:
            self._visit(instruccion)

    def visit_Declaracion(self, nodo):
        try:
            self.symbol_table.declare(nodo.id_variable, nodo.tipo_dato, nodo.linea)
        except Exception as e:
            mensaje = str(e)
            if not mensaje.startswith('Error Semántico'):
                mensaje = f"Error Semántico (Línea {nodo.linea}): {mensaje}"
            self.errores.append(mensaje)

    def visit_Asignacion(self, nodo):
        try:
            variable_info = self.symbol_table.lookup(nodo.id_variable, nodo.linea)
            tipo_expresion = self._visit(nodo.expresion)

            if tipo_expresion and variable_info['tipo'] != tipo_expresion and tipo_expresion != 'ERROR':
                if not (variable_info['tipo'] == 'REAL' and tipo_expresion == 'ENTERO'):
                    self.errores.append(
                        f"Error Semántico (Línea {nodo.linea}): Incompatibilidad. La variable '{nodo.id_variable}' ({variable_info['tipo']}) no acepta un valor ({tipo_expresion})."
                    )
        except Exception as e:
            mensaje = str(e)
            if not mensaje.startswith('Error Semántico'):
                mensaje = f"Error Semántico (Línea {nodo.linea}): {mensaje}"
            self.errores.append(mensaje)

    def visit_OperacionBinaria(self, nodo):
        tipo_izq = self._visit(nodo.izquierda)
        tipo_der = self._visit(nodo.derecha)

        if nodo.operador in ['+', '-', '*', '/']:
            if tipo_izq not in ['ENTERO', 'REAL'] or tipo_der not in ['ENTERO', 'REAL']:
                self.errores.append(
                    f"Error Semántico (Línea {nodo.linea}): Matemática inválida entre tipos '{tipo_izq}' y '{tipo_der}'."
                )
                return 'ERROR'
            if tipo_izq == 'REAL' or tipo_der == 'REAL':
                return 'REAL'
            return 'ENTERO'

        if nodo.operador in ['>', '<', '==', '!=']:
            return 'BOOLEANO'

        if nodo.operador in ['Y', 'O']:
            if tipo_izq != 'BOOLEANO' or tipo_der != 'BOOLEANO':
                self.errores.append(
                    f"Error Semántico (Línea {nodo.linea}): Operación lógica inválida entre '{tipo_izq}' y '{tipo_der}'."
                )
                return 'ERROR'
            return 'BOOLEANO'

        return 'ERROR'

    def visit_Numero(self, nodo):
        if isinstance(nodo.valor, float):
            return 'REAL'

        if isinstance(nodo.valor, str):
            if nodo.valor in ['VERDADERO', 'FALSO']:
                return 'BOOLEANO'
            return 'CADENA'

        return 'ENTERO'

    def visit_Identificador(self, nodo):
        try:
            var_info = self.symbol_table.lookup(nodo.nombre, nodo.linea)
            return var_info['tipo']
        except Exception as e:
            mensaje = str(e)
            if not mensaje.startswith('Error Semántico'):
                mensaje = f"Error Semántico (Línea {nodo.linea}): {mensaje}"
            self.errores.append(mensaje)
            return 'ERROR'

    def visit_CondicionalSi(self, nodo):
        tipo_cond = self._visit(nodo.condicion)
        if tipo_cond != 'BOOLEANO' and tipo_cond != 'ERROR':
            self.errores.append(
                f"Error Semántico (Línea {nodo.linea}): La condición SI debe ser lógica (BOOLEANO)."
            )
        for instr in nodo.bloque_si:
            self._visit(instr)
        if nodo.bloque_sino:
            for instr in nodo.bloque_sino:
                self._visit(instr)

    def visit_CicloMientras(self, nodo):
        tipo_cond = self._visit(nodo.condicion)
        if tipo_cond != 'BOOLEANO' and tipo_cond != 'ERROR':
            self.errores.append(
                f"Error Semántico (Línea {nodo.linea}): La condición MIENTRAS debe ser lógica (BOOLEANO)."
            )
        for instr in nodo.bloque:
            self._visit(instr)

    def visit_Escribir(self, nodo):
        self._visit(nodo.expresion)

    def visit_Leer(self, nodo):
        try:
            self.symbol_table.lookup(nodo.id_variable, nodo.linea)
        except Exception as e:
            mensaje = str(e)
            if not mensaje.startswith('Error Semántico'):
                mensaje = f"Error Semántico (Línea {nodo.linea}): {mensaje}"
            self.errores.append(mensaje)
