"""
Cálculo de macronutrientes y distribución calórica.
"""


def calcular_macros_diarios(kcal_quemadas: float, peso: float) -> dict:
    """
    Calcula la distribución de macronutrientes para el día basándose en el gasto
    calórico total, manteniendo proteína y grasa fijas para rendimiento deportivo.

    Pilares fijos:
        - Proteína: 2 g por kg de peso corporal
        - Grasa:    0.8 g por kg de peso corporal
        - Carbohidratos: el resto de calorías hasta cubrir el gasto total

    Args:
        kcal_quemadas: Gasto calórico total del día (kcal).
        peso:          Peso corporal en kg.

    Returns:
        Diccionario con las claves:
            ``"Proteína (g)"``, ``"Grasas (g)"``, ``"Carbohidratos (g)"``
            y ``"Calorías Totales"``.

    Raises:
        ValueError: Si kcal_quemadas o peso son no positivos.

    Nota:
        Si las calorías indicadas son inferiores a las necesarias para cubrir
        los pilares fijos de proteína y grasa, los carbohidratos se ajustan a 0
        en lugar de lanzar un error, permitiendo enviar cualquier valor de
        calorías positivo.
    """
    if kcal_quemadas <= 0:
        raise ValueError("kcal_quemadas debe ser un valor positivo.")
    if peso <= 0:
        raise ValueError("peso debe ser un valor positivo.")

    proteina_g = peso * 2.0
    grasa_g = peso * 0.8

    cal_proteina = proteina_g * 4
    cal_grasa = grasa_g * 9

    cal_restantes = kcal_quemadas - (cal_proteina + cal_grasa)
    carbohidratos_g = max(cal_restantes / 4, 0.0)

    return {
        "Proteína (g)": round(proteina_g, 1),
        "Grasas (g)": round(grasa_g, 1),
        "Carbohidratos (g)": round(carbohidratos_g, 1),
        "Calorías Totales": kcal_quemadas,
    }


def carbos_flash(kcal: float, peso: float) -> float:
    """
    Calcula rápidamente los gramos de carbohidratos necesarios para un gasto
    calórico dado, descontando las calorías fijas de proteína (2 g/kg) y
    grasa (0.8 g/kg).

    Args:
        kcal:  Gasto calórico total del día (kcal).
        peso:  Peso corporal en kg.

    Returns:
        Gramos de carbohidratos redondeados a 1 decimal. Si las calorías
        fijas superan el gasto total, se devuelve ``0.0`` en lugar de lanzar
        un error.

    Raises:
        ValueError: Si kcal o peso son no positivos.
    """
    if kcal <= 0:
        raise ValueError("kcal debe ser un valor positivo.")
    if peso <= 0:
        raise ValueError("peso debe ser un valor positivo.")

    cal_fijas = (peso * 2.0 * 4) + (peso * 0.8 * 9)
    g_carbos = max((kcal - cal_fijas) / 4, 0.0)

    return round(g_carbos, 1)
