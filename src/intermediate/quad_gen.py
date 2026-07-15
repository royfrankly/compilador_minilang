class Cuadruplo:
    def __init__(self, operador, arg1, arg2, resultado):
        self.operador = operador
        self.arg1 = arg1
        self.arg2 = arg2
        self.resultado = resultado

    def __str__(self):
        # Formato de impresión limpio para la interfaz y la consola
        arg1_str = self.arg1 if self.arg1 is not None else ""
        arg2_str = self.arg2 if self.arg2 is not None else ""
        return f"({self.operador}, {arg1_str}, {arg2_str}, {self.resultado})"

class QuadrupleGenerator:
    def __init__(self):
        self.cuadruplos = []
        self.temp_count = 0  # Contador para variables temporales (t1, t2...)
        self.label_count = 0 # Contador para etiquetas de salto (L1, L2...)

    def new_temp(self):
        """Genera una nueva variable temporal, ej: t1, t2"""
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        """Genera una nueva etiqueta para saltos lógicos, ej: L1, L2"""
        self.label_count += 1
        return f"L{self.label_count}"

    def add_quad(self, operador, arg1, arg2, resultado):
        """Agrega un cuádruplo a la lista global"""
        cuad = Cuadruplo(operador, arg1, arg2, resultado)
        self.cuadruplos.append(cuad)

    def generate(self, nodo_ast):
        if nodo_ast:
            self._visit(nodo_ast)
        return self.cuadruplos

    def _visit(self, nodo):
        method_name = f'visit_{type(nodo).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(nodo)

    def generic_visit(self, nodo):
        pass

    def visit_Programa(self, nodo):
        for instruccion in nodo.instrucciones:
            self._visit(instruccion)

    def visit_Declaracion(self, nodo):
        # Las declaraciones de variables no generan cuádruplos per se en esta etapa,
        # su existencia ya se validó en el análisis semántico.
        pass

    def visit_Numero(self, nodo):
        return str(nodo.valor)

    def visit_Identificador(self, nodo):
        return nodo.nombre

    def visit_OperacionBinaria(self, nodo):
        # Primero resolvemos el lado izquierdo y el derecho
        arg1 = self._visit(nodo.izquierda)
        arg2 = self._visit(nodo.derecha)
        
        # Creamos una variable temporal para guardar el resultado de esta operación
        temp = self.new_temp()
        self.add_quad(nodo.operador, arg1, arg2, temp)
        return temp

    def visit_Asignacion(self, nodo):
        # Evaluamos todo lo que está a la derecha del igual (=)
        resultado_expresion = self._visit(nodo.expresion)
        # Generamos el cuádruplo de asignación
        self.add_quad('=', resultado_expresion, '', nodo.id_variable)

    def visit_CondicionalSi(self, nodo):
        # 1. Evaluamos la condición lógica
        cond_temp = self._visit(nodo.condicion)
        
        # 2. Creamos etiquetas para los saltos
        label_falso = self.new_label()
        label_fin = self.new_label()

        # 3. Si la condición es FALSA, saltar al bloque SINO (o al final)
        self.add_quad('IF_FALSE', cond_temp, '', label_falso)

        # 4. Generar código para el bloque SI (Verdadero)
        for instr in nodo.bloque_si:
            self._visit(instr)
        
        # 5. Salto incondicional al final del IF para evitar ejecutar el SINO
        self.add_quad('GOTO', '', '', label_fin)

        # 6. Colocar la etiqueta del bloque SINO (Falso)
        self.add_quad('LABEL', '', '', label_falso)
        if getattr(nodo, 'bloque_sino', None):
            for instr in nodo.bloque_sino:
                self._visit(instr)

        # 7. Colocar la etiqueta de FIN del IF
        self.add_quad('LABEL', '', '', label_fin)

    def visit_CicloMientras(self, nodo):
        # 1. Etiqueta de inicio del ciclo (para regresar)
        label_inicio = self.new_label()
        self.add_quad('LABEL', '', '', label_inicio)

        # 2. Evaluar condición
        cond_temp = self._visit(nodo.condicion)

        # 3. Etiqueta de salida del ciclo
        label_fin = self.new_label()

        # 4. Si la condición es falsa, salir del ciclo
        self.add_quad('IF_FALSE', cond_temp, '', label_fin)

        # 5. Bloque de instrucciones a repetir
        for instr in nodo.bloque:
            self._visit(instr)

        # 6. Regresar al inicio para re-evaluar la condición
        self.add_quad('GOTO', '', '', label_inicio)

        # 7. Etiqueta del final del ciclo
        self.add_quad('LABEL', '', '', label_fin)

    def visit_Leer(self, nodo):
        self.add_quad('READ', '', '', nodo.id_variable)

    def visit_Escribir(self, nodo):
        res = self._visit(nodo.expresion)
        self.add_quad('WRITE', '', '', res)