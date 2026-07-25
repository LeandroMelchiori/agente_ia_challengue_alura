"""
Interfaz de chat del agente TechRetAI.

Chat web simple pero cuidado, con:
- Marca del asistente (TechRetAI) y aviso claro de que es un agente de IA.
- Pantalla de bienvenida con preguntas de ejemplo clickeables.
- Historial de conversación dentro de la sesión.
- Visualización de las fuentes/documentos citados en cada respuesta.
- Botones de feedback (👍 / 👎) que quedan registrados en el log.

Ejecutar con:  streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Permite importar el paquete src cuando Streamlit ejecuta este archivo.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import vectorstore  # noqa: E402
from src.agent import responder  # noqa: E402
from src.config import settings  # noqa: E402
from src.logging_utils import registrar  # noqa: E402

ACCENT = "#12B5A5"

st.set_page_config(page_title="TechRetAI", page_icon="🤖", layout="centered")

# Preguntas sugeridas para la pantalla de bienvenida (una por área clave).
EJEMPLOS = [
    "¿Cuántos días de vacaciones me corresponden con 6 años de antigüedad?",
    "¿Qué comisión cobra MercadoPago por tarjeta de crédito?",
    "¿Cuánto cuesta el plan Growth y qué incluye?",
    "¿Cómo funciona la facturación automática contra ARCA?",
]


# --------------------------------------------------------------------------
#  Estilos
# --------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    /* Encabezado de marca */
    .marca {{ font-size: 2.5rem; font-weight: 800; line-height: 1.1; margin-bottom: .2rem; }}
    .marca .ai {{ color: {ACCENT}; }}
    .subt {{ color: #9AA0A6; font-size: 1.02rem; margin-bottom: .3rem; }}
    /* Botones de ejemplo con aspecto de "chips" */
    div[data-testid="stButton"] > button {{
        text-align: left; border: 1px solid #2A2F3A; background: #161A23;
        border-radius: 12px; padding: .7rem .9rem; font-weight: 500;
        transition: border-color .15s ease;
    }}
    div[data-testid="stButton"] > button:hover {{
        border-color: {ACCENT}; color: {ACCENT};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
#  Barra lateral
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"### 🤖 TechRet<span class='ai' style='color:{ACCENT}'>AI</span>", unsafe_allow_html=True)
    st.caption("Asistente corporativo de TechRetail Solutions")
    st.divider()

    st.markdown("**Estado**")
    st.caption(f"Modelo: `{settings.provider}`")
    try:
        st.caption(f"Documentos indexados: **{vectorstore.stats()['fragmentos']}** fragmentos")
    except Exception:
        st.caption("Base de conocimiento: (no inicializada)")

    st.divider()
    if st.button("🧹 Nueva conversación", use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()

    st.caption(
        "⚠️ Estás conversando con un **agente de IA**. Las respuestas se basan en "
        "documentos internos y pueden contener errores: verificá en la fuente citada."
    )


# --------------------------------------------------------------------------
#  Encabezado
# --------------------------------------------------------------------------
st.markdown(
    "<div class='marca'>TechRet<span class='ai'>AI</span></div>"
    "<div class='subt'>Preguntá lo que necesites sobre la documentación interna de la empresa.</div>",
    unsafe_allow_html=True,
)
st.write("")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []


# --------------------------------------------------------------------------
#  Procesamiento de una pregunta
# --------------------------------------------------------------------------
def procesar(pregunta: str) -> None:
    st.session_state.mensajes.append({"rol": "user", "texto": pregunta})
    try:
        settings.validate()
        resp = responder(pregunta)
        registrar(resp)  # registro de ejecución
    except Exception as e:  # noqa: BLE001
        st.session_state.mensajes.append(
            {"rol": "assistant", "texto": f"⚠️ Ocurrió un error: {e}", "fuentes": []}
        )
        st.rerun()
        return
    st.session_state.mensajes.append(
        {
            "rol": "assistant",
            "texto": resp.texto,
            "fuentes": resp.fuentes,
            "respuesta_obj": resp,
            "feedback_dado": False,
        }
    )
    st.rerun()


# --------------------------------------------------------------------------
#  Pantalla de bienvenida (solo sin conversación) con preguntas de ejemplo
# --------------------------------------------------------------------------
if not st.session_state.mensajes:
    st.markdown("##### 💡 Probá con una de estas preguntas")
    cols = st.columns(2)
    for i, ejemplo in enumerate(EJEMPLOS):
        if cols[i % 2].button(ejemplo, key=f"ej_{i}", use_container_width=True):
            procesar(ejemplo)


# --------------------------------------------------------------------------
#  Historial de conversación
# --------------------------------------------------------------------------
for i, msg in enumerate(st.session_state.mensajes):
    avatar = "🤖" if msg["rol"] == "assistant" else "🧑"
    with st.chat_message(msg["rol"], avatar=avatar):
        st.markdown(msg["texto"])
        if msg.get("fuentes"):
            with st.expander("📄 Fuentes citadas"):
                for f in msg["fuentes"]:
                    st.markdown(
                        f"- **{f['archivo']}** · _{f['categoria']}_ "
                        f"({f['formato']}) — relevancia {f['relevancia']:.2f}"
                    )
        # Feedback solo en respuestas del asistente aún sin votar.
        if msg["rol"] == "assistant" and msg.get("respuesta_obj") and not msg.get("feedback_dado"):
            c1, c2, _ = st.columns([1, 1, 8])
            if c1.button("👍", key=f"up_{i}"):
                registrar(msg["respuesta_obj"], feedback="positivo")
                st.session_state.mensajes[i]["feedback_dado"] = True
                st.toast("¡Gracias por tu feedback!")
                st.rerun()
            if c2.button("👎", key=f"down_{i}"):
                registrar(msg["respuesta_obj"], feedback="negativo")
                st.session_state.mensajes[i]["feedback_dado"] = True
                st.toast("Feedback registrado, lo tendremos en cuenta.")
                st.rerun()


# --------------------------------------------------------------------------
#  Entrada del usuario
# --------------------------------------------------------------------------
pregunta = st.chat_input("Escribí tu pregunta...")
if pregunta:
    procesar(pregunta)
