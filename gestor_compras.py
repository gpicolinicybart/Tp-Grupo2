from collections import deque

class GestorCompras:
    def __init__(self):
        self._registro_historico = []
        self._compras_pendientes = deque() 

    def agregar_compra(self, compra):
        """Registra la compra en el historial y en la cola si está pendiente"""
        self._registro_historico.append(compra)
        if compra._estado == "Solicitada":
            self._compras_pendientes.append(compra)

    def recibir_proxima_compra(self):
        """Saca la orden más antigua de la cola y la recibe"""
        if not self._compras_pendientes:
            return None 
        
        compra_a_recibir = self._compras_pendientes.popleft()
        compra_a_recibir._estado = "Recibida"
        return compra_a_recibir

    def obtener_historial(self):
        return self._registro_historico