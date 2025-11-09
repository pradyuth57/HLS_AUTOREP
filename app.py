import os, re, requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN     = os.getenv("VERIFY_TOKEN", "pradyuth-verify")
WHATSAPP_TOKEN   = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID  = os.getenv("PHONE_NUMBER_ID")
SARAN_WA_ID      = os.getenv("SARAN_WA_ID")  # we'll capture this later

ROSTER_REPLY = """\
Pradyuth Balaji - S
Pavish Kumar - S
Saran Kanagaraj - S
Sarada Gopinath - S
Navanthika - S
Vikram Balaji - S
"""

KEYWORDS = re.compile(r"(steward|staff|required|wanted)", re.IGNORECASE)

def send_reply(to, text):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=data, timeout=10)

@app.get("/webhook")
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "forbidden", 403

@app.post("/webhook")
def incoming():
    payload = request.get_json()
    try:
        msg = payload["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = msg["from"]
        text   = msg["text"]["body"]
        if sender == SARAN_WA_ID and KEYWORDS.search(text):
            send_reply(sender, ROSTER_REPLY)
    except Exception as e:
        print("Error:", e)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)