import os, re, requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN    = os.getenv("VERIFY_TOKEN", "pradyuth-verify")
WHATSAPP_TOKEN  = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WA_ID     = os.getenv("WA_ID")        # e.g. 3538xxxxxxx
ALLOWED_GROUP   = os.getenv("GROUP_ID")           # optional: restrict to 1 group

ROSTER_REPLY = (
    "Pradyuth Balaji - S\n"
    "Pavish Kumar - S\n"
    "Saran Kanagaraj - S\n"
    "Sarada Gopinath - S\n"
    "Navanthika - S\n"
    "Vikram balaji - S"
)

KEYWORDS = re.compile(r"(steward|stewards|staff|staffs|required|wanted)", re.IGNORECASE)

def send_text(chat_id: str, body: str, context_id: str | None = None):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": chat_id, "type": "text", "text": {"body": body}}
    if context_id:
        data["context"] = {"message_id": context_id}  # nice threaded reply
    r = requests.post(url, headers=headers, json=data, timeout=10)
    r.raise_for_status()

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
    payload = request.get_json(silent=True) or {}
    try:
        value = payload["entry"][0]["changes"][0]["value"]
        msgs = value.get("messages", [])
        if not msgs:
            return "ok", 200
        msg = msgs[0]

        chat_id   = msg.get("from")             # for groups: group JID (…@g.us)
        author_id = msg.get("author", msg.get("from"))  # sender WA ID in groups; fallback
        text      = (msg.get("text", {}) or {}).get("body", "")
        msg_id    = msg.get("id")

        # Optional: restrict to a single group
        if ALLOWED_GROUP and chat_id != ALLOWED_GROUP:
            return "ok", 200

        # Only trigger on waid + keywords
        if author_id == WA_ID and KEYWORDS.search(text):
            send_text(chat_id, ROSTER_REPLY, context_id=msg_id)

    except Exception as e:
        print("Webhook parse error:", e)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
