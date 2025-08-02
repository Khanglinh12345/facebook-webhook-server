from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

VERIFY_TOKEN = "my_verify_token"
PAGE_ACCESS_TOKEN = "EAAQVxdOj0qYBPGnFN4rm6aQQuqMKYg7yol1wULU3bFFu1jhNSTQaMDb6fbdB9liVE8ITK8vEKrB9p4qDrRX4brTf9zFRuy76lEKkGPZB5ZA7Ma87aa8j2WCBybpD2eq1dZBlCKfcUJPHtpQ0UrL1tCCEnKk0Nd7CDIaPNwPMG67IUanpZCZBIaGZCVyZBHdUfstjbZActP6cnz5OaHArGLc7gyih0QZDZD"

LABELS_FILE = "labels.json"
STATE_FILE = "state.json"
NAMES = ["Thảo", "Giang", "Kim Anh", "Nhung", "Hoa"]

# 📦 Load trạng thái
def load_state():
    if not os.path.exists(STATE_FILE):
        return {"current_index": 0, "processed_psids": []}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

# 💾 Lưu trạng thái
def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# 📦 Load danh sách label
def load_labels():
    if not os.path.exists(LABELS_FILE):
        return []
    with open(LABELS_FILE, "r") as f:
        return json.load(f)

# 💾 Lưu danh sách label
def save_labels(labels):
    with open(LABELS_FILE, "w") as f:
        json.dump(labels, f)

# 🏷️ Tạo label qua API
def create_label(name):
    url = "https://graph.facebook.com/v17.0/me/custom_labels"
    headers = {
        "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}"
    }
    data = {
        "name": name
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        print(f"❌ Lỗi tạo label '{name}': {response.text}")
        return None

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

# 📡 Xác minh webhook
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid token", 403

# 📨 Xử lý tin nhắn
@app.route("/webhook", methods=["POST"])
def webhook():
    state = load_state()
    labels = load_labels()
    current_index = state["current_index"]
    processed_psids = set(state["processed_psids"])

    data = request.json
    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender_id = messaging["sender"]["id"]
            if sender_id not in processed_psids and labels:
                tag = labels[current_index]
                tag_id = tag["id"]
                tag_name = tag["name"]
                success = assign_tag_to_user(sender_id, tag_id)
                if success:
                    print(f"✅ Gắn tag '{tag_name}' cho người dùng {sender_id}")
                    processed_psids.add(sender_id)
                    current_index = (current_index + 1) % len(labels)

    state["current_index"] = current_index
    state["processed_psids"] = list(processed_psids)
    save_state(state)

    return "OK", 200

# 🚀 Tạo label khi truy cập /init-labels
@app.route("/init-labels", methods=["GET"])
def init_labels():
    created = []
    for name in NAMES:
        label_id = create_label(name)
        if label_id:
            created.append({"id": label_id, "name": name})
            print(f"✅ Tạo label '{name}' → ID: {label_id}")
    save_labels(created)
    return f"Đã tạo {len(created)} label thành công.", 200

# 🚀 Khởi chạy server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


