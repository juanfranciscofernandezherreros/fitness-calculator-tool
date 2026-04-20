"""
main.py — Herramienta CLI de composición corporal y nutrición deportiva.

Calcula la distribución de macronutrientes del día, el porcentaje de grasa
corporal (fórmula US Navy hombres/mujeres), el IMC y el FFMI a partir de los
datos introducidos por argumento.

Uso básico (hombre):
    python main.py --calorias 3343 --peso 72.25 --altura 175 \\
                   --cintura 84 --cuello 38

Uso básico (mujer):
    python main.py --calorias 2200 --peso 60 --altura 165 \\
                   --cintura 70 --cuello 32 --cadera 95 --sexo mujer

Uso completo:
    python main.py --calorias 3343 --peso 72.25 --altura 175 \\
                   --grasa 14.5 \\
                   --cintura 84  --cuello 38   --cadera 95 \\
                   --biceps-der 35  --biceps-izq 34.5 \\
                   --cuadriceps-der 55 --cuadriceps-izq 54.5 \\
                   --gemelos-der 37  --gemelos-izq 36.5 \\
                   --pectoral 100 \\
                   --sexo hombre
"""

import argparse
import sys

from fitness_tools import (
    MedidasCorporales,
    calcular_bmi,
    calcular_ffmi,
    calcular_grasa_navy,
    calcular_macros_diarios,
    clasificar_bmi,
)


def _separador(titulo: str = "", ancho: int = 45) -> None:
    if titulo:
        print(f"\n{'─' * 3} {titulo} {'─' * (ancho - len(titulo) - 5)}")
    else:
        print("─" * ancho)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Composición corporal y distribución de macros diarios.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # ── Obligatorios ──────────────────────────────────────────────────────────
    parser.add_argument("--calorias", type=float, required=True,
                        metavar="KCAL",
                        help="Gasto calórico total del día (kcal).")
    parser.add_argument("--peso", type=float, required=True,
                        metavar="KG",
                        help="Peso corporal en kg.")
    parser.add_argument("--altura", type=float, required=True,
                        metavar="CM",
                        help="Altura en cm.")
    parser.add_argument("--cintura", type=float, required=True,
                        metavar="CM",
                        help="Circunferencia de cintura en cm.")
    parser.add_argument("--cuello", type=float, required=True,
                        metavar="CM",
                        help="Circunferencia de cuello en cm.")

    # ── Opcionales ────────────────────────────────────────────────────────────
    parser.add_argument("--sexo", choices=["hombre", "mujer"], default="hombre",
                        help="Sexo biológico (hombre o mujer). "
                             "La fórmula US Navy para mujeres requiere --cadera.")
    parser.add_argument("--grasa", type=float, default=None,
                        metavar="%",
                        help="Porcentaje de grasa medido directamente (ej. báscula).")
    parser.add_argument("--biceps-der", type=float, default=None,
                        metavar="CM", help="Circunferencia de bíceps derecho en cm.")
    parser.add_argument("--biceps-izq", type=float, default=None,
                        metavar="CM", help="Circunferencia de bíceps izquierdo en cm.")
    parser.add_argument("--cuadriceps-der", type=float, default=None,
                        metavar="CM", help="Circunferencia de cuádriceps derecho en cm.")
    parser.add_argument("--cuadriceps-izq", type=float, default=None,
                        metavar="CM", help="Circunferencia de cuádriceps izquierdo en cm.")
    parser.add_argument("--cadera", type=float, default=None,
                        metavar="CM",
                        help="Circunferencia de cadera en cm. "
                             "Obligatorio si --sexo mujer.")
    parser.add_argument("--gemelos-der", type=float, default=None,
                        metavar="CM", help="Circunferencia de gemelos derechos en cm.")
    parser.add_argument("--gemelos-izq", type=float, default=None,
                        metavar="CM", help="Circunferencia de gemelos izquierdos en cm.")
    parser.add_argument("--pectoral", type=float, default=None,
                        metavar="CM", help="Circunferencia de pectoral en cm.")

    args = parser.parse_args()

    # ── Registrar medidas ─────────────────────────────────────────────────────
    medidas = MedidasCorporales(
        peso=args.peso,
        altura=args.altura,
        cintura=args.cintura,
        cuello=args.cuello,
        sexo=args.sexo,
        grasa_directa=args.grasa,
        biceps_der=args.biceps_der,
        biceps_izq=args.biceps_izq,
        cuadriceps_der=args.cuadriceps_der,
        cuadriceps_izq=args.cuadriceps_izq,
        cadera=args.cadera,
        gemelos_der=args.gemelos_der,
        gemelos_izq=args.gemelos_izq,
        pectoral=args.pectoral,
    )

    # ── Calcular grasa Navy ───────────────────────────────────────────────────
    try:
        grasa_navy, masa_magra = calcular_grasa_navy(
            medidas.peso, medidas.altura, medidas.cintura, medidas.cuello,
            sexo=medidas.sexo, cadera=medidas.cadera,
        )
    except ValueError as exc:
        print(f"[ERROR] Cálculo de grasa Navy: {exc}", file=sys.stderr)
        sys.exit(1)

    # ── Calcular IMC y FFMI ───────────────────────────────────────────────────
    try:
        bmi = calcular_bmi(medidas.peso, medidas.altura)
        bmi_categoria = clasificar_bmi(bmi)
        ffmi, ffmi_norm = calcular_ffmi(masa_magra, medidas.altura)
    except ValueError as exc:
        print(f"[ERROR] Cálculo de IMC/FFMI: {exc}", file=sys.stderr)
        sys.exit(1)

    # ── Calcular macros ───────────────────────────────────────────────────────
    try:
        macros = calcular_macros_diarios(args.calorias, medidas.peso)
    except ValueError as exc:
        print(f"[ERROR] Cálculo de macros: {exc}", file=sys.stderr)
        sys.exit(1)

    # ── Mostrar resultados ────────────────────────────────────────────────────
    _separador("MEDIDAS CORPORALES")
    for nombre, valor in medidas.resumen().items():
        print(f"  {nombre:<25} {valor}")

    _separador("COMPOSICIÓN CORPORAL (US Navy)")
    print(f"  {'Grasa corporal (%):':<25} {grasa_navy} %")
    print(f"  {'Masa magra (kg):':<25} {masa_magra} kg")
    if medidas.grasa_directa is not None:
        diferencia = round(medidas.grasa_directa - grasa_navy, 2)
        signo = "+" if diferencia >= 0 else ""
        print(f"  {'Grasa directa (%):':<25} {medidas.grasa_directa} %  "
              f"(Δ Navy {signo}{diferencia} %)")

    _separador("IMC / FFMI")
    print(f"  {'IMC (kg/m²):':<25} {bmi}  [{bmi_categoria}]")
    print(f"  {'FFMI (kg/m²):':<25} {ffmi}")
    print(f"  {'FFMI normalizado:':<25} {ffmi_norm}  [referencia ♂ < 25 / ♀ < 22]")

    _separador("MACROS DEL DÍA")
    for nombre, valor in macros.items():
        unidad = "kcal" if "Calorías" in nombre else "g"
        print(f"  {nombre + ':':<25} {valor} {unidad}")

    _separador()


if __name__ == "__main__":
    main()
