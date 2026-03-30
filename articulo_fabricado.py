
from elemento import Elemento

class ArticuloFabricadoInternamente(Elemento):
    def __init__(self, id_elemento: int, nombre: str, bom: list, lista_tareas: list):
        super().__init__(id_elemento, nombre)
        self._bom = bom # Lista de elementos
        self._lista_tareas = lista_tareas 

    def get_costo_unitario(self) -> float:
        costo_total = 0.0
        
        # 1. Sumamos materiales (Recursivo)
        for elemento, cantidad in self._bom.items():
            costo_total += elemento.get_costo_unitario() * cantidad
            
        # 2. Sumamos tareas (Delegamos el cálculo a cada tarea)
        for tarea in self._lista_tareas:
            costo_total += tarea.get_costo()
            
        return costo_total
    #Arriba se define el metodo para calcular el costo total del artículo sumando el costo de los materiales (usando get_costo_unitario de cada elemento) y el costo de las tareas (usando get_costo de cada tarea).
    #respeta encapsulamiento porque cada clase se encarga de calcular su propio costo, no accede directamente a los atributos de otras clases, sino que llama a sus métodos públicos para obtener la información necesaria.




        #Empezar en el producto actual.
        #Mirar todos sus componentes en la BOM.
        #Si alguno de esos componentes es el producto original, tira error de ciclo.
        #Si no, revisar los componentes de los componentes (recursión profunda)
    def validar_ciclos(self, visitados=None) -> bool:
        if visitados is None:
            visitados = []
        
        # Si el ID ya está en la lista, lanzamos la excepción
        if self._id in visitados:
            raise ValueError(f"ERROR DE DISEÑO: Ciclo detectado. El artículo '{self._nombre}' (ID: {self._id}) se requiere a sí mismo en su propia cadena de producción.")
        
        nuevo_camino = visitados + [self._id]
        
        for elemento in self._bom.keys():
            if isinstance(elemento, ArticuloFabricadoInternamente):
                # La recursión sigue, y si un hijo lanza el raise, 
                # este "sube" automáticamente hasta el nivel más alto.
                elemento.validar_ciclos(nuevo_camino)
        
        return False # Si llega acá, es que todo está OK
    
