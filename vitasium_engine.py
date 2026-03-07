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
    If no (on Render), it returns the function normally.
    """
    try:
        import streamlit as st
        return st.cache_resource(func)
    except ImportError:
        return func

@st_cache_decorator
def load_vitasium_brain():
    """
    Initializes AI components with a hard-fix for the Pinecone 'proxies' version error.
    """
    # 1. Initialize Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=EMBEDDING_KEY
    )

    # 2. Initialize VectorStore - THE HARD FIX
    from pinecone import Pinecone
    from langchain_pinecone import PineconeVectorStore

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index("vitasium-index")

    # Now we wrap that existing index into LangChain
    vectorstore = PineconeVectorStore(
        index=index, 
        embedding=embeddings
    )

    # 3. Initialize LLM
    llm = ChatGroq(
        temperature=0.3, # Low temperature helps with strict language following
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
            f"CRITICAL: The user has chosen to communicate in: {preferred_language}. "
            f"You MUST provide your ENTIRE response in {preferred_language}.\n\n"
            
            "CRITICAL SAFETY MANDATE:\n"
            "Evaluate if the USER QUERY describes a life-threatening emergency. "
            "If YES, respond ONLY with the code: 'GLOBAL_EMERGENCY_DETECTED'.\n\n"

            "SOURCE HIERARCHY:\n"
            "1. PRIMARY SOURCE: Synthesize info from the curated clinical library context provided.\n"
            "2. STYLE: Structured, bulleted, professional medical tone.\n"
            f"3. LANGUAGE: Respond ONLY in {preferred_language}.\n"
            "4. If info is missing from the library, use reliable medical sources (WHO/CDC).\n"
            "5. If query is irrelevant, state you do not have the information.\n\n"

            "CLINICAL CONTEXT:\n{context}\n\n"
            "CHAT HISTORY:\n{chat_history}\n\n"
            "USER QUERY:\n{input}"
        )

        # Build prompt and include variables
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ]).partial(preferred_language=preferred_language) 

        # CHAIN CREATION 
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain.chains import create_retrieval_chain

        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        # EXECUTION
        response = rag_chain.invoke({
            "input": user_query, 
            "chat_history": chat_history,
            "preferred_language": preferred_language
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
        
        return answer + f"\n\n---\n*Assistance provided in {preferred_language} for health awareness.*"

    except Exception as e:
        print(f"[ENGINE ERROR] Details: {e}")
        return "I'm having trouble connecting to my clinical library. Please try again in a moment."





