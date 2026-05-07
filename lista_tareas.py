class NodoTarea:
    def __init__(self, tarea):
        self.tarea = tarea
        self.siguiente = None


class ListaEnlazadaTareas:
    def __init__(self):
        self.cabecera = None

    def agregar_al_final(self, tarea):
        nuevo_nodo = NodoTarea(tarea)
        if self.cabecera is None:
            self.cabecera = nuevo_nodo
        else:
            nodo_actual = self.cabecera
            while nodo_actual.siguiente is not None:
                nodo_actual = nodo_actual.siguiente
            nodo_actual.siguiente = nuevo_nodo

    def __len__(self):
        contador = 0
        nodo_actual = self.cabecera
        while nodo_actual is not None:
            contador += 1
            nodo_actual = nodo_actual.siguiente
        return contador
