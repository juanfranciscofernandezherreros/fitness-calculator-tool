"""
api_rest.py — Public REST API with Swagger UI (flask-restx).

Provides a JSON-based REST endpoint for all fitness calculations.
Swagger UI is served at /api/docs.
"""

from flask_restx import Api, Namespace, Resource, fields

from fitness_tools import (
    MedidasCorporales,
    calcular_bmi,
    calcular_ffmi,
    calcular_grasa_navy,
    calcular_macros_diarios,
    clasificar_bmi,
)

# ── API definition ────────────────────────────────────────────────────────────

api = Api(
    title="Fitness Calculator API",
    version="1.0",
    description=(
        "Public REST API for body composition and daily macronutrient calculations.\n\n"
        "**Formulas implemented:**\n"
        "- **US Navy body-fat formula** (male & female)\n"
        "- **BMI** (WHO classification)\n"
        "- **FFMI** (normalised to 1.80 m)\n"
        "- **Daily macros** (protein 2 g/kg · fat 0.8 g/kg · remaining carbs)\n"
    ),
    doc="/api/docs",
    prefix="/api/v1",
)

ns = Namespace("calculate", description="Fitness calculations")
api.add_namespace(ns)

# ── Request model ─────────────────────────────────────────────────────────────

_input_model = api.model(
    "CalculateInput",
    {
        "calorias": fields.Float(
            required=True,
            description="Total daily caloric expenditure (kcal). Must be > 0.",
            example=3343.0,
        ),
        "peso": fields.Float(
            required=True,
            description="Body weight in kg. Must be > 0.",
            example=72.25,
        ),
        "altura": fields.Float(
            required=True,
            description="Height in cm. Must be > 0.",
            example=175.0,
        ),
        "cintura": fields.Float(
            required=True,
            description="Waist circumference in cm. Must be > 0 and > neck.",
            example=84.0,
        ),
        "cuello": fields.Float(
            required=True,
            description="Neck circumference in cm. Must be > 0.",
            example=38.0,
        ),
        "sexo": fields.String(
            required=False,
            description='Biological sex: "hombre" (male) or "mujer" (female). Default: "hombre".',
            enum=["hombre", "mujer"],
            default="hombre",
            example="hombre",
        ),
        "grasa": fields.Float(
            required=False,
            description="Directly measured body-fat percentage (e.g. from a smart scale). Optional.",
            example=14.5,
        ),
        "cadera": fields.Float(
            required=False,
            description="Hip circumference in cm. Required when sexo=mujer.",
            example=None,
        ),
        "biceps_der": fields.Float(
            required=False,
            description="Right bicep circumference in cm. Optional.",
            example=35.0,
        ),
        "biceps_izq": fields.Float(
            required=False,
            description="Left bicep circumference in cm. Optional.",
            example=34.5,
        ),
        "cuadriceps_der": fields.Float(
            required=False,
            description="Right quadriceps circumference in cm. Optional.",
            example=55.0,
        ),
        "cuadriceps_izq": fields.Float(
            required=False,
            description="Left quadriceps circumference in cm. Optional.",
            example=54.5,
        ),
        "gemelos_der": fields.Float(
            required=False,
            description="Right calf circumference in cm. Optional.",
            example=37.0,
        ),
        "gemelos_izq": fields.Float(
            required=False,
            description="Left calf circumference in cm. Optional.",
            example=36.5,
        ),
        "pectoral": fields.Float(
            required=False,
            description="Chest circumference in cm. Optional.",
            example=100.0,
        ),
    },
)

# ── Response models ───────────────────────────────────────────────────────────

_macros_model = api.model(
    "Macros",
    {
        "Proteína (g)": fields.Float(description="Daily protein in grams (2 g/kg)."),
        "Grasas (g)": fields.Float(description="Daily fat in grams (0.8 g/kg)."),
        "Carbohidratos (g)": fields.Float(description="Daily carbohydrates in grams (remaining calories / 4)."),
        "Calorías Totales": fields.Float(description="Total daily calories provided as input."),
    },
)

_result_model = api.model(
    "CalculateResult",
    {
        "grasa_navy": fields.Float(description="Body-fat percentage estimated by the US Navy formula."),
        "masa_magra": fields.Float(description="Lean body mass in kg."),
        "grasa_directa": fields.Float(description="Directly measured body-fat percentage (if provided), else null."),
        "diferencia_grasa": fields.Float(
            description="Difference between direct body-fat % and Navy estimate (if grasa was provided)."
        ),
        "bmi": fields.Float(description="Body Mass Index (kg/m²)."),
        "bmi_categoria": fields.String(description="WHO BMI category (e.g. 'Peso normal')."),
        "ffmi": fields.Float(description="Fat-Free Mass Index (kg/m²)."),
        "ffmi_norm": fields.Float(description="Normalised FFMI (referenced to 1.80 m height)."),
        "macros": fields.Nested(_macros_model, description="Daily macronutrient distribution."),
        "medidas": fields.Raw(description="Summary of all body measurements provided as input."),
    },
)

_response_model = api.model(
    "CalculateResponse",
    {
        "resultados": fields.Nested(_result_model, description="Calculation results."),
    },
)

_error_model = api.model(
    "ErrorResponse",
    {
        "error": fields.String(description="Human-readable error message."),
        "field": fields.String(description="Name of the field that caused the error, if applicable."),
    },
)


# ── Resource ──────────────────────────────────────────────────────────────────

@ns.route("")
class Calculate(Resource):
    """Endpoint for body-composition and macronutrient calculations."""

    @ns.expect(_input_model)
    @ns.response(200, "Calculation successful.", _response_model)
    @ns.response(400, "Invalid input data.", _error_model)
    @ns.response(500, "Unexpected server error.", _error_model)
    def post(self):
        """
        Calculate body composition and daily macros.

        Submit your body measurements and daily caloric expenditure to receive:
        - Body-fat percentage (US Navy formula)
        - Lean body mass
        - BMI with WHO category
        - FFMI (raw and normalised)
        - Daily macronutrient distribution (protein, fat, carbs)
        """
        data = api.payload or {}

        # ── Required fields ──────────────────────────────────────────────────
        for field in ("calorias", "peso", "altura", "cintura", "cuello"):
            if field not in data or data[field] is None:
                return {"error": f"The field '{field}' is required.", "field": field}, 400
            try:
                val = float(data[field])
            except (TypeError, ValueError):
                return {
                    "error": f"'{data[field]}' is not a valid number for '{field}'.",
                    "field": field,
                }, 400
            if val <= 0:
                return {
                    "error": f"'{field}' must be a positive number greater than zero.",
                    "field": field,
                }, 400

        calorias = float(data["calorias"])
        peso = float(data["peso"])
        altura = float(data["altura"])
        cintura = float(data["cintura"])
        cuello = float(data["cuello"])

        sexo = data.get("sexo", "hombre")
        if sexo not in ("hombre", "mujer"):
            sexo = "hombre"

        # ── Optional fields ──────────────────────────────────────────────────
        def _optional(key):
            val = data.get(key)
            if val is None:
                return None
            try:
                f = float(val)
            except (TypeError, ValueError):
                return None
            return f if f > 0 else None

        grasa = _optional("grasa")
        cadera = _optional("cadera")
        biceps_der = _optional("biceps_der")
        biceps_izq = _optional("biceps_izq")
        cuadriceps_der = _optional("cuadriceps_der")
        cuadriceps_izq = _optional("cuadriceps_izq")
        gemelos_der = _optional("gemelos_der")
        gemelos_izq = _optional("gemelos_izq")
        pectoral = _optional("pectoral")

        # ── Calculations ─────────────────────────────────────────────────────
        try:
            medidas = MedidasCorporales(
                peso=peso,
                altura=altura,
                cintura=cintura,
                cuello=cuello,
                sexo=sexo,
                grasa_directa=grasa,
                biceps_der=biceps_der,
                biceps_izq=biceps_izq,
                cuadriceps_der=cuadriceps_der,
                cuadriceps_izq=cuadriceps_izq,
                cadera=cadera,
                gemelos_der=gemelos_der,
                gemelos_izq=gemelos_izq,
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

        except ValueError as exc:
            return {"error": str(exc), "field": ""}, 400
        except Exception as exc:
            return {"error": f"Unexpected error: {exc}", "field": ""}, 500

        return {
            "resultados": {
                "grasa_navy": grasa_navy,
                "masa_magra": masa_magra,
                "grasa_directa": medidas.grasa_directa,
                "diferencia_grasa": diferencia_grasa,
                "bmi": bmi,
                "bmi_categoria": bmi_categoria,
                "ffmi": ffmi,
                "ffmi_norm": ffmi_norm,
                "macros": macros,
                "medidas": medidas.resumen(),
            }
        }, 200
