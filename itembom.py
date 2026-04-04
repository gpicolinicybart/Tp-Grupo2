
class ItemBOM:
    def __init__(self, id_item: int, nombre: str, diccionario_elementos: dict):
        self._id = id_item
        self._nombre = nombre
        for cantidad in diccionario_elementos.values():
            self.validar_entero_positivo(cantidad)
        self._diccionario = diccionario_elementos 
    
    def __str__(self):
        cant_componentes = len(self._diccionario)
        return f"Receta (Item BOM) -> ID: {self._id} | Nombre: '{self._nombre}' | Cantidad de insumos distintos: {cant_componentes}"

    def get_id(self) -> int:
        return self._id
        
    def get_nombre(self) -> str:
        return self._nombre
        
    def get_diccionario(self) -> dict:
        return self._diccionario
     
    def validar_entero_positivo(self, valor: int) -> int:
        if not isinstance(valor, int):
            raise TypeError(f"Error: La cantidad debe ser un número entero. Ingresaste: {type(valor).__name__}")
        if valor <= 0:
            raise ValueError(f"Error: La cantidad en una receta debe ser mayor a cero. Ingresaste: {valor}")
        return valor
        
    def get_costo_total(self) -> float:
        costo_total = 0.0
        for elemento, cantidad in self._diccionario.items():
            costo_total += elemento.get_costo_unitario() * self.validar_entero_positivo(cantidad)
        return costo_total