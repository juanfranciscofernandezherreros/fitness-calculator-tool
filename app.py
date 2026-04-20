"""
app.py — Web app de composición corporal y nutrición deportiva.

Punto de entrada para Heroku (gunicorn app:app).
"""

import os

from flask import Flask, render_template, request

from fitness_tools import MedidasCorporales, calcular_grasa_navy, calcular_macros_diarios

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    resultados = None
    error = None

    if request.method == "POST":
        try:
            calorias = float(request.form["calorias"])
            peso = float(request.form["peso"])
            altura = float(request.form["altura"])
            cintura = float(request.form["cintura"])
            cuello = float(request.form["cuello"])

            grasa = _optional_float(request.form.get("grasa"))
            biceps = _optional_float(request.form.get("biceps"))
            cuadriceps = _optional_float(request.form.get("cuadriceps"))
            cadera = _optional_float(request.form.get("cadera"))
            gemelos = _optional_float(request.form.get("gemelos"))
            pectoral = _optional_float(request.form.get("pectoral"))

            medidas = MedidasCorporales(
                peso=peso,
                altura=altura,
                cintura=cintura,
                cuello=cuello,
                grasa_directa=grasa,
                biceps=biceps,
                cuadriceps=cuadriceps,
                cadera=cadera,
                gemelos=gemelos,
                pectoral=pectoral,
            )

            grasa_navy, masa_magra = calcular_grasa_navy(
                medidas.peso, medidas.altura, medidas.cintura, medidas.cuello
            )

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
                "macros": macros,
            }

        except ValueError as exc:
            error = str(exc)

    return render_template("index.html", resultados=resultados, error=error)


def _optional_float(value: str | None) -> float | None:
    """Devuelve float si el valor tiene contenido, None en caso contrario."""
    if value is None or value.strip() == "":
        return None
    return float(value)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
