import pytest
from unittest.mock import MagicMock
from tarea import Tarea

@pytest.fixture
def unidad_mock():
    unidad = MagicMock()
    unidad.get_id.return_value = 1
    unidad.get_costo_operativo.return_value = 500.0
    return unidad

@pytest.fixture
def tarea_setup(unidad_mock):
    # id_tarea_maestra, unidad_requerida, cant_colaboradores_req, tiempo_por_unidad, 
    # id_habilidad_requerida, costo_mano_obra_hora
    return Tarea(10, unidad_mock, 2, 1.5, 5, 1000.0)

def test_creacion_y_getters_correctos(tarea_setup, unidad_mock):
    assert tarea_setup.get_id_tarea_maestra() == 10
    assert tarea_setup.get_unidad_requerida() == unidad_mock
    assert tarea_setup.get_cant_colaboradores_req() == 2
    assert tarea_setup.get_tiempo_por_unidad() == 1.5
    assert tarea_setup.get_id_habilidad_requerida() == 5
    assert tarea_setup.get_costo_mano_obra_hora() == 1000.0
    assert "Tarea (ID Maestro: 10)" in str(tarea_setup)

def test_validaciones_estrictas_lanzan_error(unidad_mock):
    with pytest.raises(ValueError, match="El costo de mano de obra por hora debe ser un valor no negativo."):
        Tarea(10, unidad_mock, 2, 1.5, 5, -100.0)

def test_calculo_costo_total(tarea_setup):
    # Costo Unidad = 500.0 * 1.5 hs = 750.0
    # Costo Personal = 1000.0 * 2 empleados * 1.5 hs = 3000.0
    # Total esperado = 3750.0
    assert tarea_setup.get_costo() == 3750.0

def test_calcular_horas_totales(tarea_setup):
    # 1.5 horas por unidad * 10 unidades a fabricar = 15.0 horas
    assert tarea_setup.calcular_horas_totales(10) == 15.0

def test_filtrar_colaboradores_aptos_y_ordenados(tarea_setup):
    # Colaborador 1: apto, cobra 1500
    colab1 = MagicMock()
    colab1.tiene_habilidad.return_value = True
    colab1.verificar_disponibilidad.return_value = True
    colab1.get_salario_hora.return_value = 1500.0

    # Colaborador 2: No sabe hacer la tarea
    colab2 = MagicMock()
    colab2.tiene_habilidad.return_value = False
    colab2.verificar_disponibilidad.return_value = True
    colab2.get_salario_hora.return_value = 1000.0

    # Colaborador 3: apto y cobra 1200
    colab3 = MagicMock()
    colab3.tiene_habilidad.return_value = True
    colab3.verificar_disponibilidad.return_value = True
    colab3.get_salario_hora.return_value = 1200.0

    # Colaborador 4: Sabe hacer la tarea, pero no tiene disponibilidad
    colab4 = MagicMock()
    colab4.tiene_habilidad.return_value = True
    colab4.verificar_disponibilidad.return_value = False
    colab4.get_salario_hora.return_value = 1000.0

    diccionario_colabs = {1: colab1, 2: colab2, 3: colab3, 4: colab4}
    
    # Filtramos pidiendo 10.0 horas de trabajo
    aptos = tarea_setup.filtrar_colaboradores_aptos(diccionario_colabs, 10.0)

    # Solo colab1 y colab3 son aptos
    assert len(aptos) == 2
    
    # El de $1200 (colab3) debe quedar primero, el de $1500 (colab1) segundo.
    assert aptos[0] == colab3
    assert aptos[1] == colab1
    
    # Comprobamos que el filtro interactuó con el ID de habilidad correcto (5)
    colab1.tiene_habilidad.assert_called_with(5)
    colab1.verificar_disponibilidad.assert_called_with(10.0)

def test_ejecutar_reservas_delega_correctamente(tarea_setup, unidad_mock):
    colab1 = MagicMock()
    colab2 = MagicMock()
    colaboradores = [colab1, colab2]
    # Ejecutamos las reservas de 20 horas en la máquina y en los empleados
    tarea_setup.ejecutar_reservas(20.0, colaboradores)
    # la unidad de trabajo recibió la orden
    unidad_mock.reservar_horas.assert_called_once_with(20.0)
    # a cada colaborador se le asignó la tarea con el ID 5 (la habilidad de la tarea)
    colab1.asignar_tarea.assert_called_once_with(5, 20.0)
    colab2.asignar_tarea.assert_called_once_with(5, 20.0)