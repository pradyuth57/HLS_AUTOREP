import os, re, requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN    = os.getenv("VERIFY_TOKEN", "pradyuth-verify")
WHATSAPP_TOKEN  = os.getenv("WHATSAPP_TOKEN")          # paste into Render env
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")         # paste into Render env

ROSTER_REPLY = (
    "Pradyuth Balaji - S\n"
    "Pavish Kumar - S\n"
    "Saran Kanagaraj - S\n"
    "Sarada Gopinath - S\n"
    "Navanthika - S\n"
    "Vikram balaji - S"
)

# trigger words like your examples
KEYWORDS = re.compile(r"(steward|stewards|staff|required|wanted)", re.IGNORECASE)

def send_text(to, body, context_id=None):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product":"whatsapp","to":to,"type":"text","text":{"body":body}}
    if context_id: data["context"] = {"message_id": context_id}  # threaded reply
    requests.post(url, headers=headers, json=data, timeout=10)

@app.get("/webhook")
def verify():
    mode  = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    chall = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return chall, 200
    return "forbidden", 403

@app.post("/webhook")
def incoming():
    v = (request.get_json() or {})["entry"][0]["changes"][0]["value"]
    msgs = v.get("messages", [])
    if not msgs: return "ok", 200
    m = msgs[0]
    sender = m.get("from")                        # your WA id in DMs
    text   = (m.get("text", {}) or {}).get("body","")
    mid    = m.get("id")
    if KEYWORDS.search(text):
        send_text(sender, ROSTER_REPLY, context_id=mid)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
