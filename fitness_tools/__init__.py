"""
fitness_tools — Librería de herramientas para composición corporal y nutrición deportiva.

Módulos disponibles:
    body_composition: Cálculo de grasa corporal y masa magra (fórmula US Navy).
    nutrition:        Distribución de macronutrientes y cálculo rápido de carbohidratos.

Ejemplo rápido::

    from fitness_tools import calcular_grasa_navy, calcular_macros_diarios, carbos_flash

    grasa, magra = calcular_grasa_navy(peso=72.25, altura=175.0, cintura=84.0, cuello=38.0)
    macros = calcular_macros_diarios(kcal_quemadas=3343, peso=72.25)
    carbos = carbos_flash(kcal=2930, peso=72.25)
"""

from fitness_tools.body_composition import calcular_grasa_navy
from fitness_tools.nutrition import calcular_macros_diarios, carbos_flash

__all__ = [
    "calcular_grasa_navy",
    "calcular_macros_diarios",
    "carbos_flash",
]
