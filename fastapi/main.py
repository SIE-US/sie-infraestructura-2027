"""
main.py
-------
Objetivo: ofrecer una API inicial sencilla para aprender FastAPI y conceptos de integración.
Info: http://localhost:8000/docs y http://localhost:8000/redoc
"""

# Librerías estándar.
import os
from typing import Any, Literal

# FastAPI para exponer endpoints HTTP y respuestas de error.
from fastapi import FastAPI, HTTPException, status

# Pydantic valida automáticamente los datos de entrada.
from pydantic import BaseModel, Field

# requests es simple y permite hacer peticiones (p.e. a Ollama).
import requests

# Para conectarse a Odoo vía XML-RPC.
import xmlrpc.client

# Para conectarse a Odoo vía JSON-2-RPC (Odoo 19 introduce esta nueva opción).
# También para conectarse a Bonita.
import httpx

# Para controlar la caducidad del token de SuiteCRM.
import time
suitecrm_token = None
suitecrm_token_expiration = 0

# ---------------------------------------------------------------------------
# Configuración 
# ---------------------------------------------------------------------------
# Se leen desde variables de entorno para que docker-compose pueda cambiarlas
# sin tocar el código. Si no existen, se usan valores por defecto.
ODOO_URL = os.getenv("ODOO_URL", "http://odoo:8069")
SUITECRM_URL = os.getenv("SUITECRM_URL", "http://suitecrm")
BONITA_URL = os.getenv("BONITA_URL", "http://bonita:8080")
N8N_URL = os.getenv("N8N_URL", "http://n8n:5678")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
ODOO_DB = os.getenv("ODOO_DB", "SIE-test")
ODOO_API_USER = os.getenv("ODOO_API_USER", "fastapi@sie-test.es")
ODOO_API_PASSWORD = os.getenv("ODOO_API_PASSWORD", "fastapi")
ODOO_API_KEY = os.getenv("ODOO_API_KEY", "98bccfeeb643771eec9f8b320427cc4192a7da9c")
SUITECRM_CLIENT_ID = os.getenv("SUITECRM_CLIENT_ID")
SUITECRM_CLIENT_SECRET = os.getenv("SUITECRM_CLIENT_SECRET")
BONITA_USERNAME = os.getenv("BONITA_USERNAME", "install")
BONITA_PASSWORD = os.getenv("BONITA_PASSWORD", "install")


# ---------------------------------------------------------------------------
# Inicialización de la aplicación FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="SIE Integration API",
    description="Ejemplos de integración ERP + CRM + BPM + IA",
    version="1.0",
)


# ---------------------------------------------------------------------------
# Modelos de entrada (request body)
# ---------------------------------------------------------------------------
class Contacto(BaseModel):
    """
    Modelo unificado de contacto utilizado por la API.

    Independientemente del sistema origen (Odoo, SuiteCRM, etc.),
    todos los contactos se devuelven con esta estructura.
    Este proceso se conoce como transformación o normalización
    de datos y es muy habitual en plataformas de integración.
    """
    origen: str
    id: int | str
    nombre: str
    email: str | None = None
    telefono: str | None = None
    ciudad: str | None = None

class ProcesoBonita(BaseModel):
    """
    Modelo simplificado de un proceso desplegado en Bonita.
    """
    id: str
    nombre: str
    version: str
    activo: bool

class Prompt(BaseModel):
    """
    Texto que se enviará al modelo de IA.
    """
    prompt: str = Field(..., min_length=1, max_length=4000)


# ---------------------------------------------------------------------------
# Funciones auxiliares para Odoo
# ---------------------------------------------------------------------------
def conectar_odoo():
    """
    Establece la conexión con Odoo.

    Devuelve:
        uid: identificador del usuario autenticado.
        models: objeto que permite acceder a los modelos de Odoo.

    Lanza una excepción HTTP si no consigue autenticarse.
    """

    # Servicio de autenticación
    common = xmlrpc.client.ServerProxy(
        f"{ODOO_URL}/xmlrpc/2/common"
    )

    # Autenticación
    uid = common.authenticate(
        ODOO_DB,
        ODOO_API_USER,
        ODOO_API_PASSWORD,
        {}
    )

    if not uid:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo autenticar con Odoo."
        )

    # Servicio que permite acceder a los modelos (res.partner, sale.order...)
    models = xmlrpc.client.ServerProxy(
        f"{ODOO_URL}/xmlrpc/2/object"
    )

    return uid, models


# ---------------------------------------------------------------------------
# Funciones auxiliares para SuiteCRM
# ---------------------------------------------------------------------------
def obtener_token_suitecrm() -> str:
    """
    Obtiene un token OAuth2 para acceder a la API REST de SuiteCRM.

    El token se reutiliza mientras siga siendo válido.
    """
    global suitecrm_token
    global suitecrm_token_expiration

    # Si el token todavía no ha caducado, reutilizarlo.
    if suitecrm_token and time.time() < suitecrm_token_expiration:
        return suitecrm_token

    headers = {
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json",
    }

    body = {
        "grant_type": "client_credentials",
        "client_id": SUITECRM_CLIENT_ID,
        "client_secret": SUITECRM_CLIENT_SECRET,
    }

    try:
        response = httpx.post(
            f"{SUITECRM_URL}/legacy/Api/access_token",
            headers=headers,
            json=body,
            timeout=30,
        )
        response.raise_for_status()

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Error autenticando con SuiteCRM: {exc.response.text}",
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"No se pudo conectar con SuiteCRM: {exc}",
        )

    datos = response.json()
    suitecrm_token = datos["access_token"]

    # Renovarlo un minuto antes de que expire.
    suitecrm_token_expiration = time.time() + datos["expires_in"] - 60

    return suitecrm_token


# ---------------------------------------------------------------------------
# Funciones auxiliares para Bonita Runtime
# ---------------------------------------------------------------------------
def autenticar_bonita() -> httpx.Client:
    """
    Crea una sesión autenticada con Bonita Runtime.

    Bonita utiliza autenticación basada en sesión HTTP.
    Tras autenticarse, el servidor devuelve las cookies
    necesarias para acceder a la API REST.
    """
    cliente = httpx.Client(follow_redirects=True, timeout=10)
    respuesta = cliente.post(
        f"{BONITA_URL}/bonita/loginservice",
        data={
            "username": BONITA_USERNAME,
            "password": BONITA_PASSWORD,
            "redirect": "false",
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
    )
    respuesta.raise_for_status()

    return cliente


# ---------------------------------------------------------------------------
# Endpoints básicos para empezar
# ---------------------------------------------------------------------------
@app.get("/", tags=["Sistema"])
def root() -> dict[str, str]:
    return {"mensaje": "API de integración SIE"}


@app.get("/health", tags=["Sistema"])
def health() -> dict[str, str]:
    # Endpoint mínimo de vida de la API.
    return {"status": "ok"}


@app.get("/servicios", tags=["Sistema"])
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
# Endpoints de Odoo
# ---------------------------------------------------------------------------
@app.get("/odoo/contactos", response_model=list[Contacto], tags=["Odoo"])
def obtener_contactos_odoo(tipo: Literal["todos", "clientes", "proveedores"] = "todos"):
    """
    Recupera los contactos de Odoo.

    Parámetros:
        - todos (por defecto)
        - clientes
        - proveedores

    Solo devuelve algunos campos para simplificar el ejemplo.
    """
    uid, models = conectar_odoo()

    # Dominio de búsqueda según el tipo solicitado
    dominio = []
    if tipo == "clientes":
        dominio = [["customer_rank", ">", 0]]
    elif tipo == "proveedores":
        dominio = [["supplier_rank", ">", 0]]

    try:
        contactos = models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_API_PASSWORD,
            "res.partner",
            "search_read",
            [dominio],
            {
                "fields": [
                    "id",
                    "name",
                    "email",
                    "phone",
                    "city",
                ],
                "order": "name",
            },
        )

    # Odoo respondió, pero con error (p.e. permisos insuficientes o un modelo inexistente)
    except xmlrpc.client.Fault as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Odoo devolvió un error: {exc}",
        )

    # No se pudo conectar con Odoo (p.e. servicio caído o URL incorrecta)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"No se pudo conectar con Odoo: {exc}",
        )

    resultado = []

    # Se transforma la lista de contactos en un formato más sencillo para la API.
    # Aquí vemos que FastAPI no es un mero proxy de Odoo, sino que puede:
    # eliminar campos, renombrarlos, combinar varios sistemas, validar datos, ocultar información,...
    for contacto in contactos:
        # Odoo a veces devuelve False en vez de None si un campo no tiene valor. 
        # Se normaliza a None para que Pydantic no de error de validación e "internal server error"
        # (el modelo definido más arriba dice que debe ser str o None).
        resultado.append(
            Contacto(
                origen="Odoo",
                id=contacto["id"],
                nombre=contacto["name"],
                email=contacto["email"] or None,
                telefono=contacto["phone"] or None,
                ciudad=contacto["city"] or None,
            )
        )

    return resultado


@app.get("/odoo/contactos/json2", response_model=list[Contacto], tags=["Odoo"])
def obtener_contactos_odoo_json2(tipo: Literal["todos", "clientes", "proveedores"] = "todos"):
    """
    Implementación equivalente utilizando la nueva API JSON-2 de Odoo 19.

    La respuesta es exactamente la misma que en el endpoint XML-RPC.
    Lo único que cambia es la tecnología utilizada para comunicarse con Odoo.
    """
    dominio = []
    if tipo == "clientes":
        dominio = [["customer_rank", ">", 0]]
    elif tipo == "proveedores":
        dominio = [["supplier_rank", ">", 0]]

    headers = {
        "Authorization": f"bearer {ODOO_API_KEY}",
        "X-Odoo-Database": ODOO_DB,
        "Content-Type": "application/json",
        "User-Agent": "SIE FastAPI",
    }

    payload = {
        "domain": dominio,
        "fields": [
            "id",
            "name",
            "email",
            "phone",
            "city"
        ],
        "order": "name",
    }

    try:
        response = httpx.post(
            f"{ODOO_URL}/json/2/res.partner/search_read",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Odoo devolvió un error: {exc.response.text}",
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"No se pudo conectar con Odoo: {exc}",
        )

    contactos = response.json()

    resultado = []
    for contacto in contactos:
        resultado.append(
            Contacto(
                origen="Odoo",
                id=contacto["id"],
                nombre=contacto["name"],
                email=contacto["email"] or None,
                telefono=contacto["phone"] or None,
                ciudad=contacto["city"] or None,
            )
        )

    return resultado


# ---------------------------------------------------------------------------
# Endpoints de SuiteCRM
# ---------------------------------------------------------------------------
@app.get("/suitecrm/contactos", response_model=list[Contacto], tags=["SuiteCRM"])
def obtener_contactos_suitecrm():
    """
    Recupera los contactos de SuiteCRM.
    Utiliza el mismo modelo que el endpoint /odoo/contactos.
    """
    token = obtener_token_suitecrm()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json",
    }

    try:
        response = httpx.get(
            f"{SUITECRM_URL}/legacy/Api/V8/module/Contacts",
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=exc.response.text,
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    datos = response.json()
    resultado = []
    for contacto in datos["data"]:
        atributos = contacto["attributes"]
        nombre = f"{atributos.get('first_name','')} {atributos.get('last_name','')}".strip()
        resultado.append(
            Contacto(
                origen="SuiteCRM",
                id=contacto["id"],
                nombre=nombre,
                email=atributos.get("email1"),
                telefono=atributos.get("phone_work"),
                ciudad=atributos.get("primary_address_city"),
            )
        )

    return resultado


# ---------------------------------------------------------------------------
# Endpoints de Bonita
# ---------------------------------------------------------------------------
@app.get("/bonita/version", tags=["Bonita"])
def bonita_version():
    try:
        cliente = autenticar_bonita()

        respuesta = cliente.get(
            f"{BONITA_URL}/bonita/API/system/session/unusedId"
        )
        respuesta.raise_for_status()

        datos = respuesta.json()

        return {
            "version": datos.get("version"),
            "usuario": datos.get("user_name"),
            "session_id": datos.get("session_id"),
        }

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=exc.response.text,
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"No se pudo conectar con Bonita: {exc}",
        )

@app.get("/bonita/procesos", response_model=list[ProcesoBonita], tags=["Bonita"],
)
def obtener_procesos_bonita():
    """
    Devuelve la lista de procesos desplegados en Bonita Runtime.
    """
    try:
        # Crear una sesión autenticada con Bonita.
        cliente = autenticar_bonita()

        # Recuperar todos los procesos desplegados.
        respuesta = cliente.get(
            f"{BONITA_URL}/bonita/API/bpm/process?p=0&c=100"
        )
        respuesta.raise_for_status()

        procesos = respuesta.json()
        procesos_unificados = []
        for proceso in procesos:
            procesos_unificados.append(
                ProcesoBonita(
                    id=proceso["id"],
                    nombre=proceso["displayName"],
                    version=proceso["version"],
                    activo=proceso["activationState"] == "ENABLED",
                )
            )

        return procesos_unificados

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=exc.response.text,
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"No se pudo conectar con Bonita: {exc}",
        )


# ---------------------------------------------------------------------------
# Endpoints de Ollama
# ---------------------------------------------------------------------------
@app.get("/ollama/models", tags=["Ollama"])
def ollama_models() -> dict[str, Any]:
    '''
    Para ver qué modelos hay descargados en Ollama.
    Si la lista está vacía, primero habrá que descargar un modelo.
    '''
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


@app.post("/ollama/generate", tags=["Ollama"])
def ollama_generate(req: Prompt) -> dict[str, Any]:
    '''
    Este endpoint genera texto, pero solo funcionará cuando exista al menos
    un modelo descargado en Ollama.
    '''
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
# Endpoints de Integración
# ---------------------------------------------------------------------------
@app.get("/contactos", response_model=list[Contacto], tags=["Integración"])
def obtener_contactos():
    """
    Devuelve una lista unificada de contactos procedentes
    de varios sistemas integrados (Odoo y SuiteCRM).

    Este endpoint muestra uno de los objetivos principales
    de una plataforma de integración: ofrecer un modelo de
    datos homogéneo independientemente del sistema origen.
    """
    contactos = []
    contactos.extend(obtener_contactos_odoo())
    contactos.extend(obtener_contactos_suitecrm())

    contactos.sort(key=lambda c: c.nombre.lower()) # Orden alfabético por nombre

    return contactos
