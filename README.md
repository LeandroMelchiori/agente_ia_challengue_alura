# 🤖 TechRetAI — Asistente RAG Corporativo

[![Deploy a OCI](https://github.com/LeandroMelchiori/techretai_asistente_rag_corporativo/actions/workflows/deploy.yml/badge.svg)](https://github.com/LeandroMelchiori/techretai_asistente_rag_corporativo/actions/workflows/deploy.yml)

> **TechRetAI** es un proyecto demostrativo que simula el asistente conversacional
> interno de TechRetail Solutions S.R.L. Responde preguntas de los colaboradores
> basándose en documentación corporativa ficticia y muestra las fuentes utilizadas.

**TechRetail Solutions S.R.L.** representa una plataforma SaaS de e-commerce para
PyMEs y emprendedores en Argentina. El asistente ingiere documentación interna en
**8 formatos distintos**, la indexa en una base vectorial y responde mediante
**RAG** (*Retrieval-Augmented Generation*), incorporando mecanismos para reducir
respuestas no fundamentadas y rechazar consultas cuando no encuentra contexto
suficientemente relevante.

---

## 🌐 En producción

**TechRetAI está desplegado y accesible en vivo:** **[https://techretai.sachadev.me](https://techretai.sachadev.me)**

![TechRetAI en producción sobre OCI](docs/img/demo_agente.png)

> Desplegado en una VM de **Oracle Cloud Infrastructure** (Always Free), servido
> por Streamlit detrás de **Caddy** (HTTPS con certificado de Let's Encrypt) y
> actualizado automáticamente vía **GitHub Actions** en cada push a `main`.

---

## ✨ Características

- **Multi-formato:** procesa PDF, Word (`.docx`), Excel (`.xlsx`), PowerPoint
  (`.pptx`), Markdown, CSV, JSON y HTML.
- **Multi-dominio:** documentos organizados por área (RH, Financiero, Legal,
  Operacional, Comercial, Estratégico, Datos y Sistemas).
- **RAG completo:** extracción → limpieza → *chunking* → *embeddings* → base
  vectorial → recuperación semántica → generación con citación de fuentes.
- **Control de respuestas no fundamentadas:** si ningún fragmento supera el
  umbral de relevancia, el agente informa que no encontró la respuesta en vez de
  solicitar una generación sin contexto suficiente.
- **Citación de fuentes:** cada respuesta indica los documentos utilizados.
- **Proveedor intercambiable:** Google Gemini (por defecto) u OpenAI, cambiando
  una sola variable de entorno.
- **Interfaz de chat:** múltiples conversaciones con historial de sesión, creación,
  renombrado y eliminación, preguntas de ejemplo, fuentes y feedback.
- **Registro de ejecución:** consultas, relevancia, fuentes, latencia y feedback en
  formato JSON Lines para auditoría y análisis.
- **Desplegado en OCI:** ejecución como servicio `systemd` en una VM.
- **CI/CD:** despliegue automático mediante GitHub Actions con cada push a `main`.

---

## 🏗️ Arquitectura

```text
documentos/                 scripts/ingest.py            src/agent.py
┌───────────────┐          ┌──────────────────┐        ┌───────────────────┐
│ PDF Word XLSX │          │ 1. Extracción    │        │ 4. Recuperación   │
│ PPTX MD CSV   │  ──────► │ 2. Limpieza      │ ─────► │ 5. Generación +   │
│ JSON HTML     │          │ 3. Chunking +    │ Chroma │    citación de    │
│ (7 categorías)│          │    embeddings    │  DB    │    fuentes        │
└───────────────┘          └──────────────────┘        └───────────────────┘
                                                               │
                                                      app/streamlit_app.py
                                                        (interfaz de chat)
```

Cada componente del pipeline vive en un módulo con una única responsabilidad:

| Fase del pipeline | Dónde está en el código |
|---|---|
| Colecta y organización | `documentos/` + `scripts/generar_documentos.py` |
| Proceso y extracción | `src/ingestion/loaders.py`, `src/ingestion/chunking.py` |
| Indexación | `src/vectorstore.py`, `scripts/ingest.py` |
| Recuperación RAG | `src/vectorstore.py::query`, `src/agent.py` |
| Generación y fallback | `src/agent.py` |
| Proveedores de IA | `src/providers.py` |
| Interfaz | `app/streamlit_app.py` |
| Despliegue en OCI | `docs/deploy_oci.md`, `deploy/techretai.service`, `Dockerfile` |
| CI/CD | `.github/workflows/deploy.yml` |
| Registro de ejecución | `src/logging_utils.py`, `logs/consultas.jsonl` |

---

## 🚀 Puesta en marcha local

### 1. Requisitos

- Python 3.11+
- Una API key de [Google AI Studio](https://aistudio.google.com/app/apikey)
  **o** de [OpenAI](https://platform.openai.com/api-keys).

### 2. Instalación

```bash
git clone https://github.com/LeandroMelchiori/techretai_asistente_rag_corporativo.git
cd techretai_asistente_rag_corporativo

python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate      # Windows

pip install -r requirements.txt
cp .env.example .env
```

Completá en `.env` la API key del proveedor elegido.

### 3. Generar los documentos e indexarlos

```bash
python -m scripts.generar_documentos
python -m scripts.ingest --reset
```

### 4. Usar el agente

```bash
# Interfaz de chat
streamlit run app/streamlit_app.py

# Consulta desde terminal
python -m scripts.preguntar "¿Cuántos días de vacaciones me corresponden?"
```

---

## 💬 Preguntas de ejemplo

- *¿Cuántos días de vacaciones me corresponden con 6 años de antigüedad?* (RH)
- *¿Qué comisión cobra MercadoPago por tarjeta de crédito?* (Financiero)
- *¿Cuánto cuesta el plan Growth?* (Comercial)
- *¿Cómo funciona la facturación automática contra ARCA?* (Operacional)
- *¿Qué datos personales recolecta la empresa?* (Legal)
- *¿Qué endpoints tiene la API de TechRetail?* (Datos y Sistemas)

---

## ⚙️ Configuración

Todas las opciones se controlan por variables de entorno definidas en
`.env.example`.

| Variable | Por defecto | Descripción |
|---|---:|---|
| `LLM_PROVIDER` | `gemini` | Proveedor: `gemini` u `openai` |
| `TOP_K` | `5` | Fragmentos recuperados por consulta |
| `MIN_RELEVANCE` | `0.25` | Umbral mínimo de relevancia |
| `CHUNK_SIZE` | `800` | Tamaño de cada fragmento |

---

## 📁 Estructura del proyecto

```text
techretai_asistente_rag_corporativo/
├── documentos/                # Base ficticia: 8 formatos y 7 categorías
├── src/
│   ├── config.py              # Configuración central
│   ├── providers.py           # Gemini/OpenAI: LLM y embeddings
│   ├── ingestion/             # Extracción, limpieza y chunking
│   ├── vectorstore.py         # Base vectorial ChromaDB
│   ├── agent.py               # Orquestación RAG, fuentes y fallback
│   └── logging_utils.py       # Registro de ejecución
├── scripts/
│   ├── generar_documentos.py  # Documentación corporativa ficticia
│   ├── ingest.py              # Indexación
│   └── preguntar.py           # Cliente CLI
├── app/streamlit_app.py       # Interfaz de chat
├── docs/deploy_oci.md         # Guía de despliegue
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## ☁️ Despliegue en OCI

El agente está desplegado en **Oracle Cloud Infrastructure**, sobre una VM
Compute (Always Free), donde corre como servicio `systemd`. El pipeline de
**GitHub Actions** actualiza automáticamente la aplicación con cada push a
`main`.

La guía completa está disponible en [`docs/deploy_oci.md`](docs/deploy_oci.md).

También puede ejecutarse con Docker:

```bash
docker build -t techretai-agente .
docker run -p 8501:8501 --env-file .env techretai-agente
```

---

## 🧪 Datos y alcance

Todos los documentos incluidos en `documentos/` son **datos ficticios**, creados
exclusivamente para demostrar el funcionamiento del asistente. No representan
información real de una empresa ni contienen datos personales reales.

TechRetAI es actualmente una demostración funcional. No debe utilizarse para
procesar documentación corporativa sensible sin implementar previamente los
controles de acceso, privacidad, seguridad y evaluación detallados en la hoja de
ruta.

---

# 🗺️ Hoja de ruta

La evolución del proyecto está organizada por prioridad. El objetivo no es solo
agregar funciones, sino convertir la demostración en un sistema RAG medible,
seguro, observable y defendible técnicamente.

## Fase 1 — Calidad y evaluación del RAG

- [ ] Crear un conjunto de evaluación versionado con preguntas, categorías,
  documentos esperados, respuestas de referencia y casos que deben activar el
  fallback.
- [ ] Medir **Hit Rate@K**, **Recall@K**, **Precision@K** y **MRR** para evaluar la
  recuperación de fragmentos.
- [ ] Evaluar si la respuesta se encuentra fundamentada en el contexto
  recuperado (*groundedness*).
- [ ] Medir la exactitud de las fuentes mostradas al usuario.
- [ ] Medir falsos positivos y falsos negativos del fallback.
- [ ] Registrar latencia por etapa: embedding, recuperación y generación.
- [ ] Estimar tokens y costo por consulta para cada proveedor.
- [ ] Incorporar pruebas de regresión para evitar que un cambio de chunking,
  modelo o prompt reduzca la calidad.
- [ ] Ejecutar evaluaciones automáticamente en CI con un subconjunto estable de
  casos.

## Fase 2 — Pruebas automatizadas y calidad de código

- [ ] Agregar pruebas unitarias para loaders, limpieza, chunking, configuración,
  vectorstore y armado de contexto.
- [ ] Mockear proveedores de embeddings y generación para evitar consumo de API
  durante las pruebas.
- [ ] Agregar pruebas de integración del pipeline completo con una colección
  Chroma temporal.
- [ ] Probar archivos vacíos, corruptos, duplicados y formatos no soportados.
- [ ] Probar consultas sin documentos indexados y errores de proveedor.
- [ ] Incorporar `pytest`, cobertura mínima y reporte en GitHub Actions.
- [ ] Agregar linting, formateo y validación de tipos con herramientas como Ruff,
  Black y mypy.

## Fase 3 — Seguridad frente a prompt injection

- [ ] Tratar el contenido recuperado como **datos no confiables**, nunca como
  instrucciones para el modelo.
- [ ] Reforzar el prompt para ignorar órdenes incluidas dentro de documentos.
- [ ] Crear pruebas contra *prompt injection* directo e indirecto.
- [ ] Probar intentos de revelar el prompt del sistema, claves, configuración y
  datos de otras conversaciones.
- [ ] Detectar y marcar documentos con instrucciones sospechosas durante la
  ingestión.
- [ ] Limitar el tamaño del contexto y sanear contenido antes de enviarlo al LLM.
- [ ] Documentar el modelo de amenazas del sistema.

## Fase 4 — Autenticación y autorización

- [ ] Incorporar autenticación de usuarios.
- [ ] Implementar roles y permisos por área documental.
- [ ] Aplicar filtros de autorización durante la recuperación, no solamente en la
  interfaz.
- [ ] Registrar quién realizó cada consulta sin exponer información innecesaria.
- [ ] Agregar cierre de sesión, expiración y protección de sesiones.
- [ ] Implementar rate limiting y cuotas por usuario.
- [ ] Preparar una cuenta de demostración separada del entorno administrativo.

## Fase 5 — Privacidad y gestión segura de logs

- [ ] Evitar guardar preguntas y respuestas completas por defecto.
- [ ] Incorporar anonimización y redacción de emails, teléfonos, documentos y
  otros datos personales.
- [ ] Permitir desactivar el registro de contenido mediante configuración.
- [ ] Definir políticas de retención y eliminación de logs.
- [ ] Implementar rotación de archivos y permisos restrictivos.
- [ ] Separar logs técnicos, métricas y auditoría de usuario.
- [ ] Informar de forma transparente qué datos se registran.

## Fase 6 — Manejo de errores y resiliencia

- [ ] Reemplazar excepciones técnicas visibles por mensajes seguros para el
  usuario.
- [ ] Registrar internamente el detalle y un identificador de incidente.
- [ ] Agregar timeouts, reintentos con backoff y circuit breaker para proveedores.
- [ ] Implementar fallback entre Gemini y OpenAI cuando corresponda.
- [ ] Incorporar health checks para aplicación, vectorstore y proveedor.
- [ ] Probar recuperación ante reinicios y fallos parciales.

## Fase 7 — Citaciones verificables

- [ ] Guardar página de PDF, hoja de Excel, diapositiva, sección y posición del
  fragmento durante la ingestión.
- [ ] Mostrar el extracto exacto que fundamenta cada respuesta.
- [ ] Permitir abrir la fuente en la ubicación correspondiente.
- [ ] Diferenciar claramente fuente recuperada de interpretación generada.
- [ ] Detectar respuestas con afirmaciones no respaldadas por una cita.

## Fase 8 — Mejora de recuperación

- [ ] Comparar diferentes tamaños y solapamientos de chunks mediante evaluación.
- [ ] Incorporar búsqueda híbrida: similitud vectorial + coincidencia léxica/BM25.
- [ ] Evaluar un reranker para reordenar los fragmentos recuperados.
- [ ] Implementar eliminación de fragmentos redundantes.
- [ ] Recuperar ventanas de contexto alrededor del fragmento relevante.
- [ ] Explorar reformulación y expansión de consultas ambiguas.
- [ ] Versionar índices según modelo de embeddings y configuración.
- [ ] Implementar reindexación incremental y detección de documentos modificados.

## Fase 9 — Observabilidad y analítica

- [ ] Crear un panel con volumen de consultas, latencia, fallback, feedback y
  errores.
- [ ] Medir calidad por categoría documental.
- [ ] Identificar preguntas frecuentes y vacíos de documentación.
- [ ] Exportar métricas en un formato compatible con herramientas de monitoreo.
- [ ] Agregar alertas por fallos, aumento de latencia o caída en la calidad.
- [ ] Relacionar cada respuesta con la versión del prompt, índice y modelo usados.

## Fase 10 — Persistencia y experiencia de usuario

- [ ] Persistir conversaciones por usuario en una base de datos.
- [ ] Permitir búsqueda, archivado y exportación de conversaciones.
- [ ] Implementar filtros visibles por área documental.
- [ ] Mejorar accesibilidad, navegación por teclado y experiencia móvil.
- [ ] Incorporar estados de carga por etapa y cancelación de consultas.
- [ ] Permitir feedback detallado y corrección sugerida por el usuario.

## Fase 11 — Administración documental

- [ ] Crear una interfaz segura para subir, revisar y eliminar documentos.
- [ ] Validar tipo, tamaño y contenido de los archivos.
- [ ] Mostrar estado de procesamiento e indexación.
- [ ] Gestionar versiones y trazabilidad documental.
- [ ] Permitir reindexación selectiva por documento o categoría.
- [ ] Incorporar análisis antivirus o aislamiento para archivos no confiables.

## Fase 12 — Evolución de infraestructura

- [ ] Separar interfaz, servicio RAG y tareas de ingestión.
- [ ] Incorporar una API backend para desacoplar Streamlit del núcleo.
- [ ] Gestionar secretos mediante un servicio seguro de OCI o GitHub Environments.
- [ ] Agregar backups y restauración de la base vectorial.
- [ ] Crear ambientes separados de desarrollo, prueba y producción.
- [ ] Añadir despliegues con rollback y verificación posterior.
- [ ] Evaluar OCI Generative AI como tercer proveedor.

---

## Criterios para considerar una versión apta para uso interno

Antes de procesar documentos corporativos reales, el proyecto deberá contar como
mínimo con:

- autenticación y permisos por documento o área;
- evaluación automática y métricas mínimas definidas;
- pruebas contra prompt injection;
- logs con privacidad y retención controlada;
- citaciones precisas y verificables;
- manejo seguro de errores;
- backups, monitoreo y procedimiento de recuperación;
- revisión legal y de protección de datos aplicable al contexto de uso.

---

## 📝 Licencia y autoría

Proyecto académico y demostrativo desarrollado por **Leandro Melchiori**.

El nombre TechRetail Solutions S.R.L. y toda la documentación corporativa del
repositorio se utilizan como escenario ficticio para demostrar la arquitectura y
el funcionamiento del asistente.
