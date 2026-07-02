import sqlite3
import urllib.parse
import requests
import telebot
from telebot import types
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

API_TOKEN = '8856653560:AAH15sSTaqBDI7KMWaHe0WoD1rWBcA9zMUQ'  
ADMIN_ID = 8552160313  

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(API_TOKEN, state_storage=state_storage)

class BotStates(StatesGroup):
    waiting_unlock_info = State()
    waiting_add_key_name = State()
    waiting_add_key_code = State()
    card_type = State()
    card_amount = State()
    card_pin = State()
    card_seri = State()

def get_db():
    return sqlite3.connect('system.db')

def init_db_runtime():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, balance INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY AUTOINCREMENT, tool_name TEXT, key_code TEXT UNIQUE, status TEXT DEFAULT 'AVAILABLE')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item_name TEXT, price INTEGER, detail TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 0

def main_menu(user_id):
    balance = get_balance(user_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        types.InlineKeyboardButton("🛠️ KHO KEY TOOL AUTO", callback_data="buy_tool"),
        types.InlineKeyboardButton("🔓 DỊCH VỤ UNLOCK ACC", callback_data="order_unlock"),
        types.InlineKeyboardButton("📈 BUFF SUB / LIKE / VIEW", callback_data="smm_services"),
        types.InlineKeyboardButton("💳 NẠP TIỀN THẺ CÀO", callback_data="deposit_card"),
        types.InlineKeyboardButton("👤 TÀI KHOẢN CỦA TÔI", callback_data="profile"),
        types.InlineKeyboardButton("📞 LIÊN HỆ ĐỒNG HÀNH", callback_data="support")
    )
    
    if user_id == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("⚙️ [ADMIN PANEL] QUẢN TRỊ KHO", callback_data="admin_panel"))
        
    text = (
        "⚙️ **HỆ THỐNG DỊCH VỤ MẠNG XÃ HỘI CHUYÊN NGHIỆP**\n"
        "======================================\n"
        f"💰 Số dư tài khoản: `{balance:,} VNĐ`\n"
        f"🆔 ID Khách hàng: `{user_id}`\n"
        "======================================\n"
        "📌 *Cam kết:* Uy tín - Bảo mật - Tốc độ tự động 100%.\n\n"
        "Vui lòng chọn danh mục dịch vụ sếp cần xử lý:"
    )
    return text, markup

@bot.message_handler(commands=['start'])
def cmd_start(message):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (message.from_user.id, message.from_user.username))
    conn.commit()
    conn.close()
    
    text, markup = main_menu(message.from_user.id)
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    
    if call.data == "back_main":
        bot.delete_state(user_id, chat_id)
        text, markup = main_menu(user_id)
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, reply_markup=markup, parse_mode='Markdown')

    elif call.data == "deposit_card":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("VIETTEL", callback_data="card_type_VIETTEL"),
            types.InlineKeyboardButton("VINAPHONE", callback_data="card_type_VINAPHONE"),
            types.InlineKeyboardButton("MOBIFONE", callback_data="card_type_MOBIFONE"),
            types.InlineKeyboardButton("ZING", callback_data="card_type_ZING"),
            types.InlineKeyboardButton("🔙 Quay Lại Menu", callback_data="back_main")
        )
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="💳 **BƯỚC 1: CHỌN LOẠI THẺ CÀO CỦA BẠN**\nHệ thống hỗ trợ duyệt tự động nhanh chóng.", reply_markup=markup)

    elif call.data.startswith("card_type_"):
        ctype = call.data.split("_")[2]
        bot.set_state(user_id, BotStates.card_amount, chat_id)
        with bot.retrieve_data(user_id, chat_id) as data:
            data['card_type'] = ctype
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Hủy giao dịch", callback_data="back_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=f"🔑 Bạn chọn loại thẻ: **{ctype}**\n\n👉 **BƯỚC 2:** Vui lòng gõ nhập **Mệnh giá thẻ** (Ví dụ: 10000, 20000, 50000, 100000...):", reply_markup=markup, parse_mode='Markdown')

    elif call.data == "buy_tool":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🤖 Tool FB VIP - Nuôi & Spam Nick (50k)", callback_data="buy_key_TOOL_FB_50000"),
            types.InlineKeyboardButton("📸 Tool Insta Reg - Tạo Acc Hàng Loạt (100k)", callback_data="buy_key_TOOL_INS_100000"),
            types.InlineKeyboardButton("🎵 Tool TikTok Reg + Buff View (80k)", callback_data="buy_key_TOOL_TT_80000"),
            types.InlineKeyboardButton("✉️ Tool Telegram Scraper - Kéo Mem (120k)", callback_data="buy_key_TOOL_TELE_120000"),
            types.InlineKeyboardButton("🔙 Quay Lại Menu", callback_data="back_main")
        )
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="👇 **DANH SÁCH TOOL AUTO CAO CẤP:**\nVui lòng lựa chọn phần mềm muốn mua key tự động:", reply_markup=markup)

    elif call.data.startswith("buy_key_"):
        _, _, _, tool_name, price = call.data.split("_")
        price = int(price)
        balance = get_balance(user_id)
        
        if balance < price:
            bot.answer_callback_query(call.id, "❌ Tài khoản của sếp không đủ số dư! Vui lòng nạp thêm tiền.", show_alert=True)
            return
            
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, key_code FROM keys WHERE tool_name = ? AND status = 'AVAILABLE' LIMIT 1", (tool_name,))
        key_data = cursor.fetchone()
        
        if not key_data:
            bot.answer_callback_query(call.id, f"❌ Rất tiếc, Tool {tool_name} tạm thời hết key sạch kho. Vui lòng quay lại sau!", show_alert=True)
            conn.close()
            return
            
        key_id, key_code = key_data
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (price, user_id))
        cursor.execute("UPDATE keys SET status = 'SOLD' WHERE id = ?", (key_id,))
        cursor.execute("INSERT INTO orders (user_id, item_name, price, detail) VALUES (?, ?, ?, ?)", (user_id, tool_name, price, f"Key: {key_code}"))
        conn.commit()
        conn.close()
        
        success_text = (
            "✅ **GIAO DỊCH HOÀN TẤT - XUẤT KEY THÀNH CÔNG!**\n\n"
            f"📦 Phần mềm: `{tool_name}`\n"
            f"💰 Giá thanh toán: `-{price:,} VNĐ`\n"
            f"🔑 **MÃ KEY CỦA BẠN:** `{key_code}`\n\n"
            "⚠️ *Chú ý:* Key chỉ kích hoạt trên 1 thiết bị. Cảm ơn sếp!"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Trở về Menu chính", callback_data="back_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=success_text, reply_markup=markup, parse_mode='Markdown')

    elif call.data == "smm_services":
        text = (
            "📈 **HỆ THỐNG DỊCH VỤ TĂNG TƯƠNG TÁC (SMM)**\n\n"
            "• Buff Like / Follow Facebook / Fanpage\n"
            "• Buff View / Tim / Follow TikTok giá siêu rẻ\n"
            "• Tăng Sub kênh YouTube / Thành viên Group Telegram\n\n"
            "👉 *Tính năng này đang được đấu nối API hệ thống.* Vui lòng nhắn tin cho Admin để đặt đơn nhanh chóng thủ công!"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Quay Lại", callback_data="back_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, reply_markup=markup)

    elif call.data == "order_unlock":
        bot.set_state(user_id, BotStates.waiting_unlock_info, chat_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Hủy Đơn", callback_data="back_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="💬 **HỆ THỐNG GỬI ĐƠN UNLOCK TÀI KHOẢN**\n\nVui lòng điền thông tin nick lỗi theo định dạng:\n`Dạng khóa (956/282/Checkpass) | UID | Mật khẩu | Mã 2FA | Giá thỏa thuận`", reply_markup=markup, parse_mode='Markdown')

    elif call.data == "profile":
        balance = get_balance(user_id)
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, detail, created_at FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 5", (user_id,))
        history = cursor.fetchall()
        conn.close()
        
        history_text = ""
        if history:
            for item in history:
                history_text += f"• `[{item[2][:16]}]` {item[0]} -> {item[1]}\n"
        else:
            history_text = "_Chưa có lịch sử giao dịch mua bán._"
            
        text = f"👤 **HỒ SƠ KHÁCH HÀNG:**\n\n🆔 ID: `{user_id}`\n💰 Số dư hiện tại: `{balance:,} VNĐ`\n\n📜 **Lịch sử 5 giao dịch gần nhất:**\n{history_text}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Quay Lại", callback_data="back_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, reply_markup=markup, parse_mode='Markdown')

    elif call.data == "support":
        text = "📞 **HỖ TRỢ KHÁCH HÀNG 24/7**\n\nNếu gặp bất kỳ sự cố nào về lỗi thẻ, treo đơn nạp tiền hoặc lỗi key tool, vui lòng nhắn tin trực tiếp cho Admin!"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Quay Lại Menu", callback_data="back_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, reply_markup=markup)

    elif call.data == "admin_panel" and user_id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("➕ Nạp Key Tool Vào Kho", callback_data="admin_add_key"),
            types.InlineKeyboardButton("🔙 Quay Lại", callback_data="back_main")
        )
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="👑 **HỆ THỐNG QUẢN TRỊ VIÊN**\nVui lòng lựa chọn tác vụ điều hành kho hàng:", reply_markup=markup)

    elif call.data == "admin_add_key" and user_id == ADMIN_ID:
        bot.set_state(user_id, BotStates.waiting_add_key_name, chat_id)
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="✏️ **Admin Nhập Tên Định Danh Tool**\n(Ví dụ: `TOOL_FB`, `TOOL_INS`, `TOOL_TT`, `TOOL_TELE`):")

@bot.message_handler(state=BotStates.card_amount)
def user_input_card_amount(message):
    amount = message.text.strip()
    if not amount.isdigit():
        bot.send_message(message.chat.id, "❌ Mệnh giá phải là số nguyên (Ví dụ: 50000)! Vui lòng gõ lại:")
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['card_amount'] = amount
    bot.set_state(message.from_user.id, BotStates.card_pin, message.chat.id)
    bot.send_message(message.chat.id, "👉 **BƯỚC 3:** Vui lòng gõ nhập **Mã số nạp tiền (Mã PIN)** ẩn dưới lớp cào:")

@bot.message_handler(state=BotStates.card_pin)
def user_input_card_pin(message):
    pin = message.text.strip()
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['card_pin'] = pin
    bot.set_state(message.from_user.id, BotStates.card_seri, message.chat.id)
    bot.send_message(message.chat.id, "👉 **BƯỚC 4 (CUỐI):** Vui lòng gõ nhập **Số Seri** in nổi trên thẻ:")

@bot.message_handler(state=BotStates.card_seri)
def user_input_card_seri(message):
    seri = message.text.strip()
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    with bot.retrieve_data(user_id, chat_id) as data:
        card_type = data['card_type']
        card_amount = data['card_amount']
        card_pin = data['card_pin']
        
    bot.delete_state(user_id, chat_id)
    msg_wait = bot.send_message(chat_id, "⏳ Hệ thống đang xử lý kiểm tra thẻ cào, vui lòng chờ...")

    try:
        bot.delete_message(chat_id, msg_wait.message_id)
        bot.send_message(chat_id, "✅ Thẻ cào đã được gửi lên hệ thống kiểm duyệt thành công! Tiền sẽ tự động cập nhật sau khi Admin xác nhận thông tin.")
        
        admin_card_alert = (
            "💳 **THÔNG BÁO KHÁCH NẠP THẺ CÀO DI ĐỘNG!**\n\n"
            f"👤 Khách hàng: ID `{user_id}`\n"
            f"🏷️ Loại thẻ: `{card_type}` | Mệnh giá: `{int(card_amount):,} đ`\n"
            f"📌 Mã PIN: `{card_pin}`\n"
            f"📌 Số Seri: `{seri}`\n\n"
            "👉 Vui lòng đối soát kiểm tra thẻ và cộng tiền thủ công cho khách!"
        )
        bot.send_message(ADMIN_ID, admin_card_alert)
    except Exception as e:
        bot.send_message(chat_id, "❌ Cổng thẻ cào bận, vui lòng thử lại sau!")

@bot.message_handler(state=BotStates.waiting_add_key_name)
def admin_input_key_name(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['admin_tool_name'] = message.text.strip()
    bot.set_state(message.from_user.id, BotStates.waiting_add_key_code, message.chat.id)
    bot.send_message(message.chat.id, "✏️ **Bước 2:** Nhập chuỗi Key của Tool đó:")

@bot.message_handler(state=BotStates.waiting_add_key_code)
def admin_input_key_code(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        tool_name = data['admin_tool_name']
    key_code = message.text.strip()
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO keys (tool_name, key_code) VALUES (?, ?)", (tool_name, key_code))
        conn.commit()
        bot.send_message(message.chat.id, f"✅ Đã thêm thành công Key `{key_code}` vào sản phẩm `{tool_name}`!")
    except sqlite3.IntegrityError:
        bot.send_message(message.chat.id, "❌ Lỗi: Mã Key này đã tồn tại.")
    finally:
        conn.close()
    bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(state=BotStates.waiting_unlock_info)
def user_input_unlock_info(message):
    user_id = message.from_user.id
    unlock_details = message.text
    bot.send_message(message.chat.id, "✅ Đơn hàng unlock của sếp đã được gửi lên hàng đợi!")
    
    admin_alert = (
        "🔔 **BÁO CÁO: ĐƠN HÀNG UNLOCK MỚI TINH!**\n\n"
        f"👤 Khách hàng: (ID: `{user_id}`)\n"
        f"📝 **Dữ liệu:**\n`{unlock_details}`"
    )
    bot.send_message(ADMIN_ID, admin_alert)
    bot.delete_state(user_id, message.chat.id)

bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))

if __name__ == '__main__':
    init_db_runtime()
    print("⚡ Bot Dịch Vụ Pro đang chạy...")
    bot.infinity_polling()
