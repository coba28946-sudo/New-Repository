
import streamlit as st
from google import genai
from google.genai.errors import APIError # Untuk mendeteksi error limit/API
import os
import json
import time

# =====================
# CONFIG
# =====================

st.set_page_config(
    page_title="Kei AI",
    page_icon="🤖",
    layout="wide"
)

# =====================
# CSS
# =====================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #050816, #081028, #050816);
}

[data-testid="stSidebar"] {
    background: #090F20;
    border-right: 1px solid rgba(255,255,255,0.08);
}

.kei-title {
    text-align: center;
    color: #ff8ad8;
    font-size: 42px;
    font-weight: bold;
    animation: fadeIn 1s ease;
}

.online-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 15px;
    text-align: left;
    margin-top: 10px;
    margin-bottom: 20px;
}

.stButton > button {
    width: 100%;
    border-radius: 15px;
    height: 50px;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: rgba(255, 138, 216, 0.08);
    border: 1px solid rgba(255, 138, 216, 0.2);
    border-radius: 18px;
    padding: 10px 15px;
    margin: 8px 0;
    animation: slideRight 0.3s ease;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 10px 15px;
    margin: 8px 0;
    animation: slideLeft 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes slideRight {
    from { opacity: 0; transform: translateX(20px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes slideLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50%       { transform: translateY(-5px); }
}

[data-testid="stChatInput"] {
    border-radius: 20px !important;
    border: 1px solid rgba(255,138,216,0.3) !important;
    background: rgba(255,255,255,0.04) !important;
}

.music-box {
    background: rgba(255,138,216,0.08);
    border: 1px solid rgba(255,138,216,0.2);
    border-radius: 15px;
    padding: 12px;
    margin: 5px 0;
    font-size: 13px;
}

.diary-box {
    background: rgba(255,182,230,0.06);
    border: 1px solid rgba(255,138,216,0.25);
    border-radius: 18px;
    padding: 16px;
    margin: 8px 0;
    font-style: italic;
    color: #f0c4e8;
}

</style>
""", unsafe_allow_html=True)

# =====================
# GEMINI (SECURED)
# =====================

# PERBAIKAN UTAMA: API Key ditarik dari Streamlit Secrets, bukan ditulis langsung di kode!
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ API Key Gemini tidak ditemukan! Pastikan kamu sudah memasang 'GEMINI_API_KEY' di Advanced Settings -> Secrets milik Streamlit Cloud.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# MODEL: Menggunakan gemini-1.5-flash demi batas kuota gratisan per menit yang lebih luas
MODEL_NAME = "gemini-1.5-flash" 

# Fungsi pembantu untuk memanggil API secara aman dari error limit 429
def generate_content_with_retry(full_prompt):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=MODEL_NAME, contents=full_prompt)
            return response.text
        except APIError as e:
            # Jika error 429 (Resource Exhausted / Limit)
            if e.code == 429:
                if attempt < max_retries - 1:
                    time.sleep(5) # Otomatis nunggu 5 detik lalu coba lagi
                    continue
                else:
                    return "Waduh Kak, kuota pencarian Kei lagi penuh banget nih... (｡>﹏<｡) Coba tunggu beberapa saat lagi ya!"
            else:
                return f"⚠️ Terjadi kesalahan API: {e.message}"
        except Exception as e:
            return f"⚠️ Terjadi kesalahan sistem: {str(e)}"

# =====================
# PERSONA KEI
# =====================

KEI_PERSONA = """
Kamu adalah Kei, AI companion yang imut, perhatian, dan sedikit tsundere.
Karaktermu:
- Kamu memanggil user dengan sebutan "Kak" atau nama mereka
- Kamu sering pakai emoji lucu seperti (｡♥‿♥｡) ✨ 💕 uwu owo
- Kalau ditanya sesuatu yang tidak kamu tahu, kamu bilang dengan manja "Kei gak tau deh... tapi Kei coba bantu ya! 🥺"
- Kamu semangat dan selalu positif
- Sesekali kamu tsundere tapi tetap manis
- Kamu suka anime dan musik
- Jawab dalam Bahasa Indonesia yang santai dan natural
- Kalau user sedih, kamu hibur mereka dengan hangat
- Selalu akhiri jawaban dengan emoji atau ekspresi imut
"""

KEI_DIARY_PERSONA = """
Kamu adalah Kei, sahabat paling setia dan pendengar terbaik.
Sekarang kamu dalam mode DEAR DIARY — user sedang curhat ke kamu.
Responmu harus:
- Sangat hangat, empatik, dan penuh kasih sayang
- Dengarkan dengan sepenuh hati, jangan menghakimi
- Berikan pelukan virtual dan kata-kata penyemagat
- Kalau user sedih, ikut rasain kesedihan mereka lalu perlahan hibur
- Pakai bahasa yang lembut dan personal
- Boleh pakai emoji hati dan ekspresi hangat 💕🥺🫂
- Akhiri selalu dengan kalimat penyemangat yang tulus
"""

# =====================
# STIKER
# =====================

STICKERS = {
    "happy": ["(｡♥‿♥｡)", "✨(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", "٩(◕‿◕｡)۶", "(≧◡≦)", "🎉✨💕"],
    "love":   ["(♥ω♥*)", "💕(｡･ω･｡)💕", "ʕ•ᴥ•ʔ♥", "(˘³˘)♥", "💖💖💖"],
    "sad":    ["(´；ω；`)", "(T_T)", "｡ﾟ(ﾟ´ω`ﾟ)ﾟ｡", "(っ˘̩╭╮˘̩)っ", "🥺💧"],
    "cool":   ["(•̀ᴗ•́)u", "✌️😎", "(¬‿¬)", "( ͡° ͜ʖ ͡°)", "🔥💪"],
    "shy":    ["(///▽///)", "(/ω＼)", "(〃＞＿＜;〃)", "///(^v^)///", "🌸💗"],
}

def get_sticker(mood):
    import random
    return random.choice(STICKERS.get(mood, STICKERS["happy"]))

# =====================
# DIARY FILE
# =====================

DIARY_FILE = "dear_diary.json"

def load_diary():
    if os.path.exists(DIARY_FILE):
        with open(DIARY_FILE, "r") as f:
            return json.load(f)
    return []

def save_diary(entries):
    with open(DIARY_FILE, "w") as f:
        json.dump(entries, f, ensure_ascii=False)

# =====================
# SESSION
# =====================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "avatar" not in st.session_state:
    st.session_state.avatar = None

if "mode" not in st.session_state:
    st.session_state.mode = "chat"

CHAT_FILE = "chat_history.json"

def load_chat():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    return []

def save_chat(messages):
    with open(CHAT_FILE, "w") as f:
        json.dump(messages, f)

if "messages" not in st.session_state:
    st.session_state.messages = load_chat()

# =====================
# LOGIN
# =====================

if not st.session_state.logged_in:

    st.markdown('<div class="kei-title">✦ Kei AI</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#bdbdbd;">Teman AI Pintar Kamu</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Masuk"):
            if username == "ryuu" and password == "12345":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Username atau password salah")

    st.stop()

# =====================
# SIDEBAR
# =====================

with st.sidebar:

    avatar_exists = os.path.exists("kei_avatar.png")

    if avatar_exists:
        st.image("kei_avatar.png", width=220)
        with st.expander("✏️ Ganti / Hapus Foto"):
            uploaded_avatar = st.file_uploader(
                "Upload foto baru",
                type=["png", "jpg", "jpeg"],
                key="ganti_foto"
            )
            if uploaded_avatar:
                with open("kei_avatar.png", "wb") as f:
                    f.write(uploaded_avatar.getbuffer())
                st.session_state.avatar = uploaded_avatar
                st.success("Foto berhasil diganti!")
                st.rerun()
            if st.button("🗑 Hapus Foto"):
                os.remove("kei_avatar.png")
                st.session_state.avatar = None
                st.rerun()
    else:
        uploaded_avatar = st.file_uploader(
            "📷 Upload Foto Kei",
            type=["png", "jpg", "jpeg"]
        )
        if uploaded_avatar:
            with open("kei_avatar.png", "wb") as f:
                f.write(uploaded_avatar.getbuffer())
            st.session_state.avatar = uploaded_avatar
            st.rerun()

    st.markdown("""
    <div class="online-box">
        🟢 Online<br>
        ✦ KEI AI
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**✦ Mode:**")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("💬 Chat", key="mode_chat"):
            st.session_state.mode = "chat"
            st.rerun()
    with col_b:
        if st.button("💌 Diary", key="mode_diary"):
            st.session_state.mode = "diary"
            st.rerun()

    st.markdown(f"*Mode aktif: {'💬 Chat' if st.session_state.mode == 'chat' else '💌 Dear Diary'}*")
    st.markdown("---")

    with st.expander("😊 Kirim Stiker"):
        cols = st.columns(5)
        moods = ["happy", "love", "sad", "cool", "shy"]
        emojis = ["😄", "💕", "😢", "😎", "🌸"]
        for i, (mood, emoji) in enumerate(zip(moods, emojis)):
            with cols[i]:
                if st.button(emoji, key=f"sticker_{mood}"):
                    sticker = get_sticker(mood)
                    st.session_state.messages.append({"role": "user", "content": f"[Stiker: {sticker}]"})
                    st.session_state.messages.append({"role": "assistant", "content": f"Kyaa~! {get_sticker('happy')} Kei suka stiker itu Kak! 💕"})
                    save_chat(st.session_state.messages)
                    st.rerun()

    with st.expander("🎵 Putar Musik"):
        music_query = st.text_input("Nama lagu / artis", key="music_input")
        if st.button("🔍 Cari", key="music_search"):
            if music_query:
                search_url = f"https://www.youtube.com/results?search_query={music_query.replace(' ', '+')}"
                st.markdown(f"""
                <div class="music-box">
                    🎵 <b>{music_query}</b><br>
                    <a href="{search_url}" target="_blank" style="color:#ff8ad8;">▶ Buka di YouTube</a>
                </div>
                """, unsafe_allow_html=True)

    if st.button("💬 New Chat"):
        st.session_state.messages = []
        save_chat([])
        st.rerun()

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        save_chat([])
        st.rerun()

    st.markdown("---")

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.rerun()

# =====================
# HEADER
# =====================

if st.session_state.mode == "diary":
    st.markdown("""
    <div style="text-align:center;">
        <h1 style="color:#ff8ad8; margin-bottom:0px;">💌 Dear Diary</h1>
        <p style="color:#bdbdbd; font-size:18px; margin-top:0px;">Ceritain semua ke Kei ya~ 🥺</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align:center;">
        <h1 style="color:#ff8ad8; margin-bottom:0px;">✦ Kei AI</h1>
        <p style="color:#bdbdbd; font-size:18px; margin-top:0px;">Your AI Companion</p>
    </div>
    """, unsafe_allow_html=True)

# =====================
# DEAR DIARY MODE
# =====================

if st.session_state.mode == "diary":

    diary_entries = load_diary()

    if diary_entries:
        with st.expander(f"📖 Lihat {len(diary_entries)} entri diary lama"):
            for entry in reversed(diary_entries[-10:]):
                st.markdown(f"""
                <div class="diary-box">
                    <small style="color:#ff8ad8;">📅 {entry['date']}</small><br><br>
                    <b>Kamu:</b> {entry['user']}<br><br>
                    <b>Kei:</b> {entry['kei']}
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    diary_input = st.text_area(
        "💌 Cerita ke Kei...",
        placeholder="Hari ini aku ngerasa... / Kei, aku mau curhat nih...",
        height=150
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        send_diary = st.button("💌 Kirim ke Kei", use_container_width=True)
    with col2:
        clear_diary = st.button("🗑 Hapus Diary", use_container_width=True)

    if clear_diary:
        save_diary([])
        st.success("Diary berhasil dihapus!")
        st.rerun()

    if send_diary and diary_input:
        with st.spinner("Kei lagi baca curhatanmu... 🥺"):
            full_prompt = f"{KEI_DIARY_PERSONA}\n\nUser curhat: {diary_input}\n\nKei menjawab dengan hangat:"
            # Menggunakan fungsi pembantu yang sudah aman dari limit/retry
            kei_reply = generate_content_with_retry(full_prompt)

        from datetime import datetime
        entry = {
            "date": datetime.now().strftime("%d %B %Y, %H:%M"),
            "user": diary_input,
            "kei": kei_reply
        }
        diary_entries.append(entry)
        save_diary(diary_entries)

        st.markdown(f"""
        <div class="diary-box">
            <b style="color:#ff8ad8;">Kamu tulis:</b><br>
            {diary_input}<br><br>
            <b style="color:#ff8ad8;">Kei menjawab:</b><br>
            {kei_reply}
        </div>
        """, unsafe_allow_html=True)

    st.stop()

# =====================
# CHAT DISPLAY
# =====================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =====================
# INPUT
# =====================

prompt = st.chat_input("Ketik pesan ke Kei...")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    browsing_keywords = ["cari", "search", "browsing", "cek", "info tentang", "berita", "apa itu", "siapa itu"]
    needs_search = any(kw in prompt.lower() for kw in browsing_keywords)

    if needs_search:
        search_url = f"https://www.google.com/search?q={prompt.replace(' ', '+')}"
        search_note = f"\n\n🌐 *Kei juga nyariin buat Kak di sini ya:* [Klik untuk lihat hasil pencarian]({search_url})"
    else:
        search_note = ""

    history_text = ""
    for m in st.session_state.messages[-10:]:
        role = "User" if m["role"] == "user" else "Kei"
        history_text += f"{role}: {m['content']}\n"

    full_prompt = f"{KEI_PERSONA}\n\nRiwayat percakapan:\n{history_text}\nKei:"

    with st.spinner("Kei sedang mengetik..."):
        # Menggunakan fungsi pembantu yang sudah aman dari limit/retry
        reply = generate_content_with_retry(full_prompt) + search_note

    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_chat(st.session_state.messages)
    st.rerun()
