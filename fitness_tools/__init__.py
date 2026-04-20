"""
fitness_tools — Librería de herramientas para composición corporal y nutrición deportiva.

Módulos disponibles:
    body_composition: Cálculo de grasa corporal, masa magra (fórmula US Navy)
                      y registro de medidas antropométricas.
    nutrition:        Distribución de macronutrientes y cálculo rápido de carbohidratos.

Ejemplo rápido::

    from fitness_tools import calcular_grasa_navy, calcular_macros_diarios, MedidasCorporales

    medidas = MedidasCorporales(peso=72.25, altura=175.0, cintura=84.0, cuello=38.0,
                                biceps=35.0, cuadriceps=55.0)
    grasa, magra = calcular_grasa_navy(medidas.peso, medidas.altura,
                                       medidas.cintura, medidas.cuello)
    macros = calcular_macros_diarios(kcal_quemadas=3343, peso=medidas.peso)
"""

from fitness_tools.body_composition import MedidasCorporales, calcular_grasa_navy
from fitness_tools.nutrition import calcular_macros_diarios, carbos_flash

__all__ = [
    "MedidasCorporales",
    "calcular_grasa_navy",
    "calcular_macros_diarios",
    "carbos_flash",
]
