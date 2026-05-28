import pytest
from unittest.mock import MagicMock
from tarea import Tarea
from unidad_de_trabajo import UnidadDeTrabajo

def test_calculo_costo_tarea():
    # máquina que cuesta $100 la hora
    unidad_mock = MagicMock(spec=UnidadDeTrabajo)
    unidad_mock.get_costo_operativo.return_value = 100.0

    #tarea de 2 horas, 3 empleados a $500/hr
    tarea = Tarea(
        descripcion="Soldadura", 
        unidad_requerida=unidad_mock, 
        cant_colaboradores_req=3, 
        tiempo_por_unidad=2.0, 
        habilidad_requerida="Soldador", 
        costo_mano_obra_hora=500.0
    )

    # 3. Verificamos la cuenta:
    # Máquina: 100 * 2 = 200
    # Empleados: 500 * 3 * 2 = 3000
    # Total esperado: 3200.0
    assert tarea.get_costo() == 3200.0

def test_tarea_costo_invalido():
    unidad_mock = MagicMock(spec=UnidadDeTrabajo)
    # Si le pasamos un salario negativo (-500.0), debe saltar el ValueError
    with pytest.raises(ValueError):
        Tarea("Prueba", unidad_mock, 1, 1.0, "Prueba", -500.0)