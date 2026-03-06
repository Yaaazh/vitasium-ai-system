import streamlit as st
from vitasium_engine import get_vitasium_response

st.set_page_config(page_title="Vitasium", page_icon="🩺", layout="centered")


st.markdown("""
<style>

.stApp{
background: linear-gradient(135deg,#020617,#0f172a,#020617);
color:white;
}

/* chat bubble */

.stChatMessage{
border-radius:12px;
padding:8px;
}

/* glass container */

.block-container{
background: rgba(255,255,255,0.03);
backdrop-filter: blur(10px);
border-radius:15px;
padding:20px;
}

/* floating medical icons */

.floating{
position:fixed;
top:0;
left:0;
width:100%;
height:100%;
pointer-events:none;
z-index:-1;
overflow:hidden;
}

.med{
position:absolute;
font-size:28px;
opacity:0.2;
animation: float linear infinite;
}

@keyframes float{
0%{
transform: translateY(110vh) rotate(0deg);
}
100%{
transform: translateY(-10vh) rotate(360deg);
}
}

.med:nth-child(1){left:10%;animation-duration:25s;}
.med:nth-child(2){left:25%;animation-duration:18s;}
.med:nth-child(3){left:40%;animation-duration:22s;}
.med:nth-child(4){left:60%;animation-duration:20s;}
.med:nth-child(5){left:75%;animation-duration:26s;}
.med:nth-child(6){left:90%;animation-duration:24s;}

</style>
""", unsafe_allow_html=True)


# Floating background

st.markdown("""
<div class="floating">
<div class="med">🧬</div>
<div class="med">💊</div>
<div class="med">🧬</div>
<div class="med">💉</div>
<div class="med">🧬</div>
<div class="med">💊</div>
</div>
""", unsafe_allow_html=True)


if "messages" not in st.session_state:
    st.session_state.messages = []

if "step" not in st.session_state:
    st.session_state.step = "welcome"

if "language" not in st.session_state:
    st.session_state.language = None


with st.sidebar:
    st.header("Vitasium")

    st.markdown("""
**Vitasium** is an AI medical assistant built to provide knowledge.

Features:

• Multilingual medical conversations  
• Symptom explanation  
• Educational health guidance  
• AI assisted knowledge retrieval

⚠️ Not a replacement for professional doctors.
""")

    st.divider()

    st.success(
        f"Language: {st.session_state.language if st.session_state.language else 'Initializing...'}"
    )

    if st.button("New Session / Change Language"):
        st.session_state.messages = []
        st.session_state.step = "welcome"
        st.session_state.language = None
        st.rerun()

st.title("🩺 Vitasium Medical AI")
st.caption("Accessing the Gale Encyclopedia of Medicine")

if st.session_state.step == "welcome":

    with st.chat_message("assistant", avatar="https://cdn-icons-png.flaticon.com/512/387/387561.png"):
        st.markdown(
            "Welcome to **Vitasium**.\n\n"
            "I am your AI medical assistant.\n\n"
            "**What language would you like to communicate in?**"
        )

    if lang_input := st.chat_input(
        "Type your preferred language. Example: English, Tamil, Hindi, Spanish, Arabic..."
    ):

        st.session_state.language = lang_input
        st.session_state.step = "init_greeting"
        st.rerun()

elif st.session_state.step == "init_greeting":

    with st.spinner(f"Setting up Vitasium in {st.session_state.language}..."):

        greeting_query = (
            "Say: 'Hello! I am Vitasium, your medical assistant. "
            "How can I help you today?' "
            f"in {st.session_state.language}"
        )

        greeting = get_vitasium_response(
            greeting_query,
            st.session_state.language
        )

        st.session_state.messages.append(
            {"role": "assistant", "content": greeting}
        )

        st.session_state.step = "chatting"

        st.rerun()


elif st.session_state.step == "chatting":

    for message in st.session_state.messages:

        if message["role"] == "assistant":

            with st.chat_message(
                "assistant",
                avatar="https://cdn-icons-png.flaticon.com/512/387/387561.png"
            ):
                st.markdown(message["content"])

        else:

            with st.chat_message("user"):
                st.markdown(message["content"])


    if prompt := st.chat_input("Ask your medical question..."):

        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message(
            "assistant",
            avatar="https://cdn-icons-png.flaticon.com/512/387/387561.png"
        ):

            with st.spinner("Analyzing Encyclopedia..."):

                response = get_vitasium_response(
                    prompt,
                    st.session_state.language
                )

                st.markdown(response)

                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )