"""
Cálculos de composición corporal.
"""
import math


def calcular_grasa_navy(peso: float, altura: float, cintura: float, cuello: float) -> tuple[float, float]:
    """
    Calcula el porcentaje de grasa corporal para hombres usando la fórmula US Navy
    y la masa magra resultante.

    Args:
        peso:    Peso corporal en kg.
        altura:  Altura en cm.
        cintura: Circunferencia de cintura en cm.
        cuello:  Circunferencia de cuello en cm.

    Returns:
        Tupla (bf_porcentaje, masa_magra) redondeados a 2 decimales.

    Raises:
        ValueError: Si cintura <= cuello (logaritmo indefinido) o si alguna medida
                    es no positiva.
    """
    if peso <= 0 or altura <= 0 or cintura <= 0 or cuello <= 0:
        raise ValueError("Todas las medidas deben ser valores positivos.")
    if cintura <= cuello:
        raise ValueError("La cintura debe ser mayor que el cuello.")

    bf_porcentaje = (
        495 / (1.0324 - 0.19077 * math.log10(cintura - cuello) + 0.15456 * math.log10(altura)) - 450
    )

    masa_grasa = peso * (bf_porcentaje / 100)
    masa_magra = peso - masa_grasa

    return round(bf_porcentaje, 2), round(masa_magra, 2)
