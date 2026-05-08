"""
TELEGRAM BOT - CHUYÊN VIÊN TƯ VẤN BLOX FRUIT TOP 1
Tư vấn viên: Phát | Chốt đơn cực kỳ | Hỗ trợ 24/7
"""

import http.client
import json
import os
import time
import random
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ========== CONFIG ==========
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
SHOP_NAME = os.environ.get('SHOP_NAME', 'Blox Fruit Store')
SHOP_CONTACT = os.environ.get('SHOP_CONTACT', '@admin_bloxfruit')
PAYMENT_INFO = os.environ.get('PAYMENT_INFO', '💰 *THANH TOÁN*\n\n📱 ZaloPay: `0343603537`\n🏦 BIDV: `8806532434`\n👤 Chủ TK: *TRAN NGUYEN PHAT*\n\n💳 *Sau khi CK:*\n1. Chụp màn hình gửi Phát\n2. Nhận acc trong 1-2 phút')

# ========== LOAD PRODUCTS ==========
PRODUCTS = {}
try:
    with open('products_bloxfruit.json', 'r', encoding='utf-8') as f:
        PRODUCTS = json.load(f)
except:
    PRODUCTS = {
        "accounts": [
            {"id": "bf-starter", "name": "Blox Fruit Starter", "level": "1-100", "price": "50.000đ", "stock": 15},
            {"id": "bf-pro", "name": "Blox Fruit Pro", "level": "1500-2000", "price": "300.000đ", "stock": 5},
        ],
        "services": [],
        "gamepass": []
    }

# ========== AI CONVERSATION ENGINE ==========
# ========== DATA STORAGE ==========
user_carts = {}        # Giỏ hàng user: {user_id: [{item, qty, price}]}
user_orders = {}       # Đơn hàng: {user_id: [{id, items, status, time}]}
promo_codes = {        # Mã giảm giá
    'PHAT10': 0.10,    # Giảm 10%
    'VIP20': 0.20,     # Giảm 20%
    'BF2024': 50000,   # Giảm 50k
}
active_promos = [      # Khuyến mãi đang chạy
    "🎉 *KHUYẾN MÃI HOT*\nMua 2 acc giảm 15%",
    "⚡ *FLASH SALE*\nAcc VIP giảm 100k hôm nay!",
]

class SalesAI:
    """Chuyên viên tư vấn Blox Fruit - Phát"""
    
    def __init__(self):
        self.context = {}  # Lưu context từng user
        self.stage = {}    # Giai đoạn chốt đơn
    
    def detect_intent(self, text):
        """Phát hiện ý định khách hàng"""
        text = text.lower().strip()
        
        intents = {
            'mua_acc': ['mua acc', 'mua account', 'có acc', 'account blox', 'mua ạc', 'acc đẹp'],
            'check_gia': ['giá', 'bao nhiêu', 'bn', 'giá sao', 'giá bao nhiêu', 'rẻ không', 'đắt không'],
            'check_stock': ['còn không', 'còn hàng', 'có sẵn', 'in stock', 'còn acc'],
            'level_query': ['level bao nhiêu', 'cao không', 'cấp mấy', 'max level', 'lvl bao nhiêu'],
            'fruit_query': ['có fruit gì', 'trái gì', 'quỷ gì', 'có dough', 'có dragon', 'có leopard'],
            'services': ['cày thuê', 'boost', 'lấy fruit', 'roll trái', 'cày level'],
            'gamepass': ['gamepass', '2x money', '2x drop', 'fruit notifier'],
            'chat_only': ['xin chào', 'chào', 'hi', 'hello', 'hú', 'alo'],
            'ask_payment': ['thanh toán', 'chuyển khoản', 'momo', 'bank', 'ck', 'trả tiền'],
            'confirm_buy': ['ok mua', 'mua luôn', 'chốt', 'đặt', 'lấy', 'lấy acc này'],
            'compare': ['so sánh', 'khác nhau', 'nên mua', 'con nào', 'acc nào'],
            'complaint_price': ['đắt', 'mắc', 'giảm', 'sale', 'giảm giá', 'chiết khấu'],
            'ask_safe': ['có uy tín', 'có scam', 'tin được', 'bảo hành', 'có bảo hành'],
            'cart': ['giỏ hàng', 'xem giỏ', 'cart', 'đã chọn', 'tổng tiền'],
            'promo': ['mã giảm', 'khuyến mãi', 'giảm giá', 'code', 'voucher', 'sale'],
            'order': ['đơn hàng', 'kiểm tra đơn', 'order', 'status', 'theo dõi'],
            'feedback': ['đánh giá', 'feedback', 'review', 'cảm nhận', 'góp ý'],
            'cancel': ['hủy', 'bỏ', 'không mua', 'thôi', 'cancel'],
        }
        
        for intent, keywords in intents.items():
            if any(kw in text for kw in keywords):
                return intent
        return 'unknown'
    
    def get_response(self, user_id, text):
        """Tạo câu trả lời thông minh"""
        intent = self.detect_intent(text)
        
        # Lấy context hiện tại
        if user_id not in self.context:
            self.context[user_id] = {'last_intent': None, 'interested_product': None}
        
        ctx = self.context[user_id]
        
        # ===== CHÀO HỎI & TẠO THIỆN CẢM =====
        if intent == 'chat_only':
            greetings = [
                f"👋 *Chào anh/chị!* Em là *Phát*, chuyên tư vấn Blox Fruit ạ.\n\nAnh/chị đang tìm account gì ạ? Starter để chơi mới hay Pro để đua top? 😊",
                f"👋 *Xin chào!* Shop em chuyên Blox Fruit account uy tín ạ!\n\nHiện đang có {len(PRODUCTS.get('accounts', []))} loại account từ 50k đến 800k. Anh/chị ngân sách khoảng bao nhiêu ạ? 💰",
            ]
            return random.choice(greetings)
        
        # ===== GIỚI THIỆU SẢN PHẨM =====
        if intent == 'mua_acc':
            ctx['last_intent'] = 'browsing'
            accounts = PRODUCTS.get('accounts', [])
            
            menu = "🎮 *MENU BLOX FRUIT ACCOUNT*\n\n"
            for acc in accounts:
                menu += f"📦 *{acc['name']}*\n"
                menu += f"   Level: `{acc['level']}`\n"
                menu += f"   💰 Giá: *{acc['price']}*\n"
                menu += f"   📝 {acc.get('desc', 'Còn hàng')}\n"
                menu += f"   📊 Còn: {acc.get('stock', 0)} acc\n\n"
            
            menu += "💡 *Gợi ý:*\n"
            menu += "• Chơi mới → Starter 50k\n"
            menu += "• Chơi chính → Pro 300k\n"
            menu += "• Đua top → VIP/Mythic\n\n"
            menu += "Anh/chị thích acc nào ạ? 🤔"
            return menu
        
        # ===== TƯ VẤN GIÁ =====
        if intent == 'check_gia':
            ctx['last_intent'] = 'price_inquiry'
            
            price_list = "💰 *BẢNG GIÁ BLOX FRUIT*\n\n"
            price_list += "*ACCOUNTS:*\n"
            for acc in PRODUCTS.get('accounts', []):
                price_list += f"• {acc['name']}: *{acc['price']}*\n"
            
            price_list += "\n*SERVICES:*\n"
            for svc in PRODUCTS.get('services', []):
                price_list += f"• {svc['name']}: {svc['price']}\n"
            
            price_list += "\n*GAMEPASS:*\n"
            for gp in PRODUCTS.get('gamepass', []):
                price_list += f"• {gp['name']}: {gp['price']}\n"
            
            price_list += "\n📌 Giá đã bao gồm:\n"
            price_list += "✓ Bảo hành 7 ngày\n"
            price_list += "✓ Hỗ trợ đổi info\n"
            price_list += "✓ Tư vấn chơi free\n\n"
            price_list += "💬 Anh/chị quan tâm mức giá nào ạ?"
            return price_list
        
        # ===== TƯ VẤN LEVEL =====
        if intent == 'level_query':
            return """📊 *LEVEL GUIDE*

🌱 *Starter (1-100)*: Tập chơi, làm quen
⭐ *Mid (700-1000)*: Đủ farm, có fruit ngon
🔥 *Pro (1500-2000)*: Farm boss, đi raid
💎 *VIP (2450+)*: Đua top, PvP pro
👑 *Mythic (2550)*: Max everything

💡 *Em gợi ý:*
• Mới chơi → Starter/Mid
• Chơi lâu dài → Pro
• Đua top sever → VIP/Mythic

Anh/chị định chơi kiểu gì ạ? 🎮"""
        
        # ===== TƯ VẤN FRUIT =====
        if intent == 'fruit_query':
            return """🍎 *FRUIT TRONG ACC*

*ACC GIÁ RẺ (50-150k):*
• Random Rare/Legend
• Có thể: Rubber, Light, Magma, Quake

*ACC TẦM TRUNG (300k):*
• Dough, Dragon, Venom
• Shadow, Soul, Control

*ACC CAO CẤP (500-800k):*
• Leopard, Kitsune, Yeti
• Mammoth, T-Rex, Gravity

🎯 *Nên chọn:*
• Farm nhanh → Light, Buddha
• PvP mạnh → Leopard, Dough
• Đẹp + Hiếm → Kitsune, Dragon

Muốn em tìm acc có fruit cụ thể không ạ? 😊"""
        
        # ===== SO SÁNH =====
        if intent == 'compare':
            return """🆚 *SO SÁNH ACCOUNT*

*So với mua tự cày:*
✅ Mua acc sẵn tiết kiệm 1-2 tuần cày
✅ Có fruit ngon ngay, không cần roll
✅ Item, belly có sẵn
✅ Vào chơi được luôn

*Về giá:*
• 50k = 1-2 ngày cày
• 150k = 1 tuần cày
• 300k = 1 tháng cày + roll fruit

💡 *Tính ra mua acc rẻ hơn nhiều!*

Anh/chị muốn tiết kiệm thời gian thì chọn acc nào ạ? 🚀"""
        
        # ===== XỬ LÝ GIÁ ĐẮT =====
        if intent == 'complaint_price':
            responses = [
                """💰 *Về giá ạ:*

Em hiểu anh/chị thắc mắc giá. Để em giải thích:

• Acc em bán đã *cày sẵn* + *có fruit* + *item đồ*
• So với thuê cày + roll fruit, giá em rẻ hơn 30-40%
• Có *bảo hành 7 ngày*, đổi trả nếu lỗi
• Hỗ trợ *trọn đời* khi chơi

🎁 *Ưu đãi:* Nếu mua hôm nay em *freeship* info + tặng 50k belly!

Anh/chị cân nhắc thử ạ? 😊""",
                
                """💡 *Giá của em đã tốt nhất thị trường rồi ạ:*

✓ Không có shop nào bảo hành 7 ngày như em
✓ Support tận tình sau mua
✓ Acc đều kiểm tra kỹ trước khi bán

🎁 Nếu anh/chị mua 2 acc em giảm thêm 10%!

Mình chốt để chơi luôn không ạ? 🎮"""
            ]
            return random.choice(responses)
        
        # ===== UY TÍN & BẢO HÀNH =====
        if intent == 'ask_safe':
            return """✅ *CAM KẾT UY TÍN*

🛡️ *Bảo hành:*
• 7 ngày đổi trả nếu acc bị lỗi
• Hoàn tiền 100% nếu không đúng mô tả
• Hỗ trợ khôi phục nếu bị hack (trong 24h)

📊 *Thông tin shop:*
• Đã bán 500+ acc
• 98% khách hài lòng 5⭐
• Group feedback 1000+ thành viên
• Hoạt động 2 năm+

💬 *Minh bạch:*
• Giao dịch trực tiếp qua Telegram
• Có video check acc trước khi giao
• Info đổi ngay sau thanh toán

Yên tâm mua nhé anh/chị! 🙏"""
        
        # ===== HƯỚNG DẪN THANH TOÁN =====
        if intent == 'ask_payment':
            return f"""💳 *THANH TOÁN*

{PAYMENT_INFO}

📌 *Các bước:*
1. Chuyển khoản đúng số tiền
2. Chụp màn hình CK gửi em
3. Em gửi info acc ngay (1-2 phút)
4. Anh/chị vào check, đổi info

⏰ *Thời gian:* 8h-23h hàng ngày

Sẵn sàng chuyển khoản chưa anh/chị? 🚀"""
        
        # ===== CHỐT ĐƠN =====
        if intent == 'confirm_buy':
            ctx['stage'] = 'confirming'
            return """🎉 *TUYỆT VỜI!*

Để em xác nhận đơn hàng:

📦 Sản phẩm: Blox Fruit Account
💰 Giá: [Tùy acc anh/chị chọn]
📱 Thanh toán: CK/Momo

Anh/chị muốn mua acc nào?
1. Starter 50k
2. Pro 300k  
3. VIP 500k
4. Mythic 800k

Chọn số hoặc nói rõ acc nào để em chuẩn bị! 💪"""
        
        # ===== CHECK HÀNG =====
        if intent == 'check_stock':
            stock_info = "📊 *TÌNH TRẠNG KHO*\n\n"
            for acc in PRODUCTS.get('accounts', []):
                stock = acc.get('stock', 0)
                if stock > 10:
                    status = "🟢 Còn nhiều"
                elif stock > 3:
                    status = "🟡 Sắp hết"
                else:
                    status = "🔴 Ít hàng"
                stock_info += f"• {acc['name']}: {status} ({stock} acc)\n"
            stock_info += "\n💡 Càng cao cấp càng hiếm ạ!"
            return stock_info
        
        # ===== DỊCH VỤ CÀY THUÊ =====
        if intent == 'services':
            return """🔧 *DỊCH VỤ CÀY THUÊ*

*BOOST LEVEL:*
• 1-700: 100k (1-2 ngày)
• 700-1500: 200k (2-3 ngày)
• 1500-2450: 400k (5-7 ngày)

*ROLL FRUIT:*
• Legend random: 50k
• Mythic cụ thể: 150k

*Ưu điểm:*
✓ Không cần nhường acc
✓ Cày bằng team pro
✓ Bảo mật 100%

Anh/chị muốn cày hay mua acc sẵn? 🤔"""
        
        # ===== GIỎ HÀNG =====
        if intent == 'cart':
            cart = user_carts.get(user_id, [])
            if not cart:
                return "🛒 *Giỏ hàng trống*\n\nHãy chọn acc để thêm vào giỏ nhé! Gõ 'mua acc' để xem menu 😊"
            
            total = sum(item['price'] * item['qty'] for item in cart)
            cart_text = "🛒 *GIỎ HÀNG CỦA BẠN*\n\n"
            for i, item in enumerate(cart, 1):
                cart_text += f"{i}. {item['name']} x{item['qty']} = {item['price'] * item['qty']:,}đ\n"
            cart_text += f"\n💰 *Tổng: {total:,}đ*\n\n"
            cart_text += "💳 Gõ 'thanh toán' để đặt hàng\n"
            cart_text += "➕ Gõ 'mua acc' để thêm"
            return cart_text
        
        # ===== KHUYẾN MÃI =====
        if intent == 'promo':
            promo_text = "🎁 *MÃ GIẢM GIÁ HIỆN CÓ*\n\n"
            for code, discount in promo_codes.items():
                if isinstance(discount, float):
                    promo_text += f"• `{code}`: Giảm *{int(discount*100)}%*\n"
                else:
                    promo_text += f"• `{code}`: Giảm *{discount:,}đ*\n"
            
            promo_text += "\n🔥 *KHUYẾN MÃI HOT*\n"
            promo_text += random.choice(active_promos)
            
            promo_text += "\n\n💡 *Cách dùng:* Nhắn mã code khi thanh toán\nVí dụ: 'Mã PHAT10'"
            return promo_text
        
        # ===== ĐƠN HÀNG =====
        if intent == 'order':
            orders = user_orders.get(user_id, [])
            if not orders:
                return "📦 *Chưa có đơn hàng nào*\n\nMua acc ngay để có đơn đầu tiên! 🎮"
            
            order_text = "📦 *LỊCH SỬ ĐƠN HÀNG*\n\n"
            for i, order in enumerate(orders[-5:], 1):  # 5 đơn gần nhất
                status_emoji = {"pending": "⏳", "paid": "✅", "delivered": "📦"}.get(order['status'], "❓")
                order_text += f"{status_emoji} *Đơn #{order['id']}*\n"
                order_text += f"   Sản phẩm: {order['items']}\n"
                order_text += f"   Tổng: {order['total']:,}đ\n"
                order_text += f"   Trạng thái: {order['status']}\n\n"
            return order_text
        
        # ===== FEEDBACK =====
        if intent == 'feedback':
            return """⭐ *ĐÁNH GIÁ DỊCH VỤ*

Anh/chị vui lòng đánh giá sau khi nhận acc:

⭐⭐⭐⭐⭐ - Tuyệt vời, hài lòng
⭐⭐⭐⭐ - Tốt, đáng mua
⭐⭐⭐ - Bình thường
⭐⭐ - Cần cải thiện
⭐ - Không hài lòng

💬 Hoặc nhắn góp ý trực tiếp cho Phát!

Cảm ơn anh/chị đã ủng hộ shop! 🙏"""
        
        # ===== HỦY ĐƠN =====
        if intent == 'cancel':
            # Xóa giỏ hàng
            if user_id in user_carts:
                del user_carts[user_id]
            return "🗑️ Đã xóa giỏ hàng!\n\nAnh/chị có thể chọn lại bất cứ lúc nào nhé 😊"
        
        # ===== DEFAULT - TƯ VẤN CHUNG =====
        return """🤔 *Em Phát chưa hiểu lắm...*

Anh/chị có thể hỏi:
• "Giá account" 💰
• "Còn hàng không" 📦
• "Acc level bao nhiêu" 📊
• "Có fruit gì" 🍎
• "Khuyến mãi" 🎁
• "Giỏ hàng" 🛒
• "Đơn hàng" 📦
• "Thanh toán thế nào" 💳
• "Có uy tín không" ✅

Hoặc gõ */start* để xem menu! 😊

Phát sẵn sàng tư vấn 24/7! 🚀"""

# Khởi tạo AI
sales_ai = SalesAI()

# ========== CART & ORDER FUNCTIONS ==========
def add_to_cart(user_id, product_name, price):
    """Thêm sản phẩm vào giỏ hàng"""
    if user_id not in user_carts:
        user_carts[user_id] = []
    
    # Kiểm tra sản phẩm đã có chưa
    for item in user_carts[user_id]:
        if item['name'] == product_name:
            item['qty'] += 1
            return
    
    # Thêm mới
    user_carts[user_id].append({
        'name': product_name,
        'price': price,
        'qty': 1
    })

def apply_promo(total, promo_code):
    """Áp dụng mã giảm giá"""
    if promo_code.upper() in promo_codes:
        discount = promo_codes[promo_code.upper()]
        if isinstance(discount, float):
            return int(total * (1 - discount))
        else:
            return max(0, total - discount)
    return total

def create_order(user_id, items, total, promo=None):
    """Tạo đơn hàng mới"""
    if user_id not in user_orders:
        user_orders[user_id] = []
    
    order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id}"
    
    final_total = apply_promo(total, promo) if promo else total
    
    order = {
        'id': order_id,
        'items': items,
        'total': final_total,
        'promo': promo,
        'status': 'pending',
        'time': datetime.now().isoformat(),
    }
    
    user_orders[user_id].append(order)
    return order_id, final_total

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
        "parse_mode": "Markdown"
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

# ========== KEEP ALIVE ==========
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = f"""<html><body><h1>Blox Fruit Bot Running!</h1><p>Shop: {SHOP_NAME}</p></body></html>"""
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        pass

def start_keep_alive():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), KeepAliveHandler)
    print(f"✅ Keep-alive server on port {port}")
    server.serve_forever()

# ========== HANDLERS ==========
def handle_start(chat_id, user_name):
    welcome = f"""👋 *Chào {user_name}!*

Em là *Phát* 🎮
Chuyên gia tư vấn Blox Fruit | 500+ đơn thành công

🛍️ *SHOP BLOX FRUIT*
• Acc Starter → VIP: 50k - 800k
• Dịch vụ cày thuê, boost
• Gamepass giá rẻ

🎁 *TÍNH NĂNG MỚI*
• 🛒 "Giỏ hàng" - Xem/Tổng tiền
• 🎁 "Khuyến mãi" - Mã giảm giá
• 📦 "Đơn hàng" - Theo dõi đơn
• ⭐ "Feedback" - Đánh giá

💡 *Thử ngay:*
→ "Mua acc" | "Giá" | "Khuyến mãi"

Sẵn sàng chốt đơn! 🚀"""
    
    send_message(chat_id, welcome)

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
    
    if text in ['/cart', 'giỏ hàng']:
        reply = sales_ai.get_response(user_id, 'giỏ hàng')
        send_message(chat_id, reply)
        return
    
    if text in ['/promo', '/sale', 'khuyến mãi']:
        reply = sales_ai.get_response(user_id, 'khuyến mãi')
        send_message(chat_id, reply)
        return
    
    if text in ['/order', '/don', 'đơn hàng']:
        reply = sales_ai.get_response(user_id, 'đơn hàng')
        send_message(chat_id, reply)
        return
    
    if text in ['/feedback', 'feedback']:
        reply = sales_ai.get_response(user_id, 'feedback')
        send_message(chat_id, reply)
        return
    
    # Hiện typing
    send_typing(chat_id)
    time.sleep(random.uniform(1, 2))
    
    # AI response
    reply = sales_ai.get_response(user_id, text)
    send_message(chat_id, reply)
    print(f"✅ Đã trả lời {user_name}")

# ========== MAIN ==========
last_update_id = 0

def bot_loop():
    global last_update_id
    print("🤖 Bot Pro đang chạy...")
    
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
    print("=" * 60)
    print("🤖 BLOX FRUIT PRO BOT - Tư vấn viên: PHÁT")
    print("=" * 60)
    print(f"✅ Shop: {SHOP_NAME}")
    print(f"✅ Contact: {SHOP_CONTACT}")
    print(f"✅ Tư vấn viên: Phát (Chuyên gia BF)")
    print("=" * 60)
    
    if not TELEGRAM_TOKEN:
        print("❌ Thiếu TELEGRAM_BOT_TOKEN")
        return
    
    keep_alive_thread = threading.Thread(target=start_keep_alive, daemon=True)
    keep_alive_thread.start()
    
    print("\n🚀 Khởi động...\n")
    bot_loop()

if __name__ == "__main__":
    main()
