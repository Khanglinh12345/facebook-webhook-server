from flask import Flask, request

app = Flask(__name__)
VERIFY_TOKEN = "my_verify_token"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid token", 403
    elif request.method == "POST":
        print("Tin nhắn mới:", request.json)
        return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
