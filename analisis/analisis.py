import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv
import os

class Analisis:
    ESTADOS_ACTIVOS = {"Creada", "Planificada", "En Curso"}
    COLORES_CAT = {"Mecánico": "#e74c3c", "Eléctrico": "#3498db", "Hidráulico": "#27ae60"}

    def __init__(self, carpeta="datos"):
        self._carpeta = os.path.join(os.path.dirname(__file__), carpeta)
        self._costos = {}                                                           
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

        self._elem_por_id = {int(e["id_elemento"]): e for e in self._elementos}
        self._unidad_por_id = {int(u["id_unidad"]): u for u in self._unidades}

        self._bom_dict = {}                                             
        for fila in bom:
            padre = int(fila["producto_padre"])
            self._bom_dict.setdefault(padre, []).append(
                (int(fila["componente"]), int(fila["cantidad_requerida"])))

        self._tareas_por_art = {}                              
        for t in tareas:
            self._tareas_por_art.setdefault(int(t["articulo"]), []).append(t)

        self._activas = [s for s in self._solicitudes if s["estado"] in self.ESTADOS_ACTIVOS]

    def _tipo(self, id_elem):
        return self._elem_por_id[id_elem]["tipo"]

    def _explotar(self, id_prod, cant, acum):
                                                                  
        if self._tipo(id_prod) == "Insumo" or id_prod not in self._bom_dict:
            if self._tipo(id_prod) == "Insumo":
                acum[id_prod] = acum.get(id_prod, 0) + cant
            return
        for comp, cant_unit in self._bom_dict[id_prod]:
            self._explotar(comp, cant * cant_unit, acum)

    def _fabricados_involucrados(self, id_prod, cant, acum=None):
        if acum is None:
            acum = {}
        if id_prod not in self._bom_dict:
            return acum
        acum[id_prod] = acum.get(id_prod, 0) + cant
        for comp, cant_unit in self._bom_dict[id_prod]:
            self._fabricados_involucrados(comp, cant * cant_unit, acum)
        return acum

    def _desglose_costo(self, id_elem):
        if id_elem in self._costos:
            return self._costos[id_elem]
        elem = self._elem_por_id[id_elem]
        if elem["tipo"] == "Insumo":
            self._costos[id_elem] = (float(elem["costo_unitario"]), 0.0)
            return self._costos[id_elem]
        mat = mfg = 0.0
        for comp, q in self._bom_dict.get(id_elem, []):
            m, f = self._desglose_costo(comp)
            mat += m * q
            mfg += f * q
        for t in self._tareas_por_art.get(id_elem, []):
            unidad = self._unidad_por_id.get(int(t["id_unidad"]))
            if unidad is not None:
                mfg += float(unidad["costo_hora"]) * float(t["tiempo_estandar"])
        self._costos[id_elem] = (mat, mfg)
        return self._costos[id_elem]

    def _costo_unitario(self, id_elem):
        mat, mfg = self._desglose_costo(id_elem)
        return mat + mfg

    def analizar_inventario(self):
        print("\n--- ANALISIS 1: EXPLOSION DE MATERIALES vs STOCK ---")
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

        desglose = [self._desglose_costo(int(e["id_elemento"])) for e in fabricados]
        sc_mat = np.array([d[0] for d in desglose])
        sc_mfg = np.array([d[1] for d in desglose])
        sc_cat = np.array([e["categoria"] for e in fabricados])

        peso_mat = np.sum(sc_mat) / np.sum(sc_mat + sc_mfg) * 100
        print(f"Peso en el costo total: materiales {peso_mat:.1f}% / manufactura {100 - peso_mat:.1f}%")

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

        tope = float(max(sc_mat.max(), sc_mfg.max()))
        ax2.plot([0, tope], [0, tope], color="gray", linestyle="--", linewidth=1, alpha=0.7)
        for cat, color in self.COLORES_CAT.items():
            mascara = sc_cat == cat
            ax2.scatter(sc_mat[mascara], sc_mfg[mascara], alpha=0.6, s=30, color=color, label=cat)
        ax2.set_title("Costo de Materiales vs Manufactura por Producto")
        ax2.set_xlabel("Costo de Materiales ($)")
        ax2.set_ylabel("Costo de Manufactura ($)")
        ax2.legend(fontsize=8)
        ax2.grid(alpha=0.3)
        plt.tight_layout()
        self._guardar_figura("grafico_3_costos.png")

    def _agrupar_horas_periodo(self):
        horas_por_periodo = {int(u["id_unidad"]): {} for u in self._unidades}
        periodos_unicos = []

        for sol in self._activas:
                                                                       
            periodo = sol["fecha"][:7] 
            
            if periodo not in periodos_unicos:
                periodos_unicos.append(periodo)

            fabs = self._fabricados_involucrados(int(sol["producto"]), int(sol["cantidad"]))
            for id_art, cant_art in fabs.items():
                for t in self._tareas_por_art.get(id_art, []):
                    uid = int(t["id_unidad"])
                    if uid in horas_por_periodo:
                        actual = horas_por_periodo[uid].get(periodo, 0.0)
                        horas_por_periodo[uid][periodo] = actual + (cant_art * float(t["tiempo_estandar"]))
        periodos_unicos.sort()
        return horas_por_periodo, periodos_unicos

    def analizar_heatmap_unidades(self):
        print("\n--- ANALISIS 2B: HEATMAP DE UNIDADES POR PERIODO ---")
        horas_por_periodo, periodos_unicos = self._agrupar_horas_periodo()
        
        n_unidades = len(self._unidades)
        n_periodos = len(periodos_unicos)
        
        matriz_heatmap = np.zeros((n_unidades, n_periodos))
        nombres_unidades = np.array([u["nombre"] for u in self._unidades])
                                                          
        for i, u in enumerate(self._unidades):
            uid = int(u["id_unidad"])
            for j, p in enumerate(periodos_unicos):
                matriz_heatmap[i, j] = horas_por_periodo[uid].get(p, 0.0)

        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(matriz_heatmap, cmap="YlOrRd", aspect="auto")

        ax.set_xticks(np.arange(n_periodos))
        ax.set_yticks(np.arange(n_unidades))
        ax.set_xticklabels(periodos_unicos, rotation=45, ha="right")
        ax.set_yticklabels(nombres_unidades, fontsize=8)
                                                 
        for i in range(n_unidades):
            for j in range(n_periodos):
                valor = matriz_heatmap[i, j]
                if valor > 0:
                    color_texto = "white" if valor > np.max(matriz_heatmap) * 0.6 else "black"
                    ax.text(j, i, f"{valor:.0f}h", ha="center", va="center", color=color_texto, fontsize=7)

        ax.set_title("Heatmap: Carga de Horas por Unidad y Período", fontsize=14, pad=15)
        fig.colorbar(im, ax=ax, label="Horas de trabajo")
        
        plt.tight_layout()
        self._guardar_figura("grafico_2b_heatmap.png")

    def analizar_cuellos_botella(self):
        print("\n--- ANALISIS 4: DETECCION DE CUELLOS DE BOTELLA ---")
        
        colaboradores = self._leer("colaboradores.csv")
        periodos = sorted({s["fecha"][:7] for s in self._activas})
        n_periodos = max(1, len(periodos))
                                                                             
        stock_restante = {int(e["id_elemento"]): int(e["stock_actual"]) for e in self._elementos if e["tipo"] == "Insumo"}
        horas_uni_restante = {int(u["id_unidad"]): float(u["capacidad_horas_periodo"]) * n_periodos for u in self._unidades}
        horas_colab_restante = sum(float(c["horas_disponibles"]) for c in colaboradores) * n_periodos
        
        ordenes_sin_mat = 0
        ordenes_sin_uni = 0
        ordenes_sin_colab = 0

        for sol in self._activas:
                                                        
            demanda_mat = {}
            self._explotar(int(sol["producto"]), int(sol["cantidad"]), demanda_mat)
            
            frena_mat = False
            for id_ins, cant in demanda_mat.items():
                if stock_restante.get(id_ins, 0) < cant:
                    frena_mat = True
                    break
            
            if frena_mat:
                ordenes_sin_mat += 1
            else:
                for id_ins, cant in demanda_mat.items():
                    stock_restante[id_ins] -= cant

            fabs = self._fabricados_involucrados(int(sol["producto"]), int(sol["cantidad"]))
            
            horas_req_uni = {}
            horas_req_colab = 0.0

            for id_art, cant_art in fabs.items():
                for t in self._tareas_por_art.get(id_art, []):
                    uid = int(t["id_unidad"])
                    horas = cant_art * float(t["tiempo_estandar"])
                    
                    horas_req_uni[uid] = horas_req_uni.get(uid, 0.0) + horas
                    horas_req_colab += horas * int(t["colaboradores_requeridos"])
            
            frena_uni = False
            for uid, horas in horas_req_uni.items():
                if horas_uni_restante.get(uid, 0.0) < horas:
                    frena_uni = True
                    break
            
            if frena_uni:
                ordenes_sin_uni += 1
            else:
                for uid, horas in horas_req_uni.items():
                    horas_uni_restante[uid] -= horas
                    
            if horas_colab_restante < horas_req_colab:
                ordenes_sin_colab += 1
            else:
                horas_colab_restante -= horas_req_colab
                                                         
        categorias = np.array(["Faltante Materiales", "Sobrecarga Unidades", "Falta Colaboradores"])
        valores = np.array([ordenes_sin_mat, ordenes_sin_uni, ordenes_sin_colab])
                                                                  
        colores_base = np.array(["#e74c3c", "#f39c12", "#3498db"]) 
        
        print(f"Órdenes afectadas reales: Materiales={ordenes_sin_mat}, Unidades={ordenes_sin_uni}, Colaboradores={ordenes_sin_colab}")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle("Detección de Cuellos de Botella: Órdenes Afectadas", fontsize=15)
                                      
        mascara = valores > 0
        if np.sum(mascara) > 0:
                                                           
            ax1.pie(valores[mascara], labels=categorias[mascara], autopct='%1.1f%%', 
                    startangle=90, colors=colores_base[mascara])
        ax1.set_title("Distribución de Restricciones")
                                      
        orden = np.argsort(valores)[::-1] 
        x = np.arange(len(categorias))
                                                          
        ax2.bar(x, valores[orden], color=colores_base[orden])
        ax2.set_xticks(x)
        ax2.set_xticklabels(categorias[orden])
        ax2.set_ylabel("Cantidad de Órdenes Afectadas")
        ax2.set_title("Ranking de Restricciones")
        ax2.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        self._guardar_figura("grafico_4_cuellos_botella.png")
        
    def analizar_capacidad(self):
        print("\n--- ANALISIS 5: PLANIFICACION DE CAPACIDAD ---")                                                                                           
        capacidad_mensual_total = sum(float(u["capacidad_horas_periodo"]) for u in self._unidades)
        periodos_unicos = sorted(list({s["fecha"][:7] for s in self._activas}))
                                         
        horas_req_periodo = {p: 0.0 for p in periodos_unicos}
        horas_disp_periodo = {p: capacidad_mensual_total for p in periodos_unicos}
        
        ordenes_completables = 0
        ordenes_demoradas = 0
                                                                                     
        for sol in self._activas:
            periodo = sol["fecha"][:7]
            fabs = self._fabricados_involucrados(int(sol["producto"]), int(sol["cantidad"]))
                                                                     
            horas_orden = 0.0
            for id_art, cant_art in fabs.items():
                for t in self._tareas_por_art.get(id_art, []):
                    horas_orden += cant_art * float(t["tiempo_estandar"])
                     
            horas_req_periodo[periodo] += horas_orden
                                                                                           
            if horas_req_periodo[periodo] > capacidad_mensual_total:
                ordenes_demoradas += 1
            else:
                ordenes_completables += 1
                                                
        total_req = sum(horas_req_periodo.values())
        total_disp = len(periodos_unicos) * capacidad_mensual_total
        utilizacion_prom = (total_req / total_disp) * 100 if total_disp > 0 else 0
                    
        capacidad_residual = max(0, total_disp - total_req) 
        
        print(f"Órdenes completables a tiempo: {ordenes_completables}")
        print(f"Órdenes demoradas por saturación: {ordenes_demoradas}")
        print(f"Utilización promedio de capacidad global: {utilizacion_prom:.1f}%")
        print(f"Capacidad residual del sistema: {capacidad_residual:.0f} horas")
                                                                    
        x = np.arange(len(periodos_unicos))
        req_arr = np.array([horas_req_periodo[p] for p in periodos_unicos])
        disp_arr = np.array([horas_disp_periodo[p] for p in periodos_unicos])
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle("Planificación de Capacidad Temporal", fontsize=15)
                                            
        ax1.plot(x, req_arr, marker='o', color='#e74c3c', linewidth=2.5, label='Horas Requeridas')
        ax1.plot(x, disp_arr, color='#2ecc71', linestyle='--', linewidth=2, label='Capacidad Máxima')
               
        ax1.fill_between(x, disp_arr, req_arr, where=(req_arr > disp_arr), 
                         interpolate=True, color='#e74c3c', alpha=0.3, label='Saturación / Demoras')
                                
        ax1.fill_between(x, req_arr, disp_arr, where=(disp_arr >= req_arr), 
                         interpolate=True, color='#2ecc71', alpha=0.2, label='Capacidad Libre')
                         
        ax1.set_xticks(x)
        ax1.set_xticklabels(periodos_unicos, rotation=45, ha="right")
        ax1.set_title("Evolución Temporal de Carga Productiva")
        ax1.set_ylabel("Horas de Trabajo Globales")
        ax1.legend(fontsize=9)
        ax1.grid(alpha=0.3)
                                                    
        ancho = 0.35
        ax2.bar(x - ancho/2, disp_arr, ancho, label='Capacidad Disponible', color='#3498db', alpha=0.8)
        ax2.bar(x + ancho/2, req_arr, ancho, label='Carga Requerida', color='#f39c12', alpha=0.9)
        
        ax2.set_xticks(x)
        ax2.set_xticklabels(periodos_unicos, rotation=45, ha="right")
        ax2.set_title("Comparativa de Horas por Período")
        ax2.set_ylabel("Horas de Trabajo")
        ax2.legend(fontsize=9)
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        self._guardar_figura("grafico_5_capacidad.png")
        
    def analizar_eficiencia(self):
        print("\n--- ANALISIS 6: EFICIENCIA PRODUCTIVA ---")
                                                                        
        terminadas = [s for s in self._solicitudes if s["estado"] == "Terminada"]
        
        if len(terminadas) == 0:
            print("⚠️ No hay órdenes en estado 'Terminada' en el dataset.")
            print("⚠️ Saltando el gráfico de eficiencia para evitar errores matemáticos.")
            return
                                                          
        eficiencia_producto = {}                                           
        eficiencia_unidad = {int(u["id_unidad"]): {'ordenes': 0, 'horas': 0.0} for u in self._unidades}
            
        terminadas = [s for s in self._solicitudes if s["estado"] == "Terminada"]
        
        eficiencia_producto = {}                                           
        eficiencia_unidad = {int(u["id_unidad"]): {'ordenes': 0, 'horas': 0.0} for u in self._unidades}
        
        horas_globales = 0.0
                                        
        for sol in terminadas:
            prod_id = int(sol["producto"])
            cant = int(sol["cantidad"])
            
            if prod_id not in eficiencia_producto:
                eficiencia_producto[prod_id] = {'ordenes': 0, 'horas': 0.0}
                
            eficiencia_producto[prod_id]['ordenes'] += 1
                                               
            fabs = self._fabricados_involucrados(prod_id, cant)
            horas_orden_por_unidad = {}
            
            for id_art, cant_art in fabs.items():
                for t in self._tareas_por_art.get(id_art, []):
                    uid = int(t["id_unidad"])
                    horas = cant_art * float(t["tiempo_estandar"])
                    horas_orden_por_unidad[uid] = horas_orden_por_unidad.get(uid, 0.0) + horas
                                                                       
            horas_totales_orden = sum(horas_orden_por_unidad.values())
            eficiencia_producto[prod_id]['horas'] += horas_totales_orden
            horas_globales += horas_totales_orden
            
            for uid, horas in horas_orden_por_unidad.items():
                if horas > 0:
                    eficiencia_unidad[uid]['ordenes'] += 1
                    eficiencia_unidad[uid]['horas'] += horas

        efi_global = len(terminadas) / horas_globales if horas_globales > 0 else 0
        print(f"Órdenes históricas completadas analizadas: {len(terminadas)}")
        print(f"Eficiencia Global del Sistema: {efi_global:.4f} órdenes/hora")
                                                      
        nombres_uni = []
        efi_uni = []
        for u in self._unidades:
            uid = int(u["id_unidad"])
            datos = eficiencia_unidad[uid]
            val = datos['ordenes'] / datos['horas'] if datos['horas'] > 0 else 0
            nombres_uni.append(u["nombre"])
            efi_uni.append(val)
            
        nombres_uni = np.array(nombres_uni)
        efi_uni = np.array(efi_uni)
                               
        prods = list(eficiencia_producto.keys())
        efi_prod = []
        costo_prod = []
        for p in prods:
            datos = eficiencia_producto[p]
            val = datos['ordenes'] / datos['horas'] if datos['horas'] > 0 else 0
            efi_prod.append(val)
            costo_prod.append(self._costo_unitario(p))                                                   
            
        efi_prod = np.array(efi_prod)
        costo_prod = np.array(costo_prod)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle("Análisis de Eficiencia Productiva", fontsize=15)
                                                              
        orden = np.argsort(efi_uni)[::-1]
        x_uni = np.arange(len(nombres_uni))
        ax1.bar(x_uni, efi_uni[orden], color="#9b59b6")
        ax1.set_xticks(x_uni)
        ax1.set_xticklabels(nombres_uni[orden], rotation=45, ha="right", fontsize=8)
        ax1.set_title("Ranking de Eficiencia por Unidad")
        ax1.set_ylabel("Eficiencia (Órdenes / Hora)")
        ax1.grid(axis="y", alpha=0.3)
                 
        ax2.scatter(efi_prod, costo_prod, color="#2ecc71", alpha=0.6, edgecolors="black", s=40)    
                                                                                
        ax2.axvline(np.mean(efi_prod), color="gray", linestyle="--", alpha=0.5, label="Promedio Eficiencia")
        ax2.axhline(np.mean(costo_prod), color="gray", linestyle="--", alpha=0.5, label="Promedio Costo")
        
        ax2.set_title("Eficiencia vs Costo Unitario (por Producto)")
        ax2.set_xlabel("Eficiencia (Órdenes / Hora)")
        ax2.set_ylabel("Costo Unitario ($)")
        ax2.legend()
        ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        self._guardar_figura("grafico_6_eficiencia.png")

    def _guardar_figura(self, nombre):
        ruta = os.path.join(os.path.dirname(__file__), nombre)
        plt.savefig(ruta, dpi=130)
        plt.show()
        print(f"-> Grafico guardado en '{nombre}'")

    def correr(self):
        self.analizar_inventario()
        self.analizar_unidades()
        self.analizar_costos()
        self.analizar_heatmap_unidades()
        self.analizar_cuellos_botella()
        self.analizar_capacidad()
        self.analizar_eficiencia()
   
if __name__ == "__main__":
    analisis = Analisis()
    analisis.correr()