"""Módulo de IA: análisis de accesibilidad urbana con Google Gemini."""
import os
from enum import Enum
from typing import List, Optional

from dotenv import load_dotenv
from PIL import Image, ImageOps
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

load_dotenv()

MODELOS = [
    "gemini-3.8-flash",
    "gemini-3.8-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]

# Existen, pero no sirven para analizar imagen + JSON (voz, imagen generada, live)
MODELOS_NO_COMPATIBLES = [
    "gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts",

    "gemini-3.1-flash-image", "gemini-3.1-flash-image-preview",
    "gemini-3.1-flash-tts-preview", "gemini-3.1-flash-live-preview",
    "gemini-2.5-flash-image",
]

# Errores que justifican probar con otro modelo
_ERRORES_REINTENTABLES = ("404", "NOT_FOUND", "429", "RESOURCE_EXHAUSTED",
                          "503", "UNAVAILABLE", "500", "INTERNAL")

SYSTEM_PROMPT = (
    "Eres un experto en accesibilidad urbana y diseño universal. "
    "Analiza la imagen del entorno peatonal (y la descripción del usuario, escrita o "
    "dictada en audio, si existe) e identifica: "
    "1) si hay accesibilidad para sillas de ruedas, muletas o adultos mayores, "
    "2) obstáculos presentes (baches, autos mal estacionados, falta de rampa, banqueta bloqueada, "
    "postes, escalones, cables, obras), "
    "3) un nivel de riesgo (Bajo, Medio, Alto) y "
    "4) una recomendación breve de navegación por audio (máximo 25 palabras, lenguaje sencillo). "
    "Si no hay información suficiente o la imagen no muestra un entorno peatonal, pon "
    "'informacion_suficiente' en false y no inventes datos. "
    "Sé prudente: ante la duda, asigna el riesgo más alto. Responde siempre en español."
)


class Riesgo(str, Enum):
    BAJO = "Bajo"
    MEDIO = "Medio"
    ALTO = "Alto"


class EvaluacionAccesibilidad(BaseModel):
    informacion_suficiente: bool = Field(description="False si no se puede evaluar")

    resumen: str = Field(description="Descripción de una frase del entorno")
    cuenta_con_rampa: bool
    accesible_silla_ruedas: bool
    obstaculos: List[str]
    nivel_riesgo: Riesgo
    recomendaciones: List[str] = Field(description="Acciones inmediatas, máximo 3")
    mensaje_audio: str = Field(description="Alerta sonora, máximo 25 palabras")
    confianza: float = Field(description="Entre 0 y 1")


def _preparar_imagen(fuente) -> Image.Image:
    img = ImageOps.exif_transpose(Image.open(fuente)).convert("RGB")
    img.thumbnail((1280, 1280))  # más rápido y barato
    return img


def evaluar_accesibilidad_urbana(
    imagen_fuente=None,
    descripcion_texto: Optional[str] = None,
    audio_bytes: Optional[bytes] = None,
    modelo: Optional[str] = None,
    usar_respaldo: bool = True,
):
    """Devuelve (EvaluacionAccesibilidad | str de error, modelo_usado)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Falta GEMINI_API_KEY. Configúrala en el archivo .env", None
    if imagen_fuente is None and not audio_bytes and not descripcion_texto:
        return "Agrega una foto, un audio o una descripción.", None

    # Orden de intentos: el elegido primero y luego el resto de la lista
    primero = modelo or os.getenv("GEMINI_MODEL") or MODELOS[0]

    candidatos = [primero] + ([m for m in MODELOS if m != primero] if usar_respaldo else [])

    try:
        client = genai.Client(api_key=api_key)
        contenido = []
        if imagen_fuente is not None:
            contenido.append(_preparar_imagen(imagen_fuente))
        contenido.append("Evalúa la accesibilidad de este entorno peatonal.")
        if descripcion_texto:
            contenido.append(f"Descripción del usuario: {descripcion_texto}")
        if audio_bytes:
            contenido.append("El usuario dictó esta descripción en audio:")
            contenido.append(types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"))
    except Exception as e:
        return f"Error preparando los datos: {e}", None

    ultimo_error = ""
    for nombre in candidatos:
        try:
            resp = client.models.generate_content(
                model=nombre,
                contents=contenido,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=EvaluacionAccesibilidad,
                    temperature=0.2,
                ),
            )
            if resp.parsed is not None:
                return resp.parsed, nombre
            ultimo_error = f"{nombre}: respuesta vacía"

        except Exception as e:
            ultimo_error = f"{nombre}: {e}"
            if not any(c in str(e) for c in _ERRORES_REINTENTABLES):
                break  # error no recuperable (clave inválida, etc.)
    return f"Error en la evaluación de infraestructura. Último intento -> {ultimo_error}", None


if __name__ == "__main__":
    r, usado = evaluar_accesibilidad_urbana("banqueta_ejemplo.jpg")
    print("--- Diagnóstico de Accesibilidad Peatonal ---")
    print(r if isinstance(r, str) else f"[{usado}]\n{r.model_dump_json(indent=2)}")