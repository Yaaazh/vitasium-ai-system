import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq 

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMBEDDING_KEY = os.getenv("GOOGLE_API_KEY_1")

EMERGENCY_KEYWORDS = [
    "chest pain", "difficulty breathing", "stroke", "unconscious", "heavy bleeding", 
    "heart attack", "poisoning", "suicide", "breathless", "seizure", "choking", "major burn", "head injury"
]

def st_cache_decorator(func):
    """
    Checks if streamlit is installed. 
    If yes, it applies @st.cache_resource to save RAM. 
    If no (on Render), it returns the function normally to avoid Status 1 crash.
    """
    try:
        import streamlit as st
        return st.cache_resource(func)
    except ImportError:
        return func

@st_cache_decorator
def load_vitasium_brain():
    """
    Initializes the AI components. This is cached on Streamlit 
    to prevent the 403 'Fair Use' block.
    """
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=EMBEDDING_KEY
    )

    vectorstore = PineconeVectorStore(
        index_name="vitasium-index", 
        embedding=embeddings
    )

    llm = ChatGroq(
        temperature=0.75,
        model_name="llama-3.3-70b-versatile",
        groq_api_key=GROQ_API_KEY
    )

    return vectorstore, llm

def get_vitasium_response(user_query, preferred_language="English", chat_history=""):
    # IMMEDIATE EMERGENCY CHECK
    query_lower = user_query.lower()
    if any(word in query_lower for word in EMERGENCY_KEYWORDS):
        maps_link = "https://maps.google.com/?q=hospitals+near+me"
        return (
            "**URGENT MEDICAL ALERT**\n\n"
            "Emergency symptoms detected. Call **112** (India) immediately.\n"
            f"[Find Nearest Hospital]({maps_link})"
        )

    try:
        # FETCH CACHED BRAIN
        vectorstore, llm = load_vitasium_brain()
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        # CONTEXTUAL SYSTEM PROMPT
        system_prompt = (
            f"You are VITASIUM, an advanced professional medical assistant. "
            f"The user has chosen to communicate in: {preferred_language}.\n\n"
            
            "CRITICAL SAFETY MANDATE:\n"
            "Evaluate if the USER QUERY describes a life-threatening emergency. "
            "If YES, respond ONLY with the code: 'GLOBAL_EMERGENCY_DETECTED'.\n\n"

            "SOURCE HIERARCHY:\n"
            "1. PRIMARY SOURCE: You have access to a CURATED CLINICAL LIBRARY (Oxford Handbook, IFRC, Gale Encyclopedia). "
            "Synthesize info into a cohesive clinical answer.\n"
            "2. STYLE: Structured, bulleted, professional yet caring medical professional.\n"
            "3. LANGUAGE: Respond ONLY in {preferred_language}.\n"
            "4. If the user's query is not available in any of the content then source information from reliable sites like WHO/SARS etc. \n"
            "5. If the user's query is totally irrelevant then say your database do not have the information.\n\n"

            "CLINICAL CONTEXT:\n{context}\n\n"
            "CHAT HISTORY:\n{chat_history}\n\n"
            "USER QUERY:\n{input}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        # CHAIN CREATION 
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain.chains import create_retrieval_chain

        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        # EXECUTION
        response = rag_chain.invoke({
            "input": user_query, 
            "chat_history": chat_history
        })
        
        answer = response.get("answer", "")

        # AI-DETECTED EMERGENCY FALLBACK
        if "GLOBAL_EMERGENCY_DETECTED" in answer:
            maps_link = "https://maps.google.com/?q=hospitals+near+me"
            return (
                "**URGENT MEDICAL ALERT**\n\n"
                "Symptoms of a serious medical emergency detected.\n\n"
                "1. **Call 112** (India) immediately.\n"
                f"2. **Find Nearest Hospital:** [Hospitals near you]({maps_link})"
            )
        
        return answer + "\n\n---\n*For health awareness only - not a substitute for professional medical care.*"

    except Exception as e:
        print(f"Error details: {e}")
        return "I'm having trouble connecting to my clinical library. Please try again in a moment."


