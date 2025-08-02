from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

# 🔐 Token xác minh webhook
VERIFY_TOKEN = "my_verify_token"

# 🔑 Token truy cập trang (lấy từ Facebook Developer)
PAGE_ACCESS_TOKEN = "your_page_access_token"

# 🏷️ Danh sách tag ID tương ứng với từng nhân sự
TAGS = [
    {"id": "1111111111", "name": "Thảo"},
    {"id": "2222222222", "name": "Giang"},
    {"id": "3333333333", "name": "Kim Anh"},
    {"id": "4444444444", "name": "Nhung"},
    {"id": "5555555555", "name": "Hoa"}
]

STATE_FILE = "state.json"

# 📦 Load trạng thái từ file
def load_state():
    if not os.path.exists(STATE_FILE):
        return {"current_index": 0, "processed_psids": []}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

# 💾 Lưu trạng thái vào file
def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# 📌 Gắn tag cho người dùng
def assign_tag_to_user(psid, tag_id):
    url = f"https://graph.facebook.com/v17.0/{tag_id}/label"
    headers = {
        "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}"
    }
    data = {
        "user": psid
    }
    response = requests.post(url, headers=headers, data=data)
    return response.status_code == 200

# 📡 Xác minh webhook từ Facebook
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid token", 403

# 📨 Xử lý tin nhắn mới
@app.route("/webhook", methods=["POST"])
def webhook():
    state = load_state()
    current_index = state["current_index"]
    processed_psids = set(state["processed_psids"])

    data = request.json
    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender_id = messaging["sender"]["id"]
            if sender_id not in processed_psids:
                tag = TAGS[current_index]
                tag_id = tag["id"]
                tag_name = tag["name"]
                success = assign_tag_to_user(sender_id, tag_id)
                if success:
                    print(f"✅ Gắn tag '{tag_name}' cho người dùng {sender_id}")
                    processed_psids.add(sender_id)
                    current_index = (current_index + 1) % len(TAGS)

    # Lưu lại trạng thái mới
    state["current_index"] = current_index
    state["processed_psids"] = list(processed_psids)
    save_state(state)

    return "OK", 200

# 🚀 Khởi chạy server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
