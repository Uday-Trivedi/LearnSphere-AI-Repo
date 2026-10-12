# LearnSphere AI Study Plan Agent

The **LearnSphere AI Study Plan Agent** generates personalized, grounded study plans for students using simple LangChain conditional chains and Google Gemini.

It supports two distinct workflows without complex orchestration:
1. **PDF Study Plan Route (`mode: "pdf"`)**: Accepts the JSON output from the existing FastAPI PDF extractor, grounds all topics in the supplied PDF text, and creates a session-by-session study plan referencing actual page numbers.
2. **Competitive Exam Route (`mode: "exam"`)**: Retrieves structured curricula from local JSON knowledge bases for subjects like DSA, OS, CN, SQL, and Aptitude, grounded in educator curricula (e.g. Striver's A2Z DSA).

---

## Folder Structure

```text
agent/
├── main.py          # Conditional chain (RunnableBranch) & public entry point
├── tool1.py         # PDF study plan generation tool (@tool)
├── tool2.py         # Competitive exam plan tool (@tool) with simple JSON retriever
├── requirements.txt # Python dependencies
├── .env             # Gemini API key and model configuration
└── README.md        # Documentation and integration guide
```

The knowledge base JSON files are located in `knowledge_base/` (or `agent/knowledge_base/`):
- `dsa.json` (DSA - Striver)
- `os.json` (Operating Systems - Atchala)
- `cn.json` (Computer Networks - Neso Academy)
- `sql.json` (SQL / DBMS - Gate Smashers)
- `aptitude.json` (Aptitude - Arun Sharma)

---

## 1. Installation

From your terminal, navigate to the `agent/` folder and install dependencies:

```bash
cd agent
pip install -r requirements.txt
```

---

## 2. Configuration (`.env`)

Edit the `.env` file inside the `agent/` directory:

```env
GOOGLE_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

> **Security Note:** The `.env` file is excluded in `.gitignore` to prevent secret leaks. Never commit your API key.

---

## 3. Public Entry Point for Integration

Other developers (frontend or backend services) call one clean function:

```python
from agent.main import generate_study_plan

# Or if running inside the agent directory:
# from main import generate_study_plan
```

### Route 1: PDF Upload (`mode: "pdf"`)
Directly pass the output received from the PDF extractor endpoint `/extract-pdf`:

```python
request = {
    "mode": "pdf",
    "pdf_json": {
        "filename": "Operating_Systems.pdf",
        "total_pages": 2,
        "pages": [
            {
                "page": 1,
                "text": "Introduction to operating systems, process management, and CPU scheduling."
            },
            {
                "page": 2,
                "text": "Memory management, paging, segmentation, and virtual memory."
            }
        ]
    }
}

study_plan = generate_study_plan(request)
print(study_plan)
```

### Route 2: Competitive Exam (`mode: "exam"`)
Pass the exam, subject, and educator:

```python
request = {
    "mode": "exam",
    "exam_name": "GATE",
    "subject": "DSA",
    "teacher": "Striver"
}

study_plan = generate_study_plan(request)
print(study_plan)
```

---

## 4. Running the Built-in Test Suite

Run `main.py` directly from the command line:

```bash
python main.py
```

The built-in test suite automatically runs:
1. **Input Validation Tests**: Checks missing modes, unsupported modes, missing fields, and invalid JSON strings without calling the LLM.
2. **Subject & File Retrieval Tests**: Validates that unsupported subjects return clear errors and existing knowledge bases load accurately.
3. **Live Gemini Invocation Tests**: If a valid `GOOGLE_API_KEY` is present in `.env`, it performs end-to-end plan generation. If not, it warns the user and completes all non-network tests gracefully.
