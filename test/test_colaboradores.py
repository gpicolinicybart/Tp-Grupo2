import pytest
from colaboradores import Colaborador

@pytest.fixture
def operario_soldador():
    #fixture que prepara un colaborador con 10 horas libres
    return Colaborador(["Soldadura", "Corte"], 10.0, 3000.0)

def test_verificar_habilidades(operario_soldador):
# veo que detecte correctamente lo que sabe hacer
    assert operario_soldador.tiene_habilidad("Soldadura") is True
    assert operario_soldador.tiene_habilidad("Pintura") is False

def test_asignar_tarea_exito(operario_soldador):
    # le asigno 4 horas de Soldadura (tiene 10 libres)
    exito = operario_soldador.asignar_tarea("Soldadura", 4.0)
    assert exito is True
    # miro disponibilidad (10 - 4 = 6)
    assert operario_soldador.verificar_disponibilidad(6.0) is True
    assert operario_soldador.verificar_disponibilidad(6.1) is False

def test_asignar_tarea_sin_habilidad(operario_soldador):
    # le trato de asignar algo que no sabe hacer
    exito = operario_soldador.asignar_tarea("Carpinteria", 1.0)
    assert exito is False
    # no debería haberle restado tiempo
    assert operario_soldador.verificar_disponibilidad(10.0) is True

def test_asignar_tarea_sin_tiempo(operario_soldador):
    # trato de asignar 11 horas cuando solo tiene 10
    exito = operario_soldador.asignar_tarea("Soldadura", 11.0)
    assert exito is False
    
def test_colaborador_id_autoincremental():
    c1 = Colaborador(["Pintura"], 40.0, 1000.0)
    c2 = Colaborador(["Ensamblaje"], 40.0, 1200.0)
    assert c1.get_id() < c2.get_id()