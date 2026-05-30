from unittest.mock import MagicMock
from compra_insumo import Compra_Insumo
from inventario import Inventario
from insumo_basico import InsumoBasico

def test_estado_inicial_solicitada():
    acero_mock = MagicMock(spec=InsumoBasico)
    orden = Compra_Insumo(acero_mock, 15)
    # Verificar que el estado por defecto sea el correcto
    assert orden.get_estado() == "Solicitada"
    # Debe tener fecha de emisión al nacer
    assert orden.get_fecha_emision() is not None
    # no debe tener fecha de recepción 
    assert orden.get_fecha_recepcion() is None

def test_recibir_materiales_actualiza_estado_y_llama_inventario():
    acero_mock = MagicMock(spec=InsumoBasico)
    orden = Compra_Insumo(acero_mock, 10)
    inventario_mock = MagicMock(spec=Inventario)
    
    # recepción
    orden.recibir_materiales(inventario_mock)
    # verifica que haya interactuado bien con el Inventario
    inventario_mock.ingresar_stock.assert_called_once_with(acero_mock, 10)
    # verifica el encapsulamiento: el estado debió cambiar
    assert orden.get_estado() == "Recibida"
    # verifica que se haya sellado la fecha exacta de recepción
    assert orden.get_fecha_recepcion() is not None

def test_compra_insumo_id_autoincremental():
    acero_mock = MagicMock(spec=InsumoBasico)
    orden1 = Compra_Insumo(acero_mock, 10)
    orden2 = Compra_Insumo(acero_mock, 20)
    
    assert orden1.get_id() < orden2.get_id()