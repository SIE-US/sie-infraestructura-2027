"""
main.py
-------
Objetivo: ofrecer una API muy sencilla para aprender FastAPI y conceptos de integración.
Info: http://localhost:8000/docs y http://localhost:8000/redoc
"""

# Librerías estándar.
import os
from typing import Any

# FastAPI para exponer endpoints HTTP y respuestas de error.
from fastapi import FastAPI, HTTPException, status

# Pydantic valida automáticamente los datos de entrada.
from pydantic import BaseModel, Field

# requests se usa aquí porque es simple para una primera versión.
import requests

# ---------------------------------------------------------------------------
# 1) Configuración básica (URLs de servicios)
# ---------------------------------------------------------------------------
# Se leen desde variables de entorno para que docker-compose pueda cambiarlas
# sin tocar el código. Si no existen, se usan valores por defecto del entorno docente.
ODOO_URL = os.getenv("ODOO_URL", "http://odoo:8069")
SUITECRM_URL = os.getenv("SUITECRM_URL", "http://suitecrm/public")
BONITA_URL = os.getenv("BONITA_URL", "http://bonita:8080")
N8N_URL = os.getenv("N8N_URL", "http://n8n:5678")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# ---------------------------------------------------------------------------
# 2) Inicialización de la aplicación FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="SIE Integration API",
    description="Ejemplos de integración ERP + CRM + BPM + IA",
    version="1.0",
)


# ---------------------------------------------------------------------------
# 3) Modelos de entrada (request body)
# ---------------------------------------------------------------------------
class Prompt(BaseModel):
    # Texto que se enviará al modelo de IA.
    prompt: str = Field(..., min_length=1, max_length=4000)


class Pedido(BaseModel):
    # Ejemplo de estructura de pedido para practicar validación y JSON.
    cliente: str = Field(..., min_length=1, max_length=100)
    producto: str = Field(..., min_length=1, max_length=100)
    cantidad: int = Field(..., gt=0)


# ---------------------------------------------------------------------------
# 4) Endpoints básicos para empezar
# ---------------------------------------------------------------------------
@app.get("/")
def root() -> dict[str, str]:
    return {"mensaje": "API de integración SIE"}


@app.get("/health")
def health() -> dict[str, str]:
    # Endpoint mínimo de vida de la API.
    return {"status": "ok"}


@app.get("/servicios")
def servicios() -> dict[str, str]:
    # Muestra direcciones de los servicios, aunque aún no estén configurados.
    return {
        "odoo": ODOO_URL,
        "suitecrm": SUITECRM_URL,
        "bonita": BONITA_URL,
        "n8n": N8N_URL,
        "ollama": OLLAMA_URL,
    }


# ---------------------------------------------------------------------------
# 5) Endpoints de Ollama (primeros pasos)
# ---------------------------------------------------------------------------
@app.get("/ollama/models")
def ollama_models() -> dict[str, Any]:
    # Primer endpoint recomendado: ver qué modelos hay descargados en Ollama.
    # Si la lista está vacía, primero habrá que descargar un modelo.
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"No se pudo contactar con Ollama: {exc}",
        ) from exc

    try:
        return response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ollama respondió, pero no devolvió JSON válido.",
        ) from exc


@app.post("/ollama/generate")
def ollama_generate(req: Prompt) -> dict[str, Any]:
    # Este endpoint genera texto, pero solo funcionará cuando exista al menos
    # un modelo descargado en Ollama.
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": req.prompt,
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"No se pudo contactar con Ollama: {exc}",
        ) from exc

    try:
        return response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ollama respondió, pero no devolvió JSON válido.",
        ) from exc


# ---------------------------------------------------------------------------
# 6) Endpoint de ejemplo de orquestación (sin lógica real todavía)
# ---------------------------------------------------------------------------
@app.post("/pedido")
def pedido(p: Pedido) -> dict[str, Any]:
    # No crea nada realmente en esta fase inicial: solo explica el flujo.
    return {
        "mensaje": "Ejemplo de orquestación (modo demostración)",
        "pasos": [
            "1. Crear cliente/pedido en Odoo (más adelante)",
            "2. Crear oportunidad en SuiteCRM (más adelante)",
            "3. Iniciar proceso en Bonita (más adelante)",
            "4. Opcional: automatizar con n8n (más adelante)",
            "5. Generar resumen con Ollama",
        ],
        "datos_recibidos": p.model_dump(),
    }


# ---------------------------------------------------------------------------
# 7) Endpoints demo por sistema (guía para prácticas futuras)
# ---------------------------------------------------------------------------
@app.get("/demo/odoo")
def demo_odoo() -> dict[str, str]:
    return {
        "url": f"{ODOO_URL}/xmlrpc/2/common",
        "nota": "Fase inicial: solo referencia. Más adelante se añade autenticación y consultas.",
    }


@app.get("/demo/suitecrm")
def demo_suitecrm() -> dict[str, str]:
    return {
        "url": f"{SUITECRM_URL}/api",
        "nota": "Fase inicial: solo referencia. Más adelante se añaden llamadas REST reales.",
    }


@app.get("/demo/bonita")
def demo_bonita() -> dict[str, str]:
    return {
        "url": f"{BONITA_URL}/bonita/API",
        "nota": "Fase inicial: solo referencia. Más adelante se crearán procesos/tareas.",
    }


@app.get("/demo/integracion")
def demo_integracion() -> dict[str, list[str]]:
    # Resumen narrativo del flujo completo para entender la arquitectura.
    return {
        "flujo": [
            "Cliente realiza pedido",
            "FastAPI recibe la petición",
            "Odoo registrará el pedido (fases futuras)",
            "SuiteCRM registrará oportunidad (fases futuras)",
            "Bonita gestionará proceso BPM (fases futuras)",
            "Ollama puede generar un resumen",
            "n8n puede ampliar automatizaciones",
        ]
    }
