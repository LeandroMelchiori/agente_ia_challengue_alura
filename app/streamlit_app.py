"""
Interfaz de chat del agente TechRetAI.

Chat web con estilo "asistente de IA": varias conversaciones con historial en
la barra lateral, marca propia, preguntas de ejemplo, fuentes citadas y feedback.

Nota: las conversaciones viven en la sesión del navegador (se pierden al recargar
o reiniciar el servidor). Alcanza para el uso conversacional dentro de una visita.

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
    .marca {{ font-size: 2.5rem; font-weight: 800; line-height: 1.1; margin-bottom: .2rem; }}
    .marca .ai {{ color: {ACCENT}; }}
    .subt {{ color: #9AA0A6; font-size: 1.02rem; margin-bottom: .3rem; }}
    div[data-testid="stButton"] > button {{
        text-align: left; border: 1px solid #2A2F3A; background: #161A23;
        border-radius: 10px; padding: .55rem .8rem; font-weight: 500;
        transition: border-color .15s ease; white-space: nowrap; overflow: hidden;
        text-overflow: ellipsis;
    }}
    div[data-testid="stButton"] > button:hover {{ border-color: {ACCENT}; color: {ACCENT}; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
#  Estado: varias conversaciones
# --------------------------------------------------------------------------
def nueva_conversacion() -> int:
    cid = st.session_state.contador
    st.session_state.contador += 1
    st.session_state.conversaciones[cid] = {"titulo": "Nueva conversación", "mensajes": []}
    st.session_state.conv_actual = cid
    return cid


if "conversaciones" not in st.session_state:
    st.session_state.conversaciones = {}
    st.session_state.contador = 0
    nueva_conversacion()


def conv_actual() -> dict:
    return st.session_state.conversaciones[st.session_state.conv_actual]


# --------------------------------------------------------------------------
#  Procesamiento de una pregunta (sobre la conversación activa)
# --------------------------------------------------------------------------
def procesar(pregunta: str) -> None:
    conv = conv_actual()
    conv["mensajes"].append({"rol": "user", "texto": pregunta})
    # La primera pregunta le da título a la conversación.
    if conv["titulo"] == "Nueva conversación":
        conv["titulo"] = pregunta[:38] + ("…" if len(pregunta) > 38 else "")
    try:
        settings.validate()
        resp = responder(pregunta)
        registrar(resp)
    except Exception as e:  # noqa: BLE001
        conv["mensajes"].append(
            {"rol": "assistant", "texto": f"⚠️ Ocurrió un error: {e}", "fuentes": []}
        )
        st.rerun()
        return
    conv["mensajes"].append(
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
#  Barra lateral: marca + lista de conversaciones + estado
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"### 🤖 TechRet<span style='color:{ACCENT}'>AI</span>", unsafe_allow_html=True
    )
    st.caption("Asistente corporativo de TechRetail Solutions")

    if st.button("➕  Nueva conversación", use_container_width=True):
        nueva_conversacion()
        st.rerun()

    st.markdown("**Conversaciones**")
    # Más recientes primero.
    for cid in reversed(list(st.session_state.conversaciones.keys())):
        conv = st.session_state.conversaciones[cid]
        activa = cid == st.session_state.conv_actual
        etiqueta = ("🟢 " if activa else "💬 ") + conv["titulo"]
        if st.button(etiqueta, key=f"conv_{cid}", use_container_width=True):
            st.session_state.conv_actual = cid
            st.rerun()

    st.divider()
    st.markdown("**Estado**")
    st.caption(f"Modelo: `{settings.provider}`")
    try:
        st.caption(f"Documentos indexados: **{vectorstore.stats()['fragmentos']}** fragmentos")
    except Exception:
        st.caption("Base de conocimiento: (no inicializada)")

    st.divider()
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

conv = conv_actual()

# Pantalla de bienvenida con ejemplos (solo si la conversación está vacía).
if not conv["mensajes"]:
    st.markdown("##### 💡 Probá con una de estas preguntas")
    cols = st.columns(2)
    for i, ejemplo in enumerate(EJEMPLOS):
        if cols[i % 2].button(ejemplo, key=f"ej_{i}", use_container_width=True):
            procesar(ejemplo)

# Historial de la conversación activa.
for i, msg in enumerate(conv["mensajes"]):
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
        if msg["rol"] == "assistant" and msg.get("respuesta_obj") and not msg.get("feedback_dado"):
            c1, c2, _ = st.columns([1, 1, 8])
            cid = st.session_state.conv_actual
            if c1.button("👍", key=f"up_{cid}_{i}"):
                registrar(msg["respuesta_obj"], feedback="positivo")
                conv["mensajes"][i]["feedback_dado"] = True
                st.toast("¡Gracias por tu feedback!")
                st.rerun()
            if c2.button("👎", key=f"down_{cid}_{i}"):
                registrar(msg["respuesta_obj"], feedback="negativo")
                conv["mensajes"][i]["feedback_dado"] = True
                st.toast("Feedback registrado, lo tendremos en cuenta.")
                st.rerun()


# --------------------------------------------------------------------------
#  Entrada del usuario
# --------------------------------------------------------------------------
pregunta = st.chat_input("Escribí tu pregunta...")
if pregunta:
    procesar(pregunta)
