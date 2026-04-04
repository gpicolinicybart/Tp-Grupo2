import pytest
from insumo_basico import InsumoBasico

def test_insumo_basico_no_permite_costo_negativo():
    # Arranca el test: Le avisamos a pytest que esperamos un ValueError
    with pytest.raises(ValueError):
        # Intentamos crear el insumo con costo -500
        insumo = InsumoBasico(101, "Acero", -500.0)
        

# Por este test me di cuenta que teniamos que cambiar en insumo basico el print error por un value error
# en la parte del INNIT: if costo_fijo < 0: raise ValueError("Error: El costo fijo inicial no puede ser negativo.")

def test_insumo_basico_getters_y_setters():
    insumo = InsumoBasico(101, "Acero", 500.0)
    
# me fijo que el nombre sea el correcto
    assert insumo.get_nombre() == "Acero"
    
# cambio el costo y veo que se actualice
    insumo.set_costo_fijo(600.0)
    assert insumo.get_costo_fijo() == 600.0
    assert insumo.get_costo_unitario() == 600.0