import streamlit as st
from vitasium_engine import get_vitasium_response, load_vitasium_brain

st.set_page_config(page_title="Vitasium", page_icon="🩺", layout="centered")

# CUSTOM CSS 
st.markdown("""
<style>
.stApp{
background: linear-gradient(135deg,#020617,#0f172a,#020617);
color:white;
}
.stChatMessage{
border-radius:12px;
padding:8px;
}
.block-container{
background: rgba(255,255,255,0.03);
backdrop-filter: blur(10px);
border-radius:15px;
padding:20px;
}
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
0%{transform: translateY(110vh) rotate(0deg);}
100%{transform: translateY(-10vh) rotate(360deg);}
}
.med:nth-child(1){left:10%;animation-duration:25s;}
.med:nth-child(2){left:25%;animation-duration:18s;}
.med:nth-child(3){left:40%;animation-duration:22s;}
.med:nth-child(4){left:60%;animation-duration:20s;}
.med:nth-child(5){left:75%;animation-duration:26s;}
.med:nth-child(6){left:90%;animation-duration:24s;}
</style>
""", unsafe_allow_html=True)

# Floating background icons
st.markdown("""
<div class="floating">
<div class="med">🧬</div><div class="med">💊</div><div class="med">🧬</div>
<div class="med">💉</div><div class="med">🧬</div><div class="med">💊</div>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "step" not in st.session_state:
    st.session_state.step = "welcome"

if "language" not in st.session_state:
    st.session_state.language = None

# SIDEBAR UPDATES
with st.sidebar:
    st.header("Vitasium")
    st.markdown("""
**Vitasium** is an AI medical assistant built to provide knowledge.
                
**Features:**
• Multilingual medical conversations  
• Symptom explanation  
• Educational health guidance  
• AI assisted knowledge retrieval

**Knowledge Base:**
• Oxford Handbook of Clinical Medicine  
• IFRC First Aid Guidelines  
• Gale Encyclopedia of Medicine 

⚠️ Not a replacement for professional doctors.
""")
    
    st.divider()
    st.success(f"Language: {st.session_state.language if st.session_state.language else 'Initializing...'}")

    if st.button("New Session / Change Language"):
        st.session_state.messages = []
        st.session_state.step = "welcome"
        st.session_state.language = None
        st.rerun()

st.title("🩺 Vitasium Medical AI")
st.caption("Accessing Multi-Source Clinical Library & Emergency Guidelines")

# CHAT 

if st.session_state.step == "welcome":
    with st.chat_message("assistant", avatar="https://cdn-icons-png.flaticon.com/512/387/387561.png"):
        st.markdown("Welcome to **Vitasium**.\n\nI am your AI medical assistant.\n\n**What language would you like to communicate in?**")

    if lang_input := st.chat_input("Type language (e.g. English, Tamil, Hindi)..."):
        st.session_state.language = lang_input
        st.session_state.step = "init_greeting"
        st.rerun()

elif st.session_state.step == "init_greeting":
    with st.spinner(f"Configuring Vitasium for {st.session_state.language}..."):
        try:
            load_vitasium_brain() 
        except:
            pass
        
        greeting = f"Hello! I am Vitasium, your medical assistant. I'm ready to help you in **{st.session_state.language}**. How can I assist you today?"
        
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        st.session_state.step = "chatting"
        st.rerun()

elif st.session_state.step == "chatting":
    for message in st.session_state.messages:
        avatar = "https://cdn-icons-png.flaticon.com/512/387/387561.png" if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask your medical question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build history context 
        history_context = ""
        for msg in st.session_state.messages[-6:]: 
            history_context += f"{msg['role'].capitalize()}: {msg['content']}\n"

        # Generate AI Response
        with st.chat_message("assistant", avatar="https://cdn-icons-png.flaticon.com/512/387/387561.png"):
            with st.spinner("Analyzing Clinical Library..."):
                response = get_vitasium_response(
                    prompt, 
                    st.session_state.language, 
                    history_context
                )
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

