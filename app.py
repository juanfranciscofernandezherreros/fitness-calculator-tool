"""
app.py — Web app de composición corporal y nutrición deportiva.

Punto de entrada para Heroku (gunicorn app:app).
"""

import io
import math
import os
import re

from flask import Flask, jsonify, render_template, request, send_file
from fpdf import FPDF

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

SUPPORTED_LANGS = ["es", "en", "it", "fr", "de", "pt", "nl", "pl", "ru", "zh", "ja", "ko"]
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
    "ko": {
        "calorias": "칼로리", "peso": "체중", "altura": "키",
        "cintura": "허리", "cuello": "목",
        "grasa": "체지방률", "cadera": "엉덩이",
        "biceps_der": "오른쪽 이두근", "biceps_izq": "왼쪽 이두근",
        "cuadriceps_der": "오른쪽 대퇴사두근", "cuadriceps_izq": "왼쪽 대퇴사두근",
        "gemelos_der": "오른쪽 종아리", "gemelos_izq": "왼쪽 종아리",
        "pectoral": "가슴",
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
    "ko": {
        "field_required": "«{campo}» 필드는 필수이며 비워 둘 수 없습니다.",
        "invalid_number": "«{value}»는 «{campo}»에 유효한 숫자가 아닙니다. 72.5와 같은 값을 입력하세요.",
        "positive_values": "모든 측정값은 양수(0보다 큰 값)여야 합니다.",
        "waist_greater_neck": "공식이 유효하려면 허리 둘레가 목 둘레보다 커야 합니다. 측정값을 확인하세요.",
        "hip_required": "여성의 경우 엉덩이 둘레가 필수입니다(미 해군 공식). 선택 필드에 입력하세요.",
        "hip_sum_invalid": "여성의 경우 허리 + 엉덩이가 목보다 커야 합니다.",
        "insufficient_calories": "{kcal} kcal은 부족합니다. 기본 매크로(단백질 + 지방)에만 이미 {needed} kcal가 필요합니다. 칼로리를 늘리거나 체중을 줄이세요.",
        "unknown_error": "예기치 않은 오류: {msg}",
    },
}


class AppError(ValueError):
    """Structured application error carrying a translation key and parameters."""

    def __init__(self, key: str, fields: list | None = None, **params):
        self.error_key = key
        self.fields: list[str] = fields or []
        self.params = params
        super().__init__(key)


class MultipleAppError(ValueError):
    """Aggregates multiple AppError instances so all can be reported at once."""

    def __init__(self, errors: list[AppError]):
        self.errors: list[AppError] = errors
        super().__init__("; ".join(e.error_key for e in errors))


def _get_error_fields(exc: Exception) -> list[str]:
    """Return the HTML input IDs associated with an error."""
    if isinstance(exc, MultipleAppError):
        seen: set[str] = set()
        result: list[str] = []
        for e in exc.errors:
            for f in e.fields:
                if f not in seen:
                    seen.add(f)
                    result.append(f)
        return result
    if isinstance(exc, AppError):
        return exc.fields
    msg = str(exc)
    if "valores positivos" in msg or re.search(r"debe ser un valor positivo", msg):
        return ["calorias", "peso", "altura", "cintura", "cuello"]
    if "cintura debe ser mayor que el cuello" in msg:
        return ["cintura", "cuello"]
    if "cadera" in msg and "obligatorio" in msg:
        return ["cadera"]
    if "cintura+cadera" in msg or ("cintura" in msg and "cadera" in msg and "cuello" in msg):
        return ["cintura", "cadera"]
    if "insuficiente" in msg and "kcal" in msg:
        return ["calorias"]
    return []


def _translate_error(exc: Exception, lang: str) -> str:
    """Return a translated, human-friendly error message."""
    msgs = ERROR_MESSAGES.get(lang, ERROR_MESSAGES[DEFAULT_LANG])

    if isinstance(exc, MultipleAppError):
        parts = []
        for e in exc.errors:
            template = msgs.get(e.error_key, msgs.get("unknown_error", str(e)))
            try:
                parts.append(template.format(**e.params))
            except (KeyError, ValueError):
                parts.append(template)
        return "\n".join(parts)

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

    return msgs.get("unknown_error", "Error inesperado.").format(msg="")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/robots.txt", methods=["GET"])
def robots():
    """robots.txt — allow all crawlers and point to sitemap."""
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        "\n"
        "Sitemap: {base}/sitemap.xml\n"
    ).format(base=_base_url())
    return app.response_class(content, mimetype="text/plain")


@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    """XML sitemap listing all language variants of the home page."""
    base = _base_url()
    langs = SUPPORTED_LANGS  # ["es", "en", "it", ...]
    urls = []
    # Root / (es is the default, no lang param)
    urls.append(
        "  <url>\n"
        "    <loc>{base}/</loc>\n"
        "    <changefreq>monthly</changefreq>\n"
        "    <priority>1.0</priority>\n"
        "  </url>".format(base=base)
    )
    for lang in langs:
        if lang == "es":
            continue  # already added as root
        urls.append(
            "  <url>\n"
            "    <loc>{base}/?lang={lang}</loc>\n"
            "    <changefreq>monthly</changefreq>\n"
            "    <priority>0.8</priority>\n"
            "  </url>".format(base=base, lang=lang)
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n"
        '</urlset>'
    )
    return app.response_class(xml, mimetype="application/xml")


def _base_url() -> str:
    """Return the canonical base URL, using the APP_BASE_URL env var if set."""
    return os.environ.get("APP_BASE_URL", "").rstrip("/") or request.host_url.rstrip("/")


def _compute_results(form, lang):
    """Parse form data, run calculations and return a results dict.

    Raises MultipleAppError (or any ValueError from fitness_tools) on invalid input.
    """
    campos = CAMPO_NAMES.get(lang, CAMPO_NAMES[DEFAULT_LANG])

    # Collect all required-field errors before raising so every invalid input
    # is highlighted at once instead of stopping at the first failure.
    _required_errors: list[AppError] = []

    def _safe_parse(value, campo, field_id):
        try:
            return _parse_float(value, campo, field_id)
        except AppError as e:
            _required_errors.append(e)
            return None

    calorias = _safe_parse(form.get("calorias", ""), campos["calorias"], "calorias")
    peso     = _safe_parse(form.get("peso", ""),     campos["peso"],     "peso")
    altura   = _safe_parse(form.get("altura", ""),   campos["altura"],   "altura")
    cintura  = _safe_parse(form.get("cintura", ""),  campos["cintura"],  "cintura")
    cuello   = _safe_parse(form.get("cuello", ""),   campos["cuello"],   "cuello")

    if _required_errors:
        raise MultipleAppError(_required_errors)

    sexo = form.get("sexo", "hombre")
    if sexo not in ("hombre", "mujer"):
        sexo = "hombre"

    grasa = _optional_float(form.get("grasa"), campos["grasa"], "grasa")
    biceps_der = _optional_float(form.get("biceps_der"), campos["biceps_der"], "biceps_der")
    biceps_izq = _optional_float(form.get("biceps_izq"), campos["biceps_izq"], "biceps_izq")
    cuadriceps_der = _optional_float(form.get("cuadriceps_der"), campos["cuadriceps_der"], "cuadriceps_der")
    cuadriceps_izq = _optional_float(form.get("cuadriceps_izq"), campos["cuadriceps_izq"], "cuadriceps_izq")
    cadera = _optional_float(form.get("cadera"), campos["cadera"], "cadera")
    gemelos_der = _optional_float(form.get("gemelos_der"), campos["gemelos_der"], "gemelos_der")
    gemelos_izq = _optional_float(form.get("gemelos_izq"), campos["gemelos_izq"], "gemelos_izq")
    pectoral = _optional_float(form.get("pectoral"), campos["pectoral"], "pectoral")

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
            "495 / (1.0324 \u2212 0.19077 \u00d7 log\u2081\u2080(cintura \u2212 cuello)"
            " + 0.15456 \u00d7 log\u2081\u2080(altura)) \u2212 450"
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
            "495 / (1.29579 \u2212 0.35004 \u00d7 log\u2081\u2080(cintura + cadera \u2212 cuello)"
            " + 0.22100 \u00d7 log\u2081\u2080(altura)) \u2212 450"
        )
        navy_extra_label = "cintura + cadera \u2212 cuello"
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

    return {
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


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    """JSON endpoint used by the SPA front-end."""
    lang = request.form.get("lang", DEFAULT_LANG)
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    try:
        resultados = _compute_results(request.form, lang)
        return jsonify({"resultados": resultados})
    except (AppError, ValueError) as exc:
        return jsonify({"error": _translate_error(exc, lang), "fields": _get_error_fields(exc)}), 400
    except Exception:
        msgs = ERROR_MESSAGES.get(lang, ERROR_MESSAGES[DEFAULT_LANG])
        return jsonify({"error": msgs.get("unknown_error", "Error inesperado.").format(msg=""), "fields": []}), 500


def _parse_float(value: str | None, campo: str, field_id: str = "") -> float:
    """Convierte un valor de formulario a float; lanza AppError con clave i18n."""
    if value is None or value.strip() == "":
        raise AppError("field_required", fields=[field_id] if field_id else [], campo=campo)
    try:
        return float(value)
    except ValueError:
        raise AppError("invalid_number", fields=[field_id] if field_id else [], value=value, campo=campo)


def _optional_float(value: str | None, campo: str = "", field_id: str = "") -> float | None:
    """Devuelve float si el valor tiene contenido, None en caso contrario."""
    if value is None or value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        raise AppError("invalid_number", fields=[field_id] if field_id else [], value=value, campo=campo or "?")



# ── PDF label translations ─────────────────────────────────────────────────────

_PDF_LABELS: dict[str, dict[str, str]] = {
    "es": {
        "title": "Informe de Composición Corporal",
        "generated": "Generado por Fitness Tools",
        "measurements": "Medidas corporales",
        "body_comp": "Composición corporal (US Navy)",
        "body_fat": "Grasa corporal",
        "lean_mass": "Masa magra",
        "imc_ffmi": "IMC y FFMI",
        "imc": "IMC",
        "ffmi": "FFMI",
        "ffmi_norm": "FFMI normalizado (1.80 m)",
        "bmi_cat": "Categoría OMS",
        "macros": "Macros diarios",
        "report": "Informe detallado — Fórmulas paso a paso",
        "formula": "Fórmula",
        "result": "Resultado",
    },
    "en": {
        "title": "Body Composition Report",
        "generated": "Generated by Fitness Tools",
        "measurements": "Body measurements",
        "body_comp": "Body composition (US Navy)",
        "body_fat": "Body fat",
        "lean_mass": "Lean mass",
        "imc_ffmi": "BMI and FFMI",
        "imc": "BMI",
        "ffmi": "FFMI",
        "ffmi_norm": "Normalized FFMI (1.80 m)",
        "bmi_cat": "WHO category",
        "macros": "Daily macros",
        "report": "Detailed report — Step-by-step formulas",
        "formula": "Formula",
        "result": "Result",
    },
    "it": {
        "title": "Rapporto di Composizione Corporea",
        "generated": "Generato da Fitness Tools",
        "measurements": "Misure corporee",
        "body_comp": "Composizione corporea (US Navy)",
        "body_fat": "Grasso corporeo",
        "lean_mass": "Massa magra",
        "imc_ffmi": "IMC e FFMI",
        "imc": "IMC",
        "ffmi": "FFMI",
        "ffmi_norm": "FFMI normalizzato (1.80 m)",
        "bmi_cat": "Categoria OMS",
        "macros": "Macro giornalieri",
        "report": "Rapporto dettagliato — Formule passo passo",
        "formula": "Formula",
        "result": "Risultato",
    },
    "fr": {
        "title": "Rapport de Composition Corporelle",
        "generated": "G\u00e9n\u00e9r\u00e9 par Fitness Tools",
        "measurements": "Mesures corporelles",
        "body_comp": "Composition corporelle (US Navy)",
        "body_fat": "Graisse corporelle",
        "lean_mass": "Masse maigre",
        "imc_ffmi": "IMC et FFMI",
        "imc": "IMC",
        "ffmi": "FFMI",
        "ffmi_norm": "FFMI normalis\u00e9 (1.80 m)",
        "bmi_cat": "Cat\u00e9gorie OMS",
        "macros": "Macros journaliers",
        "report": "Rapport d\u00e9taill\u00e9 \u2014 Formules \u00e9tape par \u00e9tape",
        "formula": "Formule",
        "result": "R\u00e9sultat",
    },
    "de": {
        "title": "K\u00f6rperzusammensetzungsbericht",
        "generated": "Erstellt von Fitness Tools",
        "measurements": "K\u00f6rpermasse",
        "body_comp": "K\u00f6rperzusammensetzung (US Navy)",
        "body_fat": "K\u00f6rperfett",
        "lean_mass": "Magermasse",
        "imc_ffmi": "BMI und FFMI",
        "imc": "BMI",
        "ffmi": "FFMI",
        "ffmi_norm": "Normalisierter FFMI (1.80 m)",
        "bmi_cat": "WHO-Kategorie",
        "macros": "T\u00e4gliche Makros",
        "report": "Detaillierter Bericht \u2014 Formeln Schritt f\u00fcr Schritt",
        "formula": "Formel",
        "result": "Ergebnis",
    },
    "pt": {
        "title": "Relat\u00f3rio de Composi\u00e7\u00e3o Corporal",
        "generated": "Gerado por Fitness Tools",
        "measurements": "Medidas corporais",
        "body_comp": "Composi\u00e7\u00e3o corporal (US Navy)",
        "body_fat": "Gordura corporal",
        "lean_mass": "Massa magra",
        "imc_ffmi": "IMC e FFMI",
        "imc": "IMC",
        "ffmi": "FFMI",
        "ffmi_norm": "FFMI normalizado (1.80 m)",
        "bmi_cat": "Categoria OMS",
        "macros": "Macros di\u00e1rios",
        "report": "Relat\u00f3rio detalhado \u2014 F\u00f3rmulas passo a passo",
        "formula": "F\u00f3rmula",
        "result": "Resultado",
    },
    "nl": {
        "title": "Lichaamssamenstelling Rapport",
        "generated": "Gegenereerd door Fitness Tools",
        "measurements": "Lichaamsmetingen",
        "body_comp": "Lichaamssamenstelling (US Navy)",
        "body_fat": "Lichaamsvet",
        "lean_mass": "Magere massa",
        "imc_ffmi": "BMI en FFMI",
        "imc": "BMI",
        "ffmi": "FFMI",
        "ffmi_norm": "Genormaliseerde FFMI (1.80 m)",
        "bmi_cat": "WHO-categorie",
        "macros": "Dagelijkse macros",
        "report": "Gedetailleerd rapport — Formules stap voor stap",
        "formula": "Formule",
        "result": "Resultaat",
    },
    "pl": {
        "title": "Raport Skladu Ciala",
        "generated": "Wygenerowane przez Fitness Tools",
        "measurements": "Pomiary ciala",
        "body_comp": "Sklad ciala (US Navy)",
        "body_fat": "Tluszcz ciala",
        "lean_mass": "Masa miesniowa",
        "imc_ffmi": "BMI i FFMI",
        "imc": "BMI",
        "ffmi": "FFMI",
        "ffmi_norm": "Znormalizowany FFMI (1.80 m)",
        "bmi_cat": "Kategoria WHO",
        "macros": "Dzienne makro",
        "report": "Szczegolowy raport - Wzory krok po kroku",
        "formula": "Wz\u00f3r",
        "result": "Wynik",
    },
    "ru": {
        "title": "Otchet o sostave tela",
        "generated": "Sgenerovano servisom Fitness Tools",
        "measurements": "Telessnye merki",
        "body_comp": "Sostav tela (US Navy)",
        "body_fat": "Zhir",
        "lean_mass": "Beskhovaja massa",
        "imc_ffmi": "IMT i FFMI",
        "imc": "IMT",
        "ffmi": "FFMI",
        "ffmi_norm": "Normalizovannyj FFMI (1.80 m)",
        "bmi_cat": "Kategorija VOZ",
        "macros": "Ezhednevnye makros",
        "report": "Podrobnyj otchet — Formuly shag za shagom",
        "formula": "Formula",
        "result": "Rezul'tat",
    },
    "zh": {
        "title": "Body Composition Report",
        "generated": "Generated by Fitness Tools",
        "measurements": "Body Measurements",
        "body_comp": "Body Composition (US Navy)",
        "body_fat": "Body Fat",
        "lean_mass": "Lean Mass",
        "imc_ffmi": "BMI & FFMI",
        "imc": "BMI",
        "ffmi": "FFMI",
        "ffmi_norm": "Normalized FFMI (1.80 m)",
        "bmi_cat": "WHO Category",
        "macros": "Daily Macros",
        "report": "Detailed Report - Step-by-step Formulas",
        "formula": "Formula",
        "result": "Result",
    },
    "ja": {
        "title": "Body Composition Report",
        "generated": "Generated by Fitness Tools",
        "measurements": "Body Measurements",
        "body_comp": "Body Composition (US Navy)",
        "body_fat": "Body Fat",
        "lean_mass": "Lean Mass",
        "imc_ffmi": "BMI & FFMI",
        "imc": "BMI",
        "ffmi": "FFMI",
        "ffmi_norm": "Normalized FFMI (1.80 m)",
        "bmi_cat": "WHO Category",
        "macros": "Daily Macros",
        "report": "Detailed Report - Step-by-step Formulas",
        "formula": "Formula",
        "result": "Result",
    },
    "ko": {
        "title": "Body Composition Report",
        "generated": "Generated by Fitness Tools",
        "measurements": "Body Measurements",
        "body_comp": "Body Composition (US Navy)",
        "body_fat": "Body Fat",
        "lean_mass": "Lean Mass",
        "imc_ffmi": "BMI & FFMI",
        "imc": "BMI",
        "ffmi": "FFMI",
        "ffmi_norm": "Normalized FFMI (1.80 m)",
        "bmi_cat": "WHO Category",
        "macros": "Daily Macros",
        "report": "Detailed Report - Step-by-step Formulas",
        "formula": "Formula",
        "result": "Result",
    },
}


def _build_pdf(resultados: dict, lang: str) -> bytes:
    """Generate a PDF report from calculation results and return bytes."""
    lbl = _PDF_LABELS.get(lang, _PDF_LABELS["es"])
    r = resultados
    p = r["pasos"]

    # fpdf2 built-in Helvetica only supports latin-1; replace common Unicode symbols.
    _UNICODE_MAP = str.maketrans({
        "\u2014": "-", "\u2212": "-", "\u00d7": "x", "\u00f7": "/",
        "\u2081": "1", "\u2080": "0", "\u00b2": "2", "\u2192": "->",
        "\u00b7": ".", "\u2260": "!=", "\u2265": ">=", "\u2264": "<=",
    })

    def s(text) -> str:
        """Convert value to safe Latin-1 string for fpdf."""
        result = str(text).translate(_UNICODE_MAP)
        return result.encode("latin-1", errors="replace").decode("latin-1")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # ── Title ────────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(27, 38, 59)
    pdf.cell(0, 12, s(lbl["title"]), new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, s(lbl["generated"]) + " - fitness-calculator-tool",
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)

    def section_title(text: str) -> None:
        pdf.set_fill_color(65, 90, 119)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, s(text), fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    def row(label: str, value: str, shade: bool = False) -> None:
        if shade:
            pdf.set_fill_color(240, 244, 248)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(50, 50, 50)
        pdf.set_font("Helvetica", "", 10)
        col_w = 85
        pdf.cell(col_w, 7, s(label), fill=shade, border=0)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, s(value), fill=shade, border=0, new_x="LMARGIN", new_y="NEXT")

    def formula_row(label: str, expr: str) -> None:
        pdf.set_text_color(60, 60, 60)
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(170, 6, s(f"  {label}: {expr}"))

    def result_row(label: str, value: str) -> None:
        pdf.set_fill_color(237, 233, 254)
        pdf.set_text_color(27, 38, 59)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, s(f"  >> {label}: {value}"), fill=True,
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    # ── 1. Measurements ──────────────────────────────────────────────────────
    section_title(lbl["measurements"])
    for i, (k, v) in enumerate(r["medidas"].items()):
        row(k, str(v), shade=(i % 2 == 0))
    pdf.ln(4)

    # ── 2. Body composition ──────────────────────────────────────────────────
    section_title(lbl["body_comp"])
    fat_val = f"{r['grasa_navy']} %"
    if r.get("grasa_directa") is not None and r.get("diferencia_grasa") is not None:
        delta = r["diferencia_grasa"]
        sign = "+" if delta >= 0 else ""
        fat_val += f"  (directa {r['grasa_directa']} % | delta {sign}{delta} %)"
    row(lbl["body_fat"], fat_val, shade=True)
    row(lbl["lean_mass"], f"{r['masa_magra']} kg", shade=False)
    pdf.ln(4)

    # ── 3. BMI / FFMI ────────────────────────────────────────────────────────
    section_title(lbl["imc_ffmi"])
    row(lbl["imc"], f"{r['bmi']} kg/m2", shade=True)
    row(lbl["bmi_cat"], r["bmi_categoria"], shade=False)
    row(lbl["ffmi"], f"{r['ffmi']} kg/m2", shade=True)
    row(lbl["ffmi_norm"], f"{r['ffmi_norm']} kg/m2", shade=False)
    pdf.ln(4)

    # ── 4. Macros ────────────────────────────────────────────────────────────
    section_title(lbl["macros"])
    for i, (k, v) in enumerate(r["macros"].items()):
        unit = "kcal" if "Calor" in k or "Calorie" in k or "kkal" in k else "g"
        row(k, f"{v} {unit}", shade=(i % 2 == 0))
    pdf.ln(4)

    # ── 5. Detailed step-by-step formulas ────────────────────────────────────
    section_title(lbl["report"])
    pdf.ln(1)

    # US Navy
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(27, 38, 59)
    pdf.cell(0, 7, s("1. " + lbl["body_fat"] + " - US Navy"), new_x="LMARGIN", new_y="NEXT")
    formula_row(lbl["formula"], p["navy_formula"])
    if p["navy_sexo"] == "hombre":
        formula_row("Paso 1 - cintura - cuello",
                    f"{p['navy_cintura']} - {p['navy_cuello']} = {p['navy_dif']} cm")
    else:
        formula_row("Paso 1 - cintura + cadera - cuello",
                    f"{p['navy_cintura']} + {p['navy_cadera']} - {p['navy_cuello']} = {p['navy_dif']} cm")
    formula_row("Paso 2 - log10(dif)", f"log10({p['navy_dif']}) = {p['navy_log_dif']}")
    formula_row("Paso 3 - log10(altura)", f"log10({p['navy_altura']}) = {p['navy_log_alt']}")
    formula_row("Paso 4 - denominador", str(p["navy_denominador"]))
    result_row(lbl["result"], f"%GC = {p['navy_grasa']} %")

    # Lean mass
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(27, 38, 59)
    pdf.cell(0, 7, s("2. " + lbl["lean_mass"]), new_x="LMARGIN", new_y="NEXT")
    formula_row("Paso 1 - masa grasa",
                f"{p['mm_peso']} x ({p['navy_grasa']} / 100) = {p['mm_masa_grasa']} kg")
    formula_row("Paso 2 - masa magra",
                f"{p['mm_peso']} - {p['mm_masa_grasa']} = {p['mm_masa_magra']} kg")
    result_row(lbl["result"], f"{p['mm_masa_magra']} kg")

    # BMI
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(27, 38, 59)
    pdf.cell(0, 7, s("3. " + lbl["imc"]), new_x="LMARGIN", new_y="NEXT")
    formula_row("Paso 1 - altura m",
                f"{p['imc_altura_cm']} / 100 = {p['imc_altura_m']} m")
    formula_row("Paso 2 - IMC",
                f"{p['imc_peso']} / {p['imc_altura_m']}^2 = {p['imc_peso']} / {p['imc_altura_m_cuadrado']} = {p['imc_valor']} kg/m2")
    result_row(lbl["result"], f"{p['imc_valor']} kg/m2 | {p['imc_categoria']}")

    # FFMI
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(27, 38, 59)
    pdf.cell(0, 7, s("4. " + lbl["ffmi"]), new_x="LMARGIN", new_y="NEXT")
    formula_row("Paso 1 - FFMI bruto",
                f"{p['ffmi_masa_magra']} / {p['ffmi_altura_m']}^2 = {p['ffmi_masa_magra']} / {p['ffmi_altura_m_cuadrado']} = {p['ffmi_valor']} kg/m2")
    formula_row("Paso 2 - FFMI norm",
                f"{p['ffmi_valor']} + 6.1 x (1.80 - {p['ffmi_altura_m']}) = {p['ffmi_norm_valor']} kg/m2")
    result_row(lbl["result"], f"FFMI = {p['ffmi_valor']} | FFMI norm = {p['ffmi_norm_valor']} kg/m2")

    # Macros
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(27, 38, 59)
    pdf.cell(0, 7, s("5. " + lbl["macros"]), new_x="LMARGIN", new_y="NEXT")
    formula_row("Paso 1 - proteina",
                f"{p['macro_peso']} x 2.0 = {p['macro_proteina_g']} g -> {p['macro_proteina_g']} x 4 = {p['macro_cal_proteina']} kcal")
    formula_row("Paso 2 - grasa",
                f"{p['macro_peso']} x 0.8 = {p['macro_grasa_g']} g -> {p['macro_grasa_g']} x 9 = {p['macro_cal_grasa']} kcal")
    formula_row("Paso 3 - kcal carbos",
                f"{p['macro_kcal']} - {p['macro_cal_proteina']} - {p['macro_cal_grasa']} = {p['macro_cal_carbos']} kcal")
    formula_row("Paso 4 - carbohidratos",
                f"{p['macro_cal_carbos']} / 4 = {p['macro_carbos_g']} g")
    result_row(lbl["result"],
               f"P: {p['macro_proteina_g']} g | G: {p['macro_grasa_g']} g | C: {p['macro_carbos_g']} g | {p['macro_kcal']} kcal")

    return bytes(pdf.output())


@app.route("/api/pdf", methods=["POST"])
def api_pdf():
    """Generate and return a PDF report with all calculation results."""
    lang = request.form.get("lang", DEFAULT_LANG)
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    try:
        resultados = _compute_results(request.form, lang)
        pdf_bytes = _build_pdf(resultados, lang)
        buf = io.BytesIO(pdf_bytes)
        buf.seek(0)
        return send_file(
            buf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="fitness-report.pdf",
        )
    except (AppError, ValueError) as exc:
        return jsonify({"error": _translate_error(exc, lang), "fields": _get_error_fields(exc)}), 400
    except Exception:
        msgs = ERROR_MESSAGES.get(lang, ERROR_MESSAGES[DEFAULT_LANG])
        return jsonify({"error": msgs.get("unknown_error", "Error inesperado.").format(msg=""), "fields": []}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
