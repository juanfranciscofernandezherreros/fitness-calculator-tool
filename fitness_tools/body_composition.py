"""
Cálculos de composición corporal.

Fórmulas implementadas
----------------------
* US Navy (hombres): %BF = 495 / (1.0324 − 0.19077·log₁₀(cintura−cuello) + 0.15456·log₁₀(altura)) − 450
* US Navy (mujeres): %BF = 495 / (1.29579 − 0.35004·log₁₀(cintura+cadera−cuello) + 0.22100·log₁₀(altura)) − 450
* IMC:   peso (kg) / altura (m)²
* FFMI:  masa_magra (kg) / altura (m)²  [normalizado a 1.80 m: FFMI_n = FFMI + 6.1·(1.80 − altura_m)]
"""
import math
from dataclasses import dataclass, field
from typing import Literal, Optional

Sexo = Literal["hombre", "mujer"]


@dataclass
class MedidasCorporales:
    """Registro de medidas antropométricas en centímetros."""

    peso: float
    altura: float
    cintura: float
    cuello: float
    sexo: Sexo = "hombre"
    grasa_directa: Optional[float] = None   # % grasa medida externamente
    biceps_der: Optional[float] = None
    biceps_izq: Optional[float] = None
    cuadriceps_der: Optional[float] = None
    cuadriceps_izq: Optional[float] = None
    cadera: Optional[float] = None
    gemelos_der: Optional[float] = None
    gemelos_izq: Optional[float] = None
    pectoral: Optional[float] = None

    def resumen(self) -> dict:
        """Devuelve un diccionario con todas las medidas registradas."""
        datos = {
            "Sexo": self.sexo.capitalize(),
            "Peso (kg)": self.peso,
            "Altura (cm)": self.altura,
            "Cintura (cm)": self.cintura,
            "Cuello (cm)": self.cuello,
        }
        opcionales = {
            "Grasa directa (%)": self.grasa_directa,
            "Bíceps der. (cm)": self.biceps_der,
            "Bíceps izq. (cm)": self.biceps_izq,
            "Cuádriceps der. (cm)": self.cuadriceps_der,
            "Cuádriceps izq. (cm)": self.cuadriceps_izq,
            "Cadera (cm)": self.cadera,
            "Gemelos der. (cm)": self.gemelos_der,
            "Gemelos izq. (cm)": self.gemelos_izq,
            "Pectoral (cm)": self.pectoral,
        }
        for clave, valor in opcionales.items():
            if valor is not None:
                datos[clave] = valor
        return datos


def calcular_grasa_navy(
    peso: float,
    altura: float,
    cintura: float,
    cuello: float,
    sexo: Sexo = "hombre",
    cadera: Optional[float] = None,
) -> tuple[float, float]:
    """
    Calcula el porcentaje de grasa corporal usando la fórmula US Navy
    y la masa magra resultante.

    Fórmula hombres:
        %BF = 495 / (1.0324 − 0.19077·log₁₀(cintura−cuello)
                     + 0.15456·log₁₀(altura)) − 450

    Fórmula mujeres (requiere cadera):
        %BF = 495 / (1.29579 − 0.35004·log₁₀(cintura+cadera−cuello)
                     + 0.22100·log₁₀(altura)) − 450

    Args:
        peso:    Peso corporal en kg.
        altura:  Altura en cm.
        cintura: Circunferencia de cintura en cm.
        cuello:  Circunferencia de cuello en cm.
        sexo:    ``"hombre"`` (por defecto) o ``"mujer"``.
        cadera:  Circunferencia de cadera en cm. Obligatorio para mujeres.

    Returns:
        Tupla ``(bf_porcentaje, masa_magra)`` redondeados a 2 decimales.

    Raises:
        ValueError: Si alguna medida es no positiva, si la diferencia de
                    circunferencias produce un logaritmo indefinido, o si
                    ``sexo="mujer"`` y no se proporciona ``cadera``.
    """
    if peso <= 0 or altura <= 0 or cintura <= 0 or cuello <= 0:
        raise ValueError("Todas las medidas deben ser valores positivos.")

    if sexo not in ("hombre", "mujer"):
        raise ValueError("El parámetro 'sexo' debe ser 'hombre' o 'mujer'.")

    if sexo == "hombre":
        if cintura <= cuello:
            raise ValueError("La cintura debe ser mayor que el cuello.")
        bf_porcentaje = (
            495 / (1.0324 - 0.19077 * math.log10(cintura - cuello)
                   + 0.15456 * math.log10(altura)) - 450
        )
    else:
        if cadera is None or cadera <= 0:
            raise ValueError("Para mujeres es obligatorio proporcionar la cadera (valor positivo).")
        diferencia = cintura + cadera - cuello
        if diferencia <= 0:
            raise ValueError(
                "La suma cintura+cadera debe ser mayor que el cuello para que el "
                "logaritmo sea válido."
            )
        bf_porcentaje = (
            495 / (1.29579 - 0.35004 * math.log10(diferencia)
                   + 0.22100 * math.log10(altura)) - 450
        )

    masa_grasa = peso * (bf_porcentaje / 100)
    masa_magra = peso - masa_grasa

    return round(bf_porcentaje, 2), round(masa_magra, 2)


def calcular_bmi(peso: float, altura: float) -> float:
    """
    Calcula el Índice de Masa Corporal (IMC / BMI).

    Fórmula:
        IMC = peso (kg) / altura (m)²

    Args:
        peso:   Peso corporal en kg.
        altura: Altura en cm.

    Returns:
        IMC redondeado a 2 decimales.

    Raises:
        ValueError: Si peso o altura no son positivos.
    """
    if peso <= 0:
        raise ValueError("El peso debe ser un valor positivo.")
    if altura <= 0:
        raise ValueError("La altura debe ser un valor positivo.")

    altura_m = altura / 100.0
    return round(peso / (altura_m ** 2), 2)


def clasificar_bmi(bmi: float) -> str:
    """Devuelve la categoría de la OMS para el IMC dado."""
    if bmi < 18.5:
        return "Bajo peso"
    if bmi < 25.0:
        return "Peso normal"
    if bmi < 30.0:
        return "Sobrepeso"
    if bmi < 35.0:
        return "Obesidad grado I"
    if bmi < 40.0:
        return "Obesidad grado II"
    return "Obesidad grado III"


def calcular_ffmi(masa_magra: float, altura: float) -> tuple[float, float]:
    """
    Calcula el Índice de Masa Libre de Grasa (FFMI).

    Fórmulas:
        FFMI        = masa_magra (kg) / altura (m)²
        FFMI_norm   = FFMI + 6.1 × (1.80 − altura_m)   [normalizado a 1.80 m]

    El FFMI normalizado permite comparar entre personas de distinta estatura.
    Un FFMI > 25 en hombres o > 22 en mujeres suele considerarse el límite
    natural (sin fármacos).

    Args:
        masa_magra: Masa libre de grasa en kg.
        altura:     Altura en cm.

    Returns:
        Tupla ``(ffmi, ffmi_normalizado)`` redondeados a 2 decimales.

    Raises:
        ValueError: Si masa_magra o altura no son positivos.
    """
    if masa_magra <= 0:
        raise ValueError("La masa magra debe ser un valor positivo.")
    if altura <= 0:
        raise ValueError("La altura debe ser un valor positivo.")

    altura_m = altura / 100.0
    ffmi = masa_magra / (altura_m ** 2)
    ffmi_norm = ffmi + 6.1 * (1.80 - altura_m)

    return round(ffmi, 2), round(ffmi_norm, 2)
