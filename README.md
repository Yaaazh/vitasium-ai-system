# 🩺 Vitasium: AI-Driven Clinical Intelligence & Emergency Triage

Vitasium is a high-fidelity **Retrieval-Augmented Generation (RAG)** ecosystem that delivers "Gold-Standard" medical information via WhatsApp and a Web Dashboard. It is specifically designed to combat health misinformation by grounding every response in verified clinical literature.

## 🚀 Key Features

* **Verified Knowledge:** Grounded in the *Oxford Handbook of Clinical Medicine*, *IFRC Guidelines*, and *Gale Encyclopedia of Medicine*.
* **Multilingual Support:** Seamless communication in 50+ languages (English, Tamil, Hindi, Spanish, Arabic, etc.).
* **Emergency Triage:** Automatic detection of life-threatening symptoms with instant 112-link (India) triggers.
* **Contextual Memory:** Maintains conversation state to understand follow-up questions (e.g., "What should I do about it?").
* **Dual Interface:** High-accessibility WhatsApp bot via Twilio + Advanced Clinical Dashboard Web App via Streamlit.

## 🏗️ Technical Architecture

* **LLM:** Llama-3.3-70B-Versatile (Inference via **Groq LPU** for high-speed reasoning).
* **Vector Database:** **Pinecone (Serverless)** using Cosine Similarity for semantic search.
* **Embeddings:** **Google Gemini-Embedding-001** for high-dimensional medical context.
* **Cloud Infrastructure:** Backend hosted on **Render**; Dashboard on **Streamlit Cloud**.
* **Logic:** Built with **LangChain** using Recursive Character Text Splitting (1500 chars).

## 📁 Project Structure

```text
Vitasium_Project/
├── app.py                # Streamlit Dashboard UI
├── whatsapp_bot.py       # Flask Server & Twilio WhatsApp Integration
├── vitasium_engine.py    # Core RAG Logic & AI Inference Engine
├── ingest_v2.py          # Multithreaded Knowledge Ingestor (with Key Rotation)
├── medical_library/      # [Local Only] Curated Clinical PDFs
├── requirements.txt      # Python Dependencies
└── .env                  # API Keys & Configuration (Hidden)

```

## 🛠️ Installation & Setup

1. **Clone the repo:**

```bash
git clone https://github.com/your-username/vitasium.git
cd Vitasium_Project

```

2. **Install Dependencies:**

```bash
pip install -r requirements.txt

```

3. **Environment Variables:**
Create a `.env` file in the root directory and add your keys:

```env
GROQ_API_KEY=your_groq_key
PINECONE_API_KEY=your_pinecone_key
GOOGLE_API_KEY_1=your_google_key
GOOGLE_API_KEY_2=your_google_key
GOOGLE_API_KEY_3=your_google_key
GOOGLE_API_KEY_4=your_google_key
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token

```

## 📲 How to Interact with Vitasium

### 1. WhatsApp Assistant (Twilio Sandbox)

To access the medical assistant instantly on your phone:

* **Option A: Scan the QR Code**
*(Upload your QR code image to GitHub and link it here)*
* **Option B: Manual Join** 1. Save the number **+1 415 523 8886** to your contacts.
2. Send the message `join [your-sandbox-keyword]` (e.g., `join horn-metal`) to the number.
3. Once confirmed, type **"Hello"** to begin.

### 2. Clinical Dashboard (Web App)

For the professional web interface:

* **Live Link:** [Click here to launch Vitasium Web App]([Insert your Streamlit URL here])

## ⚖️ Safety & Disclaimer

**Vitasium is an educational health awareness tool.** It is **not** a substitute for professional medical advice, diagnosis, or treatment. The system includes hard-coded emergency overrides that trigger when life-threatening symptoms are detected, directing users to immediate professional care.