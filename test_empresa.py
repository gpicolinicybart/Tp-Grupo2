import pytest
from unittest.mock import MagicMock
from empresa import Empresa
from inventario import Inventario
from articulo_fabricado import ArticuloFabricadoInternamente

def test_registrar_producto_llama_validar_ciclos():
    # 1. Preparamos el entorno
    inv_mock = MagicMock(spec=Inventario)
    empresa = Empresa(inv_mock)
    
    # 2. Simulamos un artículo fabricado
    producto_mock = MagicMock(spec=ArticuloFabricadoInternamente)
    producto_mock._nombre = "Mesa Ratona"
    
    # 3. Lo registramos en la empresa
    empresa.registrar_producto_nuevo(producto_mock)
    
    # 4. Verificaciones
    # ¿Se guardó en el catálogo?
    assert producto_mock in empresa._catalogo_elementos
    # ¿La empresa le ordenó al producto validar que no tenga ciclos infinitos?
    producto_mock.validar_ciclos.assert_called_once()