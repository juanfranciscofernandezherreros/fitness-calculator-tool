# Contribuir a fitness-calculator-tool

¡Gracias por querer contribuir! 🎉 Estas son las pautas para mantener el proyecto ordenado y de calidad.

---

## Código de Conducta

Al participar en este proyecto aceptas nuestro [Código de Conducta](CODE_OF_CONDUCT.md).

---

## ¿Cómo puedo contribuir?

### Reportar un bug

1. Busca en los [issues existentes](https://github.com/juanfranciscofernandezherreros/fitness-calculator-tool/issues) para ver si ya está reportado.
2. Si no existe, abre un [nuevo issue](https://github.com/juanfranciscofernandezherreros/fitness-calculator-tool/issues/new/choose) usando la plantilla **Bug report**.
3. Incluye pasos para reproducirlo, salida esperada y salida real.

### Proponer una mejora

1. Abre un [issue de tipo Feature Request](https://github.com/juanfranciscofernandezherreros/fitness-calculator-tool/issues/new/choose) describiendo el caso de uso.
2. Explica por qué sería útil y cómo encajaría en el proyecto.

### Enviar un Pull Request

1. Haz un **fork** del repositorio y crea una rama descriptiva:
   ```bash
   git checkout -b feat/nombre-de-la-feature
   # o
   git checkout -b fix/descripcion-del-bug
   ```

2. Instala las dependencias de desarrollo:
   ```bash
   pip install -e ".[dev]"
   pip install -r requirements.txt
   ```

3. Realiza tus cambios siguiendo el estilo del código existente.

4. Añade o actualiza los tests correspondientes en `tests/`.

5. Asegúrate de que todos los tests pasan:
   ```bash
   pytest
   ```

6. Haz commit con mensajes claros (preferentemente en inglés, estilo [Conventional Commits](https://www.conventionalcommits.org/)):
   ```
   feat: add Harris-Benedict BMR formula
   fix: correct female US Navy formula rounding
   docs: update README with new CLI flags
   ```

7. Abre el Pull Request contra la rama `main` usando la plantilla provista.

---

## Estilo de código

- Seguimos **PEP 8**. Puedes verificarlo con `flake8` o `ruff`.
- Las docstrings siguen el formato [Google Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
- Los nombres de variables y funciones van en **español** (coherencia con el dominio), los comentarios de código pueden ir en español o inglés.

---

## Estructura del proyecto

```
fitness-calculator-tool/
├── fitness_tools/          # Librería Python (lógica de negocio)
├── templates/              # Plantillas HTML de la web app
├── tests/                  # Tests con pytest
├── app.py                  # Web app Flask
├── main.py                 # CLI
├── pyproject.toml          # Metadatos y dependencias del paquete
└── requirements.txt        # Dependencias para despliegue web
```

---

## Entorno de desarrollo

```bash
# 1. Clona el repo
git clone https://github.com/juanfranciscofernandezherreros/fitness-calculator-tool.git
cd fitness-calculator-tool

# 2. Crea un entorno virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instala el paquete en modo editable + dependencias dev
pip install -e ".[dev]"
pip install -r requirements.txt

# 4. Ejecuta los tests
pytest

# 5. Arranca la web app en local
python app.py
```

---

¿Tienes dudas? Abre un issue o contacta con el mantenedor. ¡Toda contribución, por pequeña que sea, es bienvenida! 💪
