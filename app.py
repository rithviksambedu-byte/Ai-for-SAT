import streamlit as st
import pandas as pd
import openai
import os

# --- Setup ---

# Load OpenAI API key from environment variable (Streamlit Secrets)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_OPENAI = OPENAI_API_KEY is not None
if USE_OPENAI:
    openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="SAT AI Tutor", layout="wide")

# --- Load questions ---

@st.cache_data
def load_questions():
    # Replace 'questions.csv' with your actual CSV path if needed
    df = pd.read_csv("questions.csv")
    return df

questions_df = load_questions()

# --- Helper functions ---

def ai_explain(question_text):
    if not USE_OPENAI:
        return "AI explanation unavailable. Please set your OpenAI API key in Settings."

    prompt = f"Explain this SAT question step-by-step:\n\n{question_text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500,
        )
        explanation = response.choices[0].message.content.strip()
        return explanation
    except Exception as e:
        return f"Error calling OpenAI API: {e}"

def sat_chat(user_question):
    if not USE_OPENAI:
        return "AI chat unavailable. Please set your OpenAI API key in Settings."

    prompt = (
        "You are an SAT tutor. The student asks:\n"
        f"{user_question}\n\n"
        "Provide the answer, step-by-step solution, and a test-taking tip."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling OpenAI API: {e}"

# --- UI ---

st.sidebar.title("Navigation")
action = st.sidebar.radio(
    "Choose action",
    ["Diagnostic Test", "Practice by Topic", "Full Practice Test", "SAT Chat", "My Progress", "Settings"]
)

if action == "Diagnostic Test":
    st.header("Diagnostic Test (Sample)")

    sample_qs = questions_df.sample(5).reset_index(drop=True)  # Pick 5 random questions for demo
    for i, row in sample_qs.iterrows():
        st.subheader(f"Question {i+1}")
        st.write(row['question'])
        options = [row[f'option_{c}'] for c in ['A','B','C','D'] if f'option_{c}' in row]
        choice = st.radio(f"Select answer for question {i+1}", options, key=f"diag_{i}")

        # Show AI explanation button
        if st.button(f"Show AI explanation for Q{i+1}", key=f"explain_diag_{i}"):
            explanation = ai_explain(row['question'])
            st.markdown(f"**AI explanation:**\n\n{explanation}")

elif action == "Practice by Topic":
    st.header("Practice by Topic")

    topics = questions_df['topic'].unique().tolist()
    topic = st.selectbox("Select a topic", topics)

    topic_questions = questions_df[questions_df['topic'] == topic].sample(5).reset_index(drop=True)

    for i, row in topic_questions.iterrows():
        st.subheader(f"Question {i+1}")
        st.write(row['question'])
        options = [row[f'option_{c}'] for c in ['A','B','C','D'] if f'option_{c}' in row]
        choice = st.radio(f"Select answer for question {i+1}", options, key=f"topic_{i}")

        if st.button(f"Show AI explanation for Q{i+1}", key=f"explain_topic_{i}"):
            explanation = ai_explain(row['question'])
            st.markdown(f"**AI explanation:**\n\n{explanation}")

elif action == "Full Practice Test":
    st.header("Full Practice Test")

    full_test_qs = questions_df.sample(20).reset_index(drop=True)

    for i, row in full_test_qs.iterrows():
        st.subheader(f"Question {i+1}")
        st.write(row['question'])
        options = [row[f'option_{c}'] for c in ['A','B','C','D'] if f'option_{c}' in row]
        choice = st.radio(f"Select answer for question {i+1}", options, key=f"fulltest_{i}")

        if st.button(f"Show AI explanation for Q{i+1}", key=f"explain_full_{i}"):
            explanation = ai_explain(row['question'])
            st.markdown(f"**AI explanation:**\n\n{explanation}")

elif action == "SAT Chat":
    st.header("SAT Chat — Ask any SAT question")

    user_question = st.text_area("Type your SAT question here:")

    if st.button("Get AI answer"):
        if not USE_OPENAI:
            st.warning("AI chat requires an OpenAI API key. Please set it in Settings.")
        elif not user_question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                answer = sat_chat(user_question)
                st.markdown(f"**AI Response:**\n\n{answer}")

elif action == "My Progress":
    st.header("My Progress")
    st.write("Progress tracking coming soon!")

elif action == "Settings":
    st.header("Settings")
    st.write("To enable AI features, set your OpenAI API key as a Streamlit Secret with the key `OPENAI_API_KEY`.")
    st.write("You can get an API key at https://platform.openai.com/signup")

    if USE_OPENAI:
        st.success("OpenAI API Key detected! AI features are enabled.")
    else:
        st.warning("No OpenAI API Key found. AI features are disabled.")
