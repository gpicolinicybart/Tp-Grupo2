import csv
import os
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
            print(f"-> RESERVA: Se reservaron {cant} unidades de '{elem.get_nombre()}'.")
        else:
            print(f"->ALERTA: No hay stock suficiente para reservar {cant} de '{elem.get_nombre()}'.")
            
    def descontar_stock(self, elem: Elemento, cant: int):
        # se descuenta el fisico y la reserva cuando se arranca a producir
        self.validar_cantidad(cant)
        if elem in self._stock_reservado and self._stock_reservado[elem]>=cant:
            self._stock_fisico[elem]-=cant 
            self._stock_reservado[elem]-=cant 
            print(f"->CONSUMO: Se utilizaron {cant} unidades de '{elem.get_nombre()}'.")
        else:
            print(f"->ERROR: Intentando consumir '{elem.get_nombre()}' sin reserva previa.")
        
    def ingresar_stock(self, elem: Elemento, cant: int):
        self.validar_cantidad(cant)
        if elem in self._stock_fisico:
            self._stock_fisico[elem]+=cant
        else: 
            self._stock_fisico[elem]=cant
    

    def hay_disponibilidad(self, elem: Elemento, cant_pedida: int) -> bool:
        return self.obtener_stock_disponible(elem) >= cant_pedida
    
    def obtener_stock_disponible(self, elem: Elemento) -> int:
        #Retorna el stock disponible (físico - reservado) sin acceso directo a atributos privados
        stock_real = self.consultar_stock(elem)
        reservado = self._stock_reservado.get(elem, 0)
        return stock_real - reservado
    
    @staticmethod
    def validar_cantidad(cant: int) -> bool:
        if cant <= 0:
            raise ValueError("Error: La cantidad debe ser mayor a cero.")
        return True
    
    def obtener_materiales_criticos(self, necesidades: dict) -> list:
        def es_critico(item):
            # Calcula los materiales cuyo stock disponible es menor al 20% de la cantidad necesaria
            return self.consultar_stock(item[0]) < (0.20 * item[1])
        return list(filter(es_critico, necesidades.items()))

    # ---------------------------------------------------------------------
    # MÉTODOS DE PERSISTENCIA (Sincronización con archivos CSV)

    def obtener_stock_reservado(self, elem: Elemento) -> int:
        return self._stock_reservado.get(elem, 0)

    def exportar_stock(self) -> list:
        # Reunir todos los elementos que aparezcan en cualquiera de los dos diccionarios
        elementos = set()
        for elemento in self._stock_fisico:
            elementos.add(elemento)
        for elemento in self._stock_reservado:
            elementos.add(elemento)

        # Armar la lista de tuplas 
        resultado = []
        for elemento in elementos:
            fisico = self._stock_fisico.get(elemento, 0)
            reservado = self._stock_reservado.get(elemento, 0)
            resultado.append((elemento, fisico, reservado))
        return resultado

    def establecer_stock(self, elemento, fisico, reservado):
        if fisico:
            self._stock_fisico[elemento] = fisico
        if reservado:
            self._stock_reservado[elemento] = reservado
            
    COLUMNAS_STOCK = ["id_elemento", "nombre_referencia", "stock_fisico", "stock_reservado"]

    def serializar_stock(self):
        filas = []
        for elem in self._stock_fisico:
            fisico = self._stock_fisico.get(elem, 0)
            reservado = self._stock_reservado.get(elem, 0)
            filas.append([elem.get_id(), elem.get_nombre(), fisico, reservado])
        return filas