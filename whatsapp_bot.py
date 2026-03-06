from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from vitasium_engine import get_vitasium_response, EMERGENCY_KEYWORDS
import threading
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# SESSION MEMORY
user_sessions = {}

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_async_response(user_msg, sender_id, preferred_language):
    """Generates the AI response in the PREFERRED language."""
    try:
        print(f"[ASYNC] Processing for {sender_id} in {preferred_language}")
        
        ai_response = get_vitasium_response(user_msg, preferred_language)

        if len(ai_response) > 1600:
            ai_response = ai_response[:1597] + "..."

        client.messages.create(
            body=ai_response,
            from_=f"whatsapp:{TWILIO_NUMBER}",
            to=sender_id
        )
    except Exception as e:
        print(f"[ASYNC] Error: {e}")

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    user_msg = request.values.get('Body', '').strip()
    sender_id = request.values.get('From', '')
    resp = MessagingResponse()

    # EMERGENCY CHECK
    if any(word in user_msg.lower() for word in EMERGENCY_KEYWORDS):
        resp.message(
            "*URGENT MEDICAL ALERT*\n\n"
            "Emergency symptoms detected. Call **112** (India) immediately.\n"
            "[Find Nearest Hospital](https://www.google.com/maps/search/hospital+near+me)"
        )
        return str(resp)

    # SESSION LOGIC
    if sender_id not in user_sessions:
        user_sessions[sender_id] = {"step": "awaiting_language", "language": None}
        resp.message("Welcome to *Vitasium*. I am your medical assistant.\n\n*Preferred language for communication?*")
        return str(resp)

    session = user_sessions[sender_id]

    # LANGUAGE SELECTION STEP
    if session["step"] == "awaiting_language":
        session["language"] = user_msg
        session["step"] = "chatting"
        
        greeting_query = f"Say 'Hello! I am Vitasium. How can I help you today?' in {user_msg}"
        thread = threading.Thread(target=send_async_response, args=(greeting_query, sender_id, user_msg))
        thread.start()
        
        # Return an empty response object instead of a blank string
        return str(MessagingResponse()) 

    # MEDICAL QUERY STEP
    if session["step"] == "chatting":
        resp.message("_Vitasium is Analyzing..._")
        
        thread = threading.Thread(target=send_async_response, args=(user_msg, sender_id, session["language"]))
        thread.start()
        
        return str(resp)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)