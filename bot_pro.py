"""
TELEGRAM BOT - CHUYÊN GIA TƯ VẤN BLOX FRUIT GOD LEVEL
Tư vấn viên: Phát | Hiểu mọi ngôn ngữ | Chốt đơn thần thánh
Tự động hóa: SePay QR + Webhook + Giao hàng + Admin Panel
"""

import http.client
import json
import os
import time
import random
import threading
import re
import urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Optional

# ========== MODULES MOI ==========
from database import db
from sepay import sepay
from admin import admin_notifier, admin_panel

# ========== PERSONALITY - TINH CACH BOT ==========
PERSONALITY = {
    "name": "Phát",
    "role": "Nhân viên tư vấn bán hàng Blox Fruit",
    "tone": "Thân thiện, chuyên nghiệp, tự nhiên như người thật",
    "style": "Ngắn gọn, dễ hiểu, có emoji vừa phải, không máy móc",
    "rules": [
        "Luôn đọc toàn bộ ngữ cảnh trước khi trả lời",
        "Không bỏ sót ý khách hỏi",
        "Trả lời đúng trọng tâm, không lan man",
        "Không tự bịa thông tin, không biết thì nói thật",
        "Không dùng văn mẫu AI, nói như người thật",
        "Không lặp câu hoặc lặp từ quá nhiều",
        "Giữ giọng thân thiện, không quá trang trọng, không trẻ con",
        "Hiểu tiếng Việt không dấu, viết tắt, lóng Gen Z, sai chính tả",
        "Nếu chưa hiểu thì hỏi lại lịch sự, không hỏi quá nhiều",
        "Trả lời ngắn gọn dễ hiểu, chia đoạn hợp lý",
        "Biết tư vấn sản phẩm phù hợp, so sánh rõ ràng",
        "Upsell tự nhiên, không ép mua, không spam sản phẩm",
        "Tạo cảm giác thoải mái, giữ khách trong cuộc trò chuyện",
        "Follow-up nhẹ nhàng, xử lý khách phân vân/mặc cả",
        "Không giảm giá bừa, không cãi khách, không toxic",
        "Luôn giữ lịch sự, xin lỗi và cảm ơn tự nhiên",
        "Xoa dịu khách đang bực, điều chỉnh giọng theo cảm xúc",
        "Không trả lời cụt ngủn hoặc quá dài",
        "Hướng dẫn từng bước rõ ràng, không giải thích rối",
        "Ghi nhớ sản phẩm khách quan tâm, nhớ yêu cầu trước đó",
        "Xử lý tin nhắn ngắn kiểu 'còn không', 'ib giá', 'shop ơi'",
        "Phản hồi tự nhiên như Messenger/Telegram, không cứng nhắc",
        "Không nhắc mình là AI, nói chuyện nhiều lượt tự nhiên",
        "Ưu tiên hỗ trợ khách có nhu cầu mua, hướng dẫn đặt hàng",
        "Tạo cảm giác chuyên nghiệp, đáng tin, thiện cảm",
        "Nói ngắn với khách vội, nói kỹ khi khách cần",
        "Kết thúc chat lịch sự, mời khách quay lại",
        "Ưu tiên trải nghiệm khách hàng, giữ vai trò support/sales chuyên nghiệp"
    ]
}

# ========== TIN NHẮN TỰ NHIÊN (Natural Responses) ==========
GREETINGS = [
    "Dạ em Phát đây ạ! Anh/chị cần tư vấn Blox Fruit gì ạ? 🎮",
    "Chào anh/chị! Em Phát - bên Blox Fruit. Hôm nay cần gì em hỗ trợ ạ? 😊",
    "Dạ em nghe! Anh/chị đang quan tâm acc hay trái cây ạ? 🍎",
    "Shop Phát xin chào anh/chị! Em đây, cần gì cứ hỏi em nhé! 💬",
    "Em chào! Đang cần tìm acc Blox Fruit phù hợp ạ? Em tư vấn được nè! 👋"
]

ACKNOWLEDGE_SHORT = [
    "Dạ em hiểu ạ",
    "Okie anh/chị",
    "Em nắm rồi ạ",
    "Rõ ạ",
    "Dạ vâng"
]

ASK_CLARIFY = [
    "Anh/chị nói thêm giúp em được không ạ? Em chưa hiểu rõ lắm 😅",
    "Dạ em nghe nhưng chưa rõ lắm. Anh/chị giải thích thêm chút được không ạ?",
    "Em hiểu khoảng 70% rồi ạ, anh/chị nói thêm giúp em phần còn lại được không? 🙏"
]

# ========== CONFIG ==========
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
SHOP_NAME = os.environ.get('SHOP_NAME', 'Blox Fruit Store')
SHOP_CONTACT = os.environ.get('SHOP_CONTACT', '@admin_bloxfruit')

# ========== SẢN PHẨM: Chỉ 1 acc 250k 6 perm ==========
THE_ACCOUNT = {
    "id": "bf-250k-6perm",
    "name": "Blox Fruit 6 Perm",
    "price": 250000,
    "price_str": "250.000đ",
    "level": "Max 2550",
    "fruit": "Leopard/Dough/Venom",
    "perms": ["2x Money", "2x Drop", "Fast Boats", "Fruit Notifier", "2x Mastery", "God Human"],
    "stats": {"melee": "Max", "defense": "Max", "sword": "Max", "gun": "Max", "fruit": "Max"},
    "items": ["Cursed Dual Katana", "Soul Guitar", "Valkyrie Helm"],
    "beli": "50M+",
    "fragments": "50k+",
    "stock": 3,
    "desc": "Acc max level, 6 perm đầy đủ, fruit hiếm, full item",
    "image_url": "https://i.imgur.com/bf250k.jpg",
    "screenshots": ["https://i.imgur.com/bf250k_1.jpg", "https://i.imgur.com/bf250k_2.jpg"]
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
        
        # === FRUIT PRICE QUERIES === (Ưu tiên cao - kiểm tra TRƯỚC ask_price)
        fruit_q = ["trái", "fruit", "quỷ", "bán trái", "giá trái", "mua trái", "vĩnh viễn", "perm",
                   "dough", "dragon", "leopard", "tiger", "venom", "buddha", "portal", "control",
                   "spirit", "shadow", "phoenix", "t-rex", "trex", "mammoth", "yeti", "kitsune",
                   "gas", "blizzard", "rumble", "sound", "spider", "love", "quake", "magma",
                   "ghost", "creation", "barrier", "rubber", "light", "diamond", "dark", "sand",
                   "ice", "eagle", "flame", "spike", "smoke", "bomb", "spring", "blade", "chop",
                   "spin", "rocket", "east dragon", "west dragon", "rồng đông", "rồng tây",
                   "trái ác quỷ", "devil fruit", "trái cây"]
        has_fruit = any(w in text.lower() for w in fruit_q)
        
        # === GAMEPASS QUERIES === (Ưu tiên cao)
        gamepass_q = ["gamepass", "2x money", "2x drop", "fast boats", "fruit notifier", 
                      "dark blade", "mastery", "storage", "scrolls", "boss drops", 
                      "2x mastery", "legendary scrolls", "mythical scrolls", "+1 fruit"]
        has_gamepass = any(w in text.lower() for w in gamepass_q)
        
        # Nếu có từ khóa giá + fruit/gamepass → ưu tiên fruit/gamepass price
        price_indicators = ["giá", "bao nhiêu", "bn", "tiền", "mua", "bán", "k", "nghìn", "ngàn"]
        has_price = any(p in text for p in price_indicators)
        
        if has_fruit and has_price:
            return "ask_fruit_price"
        
        if has_gamepass and has_price:
            return "ask_gamepass_price"
        
        # === INFO GATHERING ===
        if has_price:
            return "ask_price"
        
        quality_q = ["có tốt không", "uy tín", "scam", "lừa", "có thật", "đảm bảo", "bảo hành"]
        if any(w in text for w in quality_q):
            return "ask_trust"
        
        product_q = ["có gì", "có acc", "acc nào", "có loại", "có mấy", "có không"]
        if any(w in text for w in product_q):
            return "ask_product"
        
        # Nếu chỉ có fruit/gamepass không có giá → hỏi sản phẩm
        if has_fruit:
            return "ask_product"
        
        if has_gamepass:
            return "ask_product"
        
        image_q = ["ảnh", "hình", "xem", "screenshot", "preview", "chụp", "hình ảnh"]
        if any(w in text for w in image_q):
            return "ask_image"
        
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
        """Xử lý chào hỏi - Tự nhiên như người thật"""
        emotion = analysis.get("emotion", "neutral")
        
        # Chọn ngẫu nhiên để không lặp lại
        import random
        base = random.choice(GREETINGS)
        
        # Thêm context theo cảm xúc
        if emotion == "excited":
            base += "\n\nThấy anh/chị hào hứng quá, chắc đang muốn sắm acc Blox Fruit xịn đây! Em có acc 6 perm giá 250k nè 😄"
        elif emotion == "interested":
            base += "\n\nAnh/chị đang tìm acc hay trái cây ạ? Em có cả hai, giá hợp lý lắm!"
        
        return {
            "type": "text",
            "content": base + "\n\nNhắn /start để xem menu hoặc hỏi em trực tiếp nhé! 🎮",
            "next_action": None
        }
    
    def _handle_price_inquiry(self, user_id, analysis):
        """Xử lý hỏi giá - Giọng tự nhiên như người thật"""
        budget = analysis.get("budget_hint")
        
        # Nếu khách hỏi giá quá thấp (dưới 200k)
        if budget and budget < 200000:
            return {
                "type": "text",
                "content": f"""Dạ em xin lỗi anh/chị, em không có acc giá {budget:,}đ ạ �\n\nThực ra acc giá rẻ thường dính ban hoặc thiếu perm lắm, khách mua về cày mệt lắm ạ.\n\nEm chỉ có duy nhất 1 loại:\n🔥 **Acc Blox Fruit 6 Perm - 250k**\n\nAcc này đầy đủ 6 perm, max level 2550, có fruit hiếm, CDK, Soul Guitar luôn. Vào chơi max ngay, không cần cày.\n\nAnh/chị có thể lên 250k được không ạ? Em bảo hành 7 ngày đàng hoàng �""",
                "next_action": "ask_upgrade_budget"
            }
        
        # Nếu khách hỏi giá cao hơn (300k+)
        if budget and budget >= 300000:
            return {
                "type": "text",
                "content": f"""Dạ em chỉ có 1 loại acc duy nhất giá **250k** thôi ạ, không có acc cao hơn đâu �\n\nNhưng nếu anh/chị có {budget:,}đ, mua acc 250k còn dư có thể mua thêm trái cây ạ. Ví dụ:\n\n🍎 Dough: 2,400 RB = {2_400 * FRUIT_RATE:,}đ\n🍎 Leopard: 3,000 RB = {3_000 * FRUIT_RATE:,}đ\n\nCombo acc + trái em giảm 10% nữa! Anh/chị muốn xem combo nào phù hợp không? 🎮""",
                "next_action": "ask_commitment"
            }
        
        # Giá đúng 250k hoặc không đề cập giá cụ thể
        msg = f"""Dạ em có **1 loại acc duy nhất** giá 250k ạ:\n\n� **Blox Fruit 6 Perm - 250.000đ**\n\nTrong acc có gì ạ:\n• Level Max 2550 - Full stats\n• 6 Perm: 2x Money, 2x Drop, Fast Boats, Fruit Notifier, 2x Mastery, God Human\n• Fruit hiếm: Leopard / Dough / Venom\n• Item hiếm: CDK, Soul Guitar, Valkyrie Helm\n• Beli 50M+, Fragments 50k+\n\n🎁 Tặng kèm: Hướng dẫn chơi + Support sau mua + Bảo hành 7 ngày\n\nEm không có acc giá khác đâu ạ (100k, 150k, 300k gì em không có). Acc 250k này là chuẩn nhất, khách mua về không lo bị ban, vào chơi max ngay luôn.\n\nAnh/chị muốn chốt acc này không ạ? Em hỗ trợ nhiệt tình! 😊"""

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
        """Xử lý nghi ngờ uy tín - Thật thà, không flex"""
        return {
            "type": "text",
            "content": """Dạ em hiểu anh/chị lo lắng, mua acc online ai cũng sợ bị scam mà 😅\n\nEm nói thật với anh/chị:\n• Em bán acc này lâu rồi, khách quen cũng nhiều\n• Acc em bán là acc chuẩn, không phải acc hack hay acc bị ban\n• Em có bảo hành 7 ngày, nếu không đúng mô tả em hoàn tiền 100%\n• Khách nào mua rồi cũng quay lại mua thêm hoặc giới thiệu bạn\n\nAnh/chị có thể yêu cầu em check acc trước khi giao, quay video cũng được. Em minh bạch lắm, không giấu gì đâu ạ!\n\nNếu vẫn phân vân thì anh/chị cứ theo dõi em thêm, đừng vội mua. Uy tín em xây dựng lâu dài chứ không phải bán 1-2 lần rồi bỏ 🙏""",
            "next_action": "ask_commitment"
        }
    
    def _handle_product_inquiry(self, user_id, analysis):
        """Xử lý hỏi sản phẩm - Giọng tư vấn tự nhiên"""
        return {
            "type": "text",
            "content": f"""Dạ em giới thiệu sơ shop em ạ:\n\n💎 **1. Acc Blox Fruit 6 Perm - 250k** (Duy nhất)\nAcc max level 2550, đầy đủ 6 perm, fruit hiếm. Vào chơi max ngay không cần cày.\n\n🍎 **2. Trái cây vĩnh viễn** ({len(FRUIT_PRICES_RB)} loại)\nTính theo giá Robux × {FRUIT_RATE}đ. Ví dụ:\n• Dough 2,400 RB = {2_400 * FRUIT_RATE:,}đ\n• Leopard 3,000 RB = {3_000 * FRUIT_RATE:,}đ\n• Dragon 5,000 RB = {5_000 * FRUIT_RATE:,}đ\nAnh/chị nhắn "giá + tên trái" em báo chi tiết!\n\n⚡ **3. Gamepass** ({len(GAMEPASS_PRICES_RB)} loại)\nCũng tính RB × {FRUIT_RATE}đ.\n• Fruit Notifier 2,700 RB = {2_700 * FRUIT_RATE:,}đ\n• Dark Blade 1,200 RB = {1_200 * FRUIT_RATE:,}đ\n\n� **Ưu đãi combo:**\nMua acc + trái/gamepass em giảm 10%, combo nhiều giảm thêm!\n\nAnh/chị đang cần loại nào ạ? Em tư vấn chi tiết hơn! 🎮""",
            "next_action": "ask_selection"
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
            "content": """Tuyệt vời! Anh/chị chốt acc Blox Fruit 6 Perm - 250k đúng không ạ? 🎉\n\n💳 Thông tin thanh toán:\n📱 ZaloPay: `0343603537`\n🏦 BIDV: `8806532434`\n👤 Chủ TK: TRAN NGUYEN PHAT\n\n💰 Số tiền: 250.000đ\n\n📌 Các bước nhận acc:\n1. CK xong chụp màn hình gửi em\n2. Em gửi info acc trong 1-2 phút\n3. Anh/chị đổi pass + email ngay\n4. Em hỗ trợ nếu cần\n\n⚡ Ưu đãi: CK trong 30 phút em tặng thêm hướng dẫn farm belly nhanh!\n\nCó gì không hiểu cứ hỏi em nhé! �""",
            "next_action": "wait_payment"
        }
    
    def _handle_considering(self, user_id, analysis):
        """Xử lý đang cân nhắc - Tự nhiên, không ép"""
        objections = analysis.get("objections", [])
        
        msg = """Dạ em hiểu anh/chị đang cân nhắc, không sao đâu ạ 😊\n\nEm chia sẻ thực tế để anh/chị dễ quyết định:\n\n💪 Tự cày từ đầu:\n• Cày lên 2550 mất 2-3 tuần chơi liên tục\n• Roll 6 perm tốn khoảng 500k+\n• Roll fruit hiếm thêm 200k+\n• Tổng hết ~700k và cả tháng cày mệt\n\n� Mua acc 250k của em:\n• Có ngay acc max, vào chơi luôn\n• Tiết kiệm hơn 450k so với tự làm\n• Không mất thời gian cày\n• Được bảo hành 7 ngày + support sau mua\n\nAnh/chị còn phân vân điều gì không ạ? Em giải đáp thoải mái, không ép mua đâu! �"""

        if "price" in objections:
            msg += "\n\n💵 Về giá 250k ạ, em bán giá này là hòa vốn thôi. Acc max 6 perm bên ngoài người ta bán 400-500k đó. Em lấy uy tín làm đầu nên giữ giá ổn định cho khách quen!"
        
        return {"type": "text", "content": msg, "next_action": "address_objections"}
    
    def _handle_negotiation(self, user_id, analysis):
        """Xử lý trả giá - Không giảm bừa, tặng quà thay"""
        return {
            "type": "text",
            "content": """Dạ em hiểu anh/chị muốn giá tốt hơn 😊\n\nThật ra em bán 250k là giá hòa vốn rồi ạ. Em không giảm thêm được vì acc max 6 perm này em cũng phải đầu tư công sức kiếm. Bên ngoài người ta bán 400-500k đó ạ.\n\nNhưng em có thể tặng thêm cho anh/chị:\n🎁 Hướng dẫn farm belly nhanh\n🎁 Tips đi boss lấy item hiếm\n🎁 Support nhiệt tình sau mua, có gì cứ hỏi em\n\nGiá 250k + quà tặng kèm + bảo hành 7 ngày, anh/chị thấy ổn không ạ? Em chuẩn bị acc đẹp cho! �""",
            "next_action": "soft_close"
        }
    
    def _handle_objection(self, user_id, analysis):
        """Xử lý từ chối - Tôn trọng, không ép, mời quay lại"""
        return {
            "type": "text",
            "content": """Dạ không sao đâu ạ 😊 Anh/chị cứ suy nghĩ thoải mái, em không ép mua đâu!\n\nEm chỉ lưu lại thông tin để anh/chị cần thì liên hệ:\n💎 Acc Blox Fruit 6 Perm - 250k\n📦 Còn {THE_ACCOUNT['stock']} acc\n\nNếu đổi ý trong 24h em vẫn giữ giá + ưu đãi như cũ ạ. Còn nếu không mua cũng không sao, em vẫn sẵn sàng tư vấn nếu anh/chị cần!\n\nCảm ơn anh/chị đã dành thời gian chat với em nhé! 🙏""",
            "next_action": "follow_up_later"
        }
    
    def _handle_thanks(self, user_id, analysis):
        """Xử lý cảm ơn - Tự nhiên, ấm áp"""
        import random
        responses = [
            "Dạ không có gì đâu ạ! Anh/chị cần gì cứ nhắn em, em luôn sẵn sàng hỗ trợ! Chúc anh/chị một ngày vui vẻ 🎮😊",
            "Em cảm ơn anh/chị đã tin tưởng ạ! Có gì cứ tìm em, em Phát luôn ở đây! 👋",
            "Không có chi đâu ạ! Anh/chị vui là em vui rồi. Cần gì thêm cứ alo em nhé! 💬"
        ]
        return {
            "type": "text",
            "content": random.choice(responses),
            "next_action": None
        }
    
    def _handle_general(self, user_id, analysis, text):
        """Xử lý chung - Tự nhiên, hỏi lại lịch sự, không bỏ sót ý"""
        emotion = analysis.get("emotion", "neutral")
        style = analysis.get("style", "neutral")
        text_lower = text.lower()
        
        # Xử lý tin nhắn ngắn đặc biệt
        short_msgs = {
            "shop ơi": "Dạ em nghe! Anh/chị cần gì ạ? Em có acc Blox Fruit 250k và trái cây vĩnh viễn! 🎮",
            "shop oi": "Dạ em nghe! Anh/chị cần gì ạ? Em có acc Blox Fruit 250k và trái cây vĩnh viễn! 🎮",
            "ib giá": "Dạ em đây! Acc Blox Fruit 6 Perm giá 250k ạ. Anh/chị muốn biết thêm chi tiết gì không? �",
            "ib gia": "Dạ em đây! Acc Blox Fruit 6 Perm giá 250k ạ. Anh/chị muốn biết thêm chi tiết gì không? 😊",
            "còn không": "Dạ em còn ạ! Acc Blox Fruit 6 Perm 250k vẫn còn hàng. Anh/chị quan tâm không? 💎",
            "con khong": "Dạ em còn ạ! Acc Blox Fruit 6 Perm 250k vẫn còn hàng. Anh/chị quan tâm không? 💎",
            "alo": "Dạ em nghe! Shop Phát đây, anh/chị cần gì em hỗ trợ ạ? 👋",
            "ei": "Dạ em đây! Cần gì cứ nói em nhé! 🎮",
            "bro": "Dạ em nghe bro! Cần tư vấn Blox Fruit gì không? 🔥",
            "help": "Dạ em đây! Anh/chị cần hỗ trợ gì ạ? Em có acc 250k, trái cây, gamepass... 🆘",
        }
        
        for key, response in short_msgs.items():
            if key in text_lower or text_lower == key:
                return {"type": "text", "content": response, "next_action": "ask_needs"}
        
        # Xử lý theo cảm xúc
        if emotion == "angry":
            return {
                "type": "text",
                "content": "Dạ em xin lỗi nếu có gì làm anh/chị không vui ạ. Anh/chị nói rõ hơn để em hỗ trợ được không? Em sẽ cố gắng giải quyết ngay! 🙏",
                "next_action": "calm_down"
            }
        
        if emotion == "excited":
            return {
                "type": "text",
                "content": "Dạ em thấy anh/chị hào hứng quá! 😄 Anh/chị đang quan tâm acc Blox Fruit 250k hay trái cây nào ạ? Em tư vấn nhiệt tình!",
                "next_action": "ask_product"
            }
        
        # Phản hồi chung - tự nhiên
        responses = [
            "Dạ em chưa hiểu rõ ý anh/chị lắm � Anh/chị đang cần tìm hiểu acc Blox Fruit 250k, hay trái cây, hay gamepass ạ?",
            "Em nghe nhưng chưa rõ lắm... Anh/chị nói thêm chút được không ạ? Ví dụ 'giá acc', 'giá Dough', 'muốn mua'... 💬",
            "Dạ em đang lắng nghe anh/chị đây! Anh/chị cần gì cứ hỏi em nhé, em có acc 250k và đủ loại trái cây! 🎮",
            f"{'Dạ' if style == 'polite' else 'Dạo'} em chưa bắt kịp ý anh/chị {'ạ' if style == 'polite' else ''} 😄 Anh/chị muốn xem sản phẩm gì? Nhắn /start để xem menu nha!",
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

# ========== TELEGRAM KEYBOARD HELPERS ==========
def send_keyboard(chat_id, text, buttons):
    """Gui tin nhan co inline keyboard"""
    try:
        conn = http.client.HTTPSConnection("api.telegram.org")
        payload = json.dumps({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": buttons},
            "disable_web_page_preview": True
        })
        headers = {"Content-type": "application/json"}
        conn.request("POST", f"/bot{TELEGRAM_TOKEN}/sendMessage", payload, headers)
        resp = conn.getresponse()
        result = json.loads(resp.read().decode())
        conn.close()
        return result
    except Exception as e:
        print(f"❌ Lỗi gửi keyboard: {e}")
        return None

def edit_message_text(chat_id, message_id, text, buttons=None):
    """Sua noi dung tin nhan + keyboard"""
    try:
        conn = http.client.HTTPSConnection("api.telegram.org")
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        if buttons:
            payload["reply_markup"] = {"inline_keyboard": buttons}
        body = json.dumps(payload)
        headers = {"Content-type": "application/json"}
        conn.request("POST", f"/bot{TELEGRAM_TOKEN}/editMessageText", body, headers)
        conn.close()
    except Exception as e:
        print(f"❌ Lỗi edit msg: {e}")

def answer_callback(callback_id, text=""):
    """Tra loi callback query (hieu ung nhan nut)"""
    try:
        conn = http.client.HTTPSConnection("api.telegram.org")
        payload = json.dumps({"callback_query_id": callback_id, "text": text})
        headers = {"Content-type": "application/json"}
        conn.request("POST", f"/bot{TELEGRAM_TOKEN}/answerCallbackQuery", payload, headers)
        conn.close()
    except:
        pass

# ========== MENU KEYBOARDS ==========
def get_main_menu():
    """Menu chinh"""
    return [
        [{"text": "🎮 Xem sản phẩm", "callback_data": "menu_products"},
         {"text": "🛒 Mua hàng", "callback_data": "menu_buy"}],
        [{"text": "💰 Kiểm tra đơn", "callback_data": "menu_orders"},
         {"text": "📜 Lịch sử mua", "callback_data": "menu_history"}],
        [{"text": "❓ Hỗ trợ / FAQ", "callback_data": "menu_support"}]
    ]

def get_products_menu():
    """Menu san pham"""
    return [
        [{"text": "💎 Acc Blox Fruit 250k", "callback_data": "buy_acc"}],
        [{"text": "🍎 Trái cây vĩnh viễn", "callback_data": "menu_fruits"}],
        [{"text": "⚡ Gamepass", "callback_data": "menu_gamepass"}],
        [{"text": "⬅️ Quay lại", "callback_data": "menu_main"}]
    ]

def get_buy_confirm_menu(order_id: int):
    """Menu xac nhan mua + thanh toan"""
    return [
        [{"text": "💳 Thanh toán QR", "callback_data": f"pay_qr_{order_id}"}],
        [{"text": "❌ Hủy đơn", "callback_data": f"cancel_{order_id}"}]
    ]

# ========== ORDER & PAYMENT FLOW ==========
def create_order_flow(user_id: int, product_type: str, product_name: str,
                       product_detail: str, amount: int) -> int:
    """Tao don hang va tra ve order_id"""
    payment_content = sepay.generate_payment_content(0, user_id)
    order_id = db.create_order(user_id, product_type, product_name,
                                product_detail, amount, payment_content)
    # Update payment content with real order_id
    payment_content = sepay.generate_payment_content(order_id, user_id)
    conn = db._connect()
    c = conn.cursor()
    c.execute('UPDATE orders SET payment_content = ? WHERE order_id = ?',
              (payment_content, order_id))
    conn.commit()
    conn.close()
    return order_id

def send_payment_qr(chat_id: int, order_id: int):
    """Gui QR thanh toan cho khach"""
    order = db.get_order(order_id)
    if not order:
        send_message(chat_id, "❌ Không tìm thấy đơn hàng.")
        return
    
    if not sepay.is_configured():
        # Fallback: chi hien thong tin CK
        msg = f"""🛒 *ĐƠN HÀNG #{order_id}*

📦 *Sản phẩm:* {order['product_name']}
💰 *Số tiền:* {order['amount']:,}đ
🏦 *Nội dung CK:* `{order['payment_content']}`

{sepay.get_bank_info_text()}

⚠️ *Quan trọng:* Dùng đúng nội dung trên để bot tự động xác nhận!

⏳ Đơn sẽ tự động xác nhận sau khi nhận được chuyển khoản.
💬 Nếu cần hỗ trợ: {SHOP_CONTACT}"""
        send_message(chat_id, msg)
        return
    
    qr_url = sepay.generate_qr_url(order['amount'], order['payment_content'])
    
    msg = f"""🛒 *ĐƠN HÀNG #{order_id}*

📦 *Sản phẩm:* {order['product_name']}
📋 *Chi tiết:* {order['product_detail'][:50]}
💰 *Số tiền:* {order['amount']:,}đ
🏦 *Nội dung CK:* `{order['payment_content']}`

📲 *Quét QR để thanh toán:*
(Hoặc chuyển khoản thủ công với đúng nội dung)

⏳ Sau khi thanh toán, bot sẽ tự động giao hàng trong 1-2 phút.
💬 Cần hỗ trợ: {SHOP_CONTACT}"""
    
    # Gui QR anh
    try:
        conn = http.client.HTTPSConnection("api.telegram.org")
        payload = json.dumps({
            "chat_id": chat_id,
            "photo": qr_url,
            "caption": msg,
            "parse_mode": "Markdown"
        })
        headers = {"Content-type": "application/json"}
        conn.request("POST", f"/bot{TELEGRAM_TOKEN}/sendPhoto", payload, headers)
        conn.close()
    except Exception as e:
        print(f"❌ Lỗi gửi QR: {e}")
        send_message(chat_id, msg + f"\n\n🔗 *QR Link:* {qr_url}")

def process_payment(order_id: int, tx_amount: int, tx_content: str) -> bool:
    """Xu ly thanh toan tu webhook"""
    order = db.get_order(order_id)
    if not order:
        print(f"⚠️ Order {order_id} không tồn tại")
        return False
    
    if order['status'] != 'pending':
        print(f"⚠️ Order {order_id} đã được xử lý ({order['status']})")
        return False
    
    # Kiem tra so tien (cho phep sai lech nho)
    if tx_amount < order['amount'] - 1000:
        print(f"⚠️ Số tiền không đủ: {tx_amount} < {order['amount']}")
        return False
    
    # Xac nhan thanh toan
    now = datetime.now().isoformat()
    db.update_order_status(order_id, 'paid', now)
    
    customer = db.get_customer(order['user_id'])
    tx_data = {'transaction_id': tx_content, 'amount': tx_amount, 'content': tx_content}
    
    # Thong bao admin
    admin_notifier.send_payment_confirmation(order, customer or {}, tx_data)
    
    # Auto giao hang
    auto_deliver(order_id)
    
    return True

def auto_deliver(order_id: int):
    """Tu dong giao hang"""
    order = db.get_order(order_id)
    if not order:
        return
    
    product_type = order['product_type']
    product_name = order['product_name']
    user_id = order['user_id']
    
    # Lay stock
    stock = db.get_available_stock(product_type, product_name)
    
    if stock:
        # Giao hang tu stock
        delivery_content = stock['content']
        db.mark_stock_sold(stock['stock_id'], order_id)
        db.record_delivery(order_id, delivery_content)
        
        # Gui cho khach
        msg = f"""🎉 *THANH TOÁN THÀNH CÔNG!*

✅ Đơn #{order_id} đã được xác nhận.

🎁 *THÔNG TIN GIAO HÀNG:*
`{delivery_content}`

⚠️ *Lưu ý:*
• Đổi mật khẩu ngay sau khi nhận
• Không chia sẻ thông tin cho người khác
• Có vấn đề liên hệ {SHOP_CONTACT}

🙏 Cảm ơn anh/chị đã tin tưởng Phát!
Để lại feedback giúp em nhé 🌟"""
        send_message(user_id, msg)
        
        # Thong bao admin giao hang xong
        customer = db.get_customer(user_id)
        admin_notifier.send_delivery_notification(order, customer or {})
    else:
        # Het hang
        db.update_order_status(order_id, 'out_of_stock')
        msg = f"""😔 *XIN LỖI ANH/CHỊ*

Đơn #{order_id} đã thanh toán thành công nhưng **hết hàng**!

💰 Số tiền {order['amount']:,}đ sẽ được hoàn lại trong 24h.
Hoặc anh/chị có thể đổi sang sản phẩm khác.

💬 Liên hệ {SHOP_CONTACT} để được hỗ trợ ngay."""
        send_message(user_id, msg)
        admin_notifier.send_low_stock_alert(product_type, product_name)

# ========== WEBHOOK HANDLER ==========
class WebhookHandler(BaseHTTPRequestHandler):
    """Xu ly keep-alive + SePay webhook"""
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>Phat Bot - God Level AI + Auto Payment Running!</h1>")
    
    def do_POST(self):
        path = self.path
        
        # SePay webhook
        if path == '/webhook/sepay':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Xac thuc signature (neu co secret)
            signature = self.headers.get('X-Sepay-Signature', '')
            if sepay.webhook_secret and not sepay.verify_webhook(body, signature):
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b'Unauthorized')
                print("❌ Webhook signature không hợp lệ")
                return
            
            try:
                data = json.loads(body.decode('utf-8'))
                tx = sepay.parse_transaction(data)
                if tx and tx['transfer_type'] == 'in':
                    order_id = sepay.extract_order_from_content(tx['content'])
                    if order_id:
                        success = process_payment(order_id, tx['amount'], tx['content'])
                        print(f"✅ Webhook: Order {order_id} processed: {success}")
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'OK')
                        return
                    else:
                        print(f"⚠️ Không tìm thấy order_id trong: {tx['content']}")
                else:
                    print(f"⚠️ Giao dịch không hợp lệ hoặc không phải chuyển vào")
            except Exception as e:
                print(f"❌ Lỗi xử lý webhook: {e}")
                admin_notifier.send_error_alert(f"Webhook error: {e}")
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            return
        
        # Default
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        pass

def start_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    print(f"✅ Server port {port} (Keep-alive + Webhook)")
    server.serve_forever()

# ========== MESSAGE HANDLER ==========
def handle_message(msg):
    chat_id = msg['chat']['id']
    user_id = msg['from']['id']
    username = msg['from'].get('username', '')
    user_name = msg['from'].get('first_name', 'Bạn')
    text = msg.get('text', '')
    
    if not text:
        return
    
    # Luu khach hang vao DB
    db.add_customer(user_id, username, user_name, msg['from'].get('last_name', ''))
    db.log_message(user_id, text)
    
    # Spam protection
    msg_count = db.get_message_count_last_minute(user_id)
    if msg_count > 15:
        send_message(chat_id, "⏳ Anh/chị nhắn hơi nhanh rồi. Đợi em xíu nhé! 😅")
        return
    
    print(f"📨 [{datetime.now().strftime('%H:%M:%S')}] {user_name}: {text[:50]}")
    
    # ========== ADMIN COMMANDS ==========
    if admin_panel.is_admin(user_id):
        if text.startswith('/don'):
            if len(text.split()) > 1:
                try:
                    oid = int(text.split()[1])
                    order = db.get_order(oid)
                    if order:
                        cus = db.get_customer(order['user_id'])
                        msg_admin = f"""� *CHI TIẾT ĐƠN #{oid}*

👤 Khách: {cus.get('first_name','N/A')} (@{cus.get('username','N/A')})
🆔 ID: `{order['user_id']}`
📦 SP: {order['product_name']}
📋 Chi tiết: {order['product_detail'][:100]}
💰 Tiền: {order['amount']:,}đ
🏦 Nội dung: `{order['payment_content']}`
🕒 Tạo: {order['created_at'][:16]}
✅ Trạng thái: {order['status'].upper()}"""
                        send_message(chat_id, msg_admin)
                    else:
                        send_message(chat_id, "❌ Không tìm thấy đơn.")
                except ValueError:
                    send_message(chat_id, "❌ Dùng: /don <order_id>")
            else:
                orders = db.get_all_orders(30)
                send_message(chat_id, admin_panel.format_order_list(orders))
            return
        
        if text == '/doanhthu':
            stats = db.get_revenue()
            send_message(chat_id, admin_panel.format_revenue(stats))
            return
        
        if text.startswith('/nhaphang'):
            parts = text.split(' ', 2)
            if len(parts) >= 3:
                ptype = parts[1]
                pname = parts[2]
                # Them stock voi noi dung mac dinh (admin nhap sau)
                db.add_stock(ptype, pname, f"STOCK_{ptype}_{datetime.now().timestamp()}")
                send_message(chat_id, f"✅ Đã thêm stock: {pname} ({ptype})")
            else:
                send_message(chat_id, "❌ Dùng: /nhaphang <loai> <ten>\nVD: /nhaphang acc BloxFruit")
            return
        
        if text == '/tonkho':
            count = db.get_stock_count()
            send_message(chat_id, admin_panel.format_stock_status(count))
            return
        
        if text == '/admin':
            send_message(chat_id, """🔧 *ADMIN PANEL*

📋 /don - Xem danh sách đơn
📋 /don <id> - Chi tiết đơn
💰 /doanhthu - Thống kê doanh thu
📦 /tonkho - Xem tồn kho
📥 /nhaphang <loại> <tên> - Nhập hàng

🤖 Bot vẫn hoạt động bình thường.""")
            return
    
    # ========== USER COMMANDS ==========
    if text == '/start':
        menu_text = f"""👋 *Chào {user_name}!*

� Em là *Phát* - Chuyên gia Blox Fruit

🔥 *MENU CHÍNH:*
Chọn nút bên dưới để sử dụng!"""
        send_keyboard(chat_id, menu_text, get_main_menu())
        return
    
    # Lệnh xem/chỉnh tỷ lệ giá
    if text.startswith('/tyle') or text.startswith('/rate') or 'tỷ lệ' in text.lower():
        rate_match = re.search(r'(\d+)', text)
        if rate_match:
            new_rate = int(rate_match.group(1))
            if 50 <= new_rate <= 500:
                global FRUIT_RATE
                FRUIT_RATE = new_rate
                send_message(chat_id, f"✅ *Đã đổi tỷ lệ!*\n\n📊 Tỷ lệ mới: *1 RB = {FRUIT_RATE}đ*\n\n🍎 Giá trái sẽ tự động tính lại!\n⚡ Giá Gamepass cũng đổi theo!\n\nVD: Dough 2,400 RB × {FRUIT_RATE} = {2_400 * FRUIT_RATE:,}đ\n\n💎 Giá acc vẫn là 250.000đ (KHÔNG đổi)")
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


# ========== CALLBACK HANDLER (INLINE KEYBOARD) ==========
def handle_callback(update):
    """Xu ly nhan nut inline keyboard"""
    callback = update.get('callback_query', {})
    if not callback:
        return
    
    callback_id = callback.get('id', '')
    data = callback.get('data', '')
    msg = callback.get('message', {})
    chat_id = msg.get('chat', {}).get('id', 0)
    message_id = msg.get('message_id', 0)
    user_id = callback.get('from', {}).get('id', 0)
    user_name = callback.get('from', {}).get('first_name', 'Bạn')
    
    # Luu khach
    db.add_customer(user_id, callback['from'].get('username', ''),
                    user_name, callback['from'].get('last_name', ''))
    
    print(f"🔘 [{datetime.now().strftime('%H:%M:%S')}] {user_name} clicked: {data}")
    answer_callback(callback_id)
    
    # === MENU NAVIGATION ===
    if data == "menu_main":
        text = f"👋 *Chào {user_name}!*\n\nChọn chức năng bên dưới:"
        edit_message_text(chat_id, message_id, text, get_main_menu())
        return
    
    if data == "menu_products":
        text = """🎮 *SẢN PHẨM*

Chọn loại sản phẩm:"""
        edit_message_text(chat_id, message_id, text, get_products_menu())
        return
    
    if data == "menu_buy":
        text = f"""🛒 *MUA HÀNG*

📦 Chọn sản phẩm để đặt:

💎 Acc Blox Fruit - 250k
🍎 Trái cây vĩnh viễn
⚡ Gamepass"""
        edit_message_text(chat_id, message_id, text, get_products_menu())
        return
    
    if data == "menu_orders":
        pending = db.get_pending_order(user_id)
        orders = db.get_customer_orders(user_id)
        if not orders:
            text = "📭 Anh/chị chưa có đơn hàng nào.\n\n🛒 Chọn 'Mua hàng' để đặt đơn đầu tiên!"
            edit_message_text(chat_id, message_id, text, get_main_menu())
            return
        
        lines = ["📋 *ĐƠN HÀNG CỦA BẠN*\n"]
        for o in orders[:10]:
            status = {'pending': '⏳ Chờ TT', 'paid': '💰 Đã TT',
                      'completed': '✅ Hoàn tất', 'cancelled': '❌ Đã hủy',
                      'out_of_stock': '🚫 Hết hàng'}
            lines.append(f"#{o['order_id']} | {o['product_name'][:15]} | {o['amount']:,}đ | {status.get(o['status'], o['status'])}")
        
        text = '\n'.join(lines)
        edit_message_text(chat_id, message_id, text, get_main_menu())
        return
    
    if data == "menu_history":
        orders = db.get_customer_orders(user_id)
        completed = [o for o in orders if o['status'] == 'completed']
        if not completed:
            text = "📜 Chưa có lịch sử giao dịch.\n\n🛒 Mua hàng để bắt đầu nhé!"
        else:
            lines = ["📜 *LỊCH SỬ MUA*\n"]
            total = sum(o['amount'] for o in completed)
            for o in completed[:10]:
                lines.append(f"✅ #{o['order_id']} | {o['product_name'][:20]} | {o['amount']:,}đ")
            lines.append(f"\n💰 Tổng chi: {total:,}đ")
            text = '\n'.join(lines)
        edit_message_text(chat_id, message_id, text, get_main_menu())
        return
    
    if data == "menu_support":
        text = f"""❓ *HỖ TRỢ / FAQ*

💬 Liên hệ trực tiếp: {SHOP_CONTACT}

🔥 *Câu hỏi thường gặp:*

❓ *Làm sao mua?*
→ Chọn "Mua hàng" > Chọn sản phẩm > Thanh toán QR > Bot tự giao hàng

❓ *Thanh toán như thế nào?*
→ Chuyển khoản qua QR SePay hoặc CK thủ công

❓ *Bao lâu nhận hàng?*
→ 1-2 phút sau khi thanh toán (tự động)

❓ *Có bảo hành không?*
→ Có, 7 ngày đổi trả nếu lỗi

❓ *Acc có bị ban không?*
→ Acc chuẩn, không lo bị ban như acc rẻ

❓ *Mua trái cây có nhận ngay không?*
→ Có, bot giao tự động sau khi thanh toán

💡 Cần hỗ trợ thêm? Nhắn trực tiếp cho em!"""
        edit_message_text(chat_id, message_id, text, get_main_menu())
        return
    
    if data == "menu_fruits":
        # Hien bang gia trai
        response = god_ai._handle_fruit_price(user_id, {}, "giá trái")
        send_message(chat_id, response["content"])
        return
    
    if data == "menu_gamepass":
        response = god_ai._handle_gamepass_price(user_id, {}, "giá gamepass")
        send_message(chat_id, response["content"])
        return
    
    # === BUY ACTIONS ===
    if data == "buy_acc":
        if THE_ACCOUNT['stock'] <= 0:
            send_message(chat_id, "😔 Xin lỗi, hiện tại hết hàng acc. Vui lòng quay lại sau!")
            return
        
        order_id = create_order_flow(
            user_id, 'acc', THE_ACCOUNT['name'],
            f"Acc {THE_ACCOUNT['name']} - Level {THE_ACCOUNT['level']} - {THE_ACCOUNT['fruit']}",
            THE_ACCOUNT['price']
        )
        
        order = db.get_order(order_id)
        customer = db.get_customer(user_id)
        admin_notifier.send_order_notification(order, customer or {})
        
        text = f"""🛒 *ĐƠN HÀNG #{order_id} ĐÃ TẠO*

📦 *Sản phẩm:* {THE_ACCOUNT['name']}
💰 *Giá:* {THE_ACCOUNT['price']:,}đ
🏦 *Nội dung CK:* `{order['payment_content']}`

👉 Chọn "Thanh toán QR" để nhận mã QR
💬 Hoặc CK thủ công với đúng nội dung trên

⏳ Sau khi thanh toán, bot tự động giao hàng!"""
        send_keyboard(chat_id, text, get_buy_confirm_menu(order_id))
        return
    
    # === PAYMENT ACTIONS ===
    if data.startswith("pay_qr_"):
        order_id = int(data.split("_")[2])
        send_payment_qr(chat_id, order_id)
        return
    
    if data.startswith("cancel_"):
        order_id = int(data.split("_")[1])
        db.update_order_status(order_id, 'cancelled')
        text = f"❌ Đơn #{order_id} đã bị hủy.\n\n🛒 Chọn lại sản phẩm nếu cần nhé!"
        edit_message_text(chat_id, message_id, text, get_main_menu())
        return
    
    # Mac dinh
    send_message(chat_id, "🤔 Em chưa hiểu. Anh/chị chọn lại trong menu nhé!")

# ========== MAIN ==========
last_update_id = 0

def main():
    print("=" * 60)
    print("🤖 PHAT BOT - GOD LEVEL AI + AUTO PAYMENT")
    print("=" * 60)
    print("✅ AI: Expert + Human Language Understanding")
    print(f"✅ Acc: Blox Fruit 6 Perm - 250k (DUY NHẤT)")
    print(f"✅ Trái cây: {len(FRUIT_PRICES_RB)} loại")
    print(f"✅ Gamepass: {len(GAMEPASS_PRICES_RB)} loại")
    print(f"✅ Tỷ lệ: 1 RB = {FRUIT_RATE}đ")
    print("-" * 60)
    print("💳 SePay QR: " + ("✅ ON" if sepay.is_configured() else "⚠️ OFF (chua config)"))
    print("📢 Admin Noti: " + ("✅ ON" if admin_notifier.is_configured() else "⚠️ OFF (chua config)"))
    print("🗄️  Database: SQLite (shop_data.db)")
    print("=" * 60)
    
    if not TELEGRAM_TOKEN:
        print("❌ Thiếu TELEGRAM_BOT_TOKEN")
        return
    
    # Start server (keep-alive + webhook)
    threading.Thread(target=start_server, daemon=True).start()
    
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
                    elif 'callback_query' in update:
                        handle_callback(update)
            
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Dừng bot")
            break
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
