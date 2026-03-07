from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from vitasium_engine import get_vitasium_response, EMERGENCY_KEYWORDS, load_vitasium_brain
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load the AI components (Synchronous)
print("[INIT] Loading Vitasium Brain...")
try:
    load_vitasium_brain()
    print("[INIT] Brain successfully loaded and ready.")
except Exception as e:
    print(f"[INIT] Critical Error during load: {e}")

user_sessions = {}

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    user_msg = request.values.get('Body', '').strip()
    sender_id = request.values.get('From', '')
    resp = MessagingResponse()

    # 1. EMERGENCY CHECK
    if any(word in user_msg.lower() for word in EMERGENCY_KEYWORDS):
        resp.message(
            "*URGENT MEDICAL ALERT*\n\n"
            "Emergency symptoms detected. Call **112** (India) immediately.\n"
            "[Find Nearest Hospital](http://maps.google.com/?q=hospital+near+me)"
        )
        return str(resp)

    # 2. SESSION SETUP
    if sender_id not in user_sessions:
        user_sessions[sender_id] = {
            "step": "awaiting_language", 
            "language": "English", # Default to English
            "history": []
        }
        resp.message("Welcome to *Vitasium*. I am your medical assistant.\n\n*What language would you like to communicate in?*")
        return str(resp)

    session = user_sessions[sender_id]

    # 3. LANGUAGE SELECTION
    if session["step"] == "awaiting_language":
        session["language"] = user_msg
        session["step"] = "chatting"
        resp.message(f"Hello! I am Vitasium. I am now set to {user_msg}. How can I help you today?")
        return str(resp)

    # 4. MEDICAL CHAT (Synchronous Processing)
    if session["step"] == "chatting":
        print(f"[PROCESS] Generating clinical response for {sender_id}...")
        
        chat_history_string = "\n".join(session["history"])
        
        try:
            ai_response = get_vitasium_response(user_msg, session["language"], chat_history_string)

            session["history"].append(f"User: {user_msg}")
            session["history"].append(f"Vitasium: {ai_response}")
            session["history"] = session["history"][-6:]

            # Send the final answer back directly
            resp.message(ai_response)
            print(f"[SUCCESS] Response sent to {sender_id}")
            
        except Exception as e:
            print(f"[ERROR] AI Generation failed: {e}")
            resp.message("I encountered a technical issue while analyzing the library. Please try asking again.")

        return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
