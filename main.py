from flask import Flask, request
import requests

app = Flask(__name__)

# 🔐 Token xác minh webhook
VERIFY_TOKEN = "my_verify_token"

# 🔑 Token truy cập trang (lấy từ Facebook Developer)
PAGE_ACCESS_TOKEN = "your_page_access_token"

# 🏷️ Danh sách tag ID tương ứng với từng nhân sự
TAGS = [
    "1234567890",  # Nhân sự 1
    "2345678901",  # Nhân sự 2
    "3456789012",  # Nhân sự 3
    "4567890123",  # Nhân sự 4
    "5678901234",  # Nhân sự 5
]

# 🔁 Biến đếm vòng nhân sự
current_index = 0

# ✅ Danh sách PSID đã xử lý
processed_psids = set()

# 📌 Hàm gắn tag cho người dùng
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
    global current_index
    data = request.json
    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender_id = messaging["sender"]["id"]
            if sender_id not in processed_psids:
                tag_id = TAGS[current_index]
                success = assign_tag_to_user(sender_id, tag_id)
                if success:
                    processed_psids.add(sender_id)
                    current_index = (current_index + 1) % len(TAGS)
    return "OK", 200

# 🚀 Khởi chạy server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
