from elemento import Elemento

class Inventario:
    def __init__(self):
        # Usamos diccionarios vacíos al instanciar el inventario
        #usamos el objeto elemento como clave y la cantidad como valor
        self._stock_fisico = {} 
        self._stock_reservado = {}
        
    def consultar_stock(self, elem: Elemento) -> int:
        return self._stock_fisico.get(elem,0) #el get va a devolver la cantidad o 0 si el elemento no existe en el dict
        
    def reservar_stock(self, elem: Elemento, cant: int):
        self.validar_cantidad(cant)
        stock_actual=self.consultar_stock(elem)
        reservado_actual=self._stock_reservado.get(elem,0)
        stock_disponible=stock_actual-reservado_actual
        if stock_disponible>=cant:
            self._stock_reservado[elem]=reservado_actual+cant
            print(f"-> RESERVA: Se reservaron {cant} unidades de '{elem._nombre}'.")
        else:
            print(f"->ALERTA: No hay stock suficiente para reservar {cant} de '{elem._nombre}'.")
    def descontar_stock(self, elem: Elemento, cant: int):
        # se descuenta el fisico y la reserva cuando se arranca a producir
        self.validar_cantidad(cant)
        if elem in self._stock_reservado and self._stock_reservado[elem]>=cant:
            self._stock_fisico[elem]-=cant 
            self._stock_reservado[elem]-=cant 
            print(f"->CONSUMO: Se utilizaron {cant} unidades de '{elem._nombre}'.")
        else:
            print(f"->ERROR: Intentando consumir '{elem._nombre}' sin reserva previa.")
        
    def ingresar_stock(self, elem: Elemento, cant: int):
        self.validar_cantidad(cant)
        if elem in self._stock_fisico:
            self._stock_fisico[elem]+=cant
        else: 
            self._stock_fisico[elem]=cant
    
    def hay_disponibilidad(self, elem: Elemento, cant_pedida: int) -> bool:
        # El inventario hace su propia cuenta interna
        stock_real = self.consultar_stock(elem)
        reservado = self._stock_reservado.get(elem, 0)
        return (stock_real - reservado) >= cant_pedida
    
    def obtener_stock_disponible(self, elem: Elemento) -> int:
        """Retorna el stock disponible (físico - reservado) sin acceso directo a atributos privados"""
        stock_real = self.consultar_stock(elem)
        reservado = self._stock_reservado.get(elem, 0)
        return stock_real - reservado
    
    @staticmethod
    def validar_cantidad(cant: int) -> bool:
        if cant <= 0:
            raise ValueError(f"Error: La cantidad debe ser mayor a cero.")
        return True