import pytest
from unittest.mock import MagicMock
from insumo_basico import InsumoBasico

def test_insumo_basico_no_permite_costo_negativo():
    with pytest.raises(ValueError): # "espero" un valueerror
        InsumoBasico("Acero", -500.0)

def test_insumo_basico_id_autoincremental():
    # hereda bien de Elemento y el ID sube solo
    insumo1 = InsumoBasico("Hierro", 100.0)
    insumo2 = InsumoBasico("Cobre", 200.0)
    assert insumo1.get_id() < insumo2.get_id()

def test_acumular_necesidades_caso_base(): # el Insumo solo se anota a sí mismo en el diccionario

    pintura = InsumoBasico("Pintura", 1500.0)
    necesidades = {}
    # Si le pedimos que acumule 5 de pintura, debe sumar 5 al diccionario
    pintura.acumular_necesidades(5, necesidades)
    assert necesidades[pintura] == 5
    # Si le pedimos 3 más, debe sumarlos y dar 8
    pintura.acumular_necesidades(3, necesidades)
    assert necesidades[pintura] == 8

def test_gestionar_reabastecimiento_delega_a_empresa(): # verifico que el insumo pueda llamar correctamente a la empresa
    tornillo = InsumoBasico("Tornillo", 10.0)
    empresa_mock = MagicMock() # Creamos una Empresa falsa
    tornillo.gestionar_reabastecimiento(empresa_mock, 500) #faltan 500 unidades
    empresa_mock.registrar_compra.assert_called_once()
    # compruebo con el Mock que el insumo se comunica con el método de la Empresa exactamente una vez
