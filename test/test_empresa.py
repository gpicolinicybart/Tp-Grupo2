import pytest
from unittest.mock import MagicMock
from empresa import Empresa
from inventario import Inventario
from articulo_fabricado import ArticuloFabricadoInternamente

def test_registrar_producto_llama_validar_ciclos():
    
    inv_mock = MagicMock(spec=Inventario)
    empresa = Empresa(inv_mock)
    
   
    producto_mock = MagicMock(spec=ArticuloFabricadoInternamente)
    producto_mock._nombre = "Mesa Ratona"
    
    
    empresa.registrar_producto_nuevo(producto_mock)
    
    assert producto_mock in empresa._catalogo_elementos
    
    producto_mock.validar_ciclos.assert_called_once()