# Financial Exercises

> ⚠️ **Purely theoretical / educational project.** The code in this repository
> exists to practice software engineering concepts applied to the financial
> domain (transfers, idempotency, instrument valuation, design patterns). **It is
> not meant for production** nor does it represent a real system: the "database"
> lives in memory, there are incomplete examples, and some snippets are written
> on purpose to reason about them.

## What's here?

The repository gathers several independent exercises around a common theme:
financial software.

### 1. Transfer service (`financial_exercises/exercises/`)

A simulation of a transfer API between accounts that practices several key
payment-system concepts:

- **Idempotency** — each transfer carries an `idempotency_key`; on retry, the
  original result is returned without touching the "DB" again.
- **Simulated atomicity** — the debit and credit happen together inside a
  `try/except` that reverts the balances if anything fails (mimicking Django's
  `transaction.atomic()`).
- **Input validation** — Pydantic schemas validate amount, account format, and
  currency before processing.
- **Audit log** — every operation is recorded.

Files:

| File | Role |
| --- | --- |
| [models.py](financial_exercises/exercises/models.py) | Dataclasses (`Account`, `Transfer`, `AuditLog`) and in-memory "DB" |
| [schemas.py](financial_exercises/exercises/schemas.py) | Request validation with Pydantic |
| [services.py](financial_exercises/exercises/services.py) | Business logic: `process_transfer()` |
| [main.py](financial_exercises/exercises/main.py) | FastAPI endpoint `POST /api/v1/transfers` |

### 2. Financial instrument portfolio (`portfolio.py`)

An **OOP and design patterns** exercise that models an investment portfolio:

- **Abstract class** (`FinancialInstrument`) that defines the common contract.
- **Polymorphism** — `Equity` (stocks) and `Bond` (bonds) compute their value
  differently behind the same `calculate_value()` method.
- **Observer pattern** — `RiskSystem` subscribes to the `Portfolio` and reacts
  automatically when high-risk instruments are added.
- **Good money practices** — use of `Decimal` (never `float`) to avoid
  floating-point errors.

It can be run directly:

```bash
python portfolio.py
```

## Notes

- The project mixes a **Django** skeleton (`manage.py`, `settings.py`) with
  **FastAPI** and **Pydantic** exercises; the exercises are the core part and
  the Django scaffolding is just the container.
- Some files contain **intentional errors or incomplete code** (syntax,
  badly-indented decorators, inconsistent names like `TRANSFER`/`TRANSFERS`)
  typical of study material. Don't take them as a reference for correct code.
- Comments are mixed in Spanish and English, reflecting the learning process.

## Requirements

- Python 3.12
- Dependencies in the `venv/` virtual environment: Django, Django REST
  Framework, FastAPI, and Pydantic.

---

# Financial Exercises (Español)

> ⚠️ **Proyecto puramente teórico / educativo.** El código de este repositorio
> existe para practicar conceptos de ingeniería de software aplicados al dominio
> financiero (transferencias, idempotencia, valoración de instrumentos, patrones
> de diseño). **No está pensado para producción** ni representa un sistema real:
> la "base de datos" vive en memoria, hay ejemplos incompletos y fragmentos
> escritos a propósito para razonar sobre ellos.

## ¿Qué hay aquí?

El repositorio reúne varios ejercicios independientes alrededor de un tema común:
software financiero.

### 1. Servicio de transferencias (`financial_exercises/exercises/`)

Una simulación de una API de transferencias entre cuentas que practica varios
conceptos clave de los sistemas de pagos:

- **Idempotencia** — cada transferencia lleva una `idempotency_key`; si se
  reintenta, se devuelve el resultado original sin volver a tocar la "DB".
- **Atomicidad simulada** — el débito y el crédito se hacen juntos con un
  `try/except` que revierte los saldos si algo falla (imitando
  `transaction.atomic()` de Django).
- **Validación de entrada** — esquemas Pydantic validan monto, formato de
  cuenta y divisa antes de procesar.
- **Audit log** — cada operación queda registrada.

Archivos:

| Archivo | Rol |
| --- | --- |
| [models.py](financial_exercises/exercises/models.py) | Dataclasses (`Account`, `Transfer`, `AuditLog`) y "DB" en memoria |
| [schemas.py](financial_exercises/exercises/schemas.py) | Validación de la petición con Pydantic |
| [services.py](financial_exercises/exercises/services.py) | Lógica de negocio: `process_transfer()` |
| [main.py](financial_exercises/exercises/main.py) | Endpoint FastAPI `POST /api/v1/transfers` |

### 2. Portfolio de instrumentos financieros (`portfolio.py`)

Un ejercicio de **POO y patrones de diseño** que modela un portafolio de
inversión:

- **Clase abstracta** (`FinancialInstrument`) que define el contrato común.
- **Polimorfismo** — `Equity` (acciones) y `Bond` (bonos) calculan su valor de
  forma distinta tras el mismo método `calculate_value()`.
- **Patrón Observer** — `RiskSystem` se suscribe al `Portfolio` y reacciona
  automáticamente cuando se agregan instrumentos de alto riesgo.
- **Buenas prácticas con dinero** — uso de `Decimal` (nunca `float`) para evitar
  errores de punto flotante.

Se puede ejecutar directamente:

```bash
python portfolio.py
```

## Notas

- El proyecto mezcla un esqueleto de **Django** (`manage.py`, `settings.py`) con
  ejercicios de **FastAPI** y **Pydantic**; los ejercicios son la parte central
  y el andamiaje Django es solo el contenedor.
- Algunos archivos contienen **errores intencionales o código incompleto**
  (sintaxis, decoradores mal indentados, nombres inconsistentes como
  `TRANSFER`/`TRANSFERS`) propios de un material de estudio. No los tomes como
  referencia de código correcto.
- Los comentarios están en español e inglés mezclados, reflejo del proceso de
  aprendizaje.

## Requisitos

- Python 3.12
- Dependencias en el entorno virtual `venv/`: Django, Django REST Framework,
  FastAPI y Pydantic.
</content>
