# RutaAccesible IA ♿
Asistente urbano multimodal: foto o voz → evaluación de accesibilidad, riesgo y alerta sonora.
Hackatón Nacional de Innovación con IA Aplicada 2026 – Ingenio Incluyente (UVM).

## Declaración de uso de IA
| Módulo | Herramienta | Rol |
|---|---|---|
| `evaluador.py` | Google Gemini API (gemini-2.5-flash) | Análisis de imagen y audio, detección de obstáculos, nivel de riesgo y alerta |
| Prompt del sistema | Google AI Studio | Diseño y depuración de instrucciones |
| Documentación y pitch | Google Workspace | Borradores de memoria y guion |
| Apoyo de código | (indica aquí cualquier asistente de IA que hayas usado) | Revisión y generación de código |

La alerta sonora usa gTTS (síntesis de voz, no es IA generativa de análisis).
Limitación: evaluación orientativa, no sustituye el criterio del usuario.

## Instalación
```bash
python -m venv venv
venv\Scripts\activate        # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env       # Mac/Linux: cp .env.example .env  (y pega tu clave)
streamlit run app.py
```
Celular: abre la Network URL (mismo wifi). Cámara/micrófono exigen HTTPS: despliega en
Streamlit Community Cloud y guarda `GEMINI_API_KEY` en Secrets.

## ODS
- **ODS 10:** reduce barreras de movilidad para personas con discapacidad y adultos mayores.
- **ODS 11:** impulsa ciudades accesibles, seguras e inclusivas.

## Referencias
Google. (2026). *Google GenAI SDK Documentation and Gemini API Reference*. Google AI for Developers. https://ai.google.dev/docs

Naciones Unidas. (2015). *Objetivos de Desarrollo Sostenible: ODS 11 Ciudades y comunidades sostenibles*. ONU. https://www.un.org/sustainabledevelopment/es/cities/
