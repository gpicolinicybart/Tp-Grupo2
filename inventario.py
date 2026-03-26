from elemento import Elemento

class Inventario:
    def __init__(self):
        self._stock_fisico = {} 
        self._stock_reservado = {}

    def __str__(self):
        return f"Inventario (Tipos de elementos en stock: {len(self._stock_fisico)} | Elementos reservados: {len(self._stock_reservado)})"   
     
    def consultar_stock(self, elem: Elemento) -> int:
        return self._stock_fisico.get(elem,0) 
        
    def reservar_stock(self, elem: Elemento, cant: int):
        stock_actual=self.consultar_stock(elem)
        reservado_actual=self._stock_reservado.get(elem,0)
        stock_disponible=stock_actual-reservado_actual
        if stock_disponible>=cant:
            self._stock_reservado[elem]=reservado_actual+cant
            print(f"-> RESERVA: Se reservaron {cant} unidades de '{elem._nombre}'.")
            return True
        else:
            print(f"->ALERTA: No hay stock suficiente para reservar {cant} de '{elem._nombre}'.")
            return False

    def descontar_stock(self, elem: Elemento, cant: int):
        
        if elem in self._stock_reservado and self._stock_reservado[elem]>=cant:
            self._stock_fisico[elem]-=cant 
            self._stock_reservado[elem]-=cant 
            print(f"->CONSUMO: Se utilizaron {cant} unidades de '{elem._nombre}'.")
        else:
            print(f"->ERROR: Intentando consumir '{elem._nombre} sin reserva previa.")
        
    def ingresar_stock(self, elem: Elemento, cant: int):
        if elem in self._stock_fisico:
            self._stock_fisico[elem]+=cant
        else: 
            self._stock_fisico[elem]=cant
