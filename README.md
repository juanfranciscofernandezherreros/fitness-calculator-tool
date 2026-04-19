# n8n + Java + Python Stack

Custom [n8n](https://n8n.io/) setup with Java 21, Maven and Python 3 pre-installed, suitable for workflows that need to run JVM or Python code directly from n8n nodes.

## Stack

| Component | Version |
|-----------|---------|
| n8n       | latest-debian |
| Java      | 21 (OpenJDK) |
| Maven     | latest via apt |
| Python    | 3 + pip + venv |

## Quick Start

```bash
docker compose up -d
```

n8n will be available at <http://localhost:5678>.

## Configuration

Copy the relevant environment variables from `docker-compose.yml` and override them in a `.env` file:

```env
# Path to your local Spring Boot / Maven project
LAUNCHER_PROJECT_PATH=/path/to/your/project
```

## Utilities

- **`macro_calculator.py`** – standalone Python script that calculates daily macronutrients (protein, fat, carbs) for runners using the US Navy body-fat formula. Run it directly with:

```bash
python3 macro_calculator.py
```

## Documentation

See [`docu.md`](docu.md) for the full Back Billing process reference, including database setup, SQL validation queries and flow diagrams.
