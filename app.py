import streamlit as st
import pandas as pd
import random
import os

# Optional OpenAI usage
USE_OPENAI = False
try:
    import openai
    if os.getenv("OPENAI_API_KEY"):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        USE_OPENAI = True
except Exception:
    USE_OPENAI = False

st.set_page_config(page_title="SAT AI Tutor", layout="wide")

st.title("SAT AI Tutor — Practice, Diagnose, Improve")

# Load sample question bank
@st.cache_data
def load_questions():
    qfile = "questions.csv"
    if os.path.exists(qfile):
        return pd.read_csv(qfile)
    else:
        return pd.DataFrame(columns=["id","section","topic","question","choices","answer","explanation"])

questions = load_questions()

# Sidebar: user profile and actions
st.sidebar.header("Your Profile")
name = st.sidebar.text_input("Your name", value="Student")
grade = st.sidebar.selectbox("Grade", ["9","10","11","12","Other"])
st.sidebar.markdown("---")
action = st.sidebar.radio("Choose action", ["Diagnostic Test","Practice by Topic","Full Practice Test","SAT Chat","My Progress","Settings"])

# Helper: call OpenAI for generation/explanation (if enabled)
def ai_explain(question_text):
    if not USE_OPENAI:
        return "AI explanations require an OpenAI API key. Use Settings to enable."
    prompt = f"Explain the following SAT-style question concisely and show step-by-step reasoning:\n\n{question_text}\n\nAnswer and short explanation:"
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        max_tokens=400,
        temperature=0.2
    )
    return resp.choices[0].message.content.strip()

# Small utility to show multiple choice
def show_mcq(qrow):
    st.write("**Question:**", qrow["question"])
    choices = eval(qrow["choices"])
    choice = st.radio("Pick one", choices, key=f"q{qrow['id']}")
    return choice

# Diagnostic Test
if action == "Diagnostic Test":
    st.header("10-question Diagnostic (Quick) — Finds weak topics")
    if "diag_started" not in st.session_state:
        st.session_state.diag_started = False
    if not st.session_state.diag_started:
        st.write("This will pick 10 questions across sections/topics.")
        if st.button("Start Diagnostic"):
            st.session_state.diag_questions = questions.sample(n=min(10,len(questions))).to_dict('records')
            st.session_state.diag_started = True
            st.session_state.diag_answers = {}
            st.session_state.diag_index = 0
            st.experimental_rerun()
    else:
        idx = st.session_state.diag_index
        q = st.session_state.diag_questions[idx]
        st.write(f"Question {idx+1} of {len(st.session_state.diag_questions)}")
        user_choice = show_mcq(q)
        col1, col2 = st.columns([1,3])
        with col1:
            if st.button("Next", key=f"next{idx}"):
                st.session_state.diag_answers[q['id']] = user_choice
                st.session_state.diag_index += 1
                if st.session_state.diag_index >= len(st.session_state.diag_questions):
                    st.session_state.diag_started = False
                    # compute results
                    correct = 0
                    topic_misses = {}
                    for qr in st.session_state.diag_questions:
                        uid = qr['id']
                        user_ans = st.session_state.diag_answers.get(uid, None)
                        if user_ans == qr['answer']:
                            correct += 1
                        else:
                            topic_misses.setdefault(qr['topic'], 0)
                            topic_misses[qr['topic']] += 1
                    st.session_state.last_diag_score = correct
                    st.session_state.last_diag_misses = topic_misses
                    st.experimental_rerun()
                else:
                    st.experimental_rerun()
        with col2:
            if st.button("Show AI explanation", key=f"exp{idx}"):
                explanation = ai_explain(q['question'])
                st.write("**AI explanation:**")
                st.write(explanation)

    # Show results after completion
    if "last_diag_score" in st.session_state:
        st.success(f"Diagnostic complete — Score: {st.session_state.last_diag_score}/{len(st.session_state.diag_questions)}")
        st.write("Topics you missed most:")
        st.json(st.session_state.last_diag_misses)
        st.write("We recommend focusing practice on the top missed topics. Go to 'Practice by Topic' and select them.")

# Practice by Topic
if action == "Practice by Topic":
    st.header("Practice by Topic — Pick a topic and get targeted practice")
    topics = sorted(questions['topic'].unique())
    chosen = st.multiselect("Choose topic(s)", topics, default=topics[:2])
    n = st.slider("Number of questions", 5, 50, 10)
    if st.button("Get Practice"):
        bank = questions[questions['topic'].isin(chosen)].sample(n=min(n, len(questions[questions['topic'].isin(chosen)])))
        for _, row in bank.iterrows():
            st.write("---")
            show_mcq(row)
            if st.button(f"Explain {row['id']}", key=f"explain_{row['id']}"):
                st.write(row['explanation'])
                if USE_OPENAI:
                    st.write("AI enhancement:")
                    st.write(ai_explain(row['question']))

# Full Practice Test (timed)
if action == "Full Practice Test":
    st.header("Full Practice Test - timed mode (you can simulate)")
    st.info("This is a simplified practice test runner. Use official College Board tests for real conditions.")
    if st.button("Generate 40-question practice test"):
        test = questions.sample(n=min(40,len(questions))).to_dict('records')
        st.session_state.test = test
        st.session_state.test_index = 0
        st.session_state.test_answers = {}
        st.experimental_rerun()
    if "test" in st.session_state:
        idx = st.session_state.test_index
        t = st.session_state.test[idx]
        st.write(f"Question {idx+1} / {len(st.session_state.test)}")
        user_choice = show_mcq(t)
        if st.button("Next Question", key=f"tnext{idx}"):
            st.session_state.test_answers[t['id']] = user_choice
            st.session_state.test_index += 1
            if st.session_state.test_index >= len(st.session_state.test):
                # grade
                correct = sum(1 for q in st.session_state.test if st.session_state.test_answers.get(q['id']) == q['answer'])
                st.session_state.last_test_score = correct
                st.session_state.last_test_total = len(st.session_state.test)
                st.experimental_rerun()
            st.experimental_rerun()
    if "last_test_score" in st.session_state:
        st.success(f"Test complete — Score: {st.session_state.last_test_score}/{st.session_state.last_test_total}")


# SAT Chat
if action == "SAT Chat":
    st.header("SAT Chat — Ask me anything about SAT questions")
    st.write("Type in a math, reading, or writing question (paste the problem) and I'll explain step-by-step how to solve it.")
    user_question = st.text_area("Your SAT question")
    if st.button("Get AI answer"):
        if not USE_OPENAI:
            st.warning("AI explanations require an OpenAI API key. Go to Settings to enable.")
        else:
            with st.spinner("Thinking..."):
                prompt = f"You are an SAT tutor. The student asks: {user_question}\\n\\nProvide the answer, then explain step-by-step how to solve it, and give one test-taking tip."
                resp = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":prompt}],
                    max_tokens=500,
                    temperature=0.3
                )
                st.write("**AI Response:**")
                st.write(resp.choices[0].message.content.strip())


# Progress
if action == "My Progress":
    st.header("Progress Dashboard")
    st.write("This prototype saves no permanent data. Deploy with a database to track progress over time.")
    if "last_diag_score" in st.session_state:
        st.write("Last diagnostic score:", st.session_state.last_diag_score)
    if "last_test_score" in st.session_state:
        st.write("Last full test score:", st.session_state.last_test_score)
    st.info("To persist progress, deploy with a backend (e.g., Supabase, Firebase) and connect user accounts.")

# Settings
if action == "Settings":
    st.header("Settings")
    st.write("To enable AI features (question generation, improved explanations), set an environment variable OPENAI_API_KEY before running the app.")
    st.code('export OPENAI_API_KEY="your_api_key_here"')
    st.write("Deployment suggestions: Streamlit Community Cloud, Render, or Vercel (for static frontends).")