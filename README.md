# fitness_tools 💪

[![CI](https://github.com/juanfranciscofernandezherreros/fitness-calculator-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/juanfranciscofernandezherreros/fitness-calculator-tool/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)](https://flask.palletsprojects.com/)

Herramienta de **composición corporal** y **distribución de macronutrientes** diarios.
Disponible como **web app Flask** multiidioma (12 idiomas) y como CLI de línea de comandos.

---

## Web app (Flask)

### Ejecución local

```bash
pip install -r requirements.txt
pip install -e .
python app.py          # abre http://localhost:5000
```

### Despliegue en Heroku

```bash
# 1. Crea la app en Heroku (solo la primera vez)
heroku create <nombre-de-tu-app>

# 2. Despliega
git push heroku main

# 3. Abre en el navegador
heroku open
```

Los archivos necesarios para Heroku ya están incluidos:

| Archivo | Descripción |
|---------|-------------|
| `Procfile` | `web: gunicorn app:app` |
| `requirements.txt` | Flask + gunicorn |
| `runtime.txt` | Versión de Python |

---

## CLI (línea de comandos)

### Instalación

```bash
pip install -e .
```

> Requiere Python ≥ 3.9.

### Uso

```bash
python main.py [OPCIONES]
```

### Argumentos obligatorios

| Argumento | Tipo | Descripción |
|-----------|------|-------------|
| `--calorias KCAL` | float | Gasto calórico total del día (kcal) |
| `--peso KG` | float | Peso corporal en kg |
| `--altura CM` | float | Altura en cm |
| `--cintura CM` | float | Circunferencia de cintura en cm |
| `--cuello CM` | float | Circunferencia de cuello en cm |

### Argumentos opcionales

| Argumento | Tipo | Descripción |
|-----------|------|-------------|
| `--sexo` | hombre\|mujer | Sexo biológico (por defecto: `hombre`) |
| `--grasa %` | float | Porcentaje de grasa medido directamente (p.ej. báscula de bioimpedancia) |
| `--cadera CM` | float | Circunferencia de cadera en cm. **Obligatorio si `--sexo mujer`** |
| `--biceps CM` | float | Circunferencia de bíceps en cm |
| `--cuadriceps CM` | float | Circunferencia de cuádriceps en cm |
| `--gemelos CM` | float | Circunferencia de gemelos en cm |
| `--pectoral CM` | float | Circunferencia de pectoral en cm |

---

## Ejemplos

### Uso mínimo — hombre

```bash
python main.py \
  --calorias 3343 \
  --peso 72.25 \
  --altura 175 \
  --cintura 84 \
  --cuello 38
```

### Uso mínimo — mujer

```bash
python main.py \
  --calorias 2200 \
  --peso 60 \
  --altura 165 \
  --cintura 70 \
  --cuello 32 \
  --cadera 95 \
  --sexo mujer
```

### Uso completo

```bash
python main.py \
  --calorias 3343 \
  --peso 72.25 \
  --altura 175 \
  --grasa 14.5 \
  --cintura 84 \
  --cuello 38 \
  --cadera 95 \
  --biceps 35 \
  --cuadriceps 55 \
  --gemelos 37 \
  --pectoral 100 \
  --sexo hombre
```

### Salida de ejemplo

```
─── MEDIDAS CORPORALES ──────────────────────
  Sexo                      Hombre
  Peso (kg)                 72.25
  Altura (cm)               175.0
  Cintura (cm)              84.0
  Cuello (cm)               38.0
  Grasa directa (%)         14.5
  Bíceps (cm)               35.0
  Cuádriceps (cm)           55.0
  Cadera (cm)               95.0
  Gemelos (cm)              37.0
  Pectoral (cm)             100.0

─── COMPOSICIÓN CORPORAL (US Navy) ──────────
  Grasa corporal (%):       14.82 %
  Masa magra (kg):          61.55 kg
  Grasa directa (%):        14.5 %  (Δ Navy -0.32 %)

─── IMC / FFMI ──────────────────────────────
  IMC (kg/m²):              23.59  [Peso normal]
  FFMI (kg/m²):             20.1
  FFMI normalizado:         20.41  [referencia ♂ < 25 / ♀ < 22]

─── MACROS DEL DÍA ──────────────────────────
  Proteína (g):             144.5 g
  Grasas (g):               57.8 g
  Carbohidratos (g):        619.1 g
  Calorías Totales:         3343 kcal
─────────────────────────────────────────────
```

---

## Cómo funciona

### Porcentaje de grasa corporal — Fórmula US Navy

#### Hombres

```
%Grasa = 495 / (1.0324 − 0.19077·log₁₀(cintura − cuello) + 0.15456·log₁₀(altura)) − 450
```

#### Mujeres (requiere circunferencia de cadera)

```
%Grasa = 495 / (1.29579 − 0.35004·log₁₀(cintura + cadera − cuello) + 0.22100·log₁₀(altura)) − 450
```

### Índice de Masa Corporal (IMC / BMI)

```
IMC = peso (kg) / altura (m)²
```

| IMC | Categoría OMS |
|-----|---------------|
| < 18.5 | Bajo peso |
| 18.5 – 24.9 | Peso normal |
| 25.0 – 29.9 | Sobrepeso |
| 30.0 – 34.9 | Obesidad grado I |
| 35.0 – 39.9 | Obesidad grado II |
| ≥ 40.0 | Obesidad grado III |

### Índice de Masa Libre de Grasa (FFMI)

```
FFMI           = masa_magra (kg) / altura (m)²
FFMI_norm      = FFMI + 6.1 × (1.80 − altura_m)   [normalizado a 1.80 m]
```

Un FFMI normalizado > 25 (hombres) o > 22 (mujeres) suele indicar el límite natural sin fármacos.

### Distribución de macros

| Macro | Cálculo |
|-------|---------|
| Proteína | 2 g × kg de peso |
| Grasa | 0.8 g × kg de peso |
| Carbohidratos | (kcal_totales − kcal_proteína − kcal_grasa) / 4 |

---

## Estructura del proyecto

```
fitness-calculator-tool/
├── .github/
│   ├── workflows/
│   │   └── ci.yml               # GitHub Actions CI (tests automáticos)
│   ├── ISSUE_TEMPLATE/          # Plantillas de issues
│   └── pull_request_template.md
├── fitness_tools/
│   ├── __init__.py              # Exportaciones públicas de la librería
│   ├── body_composition.py      # Fórmulas US Navy (♂/♀), IMC, FFMI + dataclass MedidasCorporales
│   └── nutrition.py             # Cálculo de macros y carbohidratos rápidos
├── templates/
│   └── index.html               # Plantilla HTML de la web app
├── tests/
│   └── test_fitness_tools.py    # Suite de tests (pytest)
├── app.py                       # Web app Flask (punto de entrada para Heroku)
├── main.py                      # CLI principal
├── Procfile                     # Comando de arranque para Heroku
├── requirements.txt             # Dependencias web (Flask, gunicorn)
├── runtime.txt                  # Versión de Python para Heroku
├── pyproject.toml               # Metadatos del paquete y dependencias dev
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

## Contribuir

¿Quieres añadir una nueva fórmula, idioma o mejora? ¡Lee la [guía de contribución](CONTRIBUTING.md)!

- Abre un [issue](https://github.com/juanfranciscofernandezherreros/fitness-calculator-tool/issues) para reportar bugs o proponer funcionalidades.
- Envía un [Pull Request](https://github.com/juanfranciscofernandezherreros/fitness-calculator-tool/pulls) con tus cambios.

---

## Licencia

Este proyecto está bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

