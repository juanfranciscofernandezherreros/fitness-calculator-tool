"""
app.py — Web app de composición corporal y nutrición deportiva.

Punto de entrada para Heroku (gunicorn app:app).
"""

import math
import os
import re

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

# ── Internationalisation ──────────────────────────────────────────────────────

SUPPORTED_LANGS = ["es", "en", "it", "fr", "de", "pt", "nl", "pl", "ru", "zh", "ja"]
DEFAULT_LANG = "es"

# Translated field names used inside error messages
CAMPO_NAMES: dict[str, dict[str, str]] = {
    "es": {
        "calorias": "Calorías", "peso": "Peso", "altura": "Altura",
        "cintura": "Cintura", "cuello": "Cuello",
        "grasa": "Grasa directa", "cadera": "Cadera",
        "biceps_der": "Bíceps derecho", "biceps_izq": "Bíceps izquierdo",
        "cuadriceps_der": "Cuádriceps derecho", "cuadriceps_izq": "Cuádriceps izquierdo",
        "gemelos_der": "Gemelos derechos", "gemelos_izq": "Gemelos izquierdos",
        "pectoral": "Pectoral",
    },
    "en": {
        "calorias": "Calories", "peso": "Weight", "altura": "Height",
        "cintura": "Waist", "cuello": "Neck",
        "grasa": "Body fat %", "cadera": "Hip",
        "biceps_der": "Right bicep", "biceps_izq": "Left bicep",
        "cuadriceps_der": "Right quad", "cuadriceps_izq": "Left quad",
        "gemelos_der": "Right calf", "gemelos_izq": "Left calf",
        "pectoral": "Chest",
    },
    "it": {
        "calorias": "Calorie", "peso": "Peso", "altura": "Altezza",
        "cintura": "Vita", "cuello": "Collo",
        "grasa": "Grasso corporeo %", "cadera": "Fianchi",
        "biceps_der": "Bicipite destro", "biceps_izq": "Bicipite sinistro",
        "cuadriceps_der": "Quadricipite destro", "cuadriceps_izq": "Quadricipite sinistro",
        "gemelos_der": "Polpaccio destro", "gemelos_izq": "Polpaccio sinistro",
        "pectoral": "Petto",
    },
    "fr": {
        "calorias": "Calories", "peso": "Poids", "altura": "Taille",
        "cintura": "Tour de taille", "cuello": "Tour de cou",
        "grasa": "Graisse corporelle %", "cadera": "Tour de hanches",
        "biceps_der": "Biceps droit", "biceps_izq": "Biceps gauche",
        "cuadriceps_der": "Quadriceps droit", "cuadriceps_izq": "Quadriceps gauche",
        "gemelos_der": "Mollet droit", "gemelos_izq": "Mollet gauche",
        "pectoral": "Poitrine",
    },
    "de": {
        "calorias": "Kalorien", "peso": "Gewicht", "altura": "Größe",
        "cintura": "Taillenumfang", "cuello": "Halsumfang",
        "grasa": "Körperfett %", "cadera": "Hüftumfang",
        "biceps_der": "Rechter Bizeps", "biceps_izq": "Linker Bizeps",
        "cuadriceps_der": "Rechter Oberschenkel", "cuadriceps_izq": "Linker Oberschenkel",
        "gemelos_der": "Rechte Wade", "gemelos_izq": "Linke Wade",
        "pectoral": "Brust",
    },
    "pt": {
        "calorias": "Calorias", "peso": "Peso", "altura": "Altura",
        "cintura": "Cintura", "cuello": "Pescoço",
        "grasa": "Gordura corporal %", "cadera": "Quadril",
        "biceps_der": "Bíceps direito", "biceps_izq": "Bíceps esquerdo",
        "cuadriceps_der": "Quadríceps direito", "cuadriceps_izq": "Quadríceps esquerdo",
        "gemelos_der": "Panturrilha direita", "gemelos_izq": "Panturrilha esquerda",
        "pectoral": "Peitoral",
    },
    "nl": {
        "calorias": "Calorieën", "peso": "Gewicht", "altura": "Lengte",
        "cintura": "Tailleomvang", "cuello": "Nekomvang",
        "grasa": "Lichaamsvet %", "cadera": "Heupomvang",
        "biceps_der": "Rechter biceps", "biceps_izq": "Linker biceps",
        "cuadriceps_der": "Rechter quadriceps", "cuadriceps_izq": "Linker quadriceps",
        "gemelos_der": "Rechter kuit", "gemelos_izq": "Linker kuit",
        "pectoral": "Borst",
    },
    "pl": {
        "calorias": "Kalorie", "peso": "Waga", "altura": "Wzrost",
        "cintura": "Obwód talii", "cuello": "Obwód szyi",
        "grasa": "Tłuszcz %", "cadera": "Obwód bioder",
        "biceps_der": "Prawy biceps", "biceps_izq": "Lewy biceps",
        "cuadriceps_der": "Prawy czworogłowy", "cuadriceps_izq": "Lewy czworogłowy",
        "gemelos_der": "Prawa łydka", "gemelos_izq": "Lewa łydka",
        "pectoral": "Klatka piersiowa",
    },
    "ru": {
        "calorias": "Калории", "peso": "Вес", "altura": "Рост",
        "cintura": "Талия", "cuello": "Шея",
        "grasa": "Жир %", "cadera": "Бёдра",
        "biceps_der": "Правый бицепс", "biceps_izq": "Левый бицепс",
        "cuadriceps_der": "Правое бедро", "cuadriceps_izq": "Левое бедро",
        "gemelos_der": "Правая икра", "gemelos_izq": "Левая икра",
        "pectoral": "Грудь",
    },
    "zh": {
        "calorias": "热量", "peso": "体重", "altura": "身高",
        "cintura": "腰围", "cuello": "颈围",
        "grasa": "体脂率", "cadera": "臀围",
        "biceps_der": "右侧二头肌", "biceps_izq": "左侧二头肌",
        "cuadriceps_der": "右侧大腿", "cuadriceps_izq": "左侧大腿",
        "gemelos_der": "右侧小腿", "gemelos_izq": "左侧小腿",
        "pectoral": "胸围",
    },
    "ja": {
        "calorias": "カロリー", "peso": "体重", "altura": "身長",
        "cintura": "ウエスト", "cuello": "首周り",
        "grasa": "体脂肪率", "cadera": "ヒップ",
        "biceps_der": "右上腕二頭筋", "biceps_izq": "左上腕二頭筋",
        "cuadriceps_der": "右大腿四頭筋", "cuadriceps_izq": "左大腿四頭筋",
        "gemelos_der": "右ふくらはぎ", "gemelos_izq": "左ふくらはぎ",
        "pectoral": "胸囲",
    },
}

# Translated error message templates
ERROR_MESSAGES: dict[str, dict[str, str]] = {
    "es": {
        "field_required": "El campo «{campo}» es obligatorio y no puede estar vacío.",
        "invalid_number": "«{value}» no es un número válido para «{campo}». Introduce un valor como 72.5.",
        "positive_values": "Todas las medidas deben ser valores positivos (mayores que cero).",
        "waist_greater_neck": "La cintura debe ser mayor que el cuello para que la fórmula sea válida. Comprueba tus medidas.",
        "hip_required": "Para el cálculo femenino (US Navy) la cadera es obligatoria. Introduce tu medida de cadera en los datos opcionales.",
        "hip_sum_invalid": "Para mujeres, la suma cintura + cadera debe ser mayor que el cuello.",
        "insufficient_calories": "{kcal} kcal son insuficientes. Los macros base (proteína + grasa) ya requieren {needed} kcal para tu peso. Aumenta las calorías o reduce el peso.",
        "unknown_error": "Error inesperado: {msg}",
    },
    "en": {
        "field_required": "The field «{campo}» is required and cannot be empty.",
        "invalid_number": "«{value}» is not a valid number for «{campo}». Enter a value like 72.5.",
        "positive_values": "All measurements must be positive values (greater than zero).",
        "waist_greater_neck": "Waist must be greater than neck for the formula to be valid. Check your measurements.",
        "hip_required": "Hip measurement is required for women (US Navy formula). Enter your hip circumference in the optional fields.",
        "hip_sum_invalid": "For women, waist + hip must be greater than neck.",
        "insufficient_calories": "{kcal} kcal is not enough. The base macros (protein + fat) already require {needed} kcal for your weight. Increase calories or reduce weight.",
        "unknown_error": "Unexpected error: {msg}",
    },
    "it": {
        "field_required": "Il campo «{campo}» è obbligatorio e non può essere vuoto.",
        "invalid_number": "«{value}» non è un numero valido per «{campo}». Inserisci un valore come 72.5.",
        "positive_values": "Tutte le misure devono essere valori positivi (maggiori di zero).",
        "waist_greater_neck": "La vita deve essere maggiore del collo per la validità della formula. Controlla le misure.",
        "hip_required": "La misurazione dei fianchi è obbligatoria per le donne (formula US Navy). Inseriscila nei dati facoltativi.",
        "hip_sum_invalid": "Per le donne, vita + fianchi deve essere maggiore del collo.",
        "insufficient_calories": "{kcal} kcal non è sufficiente. Le macro base richiedono già {needed} kcal per il tuo peso. Aumenta le calorie o riduci il peso.",
        "unknown_error": "Errore inaspettato: {msg}",
    },
    "fr": {
        "field_required": "Le champ «{campo}» est obligatoire et ne peut pas être vide.",
        "invalid_number": "«{value}» n'est pas un nombre valide pour «{campo}». Entrez une valeur comme 72.5.",
        "positive_values": "Toutes les mesures doivent être des valeurs positives (supérieures à zéro).",
        "waist_greater_neck": "Le tour de taille doit être supérieur au tour de cou. Vérifiez vos mesures.",
        "hip_required": "La mesure des hanches est obligatoire pour les femmes (formule US Navy). Saisissez-la dans les données facultatives.",
        "hip_sum_invalid": "Pour les femmes, taille + hanches doit être supérieur au cou.",
        "insufficient_calories": "{kcal} kcal est insuffisant. Les macros de base nécessitent déjà {needed} kcal pour votre poids. Augmentez les calories ou réduisez le poids.",
        "unknown_error": "Erreur inattendue : {msg}",
    },
    "de": {
        "field_required": "Das Feld «{campo}» ist erforderlich und darf nicht leer sein.",
        "invalid_number": "«{value}» ist keine gültige Zahl für «{campo}». Gib einen Wert wie 72.5 ein.",
        "positive_values": "Alle Maßangaben müssen positive Werte (größer als null) sein.",
        "waist_greater_neck": "Der Taillenumfang muss größer als der Halsumfang sein. Überprüfe deine Maße.",
        "hip_required": "Die Hüftmessung ist für Frauen erforderlich (US-Navy-Formel). Trage sie in die optionalen Felder ein.",
        "hip_sum_invalid": "Für Frauen muss Taille + Hüfte größer als der Hals sein.",
        "insufficient_calories": "{kcal} kcal reicht nicht aus. Die Basis-Makros erfordern bereits {needed} kcal für dein Gewicht. Erhöhe die Kalorien oder reduziere das Gewicht.",
        "unknown_error": "Unerwarteter Fehler: {msg}",
    },
    "pt": {
        "field_required": "O campo «{campo}» é obrigatório e não pode estar vazio.",
        "invalid_number": "«{value}» não é um número válido para «{campo}». Insira um valor como 72.5.",
        "positive_values": "Todas as medidas devem ser valores positivos (maiores que zero).",
        "waist_greater_neck": "A cintura deve ser maior que o pescoço para a fórmula funcionar. Verifique as medidas.",
        "hip_required": "A medida do quadril é obrigatória para mulheres (fórmula US Navy). Insira-a nos dados opcionais.",
        "hip_sum_invalid": "Para mulheres, cintura + quadril deve ser maior que o pescoço.",
        "insufficient_calories": "{kcal} kcal não é suficiente. As macros base já requerem {needed} kcal para o seu peso. Aumente as calorias ou reduza o peso.",
        "unknown_error": "Erro inesperado: {msg}",
    },
    "nl": {
        "field_required": "Het veld «{campo}» is verplicht en mag niet leeg zijn.",
        "invalid_number": "«{value}» is geen geldig getal voor «{campo}». Voer een waarde in zoals 72.5.",
        "positive_values": "Alle metingen moeten positieve waarden (groter dan nul) zijn.",
        "waist_greater_neck": "De tailleomvang moet groter zijn dan de nekumvang. Controleer je metingen.",
        "hip_required": "Heupomvang is vereist voor vrouwen (US Navy formule). Vul dit in bij de optionele velden.",
        "hip_sum_invalid": "Voor vrouwen moet taille + heup groter zijn dan nek.",
        "insufficient_calories": "{kcal} kcal is onvoldoende. De basismacro's vereisen al {needed} kcal voor jouw gewicht. Verhoog de calorieën of verlaag het gewicht.",
        "unknown_error": "Onverwachte fout: {msg}",
    },
    "pl": {
        "field_required": "Pole «{campo}» jest wymagane i nie może być puste.",
        "invalid_number": "«{value}» nie jest prawidłową liczbą dla «{campo}». Wprowadź wartość jak 72.5.",
        "positive_values": "Wszystkie pomiary muszą być wartościami dodatnimi (większymi od zera).",
        "waist_greater_neck": "Obwód talii musi być większy niż obwód szyi. Sprawdź swoje pomiary.",
        "hip_required": "Pomiar bioder jest wymagany dla kobiet (wzór US Navy). Wprowadź go w polach opcjonalnych.",
        "hip_sum_invalid": "Dla kobiet talia + biodra musi być większa niż szyja.",
        "insufficient_calories": "{kcal} kcal to za mało. Podstawowe makro wymagają już {needed} kcal dla Twojej wagi. Zwiększ kalorie lub zmniejsz wagę.",
        "unknown_error": "Nieoczekiwany błąd: {msg}",
    },
    "ru": {
        "field_required": "Поле «{campo}» обязательно и не может быть пустым.",
        "invalid_number": "«{value}» не является допустимым числом для «{campo}». Введите значение, например 72.5.",
        "positive_values": "Все измерения должны быть положительными значениями (больше нуля).",
        "waist_greater_neck": "Обхват талии должен быть больше обхвата шеи. Проверьте свои измерения.",
        "hip_required": "Обхват бёдер обязателен для женщин (формула US Navy). Введите его в дополнительных полях.",
        "hip_sum_invalid": "Для женщин талия + бёдра должны быть больше шеи.",
        "insufficient_calories": "{kcal} ккал недостаточно. Базовые макросы уже требуют {needed} ккал для вашего веса. Увеличьте калории или уменьшите вес.",
        "unknown_error": "Неожиданная ошибка: {msg}",
    },
    "zh": {
        "field_required": "字段《{campo}》是必填项，不能为空。",
        "invalid_number": "《{value}》不是《{campo}》的有效数字，请输入如 72.5 的数值。",
        "positive_values": "所有测量值必须为正数（大于零）。",
        "waist_greater_neck": "腰围必须大于颈围，才能使公式有效。请检查您的测量值。",
        "hip_required": "女性需要填写臀围（美国海军公式）。请在可选数据中填写臀围。",
        "hip_sum_invalid": "对于女性，腰围 + 臀围必须大于颈围。",
        "insufficient_calories": "{kcal} 千卡不足，基础宏量营养素已需要 {needed} 千卡。请增加热量或减少体重。",
        "unknown_error": "意外错误：{msg}",
    },
    "ja": {
        "field_required": "「{campo}」は必須項目です。空にすることはできません。",
        "invalid_number": "「{value}」は「{campo}」の有効な数値ではありません。72.5 のような数値を入力してください。",
        "positive_values": "すべての測定値はゼロより大きい正の値である必要があります。",
        "waist_greater_neck": "ウエストは首周りより大きくなければなりません。測定値を確認してください。",
        "hip_required": "女性の場合、ヒップの測定値が必要です（米海軍式）。任意フィールドに入力してください。",
        "hip_sum_invalid": "女性の場合、ウエスト + ヒップは首周りより大きくなければなりません。",
        "insufficient_calories": "{kcal} kcal は不足しています。基本マクロはすでに {needed} kcal 必要です。カロリーを増やすか体重を減らしてください。",
        "unknown_error": "予期しないエラー: {msg}",
    },
}


class AppError(ValueError):
    """Structured application error carrying a translation key and parameters."""

    def __init__(self, key: str, **params):
        self.error_key = key
        self.params = params
        super().__init__(key)


def _translate_error(exc: Exception, lang: str) -> str:
    """Return a translated, human-friendly error message."""
    msgs = ERROR_MESSAGES.get(lang, ERROR_MESSAGES[DEFAULT_LANG])

    if isinstance(exc, AppError):
        template = msgs.get(exc.error_key, msgs.get("unknown_error", str(exc)))
        try:
            return template.format(**exc.params)
        except (KeyError, ValueError):
            return template

    # Map known Spanish messages from fitness_tools to i18n keys
    msg = str(exc)
    if "valores positivos" in msg or re.search(r"debe ser un valor positivo", msg):
        return msgs["positive_values"]
    if "cintura debe ser mayor que el cuello" in msg:
        return msgs["waist_greater_neck"]
    if "cadera" in msg and "obligatorio" in msg:
        return msgs["hip_required"]
    if "cintura+cadera" in msg or ("cintura" in msg and "cadera" in msg and "cuello" in msg):
        return msgs["hip_sum_invalid"]
    if "insuficiente" in msg and "kcal" in msg:
        m = re.search(r"\((\d+(?:\.\d+)?)\s*kcal\).*\((\d+(?:\.\d+)?)\s*kcal\)", msg)
        tmpl = msgs.get("insufficient_calories", msgs["unknown_error"])
        if m:
            return tmpl.format(kcal=m.group(1), needed=m.group(2))
        return tmpl.format(kcal="?", needed="?")

    return msgs.get("unknown_error", "Error: {msg}").format(msg=msg)


@app.route("/", methods=["GET", "POST"])
def index():
    resultados = None
    error = None

    # Detect language (form POST → localStorage → default)
    lang = request.form.get("lang", DEFAULT_LANG)
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG

    if request.method == "POST":
        try:
            campos = CAMPO_NAMES.get(lang, CAMPO_NAMES[DEFAULT_LANG])
            calorias = _parse_float(request.form.get("calorias", ""), campos["calorias"])
            peso = _parse_float(request.form.get("peso", ""), campos["peso"])
            altura = _parse_float(request.form.get("altura", ""), campos["altura"])
            cintura = _parse_float(request.form.get("cintura", ""), campos["cintura"])
            cuello = _parse_float(request.form.get("cuello", ""), campos["cuello"])
            sexo = request.form.get("sexo", "hombre")
            if sexo not in ("hombre", "mujer"):
                sexo = "hombre"

            grasa = _optional_float(request.form.get("grasa"), campos["grasa"])
            biceps_der = _optional_float(request.form.get("biceps_der"), campos["biceps_der"])
            biceps_izq = _optional_float(request.form.get("biceps_izq"), campos["biceps_izq"])
            cuadriceps_der = _optional_float(request.form.get("cuadriceps_der"), campos["cuadriceps_der"])
            cuadriceps_izq = _optional_float(request.form.get("cuadriceps_izq"), campos["cuadriceps_izq"])
            cadera = _optional_float(request.form.get("cadera"), campos["cadera"])
            gemelos_der = _optional_float(request.form.get("gemelos_der"), campos["gemelos_der"])
            gemelos_izq = _optional_float(request.form.get("gemelos_izq"), campos["gemelos_izq"])
            pectoral = _optional_float(request.form.get("pectoral"), campos["pectoral"])

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
            error = _translate_error(exc, lang)

    return render_template("index.html", resultados=resultados, error=error, lang=lang)


def _parse_float(value: str | None, campo: str) -> float:
    """Convierte un valor de formulario a float; lanza AppError con clave i18n."""
    if value is None or value.strip() == "":
        raise AppError("field_required", campo=campo)
    try:
        return float(value)
    except ValueError:
        raise AppError("invalid_number", value=value, campo=campo)


def _optional_float(value: str | None, campo: str = "") -> float | None:
    """Devuelve float si el valor tiene contenido, None en caso contrario."""
    if value is None or value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        raise AppError("invalid_number", value=value, campo=campo or "?")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
