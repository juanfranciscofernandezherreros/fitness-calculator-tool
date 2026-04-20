"""
fitness_tools — Librería de herramientas para composición corporal y nutrición deportiva.

Módulos disponibles:
    body_composition: Fórmulas US Navy (hombres y mujeres), IMC, FFMI y registro
                      de medidas antropométricas.
    nutrition:        Distribución de macronutrientes y cálculo rápido de carbohidratos.

Ejemplo rápido::

    from fitness_tools import (
        MedidasCorporales,
        calcular_grasa_navy,
        calcular_bmi,
        calcular_ffmi,
        calcular_macros_diarios,
    )

    medidas = MedidasCorporales(peso=72.25, altura=175.0, cintura=84.0, cuello=38.0,
                                sexo="hombre", biceps_der=35.0, biceps_izq=34.5,
                                cuadriceps_der=55.0, cuadriceps_izq=54.5)
    grasa, magra = calcular_grasa_navy(medidas.peso, medidas.altura,
                                       medidas.cintura, medidas.cuello,
                                       sexo=medidas.sexo)
    bmi            = calcular_bmi(medidas.peso, medidas.altura)
    ffmi, ffmi_n   = calcular_ffmi(magra, medidas.altura)
    macros         = calcular_macros_diarios(kcal_quemadas=3343, peso=medidas.peso)
"""

from fitness_tools.body_composition import (
    MedidasCorporales,
    calcular_bmi,
    calcular_ffmi,
    calcular_grasa_navy,
    clasificar_bmi,
)
from fitness_tools.nutrition import calcular_macros_diarios, carbos_flash

__all__ = [
    "MedidasCorporales",
    "calcular_grasa_navy",
    "calcular_bmi",
    "clasificar_bmi",
    "calcular_ffmi",
    "calcular_macros_diarios",
    "carbos_flash",
]
