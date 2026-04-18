import pytest
from unittest.mock import MagicMock
from compra_insumo import Compra_Insumo
from insumo_basico import InsumoBasico
from inventario import Inventario

def test_recibir_materiales_llama_al_inventario():
    acero = InsumoBasico("Acero", 500.0)
    orden = Compra_Insumo(acero, 10)
    inventario_mock = MagicMock(spec=Inventario) # inventario mockeado
    orden.recibir_materiales(inventario_mock)    # la orden de recibir materiales en el inventario de mentira
# chequea que Compra_Insumo use bien los métodos de Inventario
    inventario_mock.ingresar_stock.assert_called_once_with(acero, 10)
    
    
    # XQ NO TIENE ASSERTIONS? PORQUE EL MAGICMOCK YA VERIFICA QUE SE LLAMÓ CON LOS ARGUMENTOS 
    # CORRECTOS, SI NO SE LLAMA O SE LLAMA CON ARGUMENTOS DISTINTOS, EL TEST FALLA AUTOMATICAMENTE.

def test_compra_insumo_id_autoincremental():
    acero = InsumoBasico("Acero", 500.0)
    orden1 = Compra_Insumo(acero, 10)
    orden2 = Compra_Insumo(acero, 20)
    assert orden1.get_id() < orden2.get_id()