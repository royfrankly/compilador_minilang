class Optimizer:
    def __init__(self):
        self.optimized_quads = []

    def optimize(self, cuadruplos):
        """
        Aplica el 'Plegado de Constantes'.
        Si un cuádruplo hace una operación entre dos números (no variables),
        se calcula el resultado en tiempo de compilación.
        """
        for cuad in cuadruplos:
            if cuad.operador in ['+', '-', '*', '/']:
                # Verificamos si ambos argumentos son numéricos (constantes)
                # Omitimos variables temporales o IDs.
                if self._is_number(cuad.arg1) and self._is_number(cuad.arg2):
                    resultado_calculado = self._calculate(cuad.operador, cuad.arg1, cuad.arg2)
                    
                    # Convertimos la operación matemática en una simple asignación '='
                    cuad.operador = '='
                    cuad.arg1 = str(resultado_calculado)
                    cuad.arg2 = ''
                    # cuad.resultado se mantiene igual (ej: t1)
            
            self.optimized_quads.append(cuad)
            
        return self.optimized_quads

    def _is_number(self, val):
        """Valida si el string representa un número entero o flotante."""
        if val is None or val == '':
            return False
        try:
            float(val) # Intenta convertir a float, si no falla, es numérico
            return True
        except ValueError:
            return False

    def _calculate(self, operador, arg1, arg2):
        """Realiza la operación matemática nativa de Python."""
        val1 = float(arg1)
        val2 = float(arg2)
        res = 0
        
        if operador == '+': res = val1 + val2
        elif operador == '-': res = val1 - val2
        elif operador == '*': res = val1 * val2
        elif operador == '/': 
            # Evitar división por cero en tiempo de compilación
            res = val1 / val2 if val2 != 0 else 0
            
        # Si el resultado es un entero exacto (ej 5.0), lo formateamos como int ('5')
        if res.is_integer():
            return int(res)
        return res