# Verity — Evidence Intelligence
Cog Culture Management Trainee — Product Profile, Part 2.

Verity extracts factual claims from PDFs, retrieves live web evidence with Tavily, evaluates claims with Groq, stores audit history in SQLite and exports JSON reports.

## Windows PowerShell setup
Python 3.11 or 3.12 recommended.

```powershell
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with your Groq and Tavily keys, then:

```powershell
python -m streamlit run app.py
```

If PowerShell activation is blocked, use:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Deploy
Push the project to GitHub without `.env`, database files or virtual environments. Create a Streamlit Community Cloud app with `app.py` as the entrypoint. Add these secrets in app settings:

```toml
GROQ_API_KEY = "your-groq-key"
TAVILY_API_KEY = "your-tavily-key"
```

## Verdict policy
VERIFIED = evidence directly supports. INACCURATE = evidence shows outdated or materially imprecise. FALSE = credible evidence directly contradicts. INSUFFICIENT EVIDENCE = missing/weak/inconclusive evidence. AI REVIEW FAILED and SEARCH FAILED are technical states, never factual verdicts.

The brief phrases False as “no evidence found”. Verity deliberately does not equate absence of evidence with falsity; it uses INSUFFICIENT EVIDENCE unless contradictory evidence exists.

## API usage
One extraction call; then one Tavily search (two results) and one compact Groq review call per claim. Default is three claims. Provider limits vary; no free/unlimited usage is guaranteed.

## Limitations
Text-based PDFs only (scanned PDFs require OCR). Source labels are heuristic. Search snippets may be incomplete. Human review is required. SQLite history is local and may not persist across hosted rebuilds. No authentication/multi-tenant controls; do not upload confidential documents.
