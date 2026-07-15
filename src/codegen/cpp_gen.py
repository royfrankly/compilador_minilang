class CppGenerator:
    def __init__(self):
        self.codigo_cpp = []
        self.temporales = set() # Para guardar t1, t2, etc y declararlos

    def generate(self, cuadruplos, symbol_table):
        # 1. Cabeceras estándar de C++
        self.codigo_cpp.append("#include <iostream>")
        self.codigo_cpp.append("using namespace std;\n")
        self.codigo_cpp.append("int main() {")

        # 2. Declarar las variables del usuario basadas en la tabla de símbolos
        self._declarar_variables(symbol_table)

        # 3. Recopilar y declarar variables temporales creadas en el código intermedio
        self._extraer_temporales(cuadruplos)
        if self.temporales:
            declaracion_temps = "    double " + ", ".join(self.temporales) + ";"
            self.codigo_cpp.append(declaracion_temps)
        self.codigo_cpp.append("") # Línea en blanco

        # 4. Traducir cada cuádruplo a C++
        for cuad in cuadruplos:
            linea = self._traducir_cuadruplo(cuad)
            if linea:
                self.codigo_cpp.append(linea)

        # 5. Cierre del programa
        self.codigo_cpp.append("\n    return 0;")
        self.codigo_cpp.append("}")

        return "\n".join(self.codigo_cpp)

    def _declarar_variables(self, symbol_table):
        """Traduce los tipos de MiniLang a C++ y declara las variables."""
        if not symbol_table: return
        
        simbolos = symbol_table.get_all()
        for nombre, info in simbolos.items():
            tipo_ml = info['tipo']
            tipo_cpp = "int"
            
            if tipo_ml == 'REAL': tipo_cpp = "double"
            elif tipo_ml == 'CADENA': tipo_cpp = "string"
            elif tipo_ml == 'BOOLEANO': tipo_cpp = "bool"
            
            self.codigo_cpp.append(f"    {tipo_cpp} {nombre};")

    def _extraer_temporales(self, cuadruplos):
        """Busca todas las variables 'tX' para declararlas en C++."""
        for cuad in cuadruplos:
            if cuad.resultado and cuad.resultado.startswith('t'):
                self.temporales.add(cuad.resultado)

    def _traducir_cuadruplo(self, cuad):
        """Convierte una operación de 3 direcciones a sintaxis C++."""
        op = cuad.operador
        arg1 = cuad.arg1
        arg2 = cuad.arg2
        res = cuad.resultado

        if op == '=':
            return f"    {res} = {arg1};"
        elif op in ['+', '-', '*', '/', '>', '<', '==', '!=']:
            return f"    {res} = {arg1} {op} {arg2};"
        elif op == 'Y':
            return f"    {res} = {arg1} && {arg2};"
        elif op == 'O':
            return f"    {res} = {arg1} || {arg2};"
        elif op == 'LABEL':
            return f"{res}:"
        elif op == 'GOTO':
            return f"    goto {res};"
        elif op == 'IF_FALSE':
            # Si arg1 es falso, saltar a res
            return f"    if (!({arg1})) goto {res};"
        elif op == 'READ':
            return f"    cin >> {res};"
        elif op == 'WRITE':
            return f"    cout << {res} << endl;"
        
        return f"    // Operacion desconocida: {op}"