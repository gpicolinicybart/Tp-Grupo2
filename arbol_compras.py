class NodoCompra:
    def __init__(self, compra):
        self.compra = compra
        self.izquierda = None
        self.derecha = None

class ArbolBinarioCompras:
    def __init__(self):
        self.raiz = None

    def insertar(self, compra):
        if self.raiz is None:
            self.raiz = NodoCompra(compra)
        else:
            self._insertar_recursivo(self.raiz, compra)

    def _insertar_recursivo(self, nodo_actual, compra):
        # Comparamos por ID para decidir de qué lado del árbol va
        if compra.get_id() < nodo_actual.compra.get_id():
            if nodo_actual.izquierda is None:
                nodo_actual.izquierda = NodoCompra(compra)
            else:
                self._insertar_recursivo(nodo_actual.izquierda, compra)
        elif compra.get_id() > nodo_actual.compra.get_id():
            if nodo_actual.derecha is None:
                nodo_actual.derecha = NodoCompra(compra)
            else:
                self._insertar_recursivo(nodo_actual.derecha, compra)

    def buscar_por_id(self, id_compra):
        return self._buscar_recursivo(self.raiz, id_compra)

    def _buscar_recursivo(self, nodo_actual, id_compra):
        if nodo_actual is None:
            return None
        
        if nodo_actual.compra.get_id() == id_compra:
            return nodo_actual.compra
        elif id_compra < nodo_actual.compra.get_id():
            return self._buscar_recursivo(nodo_actual.izquierda, id_compra)
        else:
            return self._buscar_recursivo(nodo_actual.derecha, id_compra)

    def obtener_lista_inorden(self):
  
        lista = []
        self._inorden_recursivo(self.raiz, lista)
        return lista

    def _inorden_recursivo(self, nodo_actual, lista):
        if nodo_actual is not None:
            self._inorden_recursivo(nodo_actual.izquierda, lista)
            lista.append(nodo_actual.compra)
            self._inorden_recursivo(nodo_actual.derecha, lista)