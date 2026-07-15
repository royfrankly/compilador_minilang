class SymbolTable:
    def __init__(self):
        # El diccionario almacenará: {'nombre_variable': {'tipo': 'ENTERO', 'valor': None, 'linea_declaracion': 5}}
        self.symbols = {}

    #    def declare(self, name, var_type, line_num):
        if name in self.symbols:
            raise Exception(f"Error Semántico (Línea {line_num}): La variable '{name}' ya ha sido declarada previamente.")
        
        self.symbols[name] = {
            'tipo': var_type,
            'valor': None, # Inicialmente no tiene valor
            'linea': line_num
        }

    #    def lookup(self, name, line_num):
        if name not in self.symbols:
            raise Exception(f"Error Semántico (Línea {line_num}): La variable '{name}' no ha sido declarada.")
        return self.symbols[name]

    #    def update_value(self, name, value, line_num):
        # Primero verificamos que exista
        self.lookup(name, line_num)
        self.symbols[name]['valor'] = value

    #    def get_all(self):
        return self.symbols