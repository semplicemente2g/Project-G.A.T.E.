# Project G.A.T.E. (Guardrail Agent Testing & Evaluation)
## An LLM-as-a-Judge Architecture for Safety and Observability in Intelligent Agents.
[🇬🇧 **Read this in English**](README-EN.md)

Questa repository contiene il progetto finale per il tirocinio, che implementa un workflow multi-agente avanzato basato sul **Google Agent Development Kit (ADK)**. L'obiettivo principale è eseguire uno "Stress Test Cognitivo" sui Large Language Models (LLM), valutando la loro capacità di mantenere il contesto, rispettare regole di business complesse (anche in contraddizione) e resistere ad attacchi di *prompt injection* o modifiche di ruolo in corso d'opera.

## Architettura del Workflow

Il workflow (`StressTest_Parallel_Pipeline_v5`) è orchestrato tramite un grafo di agenti e nodi custom in Python:

1. **Gestione della Memoria (Custom Node & LlmAgent):**
   - Estrae in modo intelligente la cronologia della conversazione.
   - Intercetta direttive segrete di sistema ("MODIFICA ISTRUZIONE:") deviando l'esecuzione con routing condizionale (Bypass).
   - Utilizza un `Memory_Summarizer_Agent` (basato su Gemini 3.1 Flash-Lite) per condensare lo storico ed estrarre regole e policy in modo strutturato.

2. **Agente Principale:**
   - Riceve il prompt "pulito" e compresso.
   - Ha il compito di rispondere all'utente (in questo caso con complesse regole di roleplay, ad es. interpretare un Lead Developer per "Nexus Cybernetics" rispettando policy specifiche aziendali e mantenendo la coerenza sul nome dell'utente).

3. **Valutazione Parallela (LLM-as-a-Judge):**
   - La risposta dell'agente principale viene sottoposta al giudizio contemporaneo e parallelo di 3 LLM differenti per mitigare i bias di valutazione:
     - **Giudice 1:** Gemini 2.5 Flash
     - **Giudice 2:** Modello OpenAI GPT OSS 120B (tramite inferenza Groq)
     - **Giudice 3:** Qwen 3.6 27B (tramite inferenza Groq)
   - I giudici restituiscono uno *score* (da 1 a 10) e un commento valutando la tenuta del contesto e la logica della risposta.

4. **Sintesi (Merger Agent):**
   - Un agente `Merger_Analysis_Agent` analizza i JSON generati dai giudici, calcola la media dei punteggi e produce un "Report Stress Test Cognitivo" in formato Markdown.

5. **Osservabilità e Telemetria:**
   - I voti generati dai giudici vengono estratti e inviati a **LangSmith** tramite un nodo custom (`Send_To_LangSmith`) sotto forma di *feedback formattato*, garantendo la tracciabilità delle performance durante lo stress test.

## Struttura dei File

- `agent.py`: Il file core contenente la definizione dell'architettura ADK, i prompt di sistema, l'impostazione degli agenti e i nodi del workflow.
- `conversazione_stress_test.md`: Uno script predefinito in 6 turni. Consiste in un test intensivo di roleplay (Nexus Cybernetics) ricco di trabocchetti, clausole di emergenza, direttive sindacali e istruzioni latenti da utilizzare per sfidare la tenuta cognitiva del workflow.
- `.env`: (Da configurare) File contenente le chiavi API per Google, Groq, Anthropic, OpenAI e la configurazione dell'endpoint LangSmith.

## Prerequisiti

Assicurati di avere Python 3 installato e di configurare le seguenti variabili d'ambiente nel tuo file `.env`:

```env
GOOGLE_API_KEY="Your_GOOGLE_API_KEY"
OPENAI_API_KEY="Your_OPENAI_API_KEY"
GROQ_API_KEY="Your_GROQ_API_KEY"

# Configurazione LangSmith
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="la_tua_chiave"
```

Inoltre, installa le dipendenze necessarie per il progetto (es. `google-adk`, `langsmith`, `python-dotenv`).

## Come eseguire il progetto

Il workflow è progettato per essere interfacciato con la UI di esecuzione di Google ADK. La variabile esportata finale è `root_agent = pipeline`, pronta per essere importata e invocata nel runtime. Utilizza i turni definiti in `conversazione_stress_test.md` per alimentare la chat ed esplorare come il sistema valuta dinamicamente il degrado o la tenuta del contesto sotto stress.
