import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

load_dotenv()

INDEX_NAME = "vitasium-index"
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
BATCH_SIZE = 80 

class KeyManager:
    def __init__(self):
        self.keys = [
            os.getenv("GOOGLE_API_KEY_1"),
            os.getenv("GOOGLE_API_KEY_2"),
            os.getenv("GOOGLE_API_KEY_3"),
            os.getenv("GOOGLE_API_KEY_4")
        ]
        self.keys = [k for k in self.keys if k] 
        self.current_idx = 0
        self.lock = threading.Lock()

    def get_current_key(self):
        with self.lock:
            return self.keys[self.current_idx]

    def switch_key(self):
        with self.lock:
            self.current_idx = (self.current_idx + 1) % len(self.keys)
            print(f"Switching API Key {self.current_idx + 1}...")
            return self.keys[self.current_idx]

key_manager = KeyManager()

def upload_batch(batch_data):
    """Function specifically for one thread to handle one batch"""
    start_idx, batch_docs = batch_data
    max_retries = len(key_manager.keys)
    attempts = 0

    while attempts < max_retries:
        try:
            active_key = key_manager.get_current_key()
            
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001", 
                google_api_key=active_key,
                task_type="retrieval_document"
            )
            
            vector_store = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)
            vector_store.add_documents(batch_docs)
            
            print(f"Batch starting at {start_idx}")
            return 
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Quota" in error_msg:
                print(f"Key {key_manager.current_idx + 1} limit hit.")
                key_manager.switch_key()
                attempts += 1
                time.sleep(2) 
            else:
                print(f"Unexpected Error at {start_idx}: {e}")
                break

def process_and_upload():
    print("Starting Ingestion...")
    
    # Load PDFs
    loader = PyPDFDirectoryLoader("medical_library/")
    print("Reading files...")
    raw_docs = loader.load()
    
    # Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    docs = text_splitter.split_documents(raw_docs)
    print(f"Created {len(docs)} snippets.")

    # Prepare Batches
    batches = [(i, docs[i : i + BATCH_SIZE]) for i in range(0, len(docs), BATCH_SIZE)]

    # Multithreaded execution
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(upload_batch, batches)

    print("Vitasium Knowledge Base Updated!")

if __name__ == "__main__":
    process_and_upload()