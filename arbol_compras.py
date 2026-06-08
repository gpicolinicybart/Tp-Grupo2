class NodoCompra:
    def __init__(self, compra):
        self.compra = compra
        self.izquierda = None
        self.derecha = None
        self.altura = 1

class ArbolBinarioCompras:
    def __init__(self):
        self.raiz = None
        self.ultimos_saltos = 0
    
    def _altura(self, nodo):
        if nodo is None:
            return 0
        return nodo.altura

    def _balance(self, nodo):
        if nodo is None:
            return 0
        return self._altura(nodo.izquierda) - self._altura(nodo.derecha)

    def _actualizar_altura(self, nodo):
        nodo.altura = 1 + max(self._altura(nodo.izquierda), self._altura(nodo.derecha))

    def _rotar_derecha(self, y):
        x = y.izquierda
        y.izquierda = x.derecha
        x.derecha = y
        self._actualizar_altura(y)
        self._actualizar_altura(x)
        return x

    def _rotar_izquierda(self, x):
        y = x.derecha
        x.derecha = y.izquierda
        y.izquierda = x
        self._actualizar_altura(x)
        self._actualizar_altura(y)
        return y
    
    def insertar(self, compra):
        self.raiz = self._insertar_recursivo(self.raiz, compra)

    def _insertar_recursivo(self, nodo, compra):
        if nodo is None:
            return NodoCompra(compra)
        if compra.get_id() < nodo.compra.get_id():
            nodo.izquierda = self._insertar_recursivo(nodo.izquierda, compra)
        elif compra.get_id() > nodo.compra.get_id():
            nodo.derecha = self._insertar_recursivo(nodo.derecha, compra)
        else:
            return nodo

        self._actualizar_altura(nodo)
        balance = self._balance(nodo)

        if balance > 1 and compra.get_id() < nodo.izquierda.compra.get_id():
            return self._rotar_derecha(nodo)
        if balance < -1 and compra.get_id() > nodo.derecha.compra.get_id():
            return self._rotar_izquierda(nodo)
        if balance > 1 and compra.get_id() > nodo.izquierda.compra.get_id():
            nodo.izquierda = self._rotar_izquierda(nodo.izquierda)
            return self._rotar_derecha(nodo)
        if balance < -1 and compra.get_id() < nodo.derecha.compra.get_id():
            nodo.derecha = self._rotar_derecha(nodo.derecha)
            return self._rotar_izquierda(nodo)
        return nodo
    

    def buscar_por_id(self, id_compra):
        self.ultimos_saltos = 0
        return self._buscar_recursivo(self.raiz, id_compra)

    def _buscar_recursivo(self, nodo_actual, id_compra):
        if nodo_actual is None:
            return None
        self.ultimos_saltos += 1 
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