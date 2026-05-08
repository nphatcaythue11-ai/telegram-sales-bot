"""
TELEGRAM BOT - CHUYÊN GIA TƯ VẤN BLOX FRUIT GOD LEVEL
Tư vấn viên: Phát | Hiểu mọi ngôn ngữ | Chốt đơn thần thánh
"""

import http.client
import json
import os
import time
import random
import threading
import re
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Optional

# ========== CONFIG ==========
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
SHOP_NAME = os.environ.get('SHOP_NAME', 'Blox Fruit Store')
SHOP_CONTACT = os.environ.get('SHOP_CONTACT', '@admin_bloxfruit')

# ========== SẢN PHẨM: Chỉ 1 acc 450k 6 perm ==========
THE_ACCOUNT = {
    "id": "bf-450k-6perm",
    "name": "Blox Fruit 6 Perm",
    "price": 450000,
    "price_str": "450.000đ",
    "level": "Max 2550",
    "fruit": "Leopard/Dough/Venom",
    "perms": ["2x Money", "2x Drop", "Fast Boats", "Fruit Notifier", "2x Mastery", "God Human"],
    "stats": {"melee": "Max", "defense": "Max", "sword": "Max", "gun": "Max", "fruit": "Max"},
    "items": ["Cursed Dual Katana", "Soul Guitar", "Valkyrie Helm"],
    "beli": "50M+",
    "fragments": "50k+",
    "stock": 5,
    "desc": "Acc max level, 6 perm đầy đủ, fruit hiếm, full item",
    "image_url": "https://i.imgur.com/bf450k.jpg",
    "screenshots": ["https://i.imgur.com/bf450k_1.jpg", "https://i.imgur.com/bf450k_2.jpg"]
}

# ========== FRUIT PRICES DATABASE (Robux) ==========
# Giá PERM trong game - CẬP NHẬT MỚI NHẤT
FRUIT_PRICES_RB = {
    # Common
    "Rocket": 50, "Spin": 75, "Blade": 100, "Spring": 180, "Bomb": 220,
    "Smoke": 250, "Spike": 380,
    # Uncommon  
    "Flame": 550, "Ice": 750, "Sand": 850, "Dark": 950, "Eagle": 975,
    "Diamond": 1000, "Light": 1100, "Rubber": 1200,
    # Rare
    "Ghost": 1275, "Magma": 1300, "Quake": 1500, "Buddha": 1650, "Love": 1700,
    "Creation": 1750,
    # Legendary
    "Spider": 1800, "Sound": 1900, "Phoenix": 2000, "Portal": 2000,
    "Rumble": 2100, "Pain": 2200, "Blizzard": 2250, "Gravity": 2300,
    # Mythic
    "Mammoth": 2350, "T-Rex": 2350, "Dough": 2400, "Shadow": 2425,
    "Venom": 2450, "Gas": 2500, "Spirit": 2550, "Leopard": 3000,
    "Tiger": 3000, "Yeti": 3000, "Kitsune": 4000, "Control": 4000,
    "East Dragon": 5000, "West Dragon": 5000,
}

# ========== GAMEPASS PRICES ==========
GAMEPASS_PRICES_RB = {
    "+1 Fruit Storage": 400,
    "2x Mastery": 450,
    "2x Money": 450,
    "Fast Boats": 350,
    "2x Boss Drops": 350,
    "Dark Blade": 1200,
    "Legendary Scrolls": 800,
    "Mythical Scrolls": 1500,
    "Fruit Notifier": 2700,
}

# TỶ LỆ QUY ĐỔI (Rate) - CÓ THỂ THAY ĐỔI
# VD: RT = 130 nghĩa là 1 RB = 130 VNĐ
FRUIT_RATE = 130  # Đồng/Robux - THAY ĐỔI ĐƯỢC

def calculate_fruit_price(fruit_name: str, rate: int = FRUIT_RATE) -> dict:
    """Tính giá trái cây theo tỷ lệ"""
    fruit_name = fruit_name.title()
    if fruit_name in FRUIT_PRICES_RB:
        rb_price = FRUIT_PRICES_RB[fruit_name]
        vnd_price = rb_price * rate
        return {
            "fruit": fruit_name,
            "rb": rb_price,
            "rate": rate,
            "vnd": vnd_price,
            "vnd_str": f"{vnd_price:,}đ"
        }
    return None

def calculate_gamepass_price(gp_name: str, rate: int = FRUIT_RATE) -> dict:
    """Tính giá gamepass theo tỷ lệ"""
    # Tìm gamepass gần đúng
    for name, rb in GAMEPASS_PRICES_RB.items():
        if gp_name.lower() in name.lower() or name.lower() in gp_name.lower():
            vnd_price = rb * rate
            return {
                "name": name,
                "rb": rb,
                "rate": rate,
                "vnd": vnd_price,
                "vnd_str": f"{vnd_price:,}đ"
            }
    return None

def get_all_gamepass_prices(rate: int = FRUIT_RATE) -> list:
    """Lấy tất cả giá gamepass"""
    result = []
    for name, rb in sorted(GAMEPASS_PRICES_RB.items(), key=lambda x: x[1]):
        vnd = rb * rate
        result.append({
            "name": name,
            "rb": rb,
            "vnd": vnd,
            "vnd_str": f"{vnd:,}đ"
        })
    return result

def get_all_fruit_prices(rate: int = FRUIT_RATE) -> list:
    """Lấy tất cả giá trái theo tỷ lệ"""
    result = []
    for fruit, rb in sorted(FRUIT_PRICES_RB.items(), key=lambda x: x[1]):
        vnd = rb * rate
        result.append({
            "fruit": fruit,
            "rb": rb,
            "vnd": vnd,
            "vnd_str": f"{vnd:,}đ"
        })
    return result

def search_fruits_by_price_range(min_vnd: int, max_vnd: int, rate: int = FRUIT_RATE) -> list:
    """Tìm trái theo khoảng giá"""
    result = []
    for fruit, rb in FRUIT_PRICES_RB.items():
        vnd = rb * rate
        if min_vnd <= vnd <= max_vnd:
            result.append({"fruit": fruit, "rb": rb, "vnd": vnd, "vnd_str": f"{vnd:,}đ"})
    return result

# ========== CHUYÊN GIA AI - PHÁT ==========
class ExpertAI:
    """Chuyên gia tư vấn Blox Fruit - Hiểu mọi ngôn ngữ"""
    
    def __init__(self):
        self.memory: Dict[int, dict] = {}  # Trí nhớ user
        self.conversation_history: Dict[int, List[dict]] = {}  # Lịch sử chat
        self.buying_stage: Dict[int, str] = {}  # Giai đoạn mua
        self.user_emotions: Dict[int, str] = {}  # Cảm xúc user
        
    def understand(self, text: str, user_id: int) -> dict:
        """Phân tích sâu ý định người dùng"""
        text = text.lower().strip()
        
        # Lưu vào trí nhớ
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        self.conversation_history[user_id].append({"role": "user", "content": text, "time": datetime.now()})
        
        # PHÂN TÍCH ĐA TẦNG
        analysis = {
            # === CẢM XÚC ===
            "emotion": self._detect_emotion(text),
            "urgency": self._detect_urgency(text),
            "budget_hint": self._detect_budget(text),
            
            # === Ý ĐỊNH MUA ===
            "intent": self._classify_intent(text),
            "buying_stage": self.buying_stage.get(user_id, "awareness"),
            "objections": self._detect_objections(text),
            
            # === THÔNG TIN CẦN ===
            "needs": self._extract_needs(text),
            "questions": self._extract_questions(text),
            
            # === NGÔN NGỮ ===
            "style": self._detect_comm_style(text),
            "slang": self._detect_slang(text),
        }
        
        return analysis
    
    def _detect_emotion(self, text: str) -> str:
        """Phát hiện cảm xúc"""
        emotions = {
            "excited": ["wow", "tuyệt", "đỉnh", "quá đẹp", "quá ngon", " thích quá", "muốn mua ngay", "chốt", "lấy liền"],
            "interested": ["hay đấy", "được đó", "cũng ổn", "khá ngon", "ngon", "tạm được", "xem thử", "cho xem"],
            "hesitant": ["để suy nghĩ", "để cân nhắc", "từ từ", "chưa chắc", "phân vân", "lăn tăn", "ngại quá"],
            "skeptical": ["lừa đảo", "scam", "tin được không", "có thật không", "sợ", "ngại", "lo lắng"],
            "price_conscious": ["đắt", "mắc", "rẻ hơn được không", "giảm đi", "sale", "khuyến mãi"],
            "urgent": ["gấp", "nhanh", "ngay", "làm liền", "cần gấp", "muốn ngay"],
            "casual": ["thôi", "để đó", "kệ", "không biết", "tùy", "gì cũng được"]
        }
        
        for emotion, keywords in emotions.items():
            if any(kw in text for kw in keywords):
                return emotion
        return "neutral"
    
    def _detect_urgency(self, text: str) -> int:
        """Phát hiện mức độ gấp 0-10"""
        urgent_words = ["gấp", "ngay", "nhanh", "làm liền", "cần ngay", "muốn ngay", "chờ không nổi"]
        return min(10, sum(2 for word in urgent_words if word in text))
    
    def _detect_budget(self, text: str) -> Optional[int]:
        """Phát hiện ngân sách từ text"""
        # Tìm số tiền trong text
        patterns = [
            r'(\d+)k',
            r'(\d+)\s*nghìn',
            r'(\d+)\s*ngàn',
            r'(\d{3,6})\s*đ',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                num = int(match.group(1))
                if num < 1000:
                    return num * 1000
                return num
        return None
    
    def _classify_intent(self, text: str) -> str:
        """Phân loại ý định nâng cao"""
        # === BUYING SIGNALS ===
        strong_buy = ["chốt", "lấy", "mua luôn", "ok", "được", "chuyển khoản", "thanh toán", "ck"]
        if any(w in text for w in strong_buy):
            return "strong_buy"
        
        weak_buy = ["tính", "định", "suy nghĩ", "cân nhắc", "xem xét", "tìm hiểu thêm"]
        if any(w in text for w in weak_buy):
            return "considering"
        
        # === INFO GATHERING ===
        price_q = ["bao nhiêu", "giá", "bn", "giá sao", "tiền", "k", "ngàn", "nghìn", "đồng"]
        if any(w in text for w in price_q):
            return "ask_price"
        
        quality_q = ["có tốt không", "uy tín", "scam", "lừa", "có thật", "đảm bảo", "bảo hành"]
        if any(w in text for w in quality_q):
            return "ask_trust"
        
        product_q = ["có gì", "có acc", "acc nào", "có loại", "có mấy", "có không"]
        if any(w in text for w in product_q):
            return "ask_product"
        
        # === FRUIT PRICE QUERIES ===
        fruit_q = ["trái", "fruit", "quỷ", "bán trái", "giá trái", "mua trái", "dough", "dragon", 
                   "leopard", "tiger", "venom", "buddha", "portal", "control", "spirit", "shadow", "phoenix",
                   "t-rex", "trex", "mammoth", "yeti", "kitsune", "gas", "blizzard", "rumble", "sound",
                   "spider", "love", "quake", "magma", "ghost", "creation", "barrier", "rubber", "light",
                   "diamond", "dark", "sand", "ice", "eagle", "flame", "spike", "smoke", "bomb",
                   "spring", "blade", "chop", "spin", "rocket", "east dragon", "west dragon", "rồng đông", "rồng tây"]
        if any(w in text.lower() for w in fruit_q):
            # Kiểm tra có phải hỏi giá không
            price_indicators = ["giá", "bao nhiêu", "bn", "tiền", "mua", "bán", "k", "nghìn", "ngàn"]
            if any(p in text for p in price_indicators):
                return "ask_fruit_price"
            return "ask_product"
        
        image_q = ["ảnh", "hình", "xem", "screenshot", "preview", "chụp", "hình ảnh"]
        if any(w in text for w in image_q):
            return "ask_image"
        
        # === GAMEPASS QUERIES ===
        gamepass_q = ["gamepass", "2x money", "2x drop", "fast boats", "fruit notifier", 
                      "dark blade", "mastery", "storage", "scrolls", "boss drops", 
                      "2x mastery", "legendary scrolls", "mythical scrolls", "+1 fruit"]
        if any(w in text.lower() for w in gamepass_q):
            price_indicators = ["giá", "bao nhiêu", "bn", "tiền", "mua", "bán"]
            if any(p in text for p in price_indicators):
                return "ask_gamepass_price"
            return "ask_product"
        
        comparison = ["so sánh", "khác nhau", "nên chọn", "con nào", "loại nào", "hơn", "kém"]
        if any(w in text for w in comparison):
            return "compare"
        
        # === NEGOTIATION ===
        negotiate = ["giảm", "rẻ", "sale", "chiết khấu", "đắt", "mắc", "khuyến mãi", "giảm giá"]
        if any(w in text for w in negotiate):
            return "negotiate"
        
        # === OBJECTIONS ===
        objection = ["để sau", "thôi", "không mua", "bỏ", "không cần", "kệ", "hủy", "cancel"]
        if any(w in text for w in objection):
            return "objection"
        
        # === CHAT ===
        greeting = ["chào", "hi", "hello", "alo", "hú", "ê", "chào buổi", "chào anh", "chào chị"]
        if any(w in text for w in greeting):
            return "greeting"
        
        thanks = ["cảm ơn", "thank", "thanks", "cám ơn", "tks", "ok", "okie"]
        if any(w in text for w in thanks):
            return "thanks"
        
        return "general_chat"
    
    def _detect_objections(self, text: str) -> List[str]:
        """Phát hiện các phản đối"""
        objections = []
        
        if any(w in text for w in ["đắt", "mắc", "giá cao", "không đủ tiền"]):
            objections.append("price")
        if any(w in text for w in ["sợ scam", "lừa đảo", "tin được không", "có thật không"]):
            objections.append("trust")
        if any(w in text for w in ["để suy nghĩ", "để xem", "chưa chắc", "từ từ"]):
            objections.append("time")
        if any(w in text for w in ["không cần", "thôi", "bỏ", "hủy", "không mua"]):
            objections.append("not_interested")
            
        return objections
    
    def _extract_needs(self, text: str) -> List[str]:
        """Trích xuất nhu cầu"""
        needs = []
        
        if any(w in text for w in ["chơi mới", "bắt đầu", "mới chơi", "tập chơi"]):
            needs.append("beginner")
        if any(w in text for w in ["đua top", "top server", "mạnh", "pro", "cày"]):
            needs.append("competitive")
        if any(w in text for w in ["đẹp", "ngầu", "hiếm", "vip", "xịn", "đỉnh"]):
            needs.append("prestige")
        if any(w in text for w in ["rẻ", "tiết kiệm", "sinh viên", "ít tiền", "giá thấp"]):
            needs.append("budget")
            
        return needs
    
    def _extract_questions(self, text: str) -> List[str]:
        """Trích xuất câu hỏi"""
        questions = []
        
        # Câu hỏi về giá
        if "bao nhiêu" in text or "giá" in text or "tiền" in text:
            questions.append("price")
        
        # Câu hỏi về chất lượng
        if any(w in text for w in ["có tốt không", "như thế nào", "ra sao", "uy tín"]):
            questions.append("quality")
        
        # Câu hỏi về thời gian
        if any(w in text for w in ["bao lâu", "khi nào", "mấy phút", "nhanh không"]):
            questions.append("time")
            
        return questions
    
    def _detect_comm_style(self, text: str) -> str:
        """Phát hiện phong cách giao tiếp"""
        if len(text) < 10:
            return "brief"
        if any(w in text for w in ["ạ", "dạ", "em", "anh", "chị"]):
            return "polite"
        if any(w in text for w in ["mày", "tao", "đm", "vcl", "cc"]):
            return "slang_rough"
        if any(w in text for w in ["bạn", "mình", "nha", "nè", "á"]):
            return "friendly"
        return "neutral"
    
    def _detect_slang(self, text: str) -> List[str]:
        """Phát hiện slang/từ lóng"""
        slang_dict = {
            "chốt": "buy_now",
            "k": "không",
            "ok": "đồng ý",
            "okie": "đồng ý",
            "dc": "được",
            "đc": "được",
            "j": "gì",
            "z": "vậy",
            "zô": "vô",
            "luôn": "ngay",
            "nhanh": "gấp",
            "ngay": "gấp",
        }
        detected = []
        for word, meaning in slang_dict.items():
            if word in text:
                detected.append(f"{word}={meaning}")
        return detected
    
    def respond(self, user_id: int, text: str) -> dict:
        """Tạo phản hồi thông minh"""
        analysis = self.understand(text, user_id)
        
        # Cập nhật stage
        current_stage = self.buying_stage.get(user_id, "awareness")
        
        # CHIẾN LƯỢC PHẢN HỒI THEO STAGE
        if analysis["intent"] == "greeting":
            return self._handle_greeting(user_id, analysis)
        
        if analysis["intent"] == "ask_price":
            return self._handle_price_inquiry(user_id, analysis)
        
        if analysis["intent"] == "ask_fruit_price":
            return self._handle_fruit_price(user_id, analysis, text)
        
        if analysis["intent"] == "ask_gamepass_price":
            return self._handle_gamepass_price(user_id, analysis, text)
        
        if analysis["intent"] == "ask_trust":
            return self._handle_trust_objection(user_id, analysis)
        
        if analysis["intent"] == "ask_product":
            return self._handle_product_inquiry(user_id, analysis)
        
        if analysis["intent"] == "ask_image":
            return self._handle_image_request(user_id, analysis)
        
        if analysis["intent"] == "strong_buy":
            return self._handle_strong_buy(user_id, analysis)
        
        if analysis["intent"] == "considering":
            return self._handle_considering(user_id, analysis)
        
        if analysis["intent"] == "negotiate":
            return self._handle_negotiation(user_id, analysis)
        
        if analysis["intent"] == "objection":
            return self._handle_objection(user_id, analysis)
        
        if analysis["intent"] == "thanks":
            return self._handle_thanks(user_id, analysis)
        
        # GENERAL CHAT
        return self._handle_general(user_id, analysis, text)
    
    # ===== HANDLER FUNCTIONS =====
    
    def _handle_greeting(self, user_id, analysis):
        """Xử lý chào hỏi"""
        emotion = analysis.get("emotion", "neutral")
        
        responses = {
            "excited": "👋 *Chào anh/chị!* Em Phát đây! Thấy anh/chị hào hứng quá, chắc là đang muốn sắm acc Blox Fruit xịn đây! 😄",
            "interested": "👋 *Xin chào!* Em Phát chuyên tư vấn Blox Fruit. Anh/chị đang tìm acc phù hợp phải không ạ?",
            "casual": "👋 *Chào!* Em Phát đây. Cần tư vấn Blox Fruit gì không ạ?",
        }
        
        msg = responses.get(emotion, "👋 *Chào anh/chị!* Em Phát - chuyên gia Blox Fruit. Anh/chị cần hỗ trợ gì ạ?")
        
        return {
            "type": "text",
            "content": msg + "\n\n🎮 *Acc hot nhất hiện tại:*\n🔥 Blox Fruit 6 Perm - 450k\n• Max level 2550\n• 6 gamepass đầy đủ\n• Fruit hiếm\n\nGõ 'xem' hoặc 'giá' để biết thêm!",
            "next_action": None
        }
    
    def _handle_price_inquiry(self, user_id, analysis):
        """Xử lý hỏi giá"""
        budget = analysis.get("budget_hint")
        
        msg = f"""💰 *GIÁ ACC BLOX FRUIT*

🎯 *ACC 6 PERM (Hot nhất)*
💵 Giá: *450.000đ*

📊 *Trong acc có:*
✅ Level Max 2550 (full stats)
✅ 6 Gamepass đầy đủ:
   • 2x Money, 2x Drop
   • Fast Boats, Fruit Notifier
   • 2x Mastery, God Human
✅ Fruit hiếm (Leopard/Dough/Venom)
✅ Beli 50M+, Fragments 50k+
✅ Item hiếm: CDK, Soul Guitar

🎁 *Quà tặng kèm:*
• Hướng dẫn chơi
• Support sau mua
• Bảo hành 7 ngày

💡 *So với tự cày:*
• Tiết kiệm 2-3 tuần cày
• Không cần roll fruit (tiết kiệm 200k+)
• Vào chơi max ngay

Anh/chị thấy giá hợp lý không ạ? 😊"""

        return {"type": "text", "content": msg, "next_action": "ask_commitment"}
    
    def _handle_fruit_price(self, user_id, analysis, text):
        """Xử lý hỏi giá trái cây - Tính RB × RT"""
        text_lower = text.lower()
        
        # Tìm tên trái trong tin nhắn
        found_fruit = None
        for fruit in FRUIT_PRICES_RB.keys():
            if fruit.lower() in text_lower:
                found_fruit = fruit
                break
        
        # Nếu tìm thấy trái cụ thể
        if found_fruit:
            price_info = calculate_fruit_price(found_fruit, FRUIT_RATE)
            
            # Kiểm tra có đề cập đến rate khác không
            rate_match = re.search(r'(\d+)', text)
            custom_rate = None
            if rate_match:
                potential_rate = int(rate_match.group(1))
                if 50 <= potential_rate <= 500 and potential_rate != FRUIT_RATE:
                    custom_rate = potential_rate
                    price_info = calculate_fruit_price(found_fruit, custom_rate)
            
            rate_text = f"Tỷ lệ: 1 RB = {price_info['rate']}đ"
            if custom_rate:
                rate_text += " (tỷ lệ tùy chỉnh)"
            
            msg = f"""🍎 *GIÁ TRÁI {found_fruit.upper()}*

💎 *Trong game:* {price_info['rb']:,} RB
📊 *Tỷ lệ:* 1 RB = {price_info['rate']:,}đ
💰 *Giá bán:* **{price_info['vnd_str']}**

{rate_text}

✨ *So sánh:*
• Mua trong game: {price_info['rb']:,} RB (khó kiếm)
• Mua ở Phát: {price_info['vnd_str']} (nhanh gọn)
• Tiết kiệm: Không cần cày/nạp Robux

💡 *Có thể thay đổi tỷ lệ:*
Nhắn "giá {found_fruit} tỷ lệ 120" để tính với tỷ lệ khác!

Muốn mua trái này không ạ? 🛒"""
            
            return {"type": "text", "content": msg, "next_action": "ask_fruit_buy"}
        
        # Nếu không tìm thấy trái cụ thể - hiện bảng giá
        all_prices = get_all_fruit_prices(FRUIT_RATE)
        
        # Phân loại theo tier
        common = [f for f in all_prices if f['rb'] <= 200]
        uncommon = [f for f in all_prices if 200 < f['rb'] <= 800]
        rare = [f for f in all_prices if 800 < f['rb'] <= 1500]
        legendary = [f for f in all_prices if 1500 < f['rb'] <= 2500]
        mythic = [f for f in all_prices if f['rb'] > 2500]
        
        msg = f"""🍎 *BẢNG GIÁ TRÁI CÂY BLOX FRUIT*
📊 *Tỷ lệ quy đổi:* 1 RB = {FRUIT_RATE}đ

💚 *Common (Dễ kiếm):*
"""
        for f in common[:5]:
            msg += f"• {f['fruit']}: {f['rb']} RB = {f['vnd_str']}\n"
        
        msg += f"""
💙 *Uncommon:*
"""
        for f in uncommon[:5]:
            msg += f"• {f['fruit']}: {f['rb']} RB = {f['vnd_str']}\n"
        
        msg += f"""
💜 *Rare:*
• Buddha: 1,200 RB = {calculate_fruit_price('Buddha')['vnd_str']}
• Love: 1,300 RB = {calculate_fruit_price('Love')['vnd_str']}

💛 *Legendary:*
• Portal: 1,900 RB = {calculate_fruit_price('Portal')['vnd_str']}
• Rumble: 2,100 RB = {calculate_fruit_price('Rumble')['vnd_str']}
• Blizzard: 2,400 RB = {calculate_fruit_price('Blizzard')['vnd_str']}

❤️ *Mythic (Hiếm):*
• Dough: 2,800 RB = {calculate_fruit_price('Dough')['vnd_str']}
• Dragon: 3,500 RB = {calculate_fruit_price('Dragon')['vnd_str']}
• Leopard: 5,000 RB = {calculate_fruit_price('Leopard')['vnd_str']}
• Kitsune: 8,000 RB = {calculate_fruit_price('Kitsune')['vnd_str']}

💡 *Cách mua:*
Nhắn "giá + tên trái" vd: "giá Dough", "giá Leopard"

🎯 *Ưu đãi:* Mua kèm acc giảm 10% giá trái!

Trái nào anh/chị thích? 🍎"""
        
        return {"type": "text", "content": msg, "next_action": "ask_fruit_selection"}
    
    def _handle_gamepass_price(self, user_id, analysis, text):
        """Xử lý hỏi giá Gamepass"""
        text_lower = text.lower()
        
        # Tìm gamepass cụ thể
        found_gp = None
        for gp_name in GAMEPASS_PRICES_RB.keys():
            if gp_name.lower() in text_lower:
                found_gp = gp_name
                break
            # Check từ khóa rút gọn
            if "2x money" in text_lower and "money" in gp_name.lower():
                found_gp = gp_name
                break
            if "mastery" in text_lower and "mastery" in gp_name.lower():
                found_gp = gp_name
                break
            if "fast boat" in text_lower or "thuyền" in text_lower:
                found_gp = "Fast Boats"
                break
            if "fruit notifier" in text_lower or "notifier" in text_lower:
                found_gp = "Fruit Notifier"
                break
            if "dark blade" in text_lower or "kiếm" in text_lower():
                found_gp = "Dark Blade"
                break
            if "storage" in text_lower or "kho" in text_lower():
                found_gp = "+1 Fruit Storage"
                break
            if "scroll" in text_lower or "cuộn" in text_lower():
                if "legendary" in text_lower:
                    found_gp = "Legendary Scrolls"
                elif "mythical" in text_lower or "mythic" in text_lower:
                    found_gp = "Mythical Scrolls"
                break
        
        if found_gp:
            price_info = calculate_gamepass_price(found_gp, FRUIT_RATE)
            
            # Check tỷ lệ tùy chỉnh
            rate_match = re.search(r'(\d+)', text)
            custom_rate = None
            if rate_match:
                potential_rate = int(rate_match.group(1))
                if 50 <= potential_rate <= 500 and potential_rate != FRUIT_RATE:
                    custom_rate = potential_rate
                    price_info = calculate_gamepass_price(found_gp, custom_rate)
            
            msg = f"""⚡ *GIÁ GAMEPASS {price_info['name'].upper()}*

💎 *Trong game:* {price_info['rb']:,} RB
📊 *Tỷ lệ:* 1 RB = {price_info['rate']}đ
💰 *Giá bán:* **{price_info['vnd_str']}**

✨ *So sánh:*
• Mua trong game: Cần nạp Robux (khó)
• Mua ở Phát: {price_info['vnd_str']} (nhanh, rẻ hơn)

💡 *Có thể đổi tỷ lệ:*
Nhắn "giá {price_info['name']} tỷ lệ 120"

🎁 *Ưu đãi:* Mua kèm acc giảm 10%!

Muốn mua gamepass này không ạ? 🛒"""
            
            return {"type": "text", "content": msg, "next_action": "ask_gamepass_buy"}
        
        # Hiện bảng giá tất cả gamepass
        all_gp = get_all_gamepass_prices(FRUIT_RATE)
        
        msg = f"""⚡ *BẢNG GIÁ GAMEPASS BLOX FRUIT*
📊 Tỷ lệ: 1 RB = {FRUIT_RATE}đ

🎯 *GAMEPASS CƠ BẢN:*
"""
        for gp in all_gp[:4]:
            msg += f"• {gp['name']}: {gp['rb']} RB = {gp['vnd_str']}\n"
        
        msg += f"""
⚔️ *GAMEPASS ĐẶC BIỆT:*
"""
        for gp in all_gp[4:]:
            msg += f"• {gp['name']}: {gp['rb']} RB = {gp['vnd_str']}\n"
        
        msg += f"""
💡 *Cách mua:*
Nhắn "giá + tên gamepass"
VD: "giá 2x Money", "giá Fruit Notifier"

🎁 *Ưu đãi:*
• Mua kèm acc: Giảm 10%
• Mua combo 2 GP: Giảm 15%
• Mua combo 3 GP+: Giảm 20%

Gamepass nào anh/chị cần? ⚡"""
        
        return {"type": "text", "content": msg, "next_action": "ask_gamepass_selection"}
    
    def _handle_trust_objection(self, user_id, analysis):
        """Xử lý nghi ngờ uy tín"""
        return {
            "type": "text",
            "content": """✅ *VỀ UY TÍN CỦA PHÁT*

📊 *Thông tin shop:*
• Đã bán 500+ acc thành công
• Group feedback 1000+ thành viên
• Hoạt động 2 năm+
• Rating 4.9/5 ⭐⭐⭐⭐⭐

🛡️ *Cam kết:*
• Bảo hành 7 ngày đổi trả
• Hoàn tiền 100% nếu không đúng mô tả
• Giao acc trong 1-2 phút sau CK
• Hỗ trợ trọn đời khi chơi

📸 *Minh bạch:*
• Có video check acc trước khi giao
• Chụp màn hình giao dịch
• Info đổi ngay sau thanh toán

💬 *Feedback khách:*
"Mua 3 acc rồi, uy tín 100%" - Minh A.
"Giao nhanh, acc đúng mô tả" - Huy B.

Anh/chị yên tâm mua nhé! 🙏""",
            "next_action": "ask_commitment"
        }
    
    def _handle_product_inquiry(self, user_id, analysis):
        """Xử lý hỏi sản phẩm"""
        return {
            "type": "text",
            "content": """🎮 *THÔNG TIN ACC BLOX FRUIT*

📦 *Tên:* Blox Fruit 6 Perm
💰 *Giá:* 450.000đ
📊 *Level:* Max 2550 (All stats max)
🍎 *Fruit:* Leopard/Dough/Venom (random)

⚡ *6 PERM ĐẦY ĐỦ:*
1️⃣ 2x Money - Farm beli nhanh
2️⃣ 2x Drop - Rớt item dễ hơn
3️⃣ Fast Boats - Di chuyển nhanh
4️⃣ Fruit Notifier - Biết fruit spawn
5️⃣ 2x Mastery - Lên cấp nhanh
6️⃣ God Human - Tộc mạnh nhất

🎒 *Item có sẵn:*
• Cursed Dual Katana (Hiếm)
• Soul Guitar (Hiếm)
• Valkyrie Helm (Hiếm)
• Beli: 50M+
• Fragments: 50k+

✨ *Ưu điểm:*
• Vào chơi max ngay
• Không cần cày
• Đủ sức đua top
• Farm boss dễ dàng

Cần xem ảnh acc không ạ? 📸""",
            "next_action": "ask_image"
        }
    
    def _handle_image_request(self, user_id, analysis):
        """Xử lý yêu cầu ảnh"""
        return {
            "type": "image",
            "image_url": THE_ACCOUNT["image_url"],
            "caption": f"""📸 *ẢNH ACC BLOX FRUIT 6 PERM*

💰 Giá: {THE_ACCOUNT['price_str']}
📊 Level: {THE_ACCOUNT['level']}
🍎 Fruit: {THE_ACCOUNT['fruit']}
⚡ 6 Perm đầy đủ
✅ Max stats 2550

🎁 *Tặng kèm:* Hướng dẫn chơi + Support

Còn {THE_ACCOUNT['stock']} acc cuối!
Chốt ngay không anh/chị? 💪""",
            "next_action": "strong_close"
        }
    
    def _handle_strong_buy(self, user_id, analysis):
        """Xử lý tín hiệu mua mạnh"""
        self.buying_stage[user_id] = "closing"
        
        return {
            "type": "text",
            "content": """🎉 *TUYỆT VỜI!*

Anh/chị chốt acc Blox Fruit 6 Perm - 450k phải không ạ?

💳 *THANH TOÁN:*
📱 ZaloPay: `0343603537`
🏦 BIDV: `8806532434`
👤 Chủ TK: TRAN NGUYEN PHAT

💰 *Số tiền:* 450.000đ

📌 *Các bước:*
1️⃣ Chuyển khoản đúng số tiền
2️⃣ Chụp màn hình gửi Phát
3️⃣ Nhận acc trong 1-2 phút
4️⃣ Vào chơi max ngay!

⚡ *Ưu đãi thêm:*
Nếu CK trong 30 phút tặng thêm 10k belly!

Sẵn sàng chuyển khoản chưa anh/chị? 🚀""",
            "next_action": "wait_payment"
        }
    
    def _handle_considering(self, user_id, analysis):
        """Xử lý đang cân nhắc"""
        objections = analysis.get("objections", [])
        
        msg = """🤔 *Em hiểu anh/chị đang cân nhắc...*

💡 *Để em giúp anh/chị quyết định:*

✨ *So với tự cày:*
• Cày lên 2550 mất 2-3 tuần
• Roll 6 perm tốn 500k+
• Roll fruit hiếm tốn 200k+
• = Tổng cộng 700k+ và 1 tháng

💰 *Mua acc 450k:*
• Có ngay acc max
• Tiết kiệm 250k+
• Tiết kiệm 1 tháng cày
• Vào chơi được luôn

🎁 *Thêm nữa:*
• Bảo hành 7 ngày
• Hoàn tiền nếu không đúng
• Support trọn đời

Còn phân vân điều gì không ạ? Em giải đáp ngay! 😊"""

        if "price" in objections:
            msg += "\n\n💵 *Về giá 450k:*\nGiá này đã rẻ hơn thị trường 100k rồi ạ. Acc max 6 perm thường bán 550k-600k đó!"
        
        return {"type": "text", "content": msg, "next_action": "address_objections"}
    
    def _handle_negotiation(self, user_id, analysis):
        """Xử lý trả giá"""
        return {
            "type": "text",
            "content": """💰 *VỀ GIÁ 450K*

Em hiểu anh/chị muốn giá tốt hơn 😊

📊 *Thực tế:*
• Acc max 6 perm thị trường bán 550k-600k
• Em bán 450k đã rẻ hơn 100k+
• Giá này chỉ hòa vốn, không lãi nhiều

🎁 *Em có thể tặng thêm:*
• 50k belly trong game
• Hướng dẫn farm nhanh
• Tips đi boss hiệu quả

⚡ *Nếu mua ngay hôm nay:*
Giữ giá 450k + tặng thêm quà!

Anh/chị chốt để em chuẩn bị acc nhé? 💪""",
            "next_action": "soft_close"
        }
    
    def _handle_objection(self, user_id, analysis):
        """Xử lý từ chối"""
        return {
            "type": "text",
            "content": """😔 *Em hiểu anh/chị chưa muốn mua ngay...*

*Không sao ạ!* 😊

📌 *Em lưu lại thông tin:*
• Acc Blox Fruit 6 Perm - 450k
• Còn {THE_ACCOUNT['stock']} acc

🎁 *Nếu đổi ý trong 24h:*
Em vẫn giữ giá 450k + ưu đãi!

💬 *Cần tư vấn gì thêm:*
Cứ nhắn Phát bất cứ lúc nào nhé!

Cảm ơn anh/chị đã quan tâm! 🙏""",
            "next_action": "follow_up_later"
        }
    
    def _handle_thanks(self, user_id, analysis):
        """Xử lý cảm ơn"""
        return {
            "type": "text",
            "content": """🙏 *Không có gì đâu anh/chị!*

Em Phát luôn sẵn sàng hỗ trợ! 

💬 *Cần gì cứ nhắn:*
• Tư vấn chơi Blox Fruit
• Hỗ trợ kỹ thuật
• Mua thêm acc/dịch vụ

Chúc anh/chị chơi game vui vẻ! 🎮

*Phát - Chuyên gia Blox Fruit* 😊""",
            "next_action": None
        }
    
    def _handle_general(self, user_id, analysis, text):
        """Xử lý chung - AI linh hoạt"""
        emotion = analysis.get("emotion", "neutral")
        style = analysis.get("style", "neutral")
        
        # Phản hồi thông minh dựa trên ngữ cảnh
        responses = [
            "Em Phát chưa hiểu ý anh/chị lắm 😅 Anh/chị muốn tìm hiểu về acc Blox Fruit 450k hay cần hỗ trợ gì ạ?",
            
            "Dạ em chưa rõ lắm... Anh/chị có thể nói rõ hơn không ạ? Ví dụ: 'giá bao nhiêu', 'có ảnh không', 'muốn mua'...",
            
            "Em đang lắng nghe anh/chị đây! 😊 Anh/chị cần tư vấn Blox Fruit gì ạ? Acc 450k 6 perm đang hot lắm!",
            
            f"Hihi em chưa hiểu ý anh/chị {'ạ' if style == 'polite' else ''} 😄 Anh/chị muốn xem acc Blox Fruit không? Gõ 'xem' hoặc 'ảnh' nhé!",
        ]
        
        return {
            "type": "text",
            "content": random.choice(responses),
            "next_action": "clarify"
        }

# Khởi tạo AI
god_ai = ExpertAI()

# ========== TELEGRAM FUNCTIONS ==========
def send_message(chat_id, text):
    try:
        conn = http.client.HTTPSConnection("api.telegram.org")
        payload = json.dumps({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })
        headers = {"Content-type": "application/json"}
        conn.request("POST", f"/bot{TELEGRAM_TOKEN}/sendMessage", payload, headers)
        conn.close()
    except Exception as e:
        print(f"❌ Lỗi gửi tin: {e}")

def send_photo(chat_id, photo_url, caption=""):
    try:
        conn = http.client.HTTPSConnection("api.telegram.org")
        payload = json.dumps({
            "chat_id": chat_id,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": "Markdown"
        })
        headers = {"Content-type": "application/json"}
        conn.request("POST", f"/bot{TELEGRAM_TOKEN}/sendPhoto", payload, headers)
        conn.close()
    except Exception as e:
        print(f"❌ Lỗi gửi ảnh: {e}")

def send_typing(chat_id):
    try:
        conn = http.client.HTTPSConnection("api.telegram.org")
        payload = json.dumps({"chat_id": chat_id, "action": "typing"})
        headers = {"Content-type": "application/json"}
        conn.request("POST", f"/bot{TELEGRAM_TOKEN}/sendChatAction", payload, headers)
        conn.close()
    except:
        pass

def get_updates(offset=0):
    try:
        conn = http.client.HTTPSConnection("api.telegram.org")
        conn.request("GET", f"/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&limit=10")
        response = conn.getresponse()
        result = json.loads(response.read().decode())
        conn.close()
        return result
    except Exception as e:
        print(f"❌ Lỗi get updates: {e}")
        return None

# ========== KEEP ALIVE ==========
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>Phat Bot - God Level AI Running!</h1>")
    def log_message(self, *args): pass

def start_keep_alive():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), KeepAliveHandler)
    print(f"✅ Server port {port}")
    server.serve_forever()

# ========== MESSAGE HANDLER ==========
def handle_message(msg):
    chat_id = msg['chat']['id']
    user_id = msg['from']['id']
    user_name = msg['from'].get('first_name', 'Bạn')
    text = msg.get('text', '')
    
    if not text:
        return
    
    print(f"📨 [{datetime.now().strftime('%H:%M:%S')}] {user_name}: {text[:50]}")
    
    # Commands
    if text == '/start':
        send_message(chat_id, f"""👋 *Chào {user_name}!*

🤖 Em là *Phát* - Chuyên gia Blox Fruit **GOD LEVEL**
📊 Tính giá: RB × Tỷ lệ = Giá VNĐ

🔥 *SẢN PHẨM:*
💎 Acc 6 Perm - *450.000đ*
🍎 {len(FRUIT_PRICES_RB)} loại trái cây
⚡ {len(GAMEPASS_PRICES_RB)} loại Gamepass

💡 *Cách hỏi giá:*
• "giá Dough" | "giá Leopard" | "giá Kitsune"
• "giá 2x Money" | "giá Fruit Notifier"
• "giá trái" - Xem tất cả trái
• "giá gamepass" - Xem tất cả GP

⚙️ *Lệnh:*
• /tyle 150 - Đổi tỷ lệ RB
• /trai - Bảng giá trái
• /gamepass - Bảng giá GP

🧠 Em hiểu mọi ngôn ngữ: "dough bn", "trái rồng giá sao" 😊""")
        return
    
    # Lệnh xem/chỉnh tỷ lệ giá
    if text.startswith('/tyle') or text.startswith('/rate') or 'tỷ lệ' in text.lower():
        rate_match = re.search(r'(\d+)', text)
        if rate_match:
            new_rate = int(rate_match.group(1))
            if 50 <= new_rate <= 500:
                global FRUIT_RATE
                FRUIT_RATE = new_rate
                send_message(chat_id, f"✅ *Đã đổi tỷ lệ!*\n\n📊 Tỷ lệ mới: *1 RB = {FRUIT_RATE}đ*\n\n🍎 Giá trái sẽ tự động tính lại!\n⚡ Giá Gamepass cũng đổi theo!\n\nVD: Dough 2,400 RB × {FRUIT_RATE} = {2_400 * FRUIT_RATE:,}đ")
            else:
                send_message(chat_id, "❌ Tỷ lệ phải từ 50đ đến 500đ / 1 RB")
        else:
            send_message(chat_id, f"📊 *TỶ LỆ GIÁ HIỆN TẠI*\n\n1 Robux (RB) = {FRUIT_RATE} VNĐ\n\n💡 Công thức: RB × {FRUIT_RATE} = Giá tiền\n\n🍎 Dough 2,400 RB = {2_400 * FRUIT_RATE:,}đ\n⚡ Fruit Notifier 2,700 RB = {2_700 * FRUIT_RATE:,}đ\n\n📝 Đổi tỷ lệ: /tyle 150")
        return
    
    # Lệnh xem tất cả giá trái
    if text in ['/fruit', '/trai', '/gia', 'giá trái', 'bảng giá trái']:
        response = god_ai._handle_fruit_price(user_id, {}, text)
        send_message(chat_id, response["content"])
        return
    
    # Lệnh xem tất cả giá gamepass
    if text in ['/gamepass', '/gp', 'giá gamepass', 'bảng giá gamepass']:
        response = god_ai._handle_gamepass_price(user_id, {}, text)
        send_message(chat_id, response["content"])
        return
    
    # Typing effect
    send_typing(chat_id)
    time.sleep(random.uniform(1, 2))
    
    # AI xử lý
    response = god_ai.respond(user_id, text)
    
    if response["type"] == "text":
        send_message(chat_id, response["content"])
    elif response["type"] == "image":
        send_photo(chat_id, response["image_url"], response["caption"])
    
    print(f"✅ Đã trả lời ({response.get('next_action', 'none')})")

# ========== MAIN ==========
last_update_id = 0

def main():
    print("=" * 60)
    print("🤖 PHAT BOT - GOD LEVEL AI (MAX INTELLIGENCE)")
    print("=" * 60)
    print("✅ AI: Expert + Human Language Understanding")
    print(f"✅ Acc: Blox Fruit 6 Perm - 450k")
    print(f"✅ Trái cây: {len(FRUIT_PRICES_RB)} loại (mới nhất)")
    print(f"✅ Gamepass: {len(GAMEPASS_PRICES_RB)} loại")
    print(f"✅ Tỷ lệ: 1 RB = {FRUIT_RATE}đ (có thể đổi)")
    print("✅ Tính năng: Tính giá RB × Rate = VNĐ")
    print("=" * 60)
    
    if not TELEGRAM_TOKEN:
        print("❌ Thiếu TELEGRAM_BOT_TOKEN")
        return
    
    # Start keep-alive
    threading.Thread(target=start_keep_alive, daemon=True).start()
    
    global last_update_id
    print("\n🚀 Đang chạy...\n")
    
    while True:
        try:
            updates = get_updates(last_update_id + 1)
            
            if updates and updates.get('ok') and updates.get('result'):
                for update in updates['result']:
                    last_update_id = update['update_id']
                    if 'message' in update:
                        handle_message(update['message'])
            
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Dừng bot")
            break
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
