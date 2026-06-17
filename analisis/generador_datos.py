import numpy as np
import csv
import os
import datetime

class GeneradorDatos:
    CATEGORIAS = ["Mecánico", "Eléctrico", "Hidráulico"]
    PERIODOS = ["Mañana", "Tarde", "Noche"]
    ESPECIALIDADES = ["Soldadura", "Mecanizado", "Ensamblaje", "Pintura", "Control de Calidad", "Hidráulica"]

    ESTADOS = ["Creada", "Planificada", "En Curso", "Terminada",
               "Demorada por falta de stock", "Demorada por falta de capacidad"]
    PESOS_ESTADO = [0.15, 0.20, 0.25, 0.25, 0.10, 0.05]
    ESTADOS_ACTIVOS = ("Creada", "Planificada", "En Curso")

    NOMBRES_UNIDADES = [
        "Corte CNC", "Soldadura MIG", "Ensamble A", "Ensamble B", "Pintura",
        "Pruebas Eléctricas", "Torneado", "Fresado", "Control Calidad",
        "Hidráulica", "Corte Plasma", "Soldadura TIG", "Ensamble Final",
        "Pintura Electrostática", "Pruebas Hidráulicas", "Desbaste",
        "Pulido", "Mecanizado CNC", "Inspección Final", "Almacén"
    ]
    PREFIJOS = ["Tubo", "Placa", "Tornillo", "Válvula", "Cable", "Sensor",
                "Rodamiento", "Resorte", "Filtro", "Conector", "Brida",
                "Junta", "Engranaje", "Bulón", "Perno"]

    def __init__(self, n_insumos=140, n_fabricados=60, n_unidades=20,
                 n_colaboradores=100, n_solicitudes=1000, carpeta="datos", semilla=42):
        self._n_insumos = n_insumos
        self._n_fabricados = n_fabricados
        self._n_unidades = n_unidades
        self._n_colaboradores = n_colaboradores
        self._n_solicitudes = n_solicitudes
        self._carpeta = os.path.join(os.path.dirname(__file__), carpeta)
        os.makedirs(self._carpeta, exist_ok=True)
        np.random.seed(semilla)
        self._unidades = []
        self._elementos = []
        self._bom = []
        self._tareas = []
        self._colaboradores = []
        self._solicitudes = []
        self._bom_dict = {}
        self._tipo = {}

    def _escribir_csv(self, nombre, columnas, filas):
        ruta = os.path.join(self._carpeta, nombre)
        with open(ruta, mode='w', newline='', encoding='utf-8') as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=columnas)
            escritor.writeheader()
            escritor.writerows(filas)

    def generar_unidades(self):
        for i in range(1, self._n_unidades + 1):
            self._unidades.append({
                "id_unidad": i,
                "nombre": self.NOMBRES_UNIDADES[i - 1],
                "capacidad_horas_periodo": round(float(np.random.uniform(300, 900)), 1),
                "max_colaboradores": int(np.random.randint(3, 13)),
                "costo_hora": round(float(np.random.uniform(200, 1200)), 2),
            })
        self._escribir_csv("unidades.csv", list(self._unidades[0].keys()), self._unidades)

    def generar_elementos(self):
        for i in range(1, self._n_insumos + 1):
            prefijo = np.random.choice(self.PREFIJOS)
            self._elementos.append({
                "id_elemento": i,
                "nombre": f"{prefijo}-{i:03d}",
                "tipo": "Insumo",
                "categoria": np.random.choice(self.CATEGORIAS),
                "costo_unitario": round(float(np.random.uniform(10, 8000)), 2),
                "stock_actual": 0,
            })
        for j in range(1, self._n_fabricados + 1):
            i = self._n_insumos + j
            es_final = j > 42
            self._elementos.append({
                "id_elemento": i,
                "nombre": f"Producto-{i:03d}" if es_final else f"Ensamble-{i:03d}",
                "tipo": "Fabricado",
                "categoria": np.random.choice(self.CATEGORIAS),
                "costo_unitario": 0,
                "stock_actual": int(np.random.randint(0, 50)),
            })
        for e in self._elementos:
            self._tipo[e["id_elemento"]] = e["tipo"]

    def generar_bom(self):
        insumos = [e["id_elemento"] for e in self._elementos if e["tipo"] == "Insumo"]
        ensambles = [e["id_elemento"] for e in self._elementos
                     if e["tipo"] == "Fabricado" and e["nombre"].startswith("Ensamble")]
        mitad = len(ensambles) // 2
        nivel1 = set(ensambles[:mitad])
        nivel2 = set(ensambles[mitad:])

        for elem in self._elementos:
            if elem["tipo"] != "Fabricado":
                continue
            id_fab = elem["id_elemento"]
            if id_fab in nivel1:
                pool_sub = []
            elif id_fab in nivel2:
                pool_sub = list(nivel1)
            else:
                pool_sub = list(nivel1) + list(nivel2)

            n_comp = int(np.random.randint(2, 7))
            n_sub = int(min(np.random.choice([0, 0, 1, 1, 2]), len(pool_sub), n_comp - 1))
            componentes = []
            if n_sub > 0:
                componentes += list(np.random.choice(pool_sub, size=n_sub, replace=False))
            componentes += list(np.random.choice(insumos, size=n_comp - n_sub, replace=False))

            for comp in componentes:
                self._bom.append({
                    "producto_padre": id_fab,
                    "componente": int(comp),
                    "cantidad_requerida": int(np.random.randint(1, 5)),
                })
        for fila in self._bom:
            self._bom_dict.setdefault(fila["producto_padre"], []).append(
                (fila["componente"], fila["cantidad_requerida"]))
        self._escribir_csv("bom.csv", ["producto_padre", "componente", "cantidad_requerida"], self._bom)

    def generar_tareas(self):
        id_tarea = 1
        for elem in self._elementos:
            if elem["tipo"] != "Fabricado":
                continue
            for _ in range(int(np.random.randint(1, 6))):
                unidad = np.random.choice(self._unidades)
                self._tareas.append({
                    "id_tarea": id_tarea,
                    "articulo": elem["id_elemento"],
                    "id_unidad": unidad["id_unidad"],
                    "colaboradores_requeridos": int(np.random.randint(1, min(5, unidad["max_colaboradores"]) + 1)),
                    "tiempo_estandar": round(float(np.random.uniform(0.25, 6.0)), 2),
                })
                id_tarea += 1
        self._escribir_csv("tareas.csv", list(self._tareas[0].keys()), self._tareas)

    def generar_colaboradores(self):
        for i in range(1, self._n_colaboradores + 1):
            self._colaboradores.append({
                "id_colaborador": i,
                "especialidad": np.random.choice(self.ESPECIALIDADES),
                "horas_disponibles": round(float(np.random.uniform(20, 40)), 1),
                "periodo": np.random.choice(self.PERIODOS),
            })
        self._escribir_csv("colaboradores.csv", list(self._colaboradores[0].keys()), self._colaboradores)

    def generar_solicitudes(self):
        finales = [e["id_elemento"] for e in self._elementos
                   if e["tipo"] == "Fabricado" and e["nombre"].startswith("Producto")]
        for i in range(1, self._n_solicitudes + 1):
            mes = int(np.random.randint(1, 7))
            dia = int(np.random.randint(1, 28))
            self._solicitudes.append({
                "id_solicitud": i,
                "producto": int(np.random.choice(finales)),
                "cantidad": int(np.random.randint(1, 6)),
                "fecha": f"2026-{mes:02d}-{dia:02d}",
                "estado": np.random.choice(self.ESTADOS, p=self.PESOS_ESTADO),
            })
        self._escribir_csv("solicitudes.csv", list(self._solicitudes[0].keys()), self._solicitudes)

    def _explotar(self, id_prod, cant, acum):
        if self._tipo[id_prod] == "Insumo" or id_prod not in self._bom_dict:
            if self._tipo[id_prod] == "Insumo":
                acum[id_prod] = acum.get(id_prod, 0) + cant
            return
        for comp, cant_unit in self._bom_dict[id_prod]:
            self._explotar(comp, cant * cant_unit, acum)

    def asignar_stock(self):
        demanda = {}
        for sol in self._solicitudes:
            if sol["estado"] in self.ESTADOS_ACTIVOS:
                self._explotar(sol["producto"], sol["cantidad"], demanda)
        for elem in self._elementos:
            if elem["tipo"] != "Insumo":
                continue
            necesidad = demanda.get(elem["id_elemento"], 0)
            if necesidad > 0:
                elem["stock_actual"] = max(1, int(necesidad * float(np.random.uniform(0.35, 1.75))))
            else:
                elem["stock_actual"] = int(np.random.randint(50, 500))
        columnas = ["id_elemento", "nombre", "tipo", "categoria", "costo_unitario", "stock_actual"]
        self._escribir_csv("elementos.csv", columnas, self._elementos)
        return demanda

    def poblar_compras_produccion(self, n_compras=1000):
        ruta_csv_principal = os.path.join(os.path.dirname(__file__), "..", "csv")
        ruta_insumos = os.path.join(ruta_csv_principal, "inventario.csv")
        ruta_destino_compras = os.path.join(ruta_csv_principal, "compras.csv")
        ids_insumos_reales = []
        try:
            with open(ruta_insumos, mode='r', newline='', encoding='utf-8') as archivo:
                lector = csv.DictReader(archivo)
                for fila in lector:
                    id_ins = fila.get("ID") or fila.get("id_elemento") or fila.get("Insumo_ID")
                    if id_ins:
                        ids_insumos_reales.append(int(id_ins))
        except FileNotFoundError:
            print(" [!] No se encontró el inventario real. Abortando.")
            return

        if not ids_insumos_reales:
            print(" [!] El catálogo está vacío. No se pueden generar compras.")
            return

        compras_sinteticas = []

        for i in range(1, n_compras + 1):
            mes = int(np.random.randint(1, 7))
            dia = int(np.random.randint(1, 28))
            hora = int(np.random.randint(8, 20))
            minuto = int(np.random.randint(0, 60))
            segundo = int(np.random.randint(0, 60))
            f_emision_dt = datetime.datetime(2026, mes, dia, hora, minuto, segundo)            
            estado = "Recibida"
            dias_demora = int(np.random.randint(1, 5))
            f_recepcion_dt = f_emision_dt + datetime.timedelta(days=dias_demora)

            compras_sinteticas.append({
                "ID": i,
                "Insumo_ID": int(np.random.choice(ids_insumos_reales)),
                "Cantidad": int(np.random.randint(10, 200)),
                "Estado": estado,
                "Fecha_Emision": f_emision_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "Fecha_Recepcion": f_recepcion_dt.strftime("%Y-%m-%d %H:%M:%S")
            })
        columnas = ["ID", "Insumo_ID", "Cantidad", "Estado", "Fecha_Emision", "Fecha_Recepcion"]
        with open(ruta_destino_compras, mode='w', newline='', encoding='utf-8') as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=columnas)
            escritor.writeheader()
            escritor.writerows(compras_sinteticas)
        print(f" -> ÉXITO: '{ruta_destino_compras}' poblado con {n_compras} compras (Todas en estado 'Recibida').")

    def generar_todo(self):
        self.generar_unidades()
        self.generar_elementos()
        self.generar_bom()
        self.generar_tareas()
        self.generar_colaboradores()
        self.generar_solicitudes()
        demanda = self.asignar_stock()
        self.poblar_compras_produccion(n_compras=1000)

        con_demanda = sum(1 for e in self._elementos
            if e["tipo"] == "Insumo" and demanda.get(e["id_elemento"], 0) > 0)
        print(f"\n-> Dataset de Análisis generado en '{self._carpeta}'")
        print(f"   {len(self._unidades)} unidades de trabajo")
        print(f"   {self._n_insumos} insumos + {self._n_fabricados} fabricados = {len(self._elementos)} elementos")
        print(f"   {len(self._bom)} relaciones BOM")
        print(f"   {len(self._tareas)} tareas | {len(self._colaboradores)} colaboradores")
        print(f"   {len(self._solicitudes)} solicitudes de fabricacion")
        print(f"   {con_demanda}/{self._n_insumos} insumos con demanda activa")

if __name__ == "__main__":
    generador = GeneradorDatos()
    generador.generar_todo()
