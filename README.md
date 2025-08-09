# SAT AI Tutor — Prototype

This bundle contains a Streamlit-based prototype for an SAT study AI tutor.
It includes:
- `app.py` — a Streamlit app with diagnostic test, practice-by-topic, full practice test, and a progress dashboard.
- `questions.csv` — a small sample question bank you can expand.
- `requirements.txt` — Python packages.
- `README.md` — this file.

## Quick start (local)
1. Install Python 3.10+.
2. Create a virtual env:
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\\Scripts\\activate    # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. (Optional) Set OpenAI API key if you want AI explanations:
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```
5. Run:
   ```bash
   streamlit run app.py
   ```

## Deploy
- **Streamlit Community Cloud** — easiest for Streamlit apps.
- **Render** or **Fly** — for more control.
- Add a database (Supabase, Firebase) to persist user progress and enable accounts.

## How the AI parts work
- If you set `OPENAI_API_KEY` in environment, the app will attempt to call OpenAI's chat completion to produce explanations and possible question generation.
- Replace the `model` in `app.py` with a supported model string for your plan.

## Next steps (ways I can help)
- Add full SAT-style question bank (official practice tests).
- Hook up user accounts + database to save progress and tailor study plans.
- Build adaptive algorithms that select questions based on weaknesses.
- Add reporting to predict score improvement over time.