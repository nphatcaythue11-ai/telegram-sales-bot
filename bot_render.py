"""
TELEGRAM BOT - Version cho Render.com
Dùng biến môi trường, không hardcode token
"""

import http.client
import json
import os
import time
import random
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ========== CONFIG TỪ ENVIRONMENT ==========
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
SHOP_NAME = os.environ.get('SHOP_NAME', 'Shop Của Tôi')
SHOP_CONTACT = os.environ.get('SHOP_CONTACT', '@shop_admin')

# ========== PRODUCTS ==========
PRODUCTS = [
    {"name": "Robux 100k", "price": "100.000đ", "desc": "Nhận trong 5 phút"},
    {"name": "Robux 200k", "price": "200.000đ", "desc": "Tiết kiệm hơn"},
    {"name": "Nitro 1 tháng", "price": "150.000đ", "desc": "Code redeem"},
]

# ========== SMART REPLIES ==========
REPLIES = {
    "xin chào": "Dạ em chào anh/chị 😊 Shop có robux và nitro, anh/chị cần gì ạ?",
    "hi": "Hello anh/chị 👋 Em là Linh, tư vấn viên ạ!",
    "robux": "Dạ shop có:\n• Robux 100k: 100.000đ\n• Robux 200k: 200.000đ\nAnh/chị mua gói nào ạ?",
    "giá": "💰 Bảng giá:\n• 100k robux: 100k\n• 200k robux: 200k\n• Nitro: 150k\nNhận hàng trong 5 phút ạ!",
    "mua": "Dạ anh/chị mua gói nào ạ? Em gửi thông tin thanh toán ngay 😊",
    "help": "📖 Lệnh:\n/start - Bắt đầu\n/products - Xem SP\n/contact - Liên hệ",
    "hỗ trợ": "Dạ em hỗ trợ đặt hàng robux và nitro ạ 💬",
    "có không": "Dạ có ạ! Shop luôn có sẵn hàng, giao trong 5 phút 🚀",
    "đắt": "Dạ giá em tính theo thị trường rồi ạ. Nhưng đảm bảo uy tín, giao nhanh ạ! 😊",
}

def get_smart_reply(text):
    """Tìm câu trả lời phù hợp"""
    text_lower = text.lower().strip()
    
    for keyword, reply in REPLIES.items():
        if keyword in text_lower:
            return reply
    
    defaults = [
        f"Dạ em chưa hiểu lắm 😅 Anh/chị cần robux hay nitro ạ? Nhắn 'giá' để xem bảng giá!",
        f"Em có robux và nitro đó ạ 😊 Anh/chị nhắn 'mua' để đặt hàng!",
        f"Shop em chuyên robux 100k, 200k và nitro ạ 🎮 Giá rẻ, giao nhanh!",
    ]
    return random.choice(defaults)

# ========== KEEP ALIVE (Giữ bot awake) ==========
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = f"""<html><head><title>Telegram Bot</title></head>
        <body><h1>Bot is running!</h1><p>Status: Online</p><p>Shop: {SHOP_NAME}</p></body></html>"""
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        pass  # Không log request để tránh spam

def start_keep_alive():
    """Khởi động web server để giữ bot awake"""
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), KeepAliveHandler)
    print(f"✅ Keep-alive server running on port {port}")
    server.serve_forever()

# ========== TELEGRAM API ==========
def telegram_api(method, data=None):
    try:
        conn = http.client.HTTPSConnection("api.telegram.org")
        url = f"/bot{TELEGRAM_TOKEN}/{method}"
        
        if data:
            payload = json.dumps(data)
            headers = {"Content-type": "application/json"}
            conn.request("POST", url, payload, headers)
        else:
            conn.request("GET", url)
        
        response = conn.getresponse()
        result = json.loads(response.read().decode())
        conn.close()
        return result
    except Exception as e:
        print(f"❌ Telegram API lỗi: {e}")
        return None

def send_message(chat_id, text):
    return telegram_api("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    })

def send_typing(chat_id):
    return telegram_api("sendChatAction", {
        "chat_id": chat_id,
        "action": "typing"
    })

def get_updates(offset=0):
    return telegram_api("getUpdates", {
        "offset": offset,
        "limit": 10
    })

# ========== HANDLERS ==========
def handle_start(chat_id, user_name):
    text = f"👋 Chào <b>{user_name}</b>!\n\nEm là <b>Linh</b> từ {SHOP_NAME} 😊\n\n🛍️ <b>Sản phẩm hot:</b>\n"
    for p in PRODUCTS[:2]:
        text += f"• {p['name']}: {p['price']}\n"
    text += f"\n💬 Nhắn <b>'giá'</b> hoặc <b>'mua'</b>\n📞 Liên hệ: {SHOP_CONTACT}"
    send_message(chat_id, text)

def handle_products(chat_id):
    text = "🛍️ <b>Sản phẩm:</b>\n\n"
    for p in PRODUCTS:
        text += f"• <b>{p['name']}</b>\n  💰 {p['price']}\n  📝 {p['desc']}\n\n"
    text += "💬 Nhắn <b>'mua'</b> để đặt hàng!"
    send_message(chat_id, text)

def handle_message(msg):
    chat_id = msg['chat']['id']
    user_id = msg['from']['id']
    user_name = msg['from'].get('first_name', 'Bạn')
    text = msg.get('text', '')
    
    print(f"📨 [{datetime.now().strftime('%H:%M:%S')}] {user_name}: {text[:50]}")
    
    # Commands
    if text == '/start':
        handle_start(chat_id, user_name)
        return
    
    if text == '/products':
        handle_products(chat_id)
        return
    
    if text == '/contact':
        send_message(chat_id, f"📞 Liên hệ: {SHOP_CONTACT}")
        return
    
    # Hiện typing
    send_typing(chat_id)
    time.sleep(random.uniform(1, 2))
    
    # Trả lời
    reply = get_smart_reply(text)
    send_message(chat_id, reply)
    print(f"✅ Trả lời: {reply[:50]}...")

# ========== MAIN ==========
last_update_id = 0

def bot_loop():
    """Vòng lặp chính của bot"""
    global last_update_id
    
    print("🤖 Bot loop started...")
    
    while True:
        try:
            updates = get_updates(last_update_id + 1)
            
            if updates and updates.get('ok') and updates.get('result'):
                for update in updates['result']:
                    last_update_id = update['update_id']
                    
                    if 'message' in update:
                        handle_message(update['message'])
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            time.sleep(5)

def main():
    print("=" * 50)
    print("🤖 TELEGRAM BOT - RENDER VERSION")
    print("=" * 50)
    
    # Kiểm tra token
    if not TELEGRAM_TOKEN:
        print("❌ LỖI: TELEGRAM_BOT_TOKEN chưa được cài đặt!")
        print("👉 Thêm Environment Variable trên Render Dashboard")
        return
    
    print(f"✅ Shop: {SHOP_NAME}")
    print(f"✅ Contact: {SHOP_CONTACT}")
    print(f"✅ Products: {len(PRODUCTS)} items")
    print("=" * 50)
    
    # Khởi động keep-alive server trong thread riêng
    keep_alive_thread = threading.Thread(target=start_keep_alive, daemon=True)
    keep_alive_thread.start()
    
    # Khởi động bot
    print("\n🚀 Đang khởi động bot...\n")
    bot_loop()

if __name__ == "__main__":
    main()
