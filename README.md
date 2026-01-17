# Mini RAG API

This project implements a simple Retrieval-Augmented Generation (RAG) API.
Users can upload text/markdown documents and ask questions about their content.
The API retrieves relevant document chunks using vector similarity search and
generates answers grounded in the retrieved context.

---

## Tech Stack

- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Database:** Supabase (PostgreSQL + pgvector)
- **Embeddings:** Deterministic mock embeddings
- **LLM:** Local LLM via Ollama (Mistral)

---

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- Supabase account (PostgreSQL with pgvector enabled)
- Ollama installed locally
  https://ollama.com/download

---

### 2. Clone the Repository

```bash
git clone <your-repo-url>
cd mini-rag-api
```

### 3. Create and Activate Virtual Environment

<pre class="overflow-visible! px-0!" data-start="940" data-end="971"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>python -m venv venv
</span></span></code></div></div></pre>

**Windows (PowerShell):**

<pre class="overflow-visible! px-0!" data-start="999" data-end="1044"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-powershell"><span><span>.\venv\Scripts\Activate.ps1
</span></span></code></div></div></pre>

---

### 4. Install Dependencies

<pre class="overflow-visible! px-0!" data-start="1080" data-end="1123"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>pip install -r requirements.txt
</span></span></code></div></div></pre>

---

### 5. Environment Variables

Create a `.env` file in the project root:

<pre class="overflow-visible! px-0!" data-start="1203" data-end="1297"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-env"><span>SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-key
</span></code></div></div></pre>

---

### 6. Supabase Setup

Enable pgvector:

<pre class="overflow-visible! px-0!" data-start="1345" data-end="1394"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-sql"><span><span>create</span><span> extension if </span><span>not</span><span></span><span>exists</span><span> vector;
</span></span></code></div></div></pre>

Create tables:

<pre class="overflow-visible! px-0!" data-start="1412" data-end="1871"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-sql"><span><span>create table</span><span> documents (
  id uuid </span><span>primary key</span><span>,
  filename text </span><span>not null</span><span>,
  created_at timestamptz </span><span>default</span><span> now()
);

</span><span>create table</span><span> document_chunks (
  id uuid </span><span>primary key</span><span></span><span>default</span><span> gen_random_uuid(),
  document_id uuid </span><span>references</span><span> documents(id) </span><span>on</span><span></span><span>delete</span><span> cascade,
  content text </span><span>not null</span><span>,
  embedding vector(</span><span>384</span><span>),
  created_at timestamptz </span><span>default</span><span> now()
);

</span><span>create</span><span> index </span><span>on</span><span> document_chunks
</span><span>using</span><span> ivfflat (embedding vector_cosine_ops)
</span><span>with</span><span> (lists </span><span>=</span><span></span><span>100</span><span>);
</span></span></code></div></div></pre>

Create similarity search function:

<pre class="overflow-visible! px-0!" data-start="1909" data-end="2285"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-sql"><span><span>create</span><span></span><span>or</span><span> replace </span><span>function</span><span> match_chunks(
  query_embedding vector(</span><span>384</span><span>),
  match_count </span><span>int</span><span>
)
</span><span>returns</span><span></span><span>table</span><span> (
  document_id uuid,
  content text,
  similarity </span><span>float</span><span>
)
</span><span>language</span><span></span><span>sql</span><span>
</span><span>as</span><span> $$
  </span><span>select</span><span>
    document_id,
    content,
    </span><span>1</span><span></span><span>-</span><span> (embedding </span><span><=></span><span> query_embedding) </span><span>as</span><span> similarity
  </span><span>from</span><span> document_chunks
  </span><span>order</span><span></span><span>by</span><span> embedding </span><span><=></span><span> query_embedding
  limit match_count;
$$;
</span></span></code></div></div></pre>

---

## How to Run the API

### 1. Start Ollama

Pull a model:

<pre class="overflow-visible! px-0!" data-start="2350" data-end="2381"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>ollama pull mistral
</span></span></code></div></div></pre>

Ollama runs automatically in the background on Windows.

---

### 2. Start FastAPI

<pre class="overflow-visible! px-0!" data-start="2467" data-end="2511"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>uvicorn app.main:app --port 8001
</span></span></code></div></div></pre>

Open Swagger UI:

<pre class="overflow-visible! px-0!" data-start="2530" data-end="2564"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>http:</span><span>//127.0.0.1:8001/docs</span><span>
</span></span></code></div></div></pre>

---

## Example API Usage

### Upload a Document

<pre class="overflow-visible! px-0!" data-start="2616" data-end="2700"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>curl -X POST http://127.0.0.1:8001/documents \
  -F </span><span>"file=@ai_intro.txt"</span><span>
</span></span></code></div></div></pre>

Response:

<pre class="overflow-visible! px-0!" data-start="2712" data-end="2792"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-json"><span><span>{</span><span>
  </span><span>"id"</span><span>:</span><span></span><span>"uuid"</span><span>,</span><span>
  </span><span>"filename"</span><span>:</span><span></span><span>"ai_intro.txt"</span><span>,</span><span>
  </span><span>"chunk_count"</span><span>:</span><span></span><span>6</span><span>
</span><span>}</span><span>
</span></span></code></div></div></pre>

---

### List Documents

<pre class="overflow-visible! px-0!" data-start="2819" data-end="2867"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>curl http://127.0.0.1:8001/documents
</span></span></code></div></div></pre>

---

### Query Documents

<pre class="overflow-visible! px-0!" data-start="2895" data-end="3069"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>curl -X POST http://127.0.0.1:8001/query \
  -H </span><span>"Content-Type: application/json"</span><span> \
  -d </span><span>'{"question":"What are the main concerns about artificial intelligence?"}'</span><span>
</span></span></code></div></div></pre>

Response:

<pre class="overflow-visible! px-0!" data-start="3081" data-end="3390"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-json"><span><span>{</span><span>
  </span><span>"answer"</span><span>:</span><span></span><span>"The document discusses concerns such as job displacement, bias in AI systems, and ethical risks."</span><span>,</span><span>
  </span><span>"sources"</span><span>:</span><span></span><span>[</span><span>
    </span><span>{</span><span>
      </span><span>"document_id"</span><span>:</span><span></span><span>"uuid"</span><span>,</span><span>
      </span><span>"content"</span><span>:</span><span></span><span>"One major concern surrounding artificial intelligence is job displacement..."</span><span>,</span><span>
      </span><span>"similarity"</span><span>:</span><span></span><span>0.84</span><span>
    </span><span>}</span><span>
  </span><span>]</span><span>
</span><span>}</span><span>
</span></span></code></div></div></pre>
