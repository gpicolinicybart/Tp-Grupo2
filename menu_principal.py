
import csv
from empresa import Empresa
from menu_admin import MenuAdministrativo
from menu_prod import MenuProduccion
from inventario import Inventario

class MenuPrincipal:
    def __init__(self):
        self.empresa = None
        self.id_actual = None
        self.rol_actual = None
        
        self._inicializar()
        
        self.cargar_datos()
        
        self.menu_admin = MenuAdministrativo(self.empresa)
        self.menu_prod = MenuProduccion(self.empresa)

    def _inicializar(self):
        mi_inventario = Inventario()
        self.empresa = Empresa(mi_inventario)

    def cargar_datos(self):
        print("Cargando memoria del sistema desde archivos CSV...")
        try:
            
            self.empresa.cargar_todos_los_datos()
            print("Memoria cargada exitosamente.")
        except OSError:
            print("Aviso al leer los CSV. Iniciando catálogos en blanco...")

    def guardar_datos(self):
        print("Guardando progreso en archivos CSV...")
        try:
            self.empresa.guardar_todos_los_datos()
            print("\n Progreso guardado correctamente en los archivos CSV.")
        except OSError as e:
            print(f" Error crítico de escritura en el disco duro")

   

    def iniciar_sesion(self) -> bool:
        usuarios_registrados = self.empresa.obtener_gestor_archivos().cargar_usuarios_csv()
        if not usuarios_registrados: 
            return False

        print("\n" + "="*40)
        print(" INICIO DE SESIÓN - SISTEMA TECNOMECÁNICA ITBA ")
        print("="*40)
        
        intentos_maximos = 3
        intentos_realizados = 0
        
        while intentos_realizados < intentos_maximos:
            if intentos_realizados > 0:
                print(f"\n Te quedan {intentos_maximos - intentos_realizados} intento(s).")
                
            id_ingresado = input("Ingrese su ID de Empleado: ").strip()
            clave_ingresada = input("Contraseña: ").strip()
            
            if id_ingresado not in usuarios_registrados:
                print(" Usuario incorrecto.")
                intentos_realizados += 1
            elif usuarios_registrados[id_ingresado]["clave"] != clave_ingresada:
                print(" Contraseña incorrecta.")
                intentos_realizados += 1
            else:
                self.id_actual = id_ingresado
                self.rol_actual = usuarios_registrados[id_ingresado]["rol"]
                print(f"\n Sesión iniciada. Acceso concedido al rol: {self.rol_actual.upper()}")
                return True
                
        print("\n Se ha superado la cantidad de intentos permitidos.")
        return False

    def ejecutar(self):
        if not self.iniciar_sesion():
            print("Apagando el sistema...")
            return 

        menu_activo = None
        if self.rol_actual == "administracion":
            menu_activo = self.menu_admin
        elif self.rol_actual == "produccion":
            menu_activo = self.menu_prod

        try:
            continuar = True
            while continuar:
                menu_activo.mostrar_opciones()
                opcion = input("\nSeleccione una opción: ").strip()
                continuar = menu_activo.ejecutar_opcion(opcion)
                
        except KeyboardInterrupt:
            print("\n\n[!] Programa interrumpido por el usuario (Ctrl+C).")
            
        finally:
            self.guardar_datos()
            if self.id_actual:
                print(f"Sesión cerrada para el empleado ID: {self.id_actual}.")