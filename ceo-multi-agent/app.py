from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from main import build_system

st.set_page_config(page_title="CEO Multi-Agent System", page_icon="🤖", layout="centered")

st.title("🤖 CEO Multi-Agent System")
st.caption("Ask a question. The Orchestrator routes it to the right department agent.")

@st.cache_resource
def get_system():
    return build_system()

orch, llm = get_system()

with st.sidebar:
    st.header("The agents")
    st.markdown(
        "- 🔧 **Engineering** — GitHub PRs, issues, bugs\n"
        "- 💰 **Sales** — pipeline, deals, revenue\n"
        "- 🔍 **Research** — competitors, market, general\n"
    )
    st.divider()
    st.caption("Design rule: tools compute the facts, the LLM only phrases them.")

st.subheader("Try an example")
examples = [
    "What's our biggest deal right now?",
    "How many PRs were merged last week?",
    "Who are our main competitors?",
]
cols = st.columns(len(examples))
clicked = None
for col, ex in zip(cols, examples):
    if col.button(ex, use_container_width=True):
        clicked = ex

query = st.text_input("Or ask your own question:", value=clicked or "")

if query:
    with st.spinner("Agents thinking..."):
        result = orch.handle(query)

    agent_emoji = {"engineering": "🔧", "sales": "💰", "research": "🔍"}
    routed = result["routing_agent"]
    st.success(f"Routed to: {agent_emoji.get(routed, '🤖')} **{routed.title()} Agent**")

    st.markdown("### Answer")
    st.write(result["answer"])

    c1, c2 = st.columns(2)
    c1.metric("Confidence", f"{result['confidence']:.0%}")
    c2.metric("Uncertain?", "Yes" if result["uncertain"] else "No")
    if result["sources"]:
        st.caption("Sources: " + ", ".join(str(s) for s in result["sources"]))

    if result["error"]:
        st.error(f"Error: {result['error']}")

st.divider()
st.caption("Baseline 90% → 100%  after diagnosing and fixing failures. See README for details.")