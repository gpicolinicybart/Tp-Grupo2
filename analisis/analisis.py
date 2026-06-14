import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv
import os

class Analisis:
    # toma el dataset generado por GeneradorDatos y calcula las metricas del MRP:
    # explosion de materiales vs stock, carga de las unidades y costos de fabricacion.
    # hay que correr primero generador_datos.py.

    ESTADOS_ACTIVOS = {"Creada", "Planificada", "En Curso"}
    COLORES_CAT = {"Mecánico": "#e74c3c", "Eléctrico": "#3498db", "Hidráulico": "#27ae60"}

    def __init__(self, carpeta="datos"):
        self._carpeta = os.path.join(os.path.dirname(__file__), carpeta)
        self._costos = {} # memoria para no recalcular el costo de un mismo articulo
        self._cargar()

    def _leer(self, nombre):
        ruta = os.path.join(self._carpeta, nombre)
        with open(ruta, mode='r', newline='', encoding='utf-8') as archivo:
            return list(csv.DictReader(archivo))

    def _cargar(self):
        self._elementos = self._leer("elementos.csv")
        self._unidades = self._leer("unidades.csv")
        self._solicitudes = self._leer("solicitudes.csv")
        bom = self._leer("bom.csv")
        tareas = self._leer("tareas.csv")

        # indices para no andar recorriendo las listas a cada rato
        self._elem_por_id = {int(e["id_elemento"]): e for e in self._elementos}
        self._unidad_por_id = {int(u["id_unidad"]): u for u in self._unidades}

        self._bom_dict = {} # producto_padre -> [(componente, cantidad)]
        for fila in bom:
            padre = int(fila["producto_padre"])
            self._bom_dict.setdefault(padre, []).append(
                (int(fila["componente"]), int(fila["cantidad_requerida"])))

        self._tareas_por_art = {} # articulo -> lista de tareas
        for t in tareas:
            self._tareas_por_art.setdefault(int(t["articulo"]), []).append(t)

        # las solicitudes activas son las que todavia van a consumir recursos
        self._activas = [s for s in self._solicitudes if s["estado"] in self.ESTADOS_ACTIVOS]

    def _tipo(self, id_elem):
        return self._elem_por_id[id_elem]["tipo"]

    def _explotar(self, id_prod, cant, acum):
        # baja recursivamente por la BOM hasta los insumos basicos
        if self._tipo(id_prod) == "Insumo" or id_prod not in self._bom_dict:
            if self._tipo(id_prod) == "Insumo":
                acum[id_prod] = acum.get(id_prod, 0) + cant
            return
        for comp, cant_unit in self._bom_dict[id_prod]:
            self._explotar(comp, cant * cant_unit, acum)

    def _fabricados_involucrados(self, id_prod, cant, acum=None):
        # como _explotar pero junta los articulos fabricados (no los insumos),
        # que son los que cargan horas en las unidades de trabajo
        if acum is None:
            acum = {}
        if id_prod not in self._bom_dict:
            return acum
        acum[id_prod] = acum.get(id_prod, 0) + cant
        for comp, cant_unit in self._bom_dict[id_prod]:
            self._fabricados_involucrados(comp, cant * cant_unit, acum)
        return acum

    def _costo_unitario(self, id_elem):
        # los insumos tienen costo fijo; los fabricados suman costo de materiales
        # (su BOM) mas el costo de manufactura (unidad x tiempo de cada tarea)
        if id_elem in self._costos:
            return self._costos[id_elem]
        elem = self._elem_por_id[id_elem]
        if elem["tipo"] == "Insumo":
            self._costos[id_elem] = float(elem["costo_unitario"])
            return self._costos[id_elem]
        costo_mat = sum(self._costo_unitario(c) * q for c, q in self._bom_dict.get(id_elem, []))
        costo_mfg = 0.0
        for t in self._tareas_por_art.get(id_elem, []):
            unidad = self._unidad_por_id.get(int(t["id_unidad"]))
            if unidad is not None:
                costo_mfg += float(unidad["costo_hora"]) * float(t["tiempo_estandar"])
        self._costos[id_elem] = costo_mat + costo_mfg
        return self._costos[id_elem]

    def analizar_inventario(self):
        print("\n--- ANALISIS 1: EXPLOSION DE MATERIALES vs STOCK ---")
        # explotamos la BOM de todas las solicitudes activas y acumulamos la demanda
        demanda = {}
        for sol in self._activas:
            parcial = {}
            self._explotar(int(sol["producto"]), int(sol["cantidad"]), parcial)
            for id_ins, cant in parcial.items():
                demanda[id_ins] = demanda.get(id_ins, 0) + cant

        ids = np.array(list(demanda.keys()))
        demandas = np.array(list(demanda.values()), dtype=float)
        stocks = np.array([int(self._elem_por_id[i]["stock_actual"]) for i in ids], dtype=float)
        cobertura = np.where(demandas > 0, stocks / demandas * 100, 100.0)

        criticos = int(np.sum(cobertura < 100))
        print(f"Solicitudes activas analizadas: {len(self._activas)}")
        print(f"Materiales distintos demandados: {len(demanda)}")
        print(f"Demanda promedio / mediana: {np.mean(demandas):.0f} / {np.median(demandas):.0f} unidades")
        print(f"Desviacion estandar: {np.std(demandas):.0f}")
        print(f"Materiales con stock critico: {criticos} ({criticos / len(demandas) * 100:.1f}%)")
        print(f"Cobertura promedio de stock: {np.mean(cobertura):.1f}%")

        # nos quedamos con los 15 mas demandados para que el grafico sea legible
        top = np.argsort(demandas)[-15:][::-1]
        nombres = [self._elem_por_id[i]["nombre"] for i in ids[top]]

        _, ax = plt.subplots(figsize=(13, 6))
        x = np.arange(len(nombres))
        ancho = 0.38
        ax.bar(x - ancho / 2, demandas[top], width=ancho, label="Demanda requerida", color="#e74c3c", alpha=0.9)
        ax.bar(x + ancho / 2, stocks[top], width=ancho, label="Stock disponible", color="#2ecc71", alpha=0.9)
        ax.set_title("Top 15 Materiales: Demanda Requerida vs Stock Disponible", fontsize=14, pad=12)
        ax.set_xlabel("Material")
        ax.set_ylabel("Unidades")
        ax.set_xticks(x)
        ax.set_xticklabels(nombres, rotation=40, ha="right", fontsize=8)
        ax.legend()
        ax.grid(axis="y", alpha=0.35)
        plt.tight_layout()
        self._guardar_figura("grafico_1_inventario.png")

    def analizar_unidades(self):
        print("\n--- ANALISIS 2: CARGA Y UTILIZACION DE UNIDADES ---")
        horas_req = {int(u["id_unidad"]): 0.0 for u in self._unidades}
        for sol in self._activas:
            fabs = self._fabricados_involucrados(int(sol["producto"]), int(sol["cantidad"]))
            for id_art, cant_art in fabs.items():
                for t in self._tareas_por_art.get(id_art, []):
                    uid = int(t["id_unidad"])
                    if uid in horas_req:
                        horas_req[uid] += cant_art * float(t["tiempo_estandar"])

        # la capacidad del CSV es POR PERIODO, pero el backlog activo abarca varios
        # meses, asi que la capacidad real disponible es la del periodo x cant. de periodos
        periodos = sorted({s["fecha"][:7] for s in self._activas})
        n_periodos = max(1, len(periodos))

        nombres = np.array([u["nombre"] for u in self._unidades])
        horas_disp = np.array([float(u["capacidad_horas_periodo"]) * n_periodos for u in self._unidades])
        horas = np.array([horas_req[int(u["id_unidad"])] for u in self._unidades])
        utilizacion = np.where(horas_disp > 0, horas / horas_disp * 100, 0.0)
        orden = np.argsort(utilizacion)[::-1]

        print(f"Horizonte de planificacion: {n_periodos} periodos ({periodos[0]} a {periodos[-1]})")
        print(f"Utilizacion promedio / mediana: {np.mean(utilizacion):.1f}% / {np.median(utilizacion):.1f}%")
        print(f"Unidad mas cargada: {nombres[np.argmax(utilizacion)]} ({np.max(utilizacion):.1f}%)")
        print(f"Unidad mas libre: {nombres[np.argmin(utilizacion)]} ({np.min(utilizacion):.1f}%)")
        print(f"Unidades saturadas (>100%): {int(np.sum(utilizacion > 100))}")

        # color segun que tan exigida esta cada unidad
        colores = ["#e74c3c" if u > 100 else "#f39c12" if u > 75 else "#2ecc71"
                   for u in utilizacion[orden]]
        _, ax = plt.subplots(figsize=(13, 6))
        x = np.arange(len(nombres))
        ax.bar(x, utilizacion[orden], color=colores, alpha=0.88)
        ax.axhline(100, color="crimson", linestyle="--", linewidth=1.5)
        ax.text(len(nombres) - 0.5, 102, "Capacidad máxima", color="crimson", fontsize=8, ha="right")
        ax.set_title("Porcentaje de Utilización por Unidad de Trabajo", fontsize=14, pad=12)
        ax.set_xlabel("Unidad de Trabajo")
        ax.set_ylabel("Utilización (%)")
        ax.set_xticks(x)
        ax.set_xticklabels(nombres[orden], rotation=40, ha="right", fontsize=8)
        leyenda = [mpatches.Patch(color="#e74c3c", label="Saturada (> 100%)"),
                   mpatches.Patch(color="#f39c12", label="Alta carga (75–100%)"),
                   mpatches.Patch(color="#2ecc71", label="Normal (< 75%)")]
        ax.legend(handles=leyenda, loc="upper right")
        ax.grid(axis="y", alpha=0.35)
        plt.tight_layout()
        self._guardar_figura("grafico_2_unidades.png")

    def analizar_costos(self):
        print("\n--- ANALISIS 3: COSTOS DE FABRICACION ---")
        fabricados = [e for e in self._elementos if e["tipo"] == "Fabricado"]
        costos = np.array([self._costo_unitario(int(e["id_elemento"])) for e in fabricados])
        categorias = np.array([e["categoria"] for e in fabricados])

        p25, p75 = np.percentile(costos, [25, 75])
        print(f"Costo unitario promedio: ${np.mean(costos):,.2f}")
        print(f"Costo mediano: ${np.median(costos):,.2f}")
        print(f"Desviacion estandar: ${np.std(costos):,.2f}")
        print(f"Minimo / Maximo: ${np.min(costos):,.2f} / ${np.max(costos):,.2f}")
        print(f"Percentiles 25 / 75: ${p25:,.2f} / ${p75:,.2f}")
        for cat in sorted(set(categorias)):
            mascara = categorias == cat
            print(f"   [{cat}] n={mascara.sum()} prom=${np.mean(costos[mascara]):,.0f} σ=${np.std(costos[mascara]):,.0f}")

        # para el scatter cruzamos la cantidad pedida con el costo del producto
        costo_por_id = {int(e["id_elemento"]): self._costo_unitario(int(e["id_elemento"])) for e in fabricados}
        cat_por_id = {int(e["id_elemento"]): e["categoria"] for e in fabricados}
        pedidas = [s for s in self._solicitudes if int(s["producto"]) in costo_por_id]
        sc_cant = np.array([int(s["cantidad"]) for s in pedidas])
        sc_costo = np.array([costo_por_id[int(s["producto"])] for s in pedidas])
        sc_cat = np.array([cat_por_id[int(s["producto"])] for s in pedidas])

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle("Análisis de Costos de Fabricación", fontsize=15)

        ax1.hist(costos, bins=15, color="#3498db", edgecolor="white", alpha=0.85)
        ax1.axvline(np.mean(costos), color="#e74c3c", linestyle="--", label=f"Media: ${np.mean(costos):,.0f}")
        ax1.axvline(np.median(costos), color="#f39c12", linestyle="--", label=f"Mediana: ${np.median(costos):,.0f}")
        ax1.set_title("Distribución de Costos Unitarios")
        ax1.set_xlabel("Costo Unitario ($)")
        ax1.set_ylabel("Frecuencia")
        ax1.legend(fontsize=8)
        ax1.grid(axis="y", alpha=0.35)

        for cat, color in self.COLORES_CAT.items():
            mascara = sc_cat == cat
            ax2.scatter(sc_cant[mascara], sc_costo[mascara], alpha=0.35, s=14, color=color, label=cat)
        ax2.set_title("Cantidad Pedida vs Costo Unitario por Categoría")
        ax2.set_xlabel("Cantidad Solicitada")
        ax2.set_ylabel("Costo Unitario ($)")
        ax2.legend(fontsize=8)
        ax2.grid(alpha=0.3)
        plt.tight_layout()
        self._guardar_figura("grafico_3_costos.png")

    def _guardar_figura(self, nombre):
        ruta = os.path.join(os.path.dirname(__file__), nombre)
        plt.savefig(ruta, dpi=130)
        plt.show()
        print(f"-> Grafico guardado en '{nombre}'")

    def correr(self):
        self.analizar_inventario()
        self.analizar_unidades()
        self.analizar_costos()


if __name__ == "__main__":
    analisis = Analisis()
    analisis.correr()
