from collections import deque
from arbol_compras import ArbolBinarioCompras

class GestorCompras:
    def __init__(self):
        # 1. Reemplazamos la lista por el Árbol Binario
        self._arbol_historico = ArbolBinarioCompras()
        self._compras_pendientes = deque() 

    def agregar_compra(self, compra):
        """Registra la compra en el historial (árbol) y en la cola si está pendiente"""
        self._arbol_historico.insertar(compra)
        
        # 2. ENCAPSULAMIENTO: Usamos get_estado() en lugar de acceder a _estado
        if compra.get_estado() == "Solicitada":
            self._compras_pendientes.append(compra)

    def recibir_proxima_compra(self, inventario):
        """Saca la orden más antigua de la cola y la recibe"""
        if not self._compras_pendientes:
            return None 
        
        compra_a_recibir = self._compras_pendientes.popleft()
        
        # 3. ENCAPSULAMIENTO: No tocamos el estado acá, le pasamos el inventario 
        # a la compra para que ella misma se actualice internamente.
        compra_a_recibir.recibir_materiales(inventario)
        
        return compra_a_recibir

    def obtener_historial(self):
        """Devuelve la lista ordenada generada por el recorrido inorden del árbol"""
        return self._arbol_historico.obtener_lista_inorden()
        
    def buscar_compra_especifica(self, id_compra):
        """Aprovecha la velocidad del árbol binario (O(log n)) para buscar una orden"""
        return self._arbol_historico.buscar_por_id(id_compra)