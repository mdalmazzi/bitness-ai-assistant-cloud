from __future__ import annotations

import os
import time
import streamlit as st

from ui.styles import inject_css
from ui.layout import (
    render_hero,
    render_intro_cards,
    render_metrics,
    render_quick_questions,
    render_empty_chat_hint,
    render_sources,
)
# =========================
# STREAMLIT CLOUD / SECRETS
# =========================

try:
    if "OPENAI_API_KEY" in st.secrets and not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = str(st.secrets["OPENAI_API_KEY"])
except Exception:
    pass


def _truthy(value) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _setting_bool(name: str, default: str = "0") -> bool:
    value = os.getenv(name, None)
    if value is None:
        try:
            value = st.secrets.get(name, default)
        except Exception:
            value = default
    return _truthy(value)


from backend import rag_engine

# =========================
# MODALITÀ AVVIO
# =========================
# BITNESS_CLIENT_DEMO=1
# - usa il backend RAG reale
# - nasconde dettagli tecnici da presentazione cliente
# - rinomina i controlli in linguaggio prodotto

CLIENT_DEMO = _setting_bool("BITNESS_CLIENT_DEMO", "0")
SHOW_TECH = _setting_bool("BITNESS_SHOW_TECH", "0")

st.set_page_config(page_title="Bitness AI Assistant", layout="wide")
inject_css(st, client_demo=CLIENT_DEMO)

# =========================
# SESSION STATE
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_sources" not in st.session_state:
    st.session_state.last_sources = []

if "rag_index" not in st.session_state:
    st.session_state.rag_index = None


def _source_to_dict(source):
    return {
        "title": getattr(source, "title", "Fonte"),
        "document": getattr(source, "document", "Documento"),
        "snippet": getattr(source, "snippet", ""),
        "score": getattr(source, "score", None),
        "page": getattr(source, "page", None),
    }


def _render_inline_sources(sources):
    """Mostra le fonti dentro la singola risposta, senza blocco separato a fondo pagina."""
    if not sources:
        return

    with st.expander("Riferimenti nei materiali"):
        for i, source in enumerate(sources, start=1):
            title = source.get("title") or f"Fonte {i}"
            document = source.get("document") or "Documento"
            page = source.get("page")
            snippet = source.get("snippet") or ""

            label = f"**Fonte {i}** — {document}"
            if page:
                label += f", pagina {page}"

            st.markdown(label)
            if snippet:
                st.caption(snippet[:900])
            if i < len(sources):
                st.divider()

# =========================
# MODALITÀ / STATO RAG
# =========================

# In modalità cliente il backend resta reale, ma sparisce tutta la sidebar:
# niente upload, niente metriche tecniche, niente pulsanti di preparazione.
# La demo cliente si lancia dopo aver già preparato documenti e indice in modalità tecnica.
if CLIENT_DEMO:
    smart_mode = True
    debug_mode = False

    try:
        if st.session_state.rag_index is None:
            st.session_state.rag_index = rag_engine.load_existing_index()
        kb_state = rag_engine.get_kb_state()
    except Exception as exc:
        kb_state = {"ready": False, "documents": 0, "chunks": 0, "mode_label": "RAG reale"}
        if SHOW_TECH:
            st.error("Assistente non disponibile.")
            st.caption(str(exc))

else:
    with st.sidebar:
        st.markdown("## Bitness Assistant")
        st.caption("Area tecnica: caricamento documenti, indicizzazione e controllo del RAG.")

        smart_mode = st.toggle(
            "Smart retrieval",
            value=True,
            help="Abilita multi-query e reranker per migliorare la qualità del retrieval.",
        )
        debug_mode = st.toggle(
            "Debug retrieval",
            value=False,
            help="Mostra le query generate e informazioni tecniche utili durante lo sviluppo.",
        )

        st.divider()
        st.markdown("### Knowledge Base")

        uploaded_files = st.file_uploader(
            "Carica documenti reali",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True,
            help="I file vengono salvati in data/ e indicizzati in ChromaDB.",
        )

        try:
            if uploaded_files:
                saved = rag_engine.save_uploaded_files(uploaded_files)
                if saved > 0:
                    st.success(f"Salvati {saved} nuovi file. Ora aggiorna la Knowledge Base.")
                else:
                    st.info("I documenti erano già presenti.")

            if st.button("Crea / aggiorna Knowledge Base", use_container_width=True):
                with st.spinner("Indicizzazione documenti in corso..."):
                    st.session_state.rag_index = rag_engine.create_or_rebuild_index()
                if st.session_state.rag_index is not None:
                    st.success("Knowledge Base aggiornata.")
                else:
                    st.warning("Nessun documento leggibile trovato.")

            if st.session_state.rag_index is None:
                st.session_state.rag_index = rag_engine.load_existing_index()

            kb_state = rag_engine.get_kb_state()
            existing_files = rag_engine.get_existing_files()

            if existing_files:
                with st.expander("Documenti caricati"):
                    for file in existing_files:
                        st.write(f"- {file.name}")

        except Exception as exc:
            kb_state = {"ready": False, "documents": 0, "chunks": 0, "mode_label": "RAG reale"}
            st.error("Backend RAG non disponibile.")
            st.caption(str(exc))

        render_metrics(kb_state)

        st.divider()
        if st.button("Svuota chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_sources = []
            st.rerun()

        if st.button("Svuota documenti e indice", use_container_width=True):
            rag_engine.clear_knowledge_base()
            st.session_state.rag_index = None
            st.session_state.messages = []
            st.session_state.last_sources = []
            st.rerun()

# =========================
# MAIN UI
# =========================

render_hero(client_demo=CLIENT_DEMO)

# In modalità Demo Reale la pagina deve sembrare prodotto, non pannello tecnico.
# Quindi nascondiamo le card di onboarding e lasciamo solo chat + fonti integrate nella risposta.
if not CLIENT_DEMO:
    render_intro_cards("RAG reale")
    st.write("")

if not kb_state.get("ready"):
    if CLIENT_DEMO:
        st.warning(
            "Assistente non ancora preparato. Apri prima la modalità tecnica, carica i documenti e prepara l’assistente."
        )
    else:
        st.warning(
            "Per fare una demo reale: carica almeno un documento, clicca 'Crea / aggiorna Knowledge Base', "
            "poi fai una domanda sui contenuti caricati."
        )

# Le domande demo restano utili in modalità tecnica.
# In modalità cliente le togliamo per evitare l'effetto mockup/prototipo.
selected_quick_question = None if CLIENT_DEMO else render_quick_questions()

if not CLIENT_DEMO:
    st.divider()

if not st.session_state.messages:
    render_empty_chat_hint(client_demo=CLIENT_DEMO)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if CLIENT_DEMO and message.get("role") == "assistant":
            _render_inline_sources(message.get("sources", []))

question = st.chat_input("Scrivi una domanda sui materiali" if CLIENT_DEMO else "Fai una domanda sui documenti reali")
if selected_quick_question:
    question = selected_quick_question

# =========================
# ANSWER FLOW
# =========================

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Mostriamo subito lo stato di attesa dentro la chat, non in alto a destra.
    # Il backend resta identico: cambia solo la percezione durante l'attesa.
    with st.chat_message("assistant"):
        placeholder = st.empty()

        waiting_text = (
            "Sto consultando i materiali e preparando una risposta verificabile..."
            if CLIENT_DEMO
            else "Elaborazione in corso: retrieval, reranking e generazione risposta..."
        )

        try:
            with placeholder.container():
                with st.spinner(waiting_text):
                    result = rag_engine.answer_question(
                        question=question,
                        index=st.session_state.rag_index,
                        smart=smart_mode,
                        debug=debug_mode,
                    )

            answer = result.answer
            st.session_state.last_sources = result.sources

            placeholder.empty()
            answer_box = st.empty()

            # Streaming più rapido: dà feedback visivo ma non allunga troppo la demo.
            streamed = ""
            for word in answer.split(" "):
                streamed += word + " "
                answer_box.markdown(streamed)
                time.sleep(0.003 if CLIENT_DEMO else 0.006)
            answer_box.markdown(answer)

            if CLIENT_DEMO:
                _render_inline_sources([_source_to_dict(source) for source in result.sources])

            assistant_message = {"role": "assistant", "content": answer}
            if CLIENT_DEMO:
                assistant_message["sources"] = [_source_to_dict(source) for source in result.sources]
            st.session_state.messages.append(assistant_message)

            if debug_mode and result.debug:
                with st.expander("Debug retrieval"):
                    st.json(result.debug)

        except Exception as exc:
            answer = "Si è verificato un errore durante la generazione della risposta."
            placeholder.empty()
            st.error(answer)
            if not CLIENT_DEMO or SHOW_TECH:
                st.caption(str(exc))
            st.session_state.messages.append({"role": "assistant", "content": answer})

if not CLIENT_DEMO:
    render_sources(st.session_state.last_sources)
