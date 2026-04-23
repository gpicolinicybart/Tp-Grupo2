import pytest
from unittest.mock import MagicMock
from articulo_fabricado import ArticuloFabricadoInternamente
from itembom import ItemBOM
from tarea import Tarea
from insumo_basico import InsumoBasico

def test_costo_unitario_articulo_fabricado():
    # simulo que los materiales cuestan $500 y la mano de obra 300
    bom_mock = MagicMock(spec=ItemBOM)
    bom_mock.get_costo_total.return_value = 500.0
    tarea_mock = MagicMock(spec=Tarea)
    tarea_mock.get_costo.return_value = 300.0
    
    #Creamos el artículo con esos mocks
    mesa = ArticuloFabricadoInternamente("Mesa", [bom_mock], [tarea_mock])
    assert mesa.get_costo_unitario() == 800.0 # Verificación: Costo Total = 500 (BOM) + 300 (Tarea) = 800
    #el assert "afirma" q tiene q ser verdadero si llega a ser Falso, hace fallar el test y tira error

def test_detectar_ciclo_infinito():
    item_a = ArticuloFabricadoInternamente("Parte A", [], []) # q no se requiera a si mismo
    bom_ciclico = ItemBOM("BOM Ciclo", {item_a: 1}) # hago un BOM que contiene al mismo item_a (circulo vicioso)
    item_a._bom = [bom_ciclico]
    
    with pytest.raises(ValueError, match="CICLO DETECTADO"):  # al validar ciclos, debe saltar el error
        item_a.validar_ciclos()

def test_articulo_fabricado_id_autoincremental():
    art1 = ArticuloFabricadoInternamente("Producto A", [], [])
    art2 = ArticuloFabricadoInternamente("Producto B", [], [])
    assert art1.get_id() < art2.get_id()

def test_calcular_materiales_necesarios_recursivo():
    #Verifica que la explosión del BOM baje correctamente por todos los niveles
    #hasta llegar a los insumos básicos, acumulando las cantidades exactas.
    # Insumos básicos
    madera = InsumoBasico("Madera", 100.0)
    tornillo = InsumoBasico("Tornillo", 5.0)
    # Sub-ensamble: Pata (1 madera, 4 tornillos)
    bom_pata = ItemBOM("Receta Pata", {madera: 1, tornillo: 4})
    pata = ArticuloFabricadoInternamente("Pata", [bom_pata], [])
    #  Prod Mesa (1 madera, 4 patas)
    bom_mesa = ItemBOM("Receta Mesa", {madera: 1, pata: 4})
    mesa = ArticuloFabricadoInternamente("Mesa", [bom_mesa], [])
    #  necesidades para fabricar 2 MESAS
    necesidades = mesa.calcular_materiales_necesarios(2)
    # verificaion
    # Maderas = 2 mesas * (1 base + 4 patas * 1 madera) = 2 * 5 = 10 maderas
    assert necesidades[madera] == 10
    # Tornillos = 2 mesas * (4 patas * 4 tornillos) = 2 * 16 = 32 tornillos
    assert necesidades[tornillo] == 32
    # y verificamos que la pata no esté en la lista final, para ver si se explotó el componente
    assert pata not in necesidades
    #conviene separarlos xq si falla alguno es mas facil identificar donde esta el problema
