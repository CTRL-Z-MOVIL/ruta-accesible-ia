"""RutaAccesible IA - Interfaz móvil rediseñada (Streamlit)."""
import io
from datetime import datetime

import pandas as pd
import streamlit as st
from gtts import gTTS

from evaluador import evaluar_accesibilidad_urbana, MODELOS

# Configuración de página
st.set_page_config(
    page_title="RutaAccesible IA",
    page_icon="♿",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Inicialización de estado
if "historial" not in st.session_state:
    st.session_state.historial = []
if "ultimo" not in st.session_state:
    st.session_state.ultimo = None

# Barra superior de accesibilidad y ajustes
col_top1, col_top2 = st.columns([1, 1])
with col_top1:
    alto_contraste = st.toggle("🌓 Alto contraste", value=False)
with col_top2:
    with st.expander("⚙️ Ajustes de IA"):
        modelo_sel = st.selectbox("Modelo Gemini", MODELOS, index=0)
        usar_respaldo = st.checkbox("Respaldo automático", value=True)

# Paleta de colores según modo
if alto_contraste:
    bg_app = "#000000"
    bg_card = "#121212"
    text_main = "#FFFFFF"
    text_sub = "#E0E0E0"
    border_col = "#FFFFFF"
    hero_bg = "#1A1A1A"
else:
    bg_app = "#F4F7FB"
    bg_card = "#FFFFFF"
    text_main = "#1E293B"
    text_sub = "#475569"
    border_col = "#E2E8F0"
    hero_bg = "linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%)"

# Estilos CSS personalizados
st.markdown(
    f"""
    <style>
    /* Fondo general y tipografía */
    [data-testid="stAppViewContainer"] {{
        background-color: {bg_app};
        color: {text_main};
    }}
    
    /* Encabezado Hero */
    .hero-box {{
        background: {hero_bg};
        color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
        border: {"2px solid #FFFFFF" if alto_contraste else "none"};
    }}
    .hero-title {{
        font-size: 1.9rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }}
    .hero-sub {{
        font-size: 0.95rem;
        opacity: 0.92;
        margin-top: 0.3rem;
        margin-bottom: 0.8rem;
    }}
    .badge {{
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.4rem;
    }}

    /* Tarjetas de sección */
    .section-card {{
        background-color: {bg_card};
        border: 1px solid {border_col};
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}
    .section-title {{
        font-size: 1.15rem;
        font-weight: 700;
        color: {text_main};
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }}

    /* Botón principal */
    .stButton>button[kind="primary"] {{
        min-height: 3.6rem;
        font-size: 1.15rem;
        font-weight: 700;
        border-radius: 14px;
        background: {"#FFD600" if alto_contraste else "#2563EB"};
        color: {"#000000" if alto_contraste else "#FFFFFF"};
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
        transition: transform 0.1s ease-in-out;
    }}
    .stButton>button[kind="primary"]:hover {{
        transform: translateY(-1px);
    }}

    /* Banner de diagnóstico */
    .result-banner {{
        border-left: 8px solid var(--c);
        background-color: {bg_card};
        border-top: 1px solid {border_col};
        border-right: 1px solid {border_col};
        border-bottom: 1px solid {border_col};
        padding: 1.2rem;
        border-radius: 14px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }}
    .riesgo-titulo {{
        font-size: 1.65rem;
        font-weight: 800;
        color: var(--c);
        margin-bottom: 0.4rem;
    }}
    .resumen-texto {{
        font-size: 1.05rem;
        color: {text_main};
        line-height: 1.45;
        margin: 0;
    }}

    /* Tarjetas métricas */
    .mini-metric {{
        background-color: {bg_card};
        border: 1px solid {border_col};
        border-radius: 12px;
        padding: 0.8rem;
        text-align: center;
    }}
    .mini-metric-label {{
        font-size: 0.8rem;
        color: {text_sub};
        text-transform: uppercase;
        font-weight: 600;
    }}
    .mini-metric-val {{
        font-size: 1.3rem;
        font-weight: 800;
        color: {text_main};
        margin-top: 0.2rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Encabezado principal
st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">♿ RutaAccesible IA</div>
        <div class="hero-sub">Asistente urbano multimodal para movilidad segura e inclusiva</div>
        <span class="badge">🌍 ODS 10 · Reducción de Desigualdades</span>
        <span class="badge">🏙️ ODS 11 · Ciudades Sostenibles</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("⚠️ Evaluación orientativa impulsada por Google Gemini. No sustituye su criterio ni acompañamiento.")

tab_eval, tab_hist = st.tabs(["📍 Nueva Evaluación", "📋 Historial y Reportes"])

with tab_eval:
    # Tarjeta 1: Imagen
    st.markdown('<div class="section-card"><div class="section-title">📸 1. Captura o sube el entorno peatonal</div>', unsafe_allow_html=True)
    foto = st.camera_input("Usar cámara", label_visibility="collapsed")
    if foto is None:
        foto = st.file_uploader("O selecciona una imagen desde tu galería", type=["jpg", "jpeg", "png", "webp"])
    st.markdown("</div>", unsafe_allow_html=True)

    # Tarjeta 2: Voz y Texto
    st.markdown('<div class="section-card"><div class="section-title">🎙️ 2. Describe o dicta el obstáculo</div>', unsafe_allow_html=True)
    audio = st.audio_input("Dictar por voz")
    c_txt, c_lug = st.columns([3, 2])
    with c_txt:
        texto = st.text_input("Descripción escrita", placeholder="Ej. Auto bloqueando la rampa")
    with c_lug:
        lugar = st.text_input("Ubicación (opcional)", placeholder="Ej. Av. Juárez")
    st.markdown("</div>", unsafe_allow_html=True)

    # Botón de acción
    if st.button("🔍 Evaluar Accesibilidad Ahora", type="primary", use_container_width=True):
        if not (foto or audio or texto):
            st.warning("Por favor toma una foto, dicta un audio o escribe una descripción para comenzar.")
        else:
            with st.spinner("Analizando infraestructura urbana con Gemini..."):
                res, modelo_usado = evaluar_accesibilidad_urbana(
                    io.BytesIO(foto.getvalue()) if foto else None,
                    descripcion_texto=texto or None,
                    audio_bytes=audio.getvalue() if audio else None,
                    modelo=modelo_sel,
                    usar_respaldo=usar_respaldo,
                )
            if isinstance(res, str):
                st.error(res)
            elif not res.informacion_suficiente:
                st.warning(
                    "Información insuficiente: la imagen o descripción no permite evaluar un entorno peatonal con seguridad. "
                    "Intenta acercarte más o mejorar la iluminación."
                )
            else:
                try:
                    buf = io.BytesIO()
                    gTTS(res.mensaje_audio, lang="es", tld="com.mx").write_to_fp(buf)
                    voz = buf.getvalue()
                except Exception:
                    voz = None

                st.session_state.ultimo = (res, voz, modelo_usado)
                st.session_state.historial.append({
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Lugar": lugar or "No especificado",
                    "Riesgo": res.nivel_riesgo.value,
                    "Rampa": "Sí" if res.cuenta_con_rampa else "No",
                    "Silla de ruedas": "Sí" if res.accesible_silla_ruedas else "No",
                    "Obstáculos": "; ".join(res.obstaculos) if res.obstaculos else "Ninguno",
                    "Alerta": res.mensaje_audio,
                    "Modelo": modelo_usado,
                })

    # Presentación de resultados
    if st.session_state.ultimo:
        res, voz, modelo_usado = st.session_state.ultimo
        nivel = res.nivel_riesgo.value
        colores = {"Bajo": "#16A34A", "Medio": "#D97706", "Alto": "#DC2626"}
        iconos = {"Bajo": "🟢", "Medio": "🟡", "Alto": "🔴"}

        st.markdown(
            f"""
            <div class="result-banner" style="--c:{colores[nivel]}">
                <div class="riesgo-titulo">{iconos[nivel]} Nivel de Riesgo: {nivel.upper()}</div>
                <p class="resumen-texto">{res.resumen}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Métricas visuales en 3 columnas
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(
                f'<div class="mini-metric"><div class="mini-metric-label">Rampa</div>'
                f'<div class="mini-metric-val">{"✅ Sí" if res.cuenta_con_rampa else "❌ No"}</div></div>',
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f'<div class="mini-metric"><div class="mini-metric-label">Silla de ruedas</div>'
                f'<div class="mini-metric-val">{"✅ Apta" if res.accesible_silla_ruedas else "⛔ No apta"}</div></div>',
                unsafe_allow_html=True,
            )
        with m3:
            st.markdown(
                f'<div class="mini-metric"><div class="mini-metric-label">Confianza IA</div>'
                f'<div class="mini-metric-val">{res.confianza:.0%}</div></div>',
                unsafe_allow_html=True,
            )

        st.write("")

        # Alerta sonora destacada
        st.info(f"🔊 **Alerta de navegación:** {res.mensaje_audio}")
        if voz:
            st.audio(voz, format="audio/mp3", autoplay=True)

        # Detalles en dos columnas
        col_obs, col_rec = st.columns(2)
        with col_obs:
            st.markdown('<div class="section-card"><div class="section-title">🚧 Obstáculos detectados</div>', unsafe_allow_html=True)
            for o in res.obstaculos or ["Ningún obstáculo crítico detectado"]:
                st.write(f"• {o}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_rec:
            st.markdown('<div class="section-card"><div class="section-title">🧭 Recomendaciones</div>', unsafe_allow_html=True)
            for r in res.recomendaciones:
                st.write(f"• {r}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.caption(f"Procesado con **{modelo_usado}**")

with tab_hist:
    st.markdown('<div class="section-card"><div class="section-title">📊 Bitácora de puntos evaluados</div>', unsafe_allow_html=True)
    if not st.session_state.historial:
        st.info("Aún no has realizado evaluaciones en esta sesión. Ve a la pestaña «Nueva Evaluación» para comenzar.")
    else:
        df = pd.DataFrame(st.session_state.historial)
        st.dataframe(df, use_container_width=True, hide_index=True)

        c_dl, c_clr = st.columns([2, 1])
        with c_dl:
            st.download_button(
                "⬇️ Exportar bitácora en CSV",
                df.to_csv(index=False).encode("utf-8-sig"),
                "reporte_ruta_accesible.csv",
                "text/csv",
                use_container_width=True,
            )
        with c_clr:
            if st.button("🗑️ Limpiar historial", use_container_width=True):
                st.session_state.historial = []
                st.session_state.ultimo = None
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)