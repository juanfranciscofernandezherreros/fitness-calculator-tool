"""
Cálculos de composición corporal.
"""
import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class MedidasCorporales:
    """Registro de medidas antropométricas en centímetros."""

    peso: float
    altura: float
    cintura: float
    cuello: float
    grasa_directa: Optional[float] = None   # % grasa medida externamente
    biceps: Optional[float] = None
    cuadriceps: Optional[float] = None
    cadera: Optional[float] = None
    gemelos: Optional[float] = None
    pectoral: Optional[float] = None

    def resumen(self) -> dict:
        """Devuelve un diccionario con todas las medidas registradas."""
        datos = {
            "Peso (kg)": self.peso,
            "Altura (cm)": self.altura,
            "Cintura (cm)": self.cintura,
            "Cuello (cm)": self.cuello,
        }
        opcionales = {
            "Grasa directa (%)": self.grasa_directa,
            "Bíceps (cm)": self.biceps,
            "Cuádriceps (cm)": self.cuadriceps,
            "Cadera (cm)": self.cadera,
            "Gemelos (cm)": self.gemelos,
            "Pectoral (cm)": self.pectoral,
        }
        for clave, valor in opcionales.items():
            if valor is not None:
                datos[clave] = valor
        return datos


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
