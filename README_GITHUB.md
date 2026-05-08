# 🤖 Telegram Sales Bot

Bot bán hàng tự động trên Telegram - Trả lời khách 24/7

## 🚀 Deploy trên Render.com

### Environment Variables cần thiết:

| Variable | Giá trị | Lấy ở đâu |
|----------|---------|-----------|
| `TELEGRAM_BOT_TOKEN` | `123456:ABC...` | @BotFather trên Telegram |
| `SHOP_NAME` | `Tên Shop` | Tự đặt |
| `SHOP_CONTACT` | `@username` | Telegram của bạn |

### Cách deploy:

1. Fork repo này
2. Vào [render.com](https://render.com)
3. New → Web Service → Connect repo
4. Settings:
   - **Runtime**: Python 3
   - **Start Command**: `python bot_render.py`
5. Add Environment Variables (3 cái trên)
6. Deploy!

## 🛍️ Sản phẩm

- Robux 100k - 100.000đ
- Robux 200k - 200.000đ  
- Nitro 1 tháng - 150.000đ

## 💬 Tính năng

- Trả lời tự động theo từ khóa
- Hiển thị typing như người thật
- Commands: /start, /products, /contact

## 📁 Files

- `bot_render.py` - Code chính
- `products.json` - Danh sách sản phẩm
- `.env.example` - Mẫu biến môi trường

---
**Miễn phí 100% với Render.com**
