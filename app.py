"""
app.py — Web app de composición corporal y nutrición deportiva.

Punto de entrada para Heroku (gunicorn app:app).
"""

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
