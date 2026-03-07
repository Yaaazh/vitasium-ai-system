from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from vitasium_engine import get_vitasium_response, EMERGENCY_KEYWORDS, load_vitasium_brain
import threading
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def pre_warm_engine():
    try:
        print("[INIT] Warming up Vitasium Engine...")
        load_vitasium_brain()
        print("[INIT] Engine ready.")
    except Exception as e:
        print(f"[INIT] Warm-up Error: {e}")

threading.Thread(target=pre_warm_engine, daemon=True).start()

user_sessions = {}

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_async_response(user_msg, sender_id, preferred_language):
    """Generates the AI response using conversation history and sends it via Twilio."""
    try:
        session = user_sessions.get(sender_id, {})
        history_list = session.get("history", [])
        
        chat_history_string = "\n".join(history_list)
        print(f"[ASYNC] Processing query for {sender_id}. History Length: {len(history_list)} lines.")
    
        ai_response = get_vitasium_response(user_msg, preferred_language, chat_history_string)

        # Update History
        history_list.append(f"User: {user_msg}")
        history_list.append(f"Vitasium: {ai_response}")
        session["history"] = history_list[-10:] # Keep last 10 interactions

        # WhatsApp Message Length Check
        if len(ai_response) > 1600:
            ai_response = ai_response[:1597] + "..."

        client.messages.create(
            body=ai_response,
            from_=f"whatsapp:{TWILIO_NUMBER}",
            to=sender_id
        )
    except Exception as e:
        print(f"[ASYNC] Final Response Error: {e}")

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    user_msg = request.values.get('Body', '').strip()
    sender_id = request.values.get('From', '')
    resp = MessagingResponse()

    # IMMEDIATE EMERGENCY CHECK 
    if any(word in user_msg.lower() for word in EMERGENCY_KEYWORDS):
        resp.message(
            "*URGENT MEDICAL ALERT*\n\n"
            "Emergency symptoms detected. Call **112** (India) immediately.\n"
            "[Find Nearest Hospital](http://maps.google.com/?q=hospital+near+me)"
        )
        return str(resp)

    # NEW SESSION INITIALIZATION
    if sender_id not in user_sessions:
        user_sessions[sender_id] = {
            "step": "awaiting_language", 
            "language": None,
            "history": []
        }
        resp.message("Welcome to *Vitasium*. I am your medical assistant.\n\n*What language would you like to communicate in?* (e.g., English, Hindi, Tamil)")
        return str(resp)

    session = user_sessions[sender_id]

    #  LANGUAGE SELECTION
    if session["step"] == "awaiting_language":
        session["language"] = user_msg
        session["step"] = "chatting"
        
        greeting = f"Hello! I am Vitasium. I am now set to assist you in {user_msg}. How can I help you today?"
        
        client.messages.create(
            body=greeting,
            from_=f"whatsapp:{TWILIO_NUMBER}",
            to=sender_id
        )
        return str(MessagingResponse()) 

    #  MEDICAL CHAT (Asynchronous to prevent Twilio timeouts)
    if session["step"] == "chatting":
        resp.message("_Vitasium is Analyzing Clinical Library..._")
        
        thread = threading.Thread(target=send_async_response, args=(user_msg, sender_id, session["language"]))
        thread.start()
        
        return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
