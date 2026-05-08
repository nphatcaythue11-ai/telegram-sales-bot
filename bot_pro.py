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

Em là *Phát* - Chuyên gia Blox Fruit 🎮
500+ đơn thành công | Uy tín 100%

🔥 *ACC HOT:* Blox Fruit 6 Perm - *450k*
• Max level 2550
• 6 perm đầy đủ
• Fruit hiếm

💡 *Hỏi em bất cứ gì:*
"giá" | "ảnh" | "mua" | "uy tín"

Em hiểu mọi ngôn ngữ! 😊""")
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
    print("🤖 PHAT BOT - GOD LEVEL AI")
    print("=" * 60)
    print("✅ AI: Expert Level - Hiểu mọi ngôn ngữ")
    print(f"✅ Sản phẩm: Blox Fruit 6 Perm - 450k")
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
