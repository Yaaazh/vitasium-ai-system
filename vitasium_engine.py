import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq 

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMBEDDING_KEY = os.getenv("GOOGLE_API_KEY_1")

# Hardcoded English Keywords
EMERGENCY_KEYWORDS = [
    "chest pain", "difficulty breathing", "stroke", "unconscious", "heavy bleeding", 
    "heart attack", "poisoning", "suicide", "breathless", "seizure", "choking", "major burn", "head injury"
]

def get_vitasium_response(user_query, preferred_language="English", chat_history=""):
    # Immediate check for emergency keywords
    query_lower = user_query.lower()
    if any(word in query_lower for word in EMERGENCY_KEYWORDS):
        maps_link = "https://maps.google.com/?q=hospitals+near+me"
        return (
            "**URGENT MEDICAL ALERT**\n\n"
            "Emergency symptoms detected. Call **112** (India) immediately.\n"
            f"[Find Nearest Hospital]({maps_link})"
        )

    try:
        # 2. Setup AI Brain & Vector Database
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=EMBEDDING_KEY
        )

        vectorstore = PineconeVectorStore(index_name="vitasium-index", embedding=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        llm = ChatGroq(
            temperature=0.75,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=GROQ_API_KEY
        )

        # Multilingual Detection 
        # --- UPDATED PROMPT FOR MULTI-SOURCE KNOWLEDGE ---
        system_prompt = (
            f"You are VITASIUM, an advanced professional medical assistant. "
            f"The user has chosen to communicate in: {preferred_language}.\n\n"
            
            "CRITICAL SAFETY MANDATE (STEP 1):\n"
            "Evaluate if the USER QUERY describes a life-threatening emergency. "
            "If YES, respond ONLY with the code: 'GLOBAL_EMERGENCY_DETECTED'.\n\n"

            "SOURCE HIERARCHY & INSTRUCTIONS (STEP 2):\n"
            "1. PRIMARY SOURCE: You have access to a CURATED CLINICAL LIBRARY (Oxford Handbook of Clinical Medicine, IFRC First Aid, and Gale Encyclopedia). "
            "Synthesize info from these sources into a single, cohesive clinical answer.\n"
            "2. STYLE: Provide structured, bulleted advice when possible. Maintain a professional yet caring 'Doctor' persona.\n"
            "3. NO CITATION CLUTTER: Do not say 'According to source X' unless the user asks where the info came from. Just give the medical facts.\n"
            f"4. LANGUAGE: Respond ONLY in {preferred_language}.\n"
            "5. LIMITATION: If the provided context doesn't cover the specific condition, use your internal medical training (WHO/CDC/NIH standards) but state that you are using general clinical guidelines. "
            "If neither the book nor trusted sites have the info, say you don't have that data yet.\n"

            "CLINICAL CONTEXT (Curated Library):\n{context}\n\n"
            "CHAT HISTORY (Context for the current conversation):\n{chat_history}\n\n"  # Added this line
            "USER QUERY:\n{input}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        # Imports for LangChain v1.0
        try:
            from langchain_classic.chains import create_retrieval_chain
            from langchain_classic.chains.combine_documents import create_stuff_documents_chain
        except ImportError:
            from langchain.chains import create_retrieval_chain
            from langchain.chains.combine_documents import create_stuff_documents_chain

        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        response = rag_chain.invoke({
            "input": user_query, 
            "chat_history": chat_history
        })
        answer = response.get("answer", "")

        # AI detects a multilingual emergency? 
        if "GLOBAL_EMERGENCY_DETECTED" in answer:
            maps_link = "https://maps.google.com/?q=hospitals+near+me"
            return (
                "**URGENT MEDICAL ALERT**\n\n"
                "Our system has detected symptoms of a serious medical emergency in your message. "
                "Please do not wait for further AI analysis.\n\n"
                "1. **Call 112** (India) or your local emergency number immediately.\n"
                f"2. **Find Nearest Hospital:** [Click here for Hospitals near you]({maps_link})"
            )
        
        return answer + "\n\n---\n*For health awareness only - not a substitute for professional medical care.*"

    except Exception as e:
        print(f"Error details: {e}")
        return f"Technical difficulty: I'm having trouble processing that. Please try again."
