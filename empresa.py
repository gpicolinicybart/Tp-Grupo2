

from inventario import Inventario
from compra_insumo import Compra_Insumo
from solicitud_fabricacion import SolicitudDeFabricacion
from colaboradores import Colaborador
from unidad_de_trabajo import UnidadDeTrabajo


class Empresa:
    def __init__(self, inventario: Inventario):
        self._inventario = inventario
        self._catalogo_elementos = []
        self._solicitudes = []
        self._unidades = []
        self._habilidades = [] 
        self._colaboradores = []
        self._compras_pendientes = []

    def __str__(self):
        return f"Empresa TecnoMecánica ITBA | Colaboradores: {len(self._colaboradores)} | Solicitudes activas: {len(self._solicitudes)}"
       
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

    def agregar_colaborador(self, nuevo_colaborador: Colaborador):
        self._colaboradores.append(nuevo_colaborador)
        print(f"EMPRESA: Colaborador ID:{nuevo_colaborador._id} agregado al equipo.")

    def agregar_unidad_trabajo(self, nueva_unidad: UnidadDeTrabajo):
        self._unidades.append(nueva_unidad)

