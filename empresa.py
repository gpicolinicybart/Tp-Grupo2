

from inventario import Inventario
from compra_insumo import Compra_Insumo
from solicitud_fabricacion import SolicitudDeFabricacion
from colaboradores import Colaborador
from unidad_de_trabajo import UnidadDeTrabajo
from elemento import Elemento
from articulo_fabricado import ArticuloFabricadoInternamente

class Empresa:
    def __init__(self, inventario: Inventario):
        self._inventario = inventario
        self._catalogo_elementos = []
        self._solicitudes = []
        self._unidades = []
        self._habilidades = [] 
        self._colaboradores = []
        self._compras_pendientes = []
        
    def registrar_compra(self,orden: Compra_Insumo):
        self._compras_pendientes.append(orden)
        print(f"EMPRESA: Se registró la orden de compra {orden._id} por {orden._cantidad} unidades de '{orden._insumo._nombre}'.")
    def crear_solicitud (self,solicitud: SolicitudDeFabricacion):
          self._solicitudes.append(solicitud)
          print(f"EMPRESA: Se registró una nueva solicitud de fabricación (ID:{solicitud._id})")
    def procesar_solicitud(self):
        pass
        
    def detectar_cuello_botella(self):
        pass
#estos dos no estan en el diagrama 

    def agregar_colaborador(self, nuevo_colaborador: Colaborador):
        self._colaboradores.append(nuevo_colaborador)
        print(f"EMPRESA: Colaborador ID:{nuevo_colaborador._id} agregado al equipo.")

    def agregar_unidad_trabajo(self, nueva_unidad: UnidadDeTrabajo):
        self._unidades.append(nueva_unidad)
    def registrar_producto_nuevo(self, producto: Elemento):
        """
        Punto de entrada para agregar cosas al catálogo. 
        Aquí es donde usamos el 'validar_ciclos' como guardia de seguridad.
        """
        try:
            # Solo validamos ciclos si es algo que se fabrica
            if isinstance(producto, ArticuloFabricadoInternamente):
                producto.validar_ciclos() # Si hay ciclo, salta al except
            
            self._catalogo_elementos.append(producto)
            print(f"EMPRESA: '{producto._nombre}' registrado exitosamente en el catálogo.")
            
        except ValueError as e:
            print(f"EMPRESA - ERROR AL REGISTRAR: {e}")

    def obtener_presupuesto(self, producto: Elemento, cantidad: int) -> float:
        """
        Método para informarle al cliente cuánto le va a salir.
        Usa el 'get_costo_unitario' del producto.
        """
        costo_unitario = producto.get_costo_unitario()
        total = costo_unitario * cantidad
        print(f"PRESUPUESTO: Fabricar {cantidad} unidades de '{producto._nombre}' cuesta ${total:.2f}")
        return total



