"""
app.py — Web app de composición corporal y nutrición deportiva.

Punto de entrada para Heroku (gunicorn app:app).
"""

import math
import os

from flask import Flask, render_template, request

from fitness_tools import (
    MedidasCorporales,
    calcular_bmi,
    calcular_ffmi,
    calcular_grasa_navy,
    calcular_macros_diarios,
    clasificar_bmi,
)

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    resultados = None
    error = None

    if request.method == "POST":
        try:
            calorias = _parse_float(request.form.get("calorias", ""), "Calorías")
            peso = _parse_float(request.form.get("peso", ""), "Peso")
            altura = _parse_float(request.form.get("altura", ""), "Altura")
            cintura = _parse_float(request.form.get("cintura", ""), "Cintura")
            cuello = _parse_float(request.form.get("cuello", ""), "Cuello")
            sexo = request.form.get("sexo", "hombre")
            if sexo not in ("hombre", "mujer"):
                sexo = "hombre"

            grasa = _optional_float(request.form.get("grasa"), "Grasa directa")
            biceps = _optional_float(request.form.get("biceps"), "Bíceps")
            cuadriceps = _optional_float(request.form.get("cuadriceps"), "Cuádriceps")
            cadera = _optional_float(request.form.get("cadera"), "Cadera")
            gemelos = _optional_float(request.form.get("gemelos"), "Gemelos")
            pectoral = _optional_float(request.form.get("pectoral"), "Pectoral")

            medidas = MedidasCorporales(
                peso=peso,
                altura=altura,
                cintura=cintura,
                cuello=cuello,
                sexo=sexo,
                grasa_directa=grasa,
                biceps=biceps,
                cuadriceps=cuadriceps,
                cadera=cadera,
                gemelos=gemelos,
                pectoral=pectoral,
            )

            grasa_navy, masa_magra = calcular_grasa_navy(
                medidas.peso,
                medidas.altura,
                medidas.cintura,
                medidas.cuello,
                sexo=medidas.sexo,
                cadera=medidas.cadera,
            )

            bmi = calcular_bmi(medidas.peso, medidas.altura)
            bmi_categoria = clasificar_bmi(bmi)
            ffmi, ffmi_norm = calcular_ffmi(masa_magra, medidas.altura)

            macros = calcular_macros_diarios(calorias, medidas.peso)

            diferencia_grasa = None
            if medidas.grasa_directa is not None:
                diferencia_grasa = round(medidas.grasa_directa - grasa_navy, 2)

            # ── Pasos intermedios para el informe detallado ──────────────────
            altura_m = round(medidas.altura / 100, 4)

            # US Navy – hombre
            if medidas.sexo == "hombre":
                navy_dif = round(medidas.cintura - medidas.cuello, 2)
                navy_log_dif = round(math.log10(navy_dif), 6)
                navy_log_alt = round(math.log10(medidas.altura), 6)
                navy_denominador = round(
                    1.0324 - 0.19077 * navy_log_dif + 0.15456 * navy_log_alt, 6
                )
                navy_formula = (
                    "495 / (1.0324 − 0.19077 × log₁₀(cintura − cuello)"
                    " + 0.15456 × log₁₀(altura)) − 450"
                )
                navy_extra_label = None
                navy_extra_val = None
            else:
                # cadera is guaranteed non-None here: calcular_grasa_navy already
                # raised ValueError if it were missing for a female subject.
                navy_dif = round(medidas.cintura + medidas.cadera - medidas.cuello, 2)
                navy_log_dif = round(math.log10(navy_dif), 6)
                navy_log_alt = round(math.log10(medidas.altura), 6)
                navy_denominador = round(
                    1.29579 - 0.35004 * navy_log_dif + 0.22100 * navy_log_alt, 6
                )
                navy_formula = (
                    "495 / (1.29579 − 0.35004 × log₁₀(cintura + cadera − cuello)"
                    " + 0.22100 × log₁₀(altura)) − 450"
                )
                navy_extra_label = "cintura + cadera − cuello"
                navy_extra_val = navy_dif

            masa_grasa_kg = round(medidas.peso * (grasa_navy / 100), 2)

            # Macros intermedios
            proteina_g = round(medidas.peso * 2.0, 1)
            grasa_g = round(medidas.peso * 0.8, 1)
            cal_proteina = round(proteina_g * 4, 1)
            cal_grasa_macro = round(grasa_g * 9, 1)
            cal_carbos = round(calorias - cal_proteina - cal_grasa_macro, 1)
            carbos_g = round(cal_carbos / 4, 1)

            pasos = {
                # --- US Navy ---
                "navy_sexo": medidas.sexo,
                "navy_formula": navy_formula,
                "navy_cintura": medidas.cintura,
                "navy_cuello": medidas.cuello,
                "navy_cadera": medidas.cadera,
                "navy_extra_label": navy_extra_label,
                "navy_extra_val": navy_extra_val,
                "navy_dif": navy_dif,
                "navy_log_dif": navy_log_dif,
                "navy_log_alt": navy_log_alt,
                "navy_altura": medidas.altura,
                "navy_denominador": navy_denominador,
                "navy_grasa": grasa_navy,
                # --- Masa magra ---
                "mm_peso": medidas.peso,
                "mm_masa_grasa": masa_grasa_kg,
                "mm_masa_magra": masa_magra,
                # --- IMC ---
                "imc_peso": medidas.peso,
                "imc_altura_cm": medidas.altura,
                "imc_altura_m": altura_m,
                "imc_altura_m_cuadrado": round(altura_m ** 2, 4),
                "imc_valor": bmi,
                "imc_categoria": bmi_categoria,
                # --- FFMI ---
                "ffmi_masa_magra": masa_magra,
                "ffmi_altura_m": altura_m,
                "ffmi_altura_m_cuadrado": round(altura_m ** 2, 4),
                "ffmi_valor": ffmi,
                "ffmi_norm_valor": ffmi_norm,
                # --- Macros ---
                "macro_kcal": calorias,
                "macro_peso": medidas.peso,
                "macro_proteina_g": proteina_g,
                "macro_grasa_g": grasa_g,
                "macro_cal_proteina": cal_proteina,
                "macro_cal_grasa": cal_grasa_macro,
                "macro_cal_carbos": cal_carbos,
                "macro_carbos_g": carbos_g,
            }

            resultados = {
                "medidas": medidas.resumen(),
                "grasa_navy": grasa_navy,
                "masa_magra": masa_magra,
                "grasa_directa": medidas.grasa_directa,
                "diferencia_grasa": diferencia_grasa,
                "bmi": bmi,
                "bmi_categoria": bmi_categoria,
                "ffmi": ffmi,
                "ffmi_norm": ffmi_norm,
                "macros": macros,
                "pasos": pasos,
            }

        except Exception as exc:
            error = str(exc)

    return render_template("index.html", resultados=resultados, error=error)


def _parse_float(value: str | None, campo: str) -> float:
    """Convierte un valor de formulario a float con mensaje de error legible."""
    if value is None or value.strip() == "":
        raise ValueError(f"El campo '{campo}' es obligatorio y no puede estar vacío.")
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"El valor '{value}' introducido en '{campo}' no es un número válido.")


def _optional_float(value: str | None, campo: str = "") -> float | None:
    """Devuelve float si el valor tiene contenido, None en caso contrario."""
    if value is None or value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        campo_txt = f" en '{campo}'" if campo else ""
        raise ValueError(f"El valor '{value}'{campo_txt} no es un número válido.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
