from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Iterable

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from dotenv import load_dotenv

from .common import AnswerResult, Source

load_dotenv()

DATA_DIR = Path("data")
CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "Bitness"
CHAT_HISTORY_FILE = Path("chat_history.json")

DATA_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)


def _setup_llama():
    """Importa e configura le dipendenze RAG solo quando servono davvero."""
    import chromadb
    import fitz
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        StorageContext,
        Settings,
        Document,
    )
    from llama_index.llms.openai import OpenAI
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.vector_stores.chroma import ChromaVectorStore
    from llama_index.core.postprocessor import LLMRerank

    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    Settings.chunk_size = 700
    Settings.chunk_overlap = 150

    return {
        "chromadb": chromadb,
        "fitz": fitz,
        "VectorStoreIndex": VectorStoreIndex,
        "SimpleDirectoryReader": SimpleDirectoryReader,
        "StorageContext": StorageContext,
        "Document": Document,
        "ChromaVectorStore": ChromaVectorStore,
        "LLMRerank": LLMRerank,
        "OpenAI": OpenAI,
    }


def get_existing_files() -> list[Path]:
    return [p for p in DATA_DIR.glob("*") if p.is_file()]


def load_chat_history() -> list[dict]:
    if CHAT_HISTORY_FILE.exists():
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_chat_history(messages: list[dict]) -> None:
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def save_uploaded_files(uploaded_files: Iterable) -> int:
    saved = 0
    for uploaded_file in uploaded_files:
        file_path = DATA_DIR / uploaded_file.name
        if not file_path.exists():
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved += 1
    return saved


def _get_chroma_collection():
    deps = _setup_llama()
    chroma_client = deps["chromadb"].PersistentClient(path=str(CHROMA_DIR))
    return chroma_client.get_or_create_collection(COLLECTION_NAME), deps


def get_kb_state() -> dict:
    try:
        collection, _ = _get_chroma_collection()
        chunk_count = collection.count()
    except Exception:
        chunk_count = 0

    return {
        "ready": chunk_count > 0,
        "documents": len(get_existing_files()),
        "chunks": chunk_count,
        "mode_label": "RAG reale",
    }


def load_existing_index():
    collection, deps = _get_chroma_collection()
    if collection.count() == 0:
        return None
    vector_store = deps["ChromaVectorStore"](chroma_collection=collection)
    return deps["VectorStoreIndex"].from_vector_store(vector_store)


def load_documents_from_data_dir():
    deps = _setup_llama()
    documents = []

    for file_path in DATA_DIR.glob("*"):
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            pdf = deps["fitz"].open(file_path)
            try:
                for page_index, page in enumerate(pdf):
                    page_text = page.get_text("text")
                    if page_text and page_text.strip():
                        documents.append(
                            deps["Document"](
                                text=page_text.strip(),
                                metadata={
                                    "file_name": file_path.name,
                                    "file_path": str(file_path),
                                    "page_label": str(page_index + 1),
                                    "file_type": "pdf",
                                },
                            )
                        )
            finally:
                pdf.close()
        else:
            loaded_docs = deps["SimpleDirectoryReader"](input_files=[str(file_path)]).load_data()
            for doc in loaded_docs:
                doc.metadata = {**doc.metadata, "file_name": file_path.name}
            documents.extend(loaded_docs)

    return documents


def create_or_rebuild_index():
    deps = _setup_llama()
    documents = load_documents_from_data_dir()
    if not documents:
        return None

    collection, deps = _get_chroma_collection()
    vector_store = deps["ChromaVectorStore"](chroma_collection=collection)
    storage_context = deps["StorageContext"].from_defaults(vector_store=vector_store)
    return deps["VectorStoreIndex"].from_documents(documents, storage_context=storage_context)


def genera_multi_query(question: str) -> list[str]:
    deps = _setup_llama()
    rewrite_llm = deps["OpenAI"](model="gpt-4o-mini", temperature=0)
    prompt = f"""
Genera 2 query aggiuntive per la ricerca documentale in un sistema RAG.

Regole:
- Una query per riga
- Nessuna numerazione
- Italiano
- Massimo 25 parole per query
- Mantieni sempre nomi propri, aziende, progetti e misure citate dall'utente
- Non inventare fatti

Domanda utente:
{question}

Query:
"""
    queries = [question]
    try:
        response = rewrite_llm.complete(prompt)
        lines = [line.strip("-•123456789. ") for line in str(response).split("\n") if line.strip()]
        for line in lines:
            if len(line) > 5 and line not in queries:
                queries.append(line)
        return queries[:3]
    except Exception:
        return queries


def answer_question(question: str, index, smart: bool = True, debug: bool = False) -> AnswerResult:
    if index is None:
        return AnswerResult(
            answer="Prima carica almeno un documento e crea la knowledge base.",
            sources=[],
            debug={"engine": "rag", "ready": False},
        )

    deps = _setup_llama()
    system_prompt = """
Sei un assistente AI basato su documenti.

Regole:
- Usa solo i documenti caricati.
- Non inventare informazioni.
- Se non trovi la risposta nei documenti, rispondi: "L'informazione non è presente nei documenti caricati."
- Rispondi in italiano.
- Sii preciso e chiaro.
- Quando possibile, usa le fonti recuperate.
"""

    if smart:
        reranker = deps["LLMRerank"](top_n=4, choice_batch_size=8)
        query_engine = index.as_query_engine(
            similarity_top_k=10,
            node_postprocessors=[reranker],
            response_mode="compact",
            system_prompt=system_prompt,
        )
    else:
        query_engine = index.as_query_engine(
            similarity_top_k=5,
            response_mode="compact",
            system_prompt=system_prompt,
        )

    retrieval_queries = genera_multi_query(question) if smart else [question]
    retrieval_input = "\n".join(retrieval_queries)
    response = query_engine.query(retrieval_input)

    sources: list[Source] = []
    for i, source in enumerate(response.source_nodes):
        metadata = source.node.metadata or {}
        filename = metadata.get("file_name", "Documento sconosciuto")
        page = metadata.get("page_label")
        score = getattr(source, "score", None)
        sources.append(
            Source(
                title=f"Fonte {i + 1}",
                document=filename,
                page=page,
                score=round(score, 3) if score is not None else None,
                snippet=source.node.text[:1200],
            )
        )

    debug_payload = {"engine": "rag", "queries": retrieval_queries} if debug else {"engine": "rag"}
    return AnswerResult(answer=response.response, sources=sources, debug=debug_payload)


def clear_knowledge_base() -> None:
    """Cancella documenti, indice locale e cronologia. Usata solo in modalità tecnica."""
    import shutil

    for file_path in DATA_DIR.glob("*"):
        if file_path.is_file():
            file_path.unlink()

    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR, ignore_errors=True)
    CHROMA_DIR.mkdir(exist_ok=True)

    if CHAT_HISTORY_FILE.exists():
        CHAT_HISTORY_FILE.unlink()
