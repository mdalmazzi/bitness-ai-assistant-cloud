# Bitness AI Assistant — Demo reale istituzionale/SaaS

Questa versione mantiene il backend RAG reale ma presenta una UI più pulita e coerente con una demo cliente.

## Modalità demo cliente

```powershell
$env:BITNESS_CLIENT_DEMO="1"
python -m streamlit run app.py
```

In questa modalità l'interfaccia nasconde elementi tecnici e mostra solo:

- header istituzionale/SaaS;
- chat centrale;
- input domanda;
- risposte generate sui documenti reali;
- riferimenti apribili sotto la risposta.

## Modalità tecnica

```powershell
python -m streamlit run app.py
```

Usala per caricare documenti, preparare/aggiornare l'assistente e verificare il comportamento tecnico.

## File da copiare se aggiorni un progetto già installato

Copia solo:

```text
app.py
backend/
ui/
README.md
```

Non sovrascrivere:

```text
.env
venv/
data/
chroma_db/
chat_history.json
```


## Deploy Streamlit Cloud

Per pubblicare la demo reale pulita su Streamlit Cloud:

1. Carica su GitHub questi file/cartelle:
   - `app.py`
   - `backend/`
   - `ui/`
   - `requirements.txt`
   - `packages.txt`
   - `.gitignore`

2. Non caricare:
   - `.env`
   - `venv/`
   - `chat_history.json`

3. In Streamlit Cloud, apri `App settings → Secrets` e inserisci:

```toml
OPENAI_API_KEY = "sk-..."
BITNESS_CLIENT_DEMO = "1"
```

Con `BITNESS_CLIENT_DEMO = "1"` l'app parte direttamente in modalità cliente: interfaccia pulita, nessun controllo tecnico visibile, backend RAG reale attivo.

Per la modalità tecnica in locale puoi lanciare senza variabile:

```powershell
python -m streamlit run app.py
```

Per la demo cliente in locale:

```powershell
$env:BITNESS_CLIENT_DEMO="1"
python -m streamlit run app.py
```
