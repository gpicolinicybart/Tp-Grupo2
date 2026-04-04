import pytest
from unittest.mock import MagicMock
from compra_insumo import Compra_Insumo
from insumo_basico import InsumoBasico
from inventario import Inventario

def test_recibir_materiales_llama_al_inventario():
    acero = InsumoBasico(101, "Acero", 500.0)
    orden = Compra_Insumo(1001, acero, 10)
    inventario_mock = MagicMock(spec=Inventario) # inventario mockeado
    orden.recibir_materiales(inventario_mock)    # la orden de recibir materiales en el inventario de mentira
# chequea que Compra_Insumo use bien los métodos de Inventario
    inventario_mock.ingresar_stock.assert_called_once_with(acero, 10)