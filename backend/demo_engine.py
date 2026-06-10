from __future__ import annotations

from .common import AnswerResult, Source

DEMO_FILES = [
    "Profilo aziendale Bitness.pdf",
    "Servizi e-learning e formazione.docx",
    "Standard SCORM - scheda tecnica.pdf",
]


def get_demo_kb_state(uploaded_count: int = 0) -> dict:
    document_count = len(DEMO_FILES) + uploaded_count
    return {
        "ready": True,
        "documents": document_count,
        "chunks": 128 + uploaded_count * 18,
        "mode_label": "Demo cliente",
    }


def answer_question(question: str) -> AnswerResult:
    q = question.lower().strip()

    if any(word in q for word in ["scorm", "standard", "lms"]):
        answer = (
            "Lo standard SCORM consente di rendere i contenuti e-learning interoperabili con piattaforme LMS diverse. "
            "In una knowledge base aziendale può essere usato per recuperare informazioni tecniche, requisiti di compatibilità, "
            "struttura dei learning object e modalità di tracciamento dell'apprendimento."
        )
        sources = [
            Source(
                title="Standard SCORM",
                document="Standard SCORM - scheda tecnica.pdf",
                page="2",
                score=0.91,
                snippet="SCORM definisce packaging, runtime e interoperabilità dei contenuti formativi digitali con piattaforme LMS.",
            )
        ]
    elif any(word in q for word in ["servizi", "offre", "offerta", "cosa fa"]):
        answer = (
            "Dai documenti demo emerge che Bitness può presentarsi come partner per formazione digitale, e-learning, "
            "progettazione di contenuti, supporto tecnico e gestione di documentazione aziendale. La demo mostra come il cliente "
            "possa interrogare questi materiali tramite chat, ottenendo risposte sintetiche con fonti verificabili."
        )
        sources = [
            Source(
                title="Servizi Bitness",
                document="Servizi e-learning e formazione.docx",
                page=None,
                score=0.88,
                snippet="La società supporta progetti digitali, formazione online, contenuti e-learning e gestione documentale.",
            )
        ]
    elif any(word in q for word in ["fonti", "citazioni", "documenti"]):
        answer = (
            "Ogni risposta può essere accompagnata dalle fonti usate: nome del documento, pagina quando disponibile, "
            "rilevanza del recupero e anteprima del testo. Nella versione completa questi dati arrivano direttamente dal motore RAG."
        )
        sources = [
            Source(
                title="Esempio fonte recuperata",
                document="Profilo aziendale Bitness.pdf",
                page="1",
                score=0.84,
                snippet="Le fonti consentono di verificare il passaggio documentale da cui viene generata la risposta.",
            )
        ]
    else:
        answer = (
            "Questa demo mostra l'esperienza finale del prodotto: l'utente carica documenti, pone domande in linguaggio naturale "
            "e riceve una risposta chiara con fonti. Nella versione completa questa stessa interfaccia viene collegata al backend RAG "
            "esistente basato su OpenAI, LlamaIndex, ChromaDB e documenti reali del cliente."
        )
        sources = [
            Source(
                title="Profilo demo knowledge base",
                document="Profilo aziendale Bitness.pdf",
                page="1",
                score=0.86,
                snippet="La demo riproduce il flusso completo: upload, knowledge base, chat, risposta e fonti.",
            ),
            Source(
                title="Architettura RAG",
                document="Servizi e-learning e formazione.docx",
                page=None,
                score=0.79,
                snippet="La versione completa collega l'interfaccia al retrieval documentale e alla generazione delle risposte.",
            ),
        ]

    return AnswerResult(answer=answer, sources=sources, debug={"engine": "demo"})
