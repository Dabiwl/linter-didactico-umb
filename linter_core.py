import ast
import re

class AnalizadorDidactico(ast.NodeVisitor):
    def __init__(self):
        self.errores = []
        self.nivel_anidamiento_actual = 0

    # 1. REGLA: Funciones largas, nombres en camelCase y variables no usadas
    def visit_FunctionDef(self, node):
        # A. Longitud de la funcion
        num_lineas = node.end_lineno - node.lineno
        if num_lineas > 15:
            self.errores.append({
                "tipo": "Code Smell",
                "penalizacion": 15,
                "linea": node.lineno,
                "hallazgo": f"La funcion '{node.name}' es demasiado larga ({num_lineas} lineas).",
                "porque": "Funciones extensas violan el principio de modularidad (ISO 25010), dificultando la lectura y las pruebas unitarias.",
                "sugerencia": "Divide esta funcion en submodulos mas pequenos con responsabilidades unicas."
            })
        
        # B. Nombre de funcion en camelCase
        if any(c.isupper() for c in node.name):
            self.errores.append({
                "tipo": "PEP8 Nomenclatura",
                "penalizacion": 5,
                "linea": node.lineno,
                "hallazgo": f"El nombre de la funcion '{node.name}' usa mayusculas (camelCase).",
                "porque": "PEP8 establece que las funciones en Python deben usar minusculas separadas por guion bajo (snake_case).",
                "sugerencia": f"Renombrala usando minusculas: '{re.sub(r'(?<!^)(?=[A-Z])', '_', node.name).lower()}'."
            })

        # C. Variables declaradas y no utilizadas dentro de la funcion
        variables_asignadas = {}
        variables_leidas = set()

        for hijo in ast.walk(node):
            # Detectar asignaciones (donde nace la variable)
            if isinstance(hijo, ast.Assign):
                for target in hijo.targets:
                    if isinstance(target, ast.Name):
                        variables_asignadas[target.id] = target.lineno
            # Detectar uso o lectura de variables
            elif isinstance(hijo, ast.Name) and isinstance(hijo.ctx, ast.Load):
                variables_leidas.add(hijo.id)

        for nombre_var, linea_var in variables_asignadas.items():
            if nombre_var not in variables_leidas and not nombre_var.startswith('_'):
                self.errores.append({
                    "tipo": "Buenas Practicas / Limpieza",
                    "penalizacion": 5,
                    "linea": linea_var,
                    "hallazgo": f"La variable '{nombre_var}' fue asignada pero nunca se utiliza.",
                    "porque": "Declarar variables que no se consumen consume memoria innecesaria y confunde la lectura del codigo.",
                    "sugerencia": f"Elimina la asignacion de '{nombre_var}' o revisa si olvidaste incluirla en un calculo posterior."
                })

        self.generic_visit(node)

    # 2. REGLA: Variables globales o modulares en camelCase
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                nombre_var = target.id
                if any(c.isupper() for c in nombre_var) and not nombre_var.isupper():
                    self.errores.append({
                        "tipo": "PEP8 Nomenclatura",
                        "penalizacion": 5,
                        "linea": target.lineno,
                        "hallazgo": f"La variable '{nombre_var}' no sigue el formato snake_case.",
                        "porque": "El uso inconsistente de mayusculas aumenta la carga cognitiva al leer codigo colaborativo.",
                        "sugerencia": f"Cambiala a minusculas: '{re.sub(r'(?<!^)(?=[A-Z])', '_', nombre_var).lower()}'."
                    })
        self.generic_visit(node)

    # 3. REGLA: Anidamiento profundo (Carga Cognitiva)
    def _verificar_anidamiento(self, node):
        self.nivel_anidamiento_actual += 1
        if self.nivel_anidamiento_actual > 2:
            self.errores.append({
                "tipo": "Carga Cognitiva",
                "penalizacion": 10,
                "linea": node.lineno,
                "hallazgo": f"Estructura de control con anidamiento profundo (Nivel {self.nivel_anidamiento_actual}).",
                "porque": "Multiples bucles y condiciones anidadas saturan la memoria de trabajo del lector (Teoria de la Carga Cognitiva).",
                "sugerencia": "Aplica clausulas de guarda (early return) o extrae el bloque interno a una funcion separada."
            })
        
        self.generic_visit(node)
        self.nivel_anidamiento_actual -= 1

    def visit_If(self, node):
        self._verificar_anidamiento(node)

    def visit_For(self, node):
        self._verificar_anidamiento(node)

    def visit_While(self, node):
        self._verificar_anidamiento(node)


def analizar_codigo(ruta_o_texto, es_texto=False):
    if es_texto:
        codigo_fuente = ruta_o_texto
    else:
        with open(ruta_o_texto, "r", encoding="utf-8") as archivo:
            codigo_fuente = archivo.read()
    
    try:
        arbol = ast.parse(codigo_fuente)
    except SyntaxError as e:
        return [{
            "tipo": "Error de Sintaxis",
            "penalizacion": 100,
            "linea": e.lineno,
            "hallazgo": f"El codigo tiene un error de sintaxis que impide analizarlo: {e.msg}",
            "porque": "El analizador AST necesita codigo Python valido para poder crear el arbol de sintaxis.",
            "sugerencia": "Revisa que no te falten dos puntos (:), parentesis de cierre o sangria."
        }], 0
    
    analizador = AnalizadorDidactico()
    analizador.visit(arbol)
    
    puntaje = 100
    for error in analizador.errores:
        puntaje -= error["penalizacion"]
    puntaje = max(0, puntaje)
    
    # Ordenar los errores cronologicamente por linea
    analizador.errores.sort(key=lambda x: x["linea"])
    
    return analizador.errores, puntaje


if __name__ == "__main__":
    errores, puntaje = analizar_codigo("codigo_prueba.py")
    print(f"\nReporte de Analisis - Calificacion: {puntaje}/100 pts")
    for e in errores:
        print(f"[Linea {e['linea']}] {e['tipo']}: {e['hallazgo']}")