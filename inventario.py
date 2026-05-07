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

    # =====================================================================
    # MÉTODOS DE PERSISTENCIA (Sincronización con archivos CSV)
    # =====================================================================

    def guardar_en_csv(self, archivo_csv="inventario.csv"):
        with open(archivo_csv, mode='w', newline='', encoding='utf-8') as archivo:
            writer = csv.writer(archivo)
            writer.writerow(["id_elemento", "nombre_referencia", "stock_fisico", "stock_reservado"])
            
            # Unimos las claves de ambos diccionarios por si hay algo reservado pero sin stock físico
            elementos_unicos = set(self._stock_fisico.keys()).union(set(self._stock_reservado.keys()))
            
            for elem in elementos_unicos:
                # Usamos getattr por seguridad, asumiendo que todos tienen un ID o nombre
                id_elem = elem.get_id() if hasattr(elem, 'get_id') else getattr(elem, '_id', 'N/A')
                nombre = elem.get_nombre() if hasattr(elem, 'get_nombre') else getattr(elem, '_nombre', 'Desconocido')
                
                fisico = self._stock_fisico.get(elem, 0)
                reservado = self._stock_reservado.get(elem, 0)
                
                writer.writerow([id_elem, nombre, fisico, reservado])

    def obtener_stock_reservado(self, elem: Elemento) -> int:
        return self._stock_reservado.get(elem, 0)

    def cargar_desde_csv(self, elementos_catalogo: list, archivo_csv="inventario.csv"):
        if not os.path.exists(archivo_csv):
            return

        elementos_por_id = {}
        elementos_por_nombre = {}
        for elemento in elementos_catalogo:
            if hasattr(elemento, 'get_id'):
                elementos_por_id[str(elemento.get_id())] = elemento
            if hasattr(elemento, 'get_nombre'):
                elementos_por_nombre[elemento.get_nombre()] = elemento

        try:
            with open(archivo_csv, mode='r', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                for fila in reader:
                    id_elem = fila.get('id_elemento', '').strip()
                    nombre = fila.get('nombre_referencia', '').strip()
                    fisico = int(fila.get('stock_fisico', 0))
                    reservado = int(fila.get('stock_reservado', 0))

                    elemento = elementos_por_id.get(id_elem) or elementos_por_nombre.get(nombre)
                    if elemento is None:
                        continue

                    if fisico:
                        self._stock_fisico[elemento] = fisico
                    if reservado:
                        self._stock_reservado[elemento] = reservado
        except Exception as e:
            print(f"-> [ERROR] Falló la carga de inventario desde CSV: {e}")