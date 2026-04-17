import streamlit as st
from defense.pipeline import DefensePipeline

st.set_page_config(page_title="Banking AI Assistant", page_icon="💬")
st.title("💬 Banking AI Assistant")

st.sidebar.header("Pipeline Capabilities & Guardrails")
st.sidebar.markdown("""
**Capabilities:**
- Translate Vietnamese to English
- Detect and block toxic content
- Rate limit per user
- Input and output guardrails (PII, SQLi, prompt injection)
- LLM response evaluation (safety, relevance, accuracy, tone)
- Audit logging & monitoring

**Guardrails:**
- Blocks empty or too long input
- Blocks off-topic (non-banking) queries
- Blocks prompt injection & SQL injection
- Redacts PII in output
- Blocks toxic or unsafe content
- Rate limits excessive requests
""")

if 'pipeline' not in st.session_state:
    st.session_state['pipeline'] = DefensePipeline()
if 'chat' not in st.session_state:
    st.session_state['chat'] = []


def handle_send():
    user_input = st.session_state.get("user_input", "")
    if user_input.strip():
        pipeline = st.session_state['pipeline']
        try:
            result = pipeline.process(user_input, user_id="user")
            if isinstance(result, tuple):
                response, scores, verdict = result
                st.session_state['chat'].append((user_input, response))
            else:
                st.session_state['chat'].append((user_input, f"[Blocked] {result}"))
        except Exception as e:
            st.session_state['chat'].append((user_input, f"[Error] {e}"))
        st.session_state["user_input"] = ""  # Clear input after send

user_input = st.text_input(
    "Ask a banking question:",
    key="user_input",
    on_change=handle_send
)

if st.button("Send"):
    handle_send()

st.markdown("---")
st.subheader("Chat History")
for q, a in st.session_state['chat']:
    st.markdown(f"**You:** {q}")
    st.markdown(f"**Assistant:** {a}")
    st.markdown("---")
