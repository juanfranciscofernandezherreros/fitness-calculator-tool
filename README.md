# fitness_tools 💪

Herramienta de línea de comandos para el seguimiento de **composición corporal** y **distribución de macronutrientes** diarios.

---

## Instalación

```bash
pip install -e .
```

> Requiere Python ≥ 3.9.

---

## Uso

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
| `--grasa %` | float | Porcentaje de grasa medido directamente (p.ej. báscula de bioimpedancia) |
| `--biceps CM` | float | Circunferencia de bíceps en cm |
| `--cuadriceps CM` | float | Circunferencia de cuádriceps en cm |
| `--cadera CM` | float | Circunferencia de cadera en cm |
| `--gemelos CM` | float | Circunferencia de gemelos en cm |
| `--pectoral CM` | float | Circunferencia de pectoral en cm |

---

## Ejemplos

### Uso mínimo (solo obligatorios)

```bash
python main.py \
  --calorias 3343 \
  --peso 72.25 \
  --altura 175 \
  --cintura 84 \
  --cuello 38
```

### Uso completo (todos los argumentos)

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
  --pectoral 100
```

### Salida de ejemplo

```
─── MEDIDAS CORPORALES ──────────────────────
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

─── MACROS DEL DÍA ──────────────────────────
  Proteína (g):             144.5 g
  Grasas (g):               57.8 g
  Carbohidratos (g):        619.1 g
  Calorías Totales:         3343 kcal
─────────────────────────────────────────────
```

---

## Cómo funciona

### Porcentaje de grasa corporal — Fórmula US Navy (hombres)

```
%Grasa = 495 / (1.0324 − 0.19077·log₁₀(cintura − cuello) + 0.15456·log₁₀(altura)) − 450
```

### Distribución de macros

| Macro | Cálculo |
|-------|---------|
| Proteína | 2 g × kg de peso |
| Grasa | 0.8 g × kg de peso |
| Carbohidratos | (kcal_totales − kcal_proteína − kcal_grasa) / 4 |

---

## Estructura del proyecto

```
repo/
├── fitness_tools/
│   ├── __init__.py          # Exportaciones públicas de la librería
│   ├── body_composition.py  # Fórmula US Navy + dataclass MedidasCorporales
│   └── nutrition.py         # Cálculo de macros y carbohidratos rápidos
├── main.py                  # CLI principal (punto de entrada)
├── pyproject.toml
└── README.md
```
