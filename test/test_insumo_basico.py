import pytest
from unittest.mock import MagicMock
from insumo_basico import InsumoBasico

def test_insumo_basico_no_permite_costo_negativo():
    with pytest.raises(ValueError, match="El costo fijo no puede ser negativo."):
        InsumoBasico("Acero", -500.0)

def test_insumo_basico_set_costo_valido_e_invalido():
    insumo = InsumoBasico("Cobre", 100.0)

    insumo.set_costo_fijo(150.0)
    assert insumo.get_costo_fijo() == 150.0
    
    with pytest.raises(ValueError, match="El costo no puede ser negativo."):
        insumo.set_costo_fijo(-10.0)

def test_insumo_basico_id_autoincremental():
    insumo1 = InsumoBasico("Hierro", 100.0)
    insumo2 = InsumoBasico("Zinc", 200.0)
    assert insumo1.get_id() < insumo2.get_id()

def test_acumular_necesidades_caso_base():
    pintura = InsumoBasico("Pintura", 1500.0)
    necesidades = {}
    
    # Acumula los primeros 5
    pintura.acumular_necesidades(5, necesidades)
    assert necesidades[pintura] == 5
    
    # Suma 3 más y llega a 8
    pintura.acumular_necesidades(3, necesidades)
    assert necesidades[pintura] == 8

def test_gestionar_reabastecimiento_delega_a_empresa():
    tornillo = InsumoBasico("Tornillo", 10.0)
    empresa_mock = MagicMock()
    
    mensaje = tornillo.gestionar_reabastecimiento(empresa_mock, 500)
    
    # Verificamos que avisó a la empresa
    empresa_mock.registrar_compra.assert_called_once()
    llamada_args = empresa_mock.registrar_compra.call_args[0]
    orden_creada = llamada_args[0]
    
    # Verificamos que la orden se creó con los datos correctos
    assert orden_creada.get_insumo() == tornillo
    assert orden_creada.get_cantidad() == 500
    assert "500" in mensaje
    assert "Tornillo" in mensaje
    
def test_polimorfismo_insumo_basico():
    madera = InsumoBasico("Madera", 120.5)
    assert madera.get_costo_unitario() == 120.5
    assert madera.get_tipo_elemento() == "Insumo Básico"