class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class ListaEnlazadaBase:
    def __init__(self):
        self.cabeza = None

    def agregar_nodo(self, dato):
        nuevo_nodo = Nodo(dato)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo

    def filtrar(self, funcion_criterio) -> list:
        """
        Función de Alto Orden heredable. 
        Devuelve una lista de Python estándar con los datos que cumplen el criterio.
        """
        resultados = []
        actual = self.cabeza
        while actual:
            if funcion_criterio(actual.dato):
                resultados.append(actual.dato)
            actual = actual.siguiente
        return resultados
        
    def obtener_todos(self) -> list:
        resultados = []
        actual = self.cabeza
        while actual:
            resultados.append(actual.dato)
            actual = actual.siguiente
        return resultados
    #cree esta clase para usarla como "padre" de las listas enlazadas de colaboradores y elementos, para evitar repetir código.