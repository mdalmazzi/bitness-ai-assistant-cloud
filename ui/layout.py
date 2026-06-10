from __future__ import annotations

import streamlit as st
from backend.common import Source


def render_hero(client_demo: bool = False):
    """Hero principale.

    In modalità cliente evita parole tecniche come RAG, backend, chunk, indice.
    In modalità tecnica mantiene invece un wording più esplicativo per lo sviluppo.
    """
    if client_demo:
        kicker = "Digital Knowledge Assistant"
        title = "Bitness AI Assistant"
        subtitle = (
            "Interroga documenti, progetti e materiali formativi con risposte chiare, "
            "verificabili e collegate ai contenuti consultati."
        )
        pills = ["Digital learning", "Aziende e PA", "Scuola", "Progetti Erasmus+"]
    else:
        kicker = "Area tecnica"
        title = "Bitness AI Assistant"
        subtitle = (
            "Ambiente tecnico per caricare documenti, preparare l’assistente, testare il motore "
            "documentale e verificare le fonti recuperate."
        )
        pills = ["Documenti reali", "Fonti verificabili", "Smart retrieval", "Controllo tecnico"]

    pills_html = "".join([f'<span class="bitness-pill">{pill}</span>' for pill in pills])

    st.markdown(
        f"""
        <div class="bitness-hero">
            <div class="bitness-hero-content">
                <div class="bitness-kicker">{kicker}</div>
                <div class="bitness-title">{title}</div>
                <div class="bitness-subtitle">{subtitle}</div>
                <div class="bitness-pill-row">{pills_html}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_intro_cards(mode_label: str):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="demo-card">
                <div class="section-title">1. Carica documenti</div>
                <div class="small-muted">PDF, DOCX e TXT diventano materiale interrogabile dalla chat.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="demo-card">
                <div class="section-title">2. Fai domande</div>
                <div class="small-muted">L'utente scrive in linguaggio naturale, senza conoscere la struttura dei file.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="demo-card">
                <div class="section-title">3. Ottieni fonti</div>
                <div class="small-muted">Modalità attiva: <b>{mode_label}</b>. Risposta più passaggi documentali usati.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_metrics(kb_state: dict):
    c1, c2, c3 = st.columns(3)
    c1.metric("Stato", "Ready" if kb_state.get("ready") else "Da creare")
    c2.metric("Documenti", kb_state.get("documents", 0))
    c3.metric("Unità informative", kb_state.get("chunks", 0))


def render_quick_questions() -> str | None:
    st.markdown("#### Domande demo")
    cols = st.columns(3)
    questions = [
        "Che tipo di assistente è questo?",
        "Quali servizi può raccontare dai documenti?",
        "Come vengono mostrate le fonti?",
    ]
    selected = None
    for col, q in zip(cols, questions):
        if col.button(q, use_container_width=True):
            selected = q
    return selected


def render_sources(sources: list[Source]):
    if not sources:
        return
    st.markdown("### Fonti utilizzate")
    for source in sources:
        title = f"{source.title} • {source.document}"
        if source.page:
            title += f" • pagina {source.page}"
        if source.score is not None:
            title += f" • score {source.score}"
        with st.expander(title):
            st.write(source.snippet)


def render_empty_chat_hint(client_demo: bool = False):
    if client_demo:
        st.markdown(
            """
            <div class="client-welcome-card">
                <div class="client-welcome-eyebrow">Assistente pronto</div>
                <div class="client-welcome-title">Come posso aiutarti a consultare i materiali?</div>
                <div class="client-welcome-text">
                    Scrivi una domanda sui documenti caricati. La risposta verrà costruita sui contenuti disponibili
                    e potrai aprire i riferimenti consultati quando desideri verificarli.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="demo-card">
                <div class="section-title">Prova la demo</div>
                <div class="small-muted">
                    Carica un documento o usa una domanda demo. Le risposte arrivano dai documenti indicizzati.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
