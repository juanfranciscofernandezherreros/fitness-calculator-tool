"""
Calculadora de Macros para Corredor (Método US Navy)
=====================================================
Fórmulas basadas en:
  - % Grasa Corporal: US Navy Body Fat Formula (hombres)
  - Proteína: 2.0 g/kg de peso
  - Grasa: 0.8 g/kg de peso
  - Carbohidratos: calorías restantes divididas entre 4
"""

import math


def calcular_porcentaje_grasa(cintura_cm: float, cuello_cm: float, altura_cm: float) -> float:
    """
    Calcula el porcentaje de grasa corporal usando la fórmula US Navy (hombres).

    BF% = 495 / (1.0324 - 0.19077 * log10(cintura - cuello) + 0.15456 * log10(altura)) - 450

    Args:
        cintura_cm: Circunferencia de cintura en centímetros.
        cuello_cm:  Circunferencia de cuello en centímetros.
        altura_cm:  Altura en centímetros.

    Returns:
        Porcentaje de grasa corporal (%).
    """
    bf_pct = (
        495 / (1.0324 - 0.19077 * math.log10(cintura_cm - cuello_cm) + 0.15456 * math.log10(altura_cm))
        - 450
    )
    return bf_pct


def calcular_masa_magra(peso_kg: float, bf_pct: float) -> float:
    """
    Calcula la masa magra (Lean Body Mass).

    LBM = peso * (1 - BF% / 100)

    Args:
        peso_kg: Peso corporal en kilogramos.
        bf_pct:  Porcentaje de grasa corporal (%).

    Returns:
        Masa magra en kilogramos.
    """
    return peso_kg * (1 - bf_pct / 100)


def calcular_macros(kcal: float, peso_kg: float) -> dict:
    """
    Calcula los macronutrientes diarios a partir de las calorías totales y el peso.

    - Proteína:      2.0 g/kg  → 4 kcal/g
    - Grasa:         0.8 g/kg  → 9 kcal/g
    - Carbohidratos: resto de calorías ÷ 4 kcal/g

    Args:
        kcal:    Calorías totales del día (p. ej. gasto energético del entrenamiento + TDEE).
        peso_kg: Peso corporal en kilogramos.

    Returns:
        Diccionario con gramos y calorías de cada macro, más el total de calorías.
    """
    proteina_g = peso_kg * 2.0
    proteina_kcal = proteina_g * 4

    grasa_g = peso_kg * 0.8
    grasa_kcal = grasa_g * 9

    cal_fijas = proteina_kcal + grasa_kcal
    carbos_g = (kcal - cal_fijas) / 4
    carbos_kcal = carbos_g * 4

    return {
        "proteina_g": round(proteina_g, 1),
        "proteina_kcal": round(proteina_kcal, 1),
        "grasa_g": round(grasa_g, 1),
        "grasa_kcal": round(grasa_kcal, 1),
        "carbos_g": round(carbos_g, 1),
        "carbos_kcal": round(carbos_kcal, 1),
        "total_kcal": round(proteina_kcal + grasa_kcal + carbos_kcal, 1),
    }


def main() -> None:
    # ── Datos personales ──────────────────────────────────────────────────────
    peso_kg = 72.25      # kg
    altura_cm = 175.0    # cm  ← ajusta tu talla real

    # ── Medidas para el % de grasa (US Navy) ─────────────────────────────────
    # Si aún no las tienes, déjalas en None y el cálculo del BF% se omitirá.
    cintura_cm: float | None = None   # p. ej. 85.0
    cuello_cm: float | None = None    # p. ej. 38.0

    # ── Calorías del día (gasto total medido/estimado) ────────────────────────
    kcal_dia = 3343.0   # ejemplo: Trail del sábado

    print("=" * 55)
    print("       CALCULADORA DE MACROS — CORREDOR")
    print("=" * 55)
    print(f"  Peso:   {peso_kg} kg")
    print(f"  Altura: {altura_cm} cm")
    print(f"  Kcal del día: {kcal_dia:.0f} kcal")
    print("-" * 55)

    # ── % Grasa corporal ──────────────────────────────────────────────────────
    if cintura_cm is not None and cuello_cm is not None:
        bf_pct = calcular_porcentaje_grasa(cintura_cm, cuello_cm, altura_cm)
        lbm = calcular_masa_magra(peso_kg, bf_pct)
        print(f"  Cintura: {cintura_cm} cm  |  Cuello: {cuello_cm} cm")
        print(f"  % Grasa corporal (US Navy): {bf_pct:.2f} %")
        print(f"  Masa Magra (LBM):           {lbm:.2f} kg")
    else:
        print("  % Grasa: introduce cintura_cm y cuello_cm para calcularlo.")

    # ── Macros ────────────────────────────────────────────────────────────────
    macros = calcular_macros(kcal_dia, peso_kg)
    print("-" * 55)
    print("  MACROS:")
    print(f"    Proteína:      {macros['proteina_g']:>6.1f} g  →  {macros['proteina_kcal']:>7.1f} kcal")
    print(f"    Grasa:         {macros['grasa_g']:>6.1f} g  →  {macros['grasa_kcal']:>7.1f} kcal")
    print(f"    Carbohidratos: {macros['carbos_g']:>6.1f} g  →  {macros['carbos_kcal']:>7.1f} kcal")
    print("-" * 55)
    print(f"    TOTAL:                      {macros['total_kcal']:>7.1f} kcal")
    print("=" * 55)

    # ── Fórmula rápida (constante fija para 72.25 kg) ─────────────────────────
    constante_fija = macros["proteina_kcal"] + macros["grasa_kcal"]
    carbos_rapido = (kcal_dia - constante_fija) / 4
    print(f"\n  Fórmula rápida (constante fija = {constante_fija:.0f} kcal):")
    print(f"    Carbos = (Kcal − {constante_fija:.0f}) / 4  =  {carbos_rapido:.1f} g")
    print()


if __name__ == "__main__":
    main()
