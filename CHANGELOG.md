# Changelog

Todos los cambios importantes de este proyecto están documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.1.0/),
y este proyecto sigue el [Versionado Semántico](https://semver.org/lang/es/).

---

## [Unreleased]

### Added
- GitHub Actions CI workflow para ejecutar tests automáticamente en cada push/PR.
- Plantillas de issues para bug reports y feature requests.
- Plantilla de Pull Request.
- `.gitignore` para proyectos Python.
- `LICENSE` MIT.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` y `SECURITY.md`.
- Badges de estado en el `README.md`.

---

## [0.1.0] — 2024-01-01

### Added
- Librería `fitness_tools` con módulos `body_composition` y `nutrition`.
- Fórmula US Navy para hombres y mujeres (porcentaje de grasa corporal).
- Cálculo de IMC (BMI) con clasificación OMS.
- Cálculo de FFMI normalizado.
- Distribución de macronutrientes diarios (proteína, grasa, carbohidratos).
- CLI (`main.py`) con todos los argumentos documentados.
- Web app Flask multiidioma (12 idiomas: es, en, it, fr, de, pt, nl, pl, ru, zh, ja, ko).
- Generación de informes en PDF desde la web app.
- Despliegue en Heroku con Procfile y runtime.txt.
- Suite de tests con pytest.

[Unreleased]: https://github.com/juanfranciscofernandezherreros/fitness-calculator-tool/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/juanfranciscofernandezherreros/fitness-calculator-tool/releases/tag/v0.1.0
