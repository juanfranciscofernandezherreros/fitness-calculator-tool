"""
test_fitness_tools.py — Tests de la funcionalidad completa de fitness_tools.

Cubre:
    - MedidasCorporales.resumen()
    - calcular_grasa_navy()
    - calcular_macros_diarios()
    - carbos_flash()
    - CLI main.py (invocación mediante subprocess)
"""

import math
import subprocess
import sys

import pytest

from fitness_tools import (
    MedidasCorporales,
    calcular_grasa_navy,
    calcular_macros_diarios,
    carbos_flash,
)


# ─────────────────────────────────────────────────────────────────────────────
# MedidasCorporales
# ─────────────────────────────────────────────────────────────────────────────

class TestMedidasCorporales:
    """Tests para el dataclass MedidasCorporales y su método resumen()."""

    def test_resumen_campos_obligatorios(self):
        """resumen() incluye siempre los cuatro campos obligatorios."""
        m = MedidasCorporales(peso=72.0, altura=175.0, cintura=84.0, cuello=38.0)
        r = m.resumen()
        assert r["Peso (kg)"] == 72.0
        assert r["Altura (cm)"] == 175.0
        assert r["Cintura (cm)"] == 84.0
        assert r["Cuello (cm)"] == 38.0

    def test_resumen_sin_opcionales(self):
        """resumen() no incluye claves opcionales cuando no se proporcionan."""
        m = MedidasCorporales(peso=70.0, altura=180.0, cintura=80.0, cuello=36.0)
        r = m.resumen()
        claves_opcionales = {
            "Grasa directa (%)", "Bíceps (cm)", "Cuádriceps (cm)",
            "Cadera (cm)", "Gemelos (cm)", "Pectoral (cm)",
        }
        assert claves_opcionales.isdisjoint(r.keys())

    def test_resumen_con_todos_los_opcionales(self):
        """resumen() incluye todos los opcionales cuando se suministran."""
        m = MedidasCorporales(
            peso=72.25, altura=175.0, cintura=84.0, cuello=38.0,
            grasa_directa=14.5, biceps=35.0, cuadriceps=55.0,
            cadera=95.0, gemelos=37.0, pectoral=100.0,
        )
        r = m.resumen()
        assert r["Grasa directa (%)"] == 14.5
        assert r["Bíceps (cm)"] == 35.0
        assert r["Cuádriceps (cm)"] == 55.0
        assert r["Cadera (cm)"] == 95.0
        assert r["Gemelos (cm)"] == 37.0
        assert r["Pectoral (cm)"] == 100.0

    def test_resumen_con_algunos_opcionales(self):
        """resumen() incluye sólo los opcionales que tienen valor."""
        m = MedidasCorporales(
            peso=80.0, altura=178.0, cintura=90.0, cuello=40.0,
            biceps=38.0,
        )
        r = m.resumen()
        assert "Bíceps (cm)" in r
        assert "Cuádriceps (cm)" not in r

    def test_grasa_directa_atributo(self):
        """El atributo grasa_directa es accesible directamente."""
        m = MedidasCorporales(
            peso=70.0, altura=175.0, cintura=82.0, cuello=37.0,
            grasa_directa=12.0,
        )
        assert m.grasa_directa == 12.0

    def test_grasa_directa_none_por_defecto(self):
        """grasa_directa es None cuando no se proporciona."""
        m = MedidasCorporales(peso=70.0, altura=175.0, cintura=82.0, cuello=37.0)
        assert m.grasa_directa is None


# ─────────────────────────────────────────────────────────────────────────────
# calcular_grasa_navy
# ─────────────────────────────────────────────────────────────────────────────

class TestCalcularGrasaNavy:
    """Tests para la función calcular_grasa_navy()."""

    # Valor de referencia calculado con la fórmula:
    #   BF% = 495 / (1.0324 - 0.19077*log10(cintura-cuello) + 0.15456*log10(altura)) - 450
    PESO, ALTURA, CINTURA, CUELLO = 72.25, 175.0, 84.0, 38.0

    def _bf_esperado(self, altura, cintura, cuello):
        return 495 / (
            1.0324
            - 0.19077 * math.log10(cintura - cuello)
            + 0.15456 * math.log10(altura)
        ) - 450

    def test_retorna_tupla_dos_floats(self):
        bf, magra = calcular_grasa_navy(self.PESO, self.ALTURA, self.CINTURA, self.CUELLO)
        assert isinstance(bf, float)
        assert isinstance(magra, float)

    def test_porcentaje_grasa_correcto(self):
        bf, _ = calcular_grasa_navy(self.PESO, self.ALTURA, self.CINTURA, self.CUELLO)
        esperado = round(self._bf_esperado(self.ALTURA, self.CINTURA, self.CUELLO), 2)
        assert bf == esperado

    def test_masa_magra_correcta(self):
        bf, magra = calcular_grasa_navy(self.PESO, self.ALTURA, self.CINTURA, self.CUELLO)
        masa_grasa = self.PESO * (bf / 100)
        esperado = round(self.PESO - masa_grasa, 2)
        assert magra == esperado

    def test_resultado_redondeado_a_dos_decimales(self):
        bf, magra = calcular_grasa_navy(self.PESO, self.ALTURA, self.CINTURA, self.CUELLO)
        assert bf == round(bf, 2)
        assert magra == round(magra, 2)

    def test_porcentaje_en_rango_fisiologico(self):
        """Para un adulto sano el BF% debe estar entre 5% y 40%."""
        bf, _ = calcular_grasa_navy(self.PESO, self.ALTURA, self.CINTURA, self.CUELLO)
        assert 5.0 <= bf <= 40.0

    def test_masa_magra_menor_que_peso(self):
        _, magra = calcular_grasa_navy(self.PESO, self.ALTURA, self.CINTURA, self.CUELLO)
        assert magra < self.PESO

    # ── Casos de error ────────────────────────────────────────────────────────

    def test_error_cintura_igual_cuello(self):
        with pytest.raises(ValueError, match="mayor que el cuello"):
            calcular_grasa_navy(70.0, 175.0, 38.0, 38.0)

    def test_error_cintura_menor_cuello(self):
        with pytest.raises(ValueError, match="mayor que el cuello"):
            calcular_grasa_navy(70.0, 175.0, 35.0, 40.0)

    def test_error_peso_cero(self):
        with pytest.raises(ValueError, match="positivos"):
            calcular_grasa_navy(0, 175.0, 84.0, 38.0)

    def test_error_peso_negativo(self):
        with pytest.raises(ValueError, match="positivos"):
            calcular_grasa_navy(-1.0, 175.0, 84.0, 38.0)

    def test_error_altura_cero(self):
        with pytest.raises(ValueError, match="positivos"):
            calcular_grasa_navy(72.0, 0, 84.0, 38.0)

    def test_error_cintura_cero(self):
        with pytest.raises(ValueError, match="positivos"):
            calcular_grasa_navy(72.0, 175.0, 0, 38.0)

    def test_error_cuello_cero(self):
        with pytest.raises(ValueError, match="positivos"):
            calcular_grasa_navy(72.0, 175.0, 84.0, 0)

    def test_valores_extremos_validos(self):
        """Valores extremos pero físicamente posibles no deben lanzar excepción."""
        bf, magra = calcular_grasa_navy(120.0, 200.0, 110.0, 40.0)
        assert isinstance(bf, float)
        assert isinstance(magra, float)


# ─────────────────────────────────────────────────────────────────────────────
# calcular_macros_diarios
# ─────────────────────────────────────────────────────────────────────────────

class TestCalcularMacrosDiarios:
    """Tests para la función calcular_macros_diarios()."""

    KCAL, PESO = 3343.0, 72.25

    def test_retorna_diccionario_con_cuatro_claves(self):
        r = calcular_macros_diarios(self.KCAL, self.PESO)
        assert set(r.keys()) == {"Proteína (g)", "Grasas (g)", "Carbohidratos (g)", "Calorías Totales"}

    def test_proteina_dos_gramos_por_kg(self):
        r = calcular_macros_diarios(self.KCAL, self.PESO)
        assert r["Proteína (g)"] == round(self.PESO * 2.0, 1)

    def test_grasa_punto_ocho_gramos_por_kg(self):
        r = calcular_macros_diarios(self.KCAL, self.PESO)
        assert r["Grasas (g)"] == round(self.PESO * 0.8, 1)

    def test_calorias_totales_iguales_a_entrada(self):
        r = calcular_macros_diarios(self.KCAL, self.PESO)
        assert r["Calorías Totales"] == self.KCAL

    def test_carbohidratos_cubren_calorias_restantes(self):
        r = calcular_macros_diarios(self.KCAL, self.PESO)
        cal_proteina = r["Proteína (g)"] * 4
        cal_grasa = r["Grasas (g)"] * 9
        cal_carbos = r["Carbohidratos (g)"] * 4
        # La suma total debe ser ≈ kcal_quemadas (error de redondeo < 2 kcal)
        assert abs(cal_proteina + cal_grasa + cal_carbos - self.KCAL) < 2.0

    def test_carbohidratos_son_positivos(self):
        r = calcular_macros_diarios(self.KCAL, self.PESO)
        assert r["Carbohidratos (g)"] >= 0

    def test_valores_redondeados_a_un_decimal(self):
        r = calcular_macros_diarios(self.KCAL, self.PESO)
        for clave in ("Proteína (g)", "Grasas (g)", "Carbohidratos (g)"):
            assert r[clave] == round(r[clave], 1)

    def test_calorias_justas_para_macros_fijos(self):
        """Cuando las kcal exactamente cubren proteína+grasa, carbos deben ser 0."""
        peso = 50.0
        cal_fijas = (peso * 2.0 * 4) + (peso * 0.8 * 9)
        r = calcular_macros_diarios(cal_fijas, peso)
        assert r["Carbohidratos (g)"] == 0.0

    # ── Casos de error ────────────────────────────────────────────────────────

    def test_error_kcal_cero(self):
        with pytest.raises(ValueError, match="positivo"):
            calcular_macros_diarios(0, 72.0)

    def test_error_kcal_negativo(self):
        with pytest.raises(ValueError, match="positivo"):
            calcular_macros_diarios(-100, 72.0)

    def test_error_peso_cero(self):
        with pytest.raises(ValueError, match="positivo"):
            calcular_macros_diarios(2000, 0)

    def test_error_peso_negativo(self):
        with pytest.raises(ValueError, match="positivo"):
            calcular_macros_diarios(2000, -5.0)

    def test_error_calorias_insuficientes(self):
        """kcal inferior a los macros fijos debe lanzar ValueError."""
        peso = 100.0
        cal_fijas = (peso * 2.0 * 4) + (peso * 0.8 * 9)  # 1520 kcal
        with pytest.raises(ValueError, match="insuficiente"):
            calcular_macros_diarios(cal_fijas - 1, peso)


# ─────────────────────────────────────────────────────────────────────────────
# carbos_flash
# ─────────────────────────────────────────────────────────────────────────────

class TestCarbosFlash:
    """Tests para la función carbos_flash()."""

    def test_resultado_igual_que_macros_diarios(self):
        """carbos_flash() debe coincidir con los carbohidratos de calcular_macros_diarios()."""
        kcal, peso = 3343.0, 72.25
        macros = calcular_macros_diarios(kcal, peso)
        assert carbos_flash(kcal, peso) == macros["Carbohidratos (g)"]

    def test_retorna_float(self):
        resultado = carbos_flash(2500.0, 70.0)
        assert isinstance(resultado, float)

    def test_redondeado_a_un_decimal(self):
        resultado = carbos_flash(2500.0, 70.0)
        assert resultado == round(resultado, 1)

    def test_calorias_justas_dan_cero_carbos(self):
        peso = 60.0
        cal_fijas = (peso * 2.0 * 4) + (peso * 0.8 * 9)
        assert carbos_flash(cal_fijas, peso) == 0.0

    # ── Casos de error ────────────────────────────────────────────────────────

    def test_error_kcal_cero(self):
        with pytest.raises(ValueError, match="positivo"):
            carbos_flash(0, 70.0)

    def test_error_kcal_negativo(self):
        with pytest.raises(ValueError, match="positivo"):
            carbos_flash(-500, 70.0)

    def test_error_peso_cero(self):
        with pytest.raises(ValueError, match="positivo"):
            carbos_flash(2000, 0)

    def test_error_peso_negativo(self):
        with pytest.raises(ValueError, match="positivo"):
            carbos_flash(2000, -10.0)

    def test_error_calorias_insuficientes(self):
        peso = 80.0
        cal_fijas = (peso * 2.0 * 4) + (peso * 0.8 * 9)
        with pytest.raises(ValueError, match="superan"):
            carbos_flash(cal_fijas - 1, peso)


# ─────────────────────────────────────────────────────────────────────────────
# CLI — main.py
# ─────────────────────────────────────────────────────────────────────────────

def _run_cli(*extra_args):
    """Ejecuta main.py con los argumentos dados y devuelve el resultado."""
    cmd = [
        sys.executable, "main.py",
        "--calorias", "3343",
        "--peso", "72.25",
        "--altura", "175",
        "--cintura", "84",
        "--cuello", "38",
        *extra_args,
    ]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd="/home/runner/work/repo/repo",
    )


class TestCLI:
    """Tests de integración para la interfaz de línea de comandos (main.py)."""

    def test_ejecucion_basica_exitosa(self):
        """La invocación mínima obligatoria debe terminar con código 0."""
        result = _run_cli()
        assert result.returncode == 0

    def test_salida_contiene_secciones_esperadas(self):
        result = _run_cli()
        stdout = result.stdout
        assert "MEDIDAS CORPORALES" in stdout
        assert "COMPOSICIÓN CORPORAL" in stdout
        assert "MACROS DEL DÍA" in stdout

    def test_salida_contiene_grasa_corporal(self):
        result = _run_cli()
        assert "Grasa corporal" in result.stdout

    def test_salida_contiene_masa_magra(self):
        result = _run_cli()
        assert "Masa magra" in result.stdout

    def test_salida_contiene_macros(self):
        result = _run_cli()
        stdout = result.stdout
        assert "Proteína" in stdout
        assert "Grasas" in stdout
        assert "Carbohidratos" in stdout

    def test_ejecucion_con_todos_los_opcionales(self):
        """Con todos los parámetros opcionales el código de retorno es 0."""
        result = _run_cli(
            "--grasa", "14.5",
            "--biceps", "35",
            "--cuadriceps", "55",
            "--cadera", "95",
            "--gemelos", "37",
            "--pectoral", "100",
        )
        assert result.returncode == 0

    def test_grasa_directa_aparece_en_salida(self):
        """Al pasar --grasa aparece la línea de grasa directa con el delta."""
        result = _run_cli("--grasa", "14.5")
        assert "Grasa directa" in result.stdout
        assert "Navy" in result.stdout

    def test_error_cintura_igual_cuello(self):
        """Cintura == cuello provoca salida con código distinto de 0."""
        cmd = [
            sys.executable, "main.py",
            "--calorias", "3000",
            "--peso", "70",
            "--altura", "175",
            "--cintura", "38",
            "--cuello", "38",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/home/runner/work/repo/repo",
        )
        assert result.returncode != 0
        assert "ERROR" in result.stderr

    def test_falta_argumento_obligatorio(self):
        """Omitir un argumento obligatorio provoca código de error."""
        cmd = [
            sys.executable, "main.py",
            "--calorias", "3000",
            "--peso", "70",
            # falta --altura, --cintura, --cuello
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/home/runner/work/repo/repo",
        )
        assert result.returncode != 0

    def test_no_stderr_en_ejecucion_normal(self):
        """En una ejecución normal no debe haber salida en stderr."""
        result = _run_cli()
        assert result.stderr == ""
