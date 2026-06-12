class NodoTarea:
    def __init__(self, tarea):
        self.tarea = tarea
        self.siguiente = None

class ListaEnlazadaTareas:
    def __init__(self):
        self.cabecera = None
        self.fin = None        
        self._costo_total = 0.0

    def agregar_al_final(self, tarea):
        nuevo_nodo = NodoTarea(tarea)
        self._costo_total += tarea.get_costo()

        if self.cabecera is None:
            self.cabecera = nuevo_nodo
            self.fin = nuevo_nodo
        else:
            self.fin.siguiente = nuevo_nodo
            self.fin = nuevo_nodo

    def __len__(self):
        contador = 0
        nodo_actual = self.cabecera
        while nodo_actual is not None:
            contador += 1
            nodo_actual = nodo_actual.siguiente
        return contador
    
    def __iter__(self):
        nodo_actual = self.cabecera
        while nodo_actual is not None:
            yield nodo_actual.tarea
            nodo_actual = nodo_actual.siguiente

    def get_costo_total(self):
        return self._costo_total