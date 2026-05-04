import csv
from empresa import Empresa
from menu_admin import MenuAdministrativo
from menu_prod import MenuProduccion
from inventario import Inventario
class MenuPrincipal:
    def __init__(self):
        mi_inventario = Inventario()
        self.empresa = Empresa(mi_inventario)
        
    
        self.dicc_insumos = {}
        self.dicc_productos = {}
        self.dicc_unidades = {}
        self.dicc_colaboradores = {}
        
        self.menu_admin = MenuAdministrativo(
            self.empresa, self.dicc_insumos, self.dicc_productos, 
            self.dicc_unidades, self.dicc_colaboradores
        )
        self.menu_prod = MenuProduccion(
            self.empresa, self.dicc_insumos, self.dicc_productos, 
            self.dicc_unidades, self.dicc_colaboradores
        )
        
        self.id_actual = None
        self.rol_actual = None

    def _leer_usuarios(self) -> dict:
        usuarios = {}
        try:
            with open("usuarios.csv", "r", encoding="utf-8") as archivo:
                lector = csv.DictReader(archivo)
                for fila in lector:
                    usuarios[fila["id"].strip()] = {
                        "clave": fila["clave"].strip(),
                        "rol": fila["rol"].strip()
                    }
        except FileNotFoundError:
            print("Archivo usuarios.csv no encontrado. Creá el archivo para continuar.")
        return usuarios

    def iniciar_sesion(self) -> bool:
        usuarios_registrados = self._leer_usuarios()
        if not usuarios_registrados: 
            return False

        print("\n" + "="*40)
        print("INICIO DE SESIÓN - SISTEMA TECNOMECÁNICA ITBA ")
        print("="*40)
        
        intentos_maximos = 3
        intentos_realizados = 0
        
        while intentos_realizados < intentos_maximos:
            if intentos_realizados > 0:
                print(f"\nTe quedan {intentos_maximos - intentos_realizados} intento/s.")
                
            id_ingresado = input("Ingrese su ID de Empleado: ").strip()
            clave_ingresada = input("Contraseña: ").strip()
        
            if id_ingresado not in usuarios_registrados:
                print("Usuario incorrecto.")
                intentos_realizados += 1
                
            elif usuarios_registrados[id_ingresado]["clave"] != clave_ingresada:
                print("Contraseña incorrecta.")
                intentos_realizados += 1
            
            else:
                self.id_actual = id_ingresado
                self.rol_actual = usuarios_registrados[id_ingresado]["rol"]
                print(f"\nSesión iniciada. Acceso concedido al rol: {self.rol_actual.upper()}")
                return True
                
        print("\n Se ha superado la cantidad de intentos permitidos.")
        return False

    def ejecutar(self):
        if not self.iniciar_sesion():
            print("Apagando el sistema...")
            return 

        menu_activo = None
        if self.rol_actual == "admin":
            menu_activo = self.menu_admin
        elif self.rol_actual == "prod":
            menu_activo = self.menu_prod

        try:
            continuar = True
            while continuar:
                menu_activo.mostrar_opciones()
                opcion = input("\nSeleccione una opción: ").strip()
                continuar = menu_activo.ejecutar_opcion(opcion)
                
        except KeyboardInterrupt:
            print("\n\n[!] Programa interrumpido por el usuario (Ctrl+C).")
        except Exception as e:
            print(f"\n[!] Error crítico en el sistema: {e}")
        finally:
            print(f"\nSesión cerrada correctamente para el empleado ID: {self.id_actual}.")