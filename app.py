import streamlit as st
from google import genai
from google.genai.errors import APIError
import os
import json
import time
import random
from datetime import datetime

# =====================
# 1. CONFIG
# =====================
st.set_page_config(page_title="Kei AI", page_icon="🤖", layout="wide")

# =====================
# 2. GOOGLE VERIFICATION & ANALYTICS
# =====================
st.markdown("""
<meta name="google-site-verification" content="s2qrn3my_Y37DRVnCKnxISqZkx2CqYL88z5BrNLGtvM" />
<script async src="https://www.googletagmanager.com/gtag/js?id=G-PGLBV0H3KF"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-PGLBV0H3KF');
</script>
""", unsafe_allow_html=True)

# =====================
# 3. CSS - MODERN GLASSMORPHISM
# =====================
st.markdown("""
<style>
/* ===== BACKGROUND ===== */
.stApp {
    background: linear-gradient(135deg, #0a0a1a, #1a0a2a, #0a0a1a);
    min-height: 100vh;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: rgba(9, 15, 32, 0.9);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* ===== SIDEBAR COMPONENTS ===== */
.online-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 15px;
    text-align: left;
    margin-top: 10px;
    margin-bottom: 20px;
    color: rgba(255,255,255,0.8);
}
.diary-box {
    background: rgba(255,182,230,0.06);
    border: 1px solid rgba(255,138,216,0.2);
    border-radius: 16px;
    padding: 16px;
    margin: 8px 0;
    font-style: italic;
    color: #f0c4e8;
}
.music-box {
    background: rgba(255,138,216,0.08);
    border: 1px solid rgba(255,138,216,0.15);
    border-radius: 12px;
    padding: 12px;
    margin: 5px 0;
    font-size: 13px;
    color: rgba(255,255,255,0.8);
}

/* ======================================== */
/* LOGIN PAGE - GLASSMORPHISM */
/* ======================================== */

/* CARD LOGIN - EFEK KACA */
.login-card {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(30px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 24px;
    padding: 50px 40px 40px 40px;
    max-width: 420px;
    margin: 0 auto;
    box-shadow: 0 25px 50px rgba(0,0,0,0.5);
    animation: fadeInUp 0.8s ease;
}

/* JUDUL - PINK */
.login-title {
    text-align: center;
    font-size: 52px;
    font-weight: 800;
    color: #ff8ad8;
    margin-bottom: 6px;
    letter-spacing: -1px;
    text-shadow: 0 0 40px rgba(255, 138, 216, 0.15);
}

/* SUBTITLE - PUTIH */
.login-subtitle {
    text-align: center;
    font-size: 17px;
    color: rgba(255,255,255,0.8);
    margin-bottom: 32px;
    letter-spacing: 1.5px;
    font-weight: 300;
}

/* HILANGKAN LABEL & ICON */
[data-testid="stTextInput"] label { 
    display: none !important; 
}
[data-testid="stTextInput"] svg { 
    display: none !important; 
}

/* INPUT FIELD - GLASS EFFECT */
[data-testid="stTextInput"] {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
}
[data-testid="stTextInput"] > div {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
}
[data-testid="stTextInput"] input {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
    border-radius: 14px !important;
    background: rgba(255,255,255,0.06) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    padding: 16px 20px !important;
    font-size: 16px !important;
    box-sizing: border-box !important;
    text-align: center !important;
    height: 56px !important;
    min-height: 56px !important;
    max-height: 56px !important;
    transition: all 0.3s ease !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #ff8ad8 !important;
    box-shadow: 0 0 30px rgba(255, 138, 216, 0.08) !important;
    background: rgba(255,255,255,0.08) !important;
}
[data-testid="stTextInput"] input::placeholder {
    color: rgba(255,255,255,0.3) !important;
    text-align: center !important;
    font-size: 15px !important;
    font-weight: 300 !important;
}

/* TOMBOL MASUK - PUTIH */
div[data-testid="stButton"] > button {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
    background: white !important;
    color: #0a0a1a !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    font-size: 17px !important;
    letter-spacing: 1px !important;
    transition: all 0.3s ease !important;
    margin-top: 8px !important;
    box-sizing: border-box !important;
    height: 56px !important;
    min-height: 56px !important;
    max-height: 56px !important;
    cursor: pointer !important;
    box-shadow: 0 4px 20px rgba(255,255,255,0.05) !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 40px rgba(255,255,255,0.15) !important;
    background: #f0f0f0 !important;
}
div[data-testid="stButton"] > button:active {
    transform: scale(0.97) !important;
}

/* COLUMN */
[data-testid="column"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: stretch !important;
}
.stVerticalBlock { gap: 10px !important; }

/* ERROR MESSAGE */
.stAlert {
    text-align: center !important;
    border-radius: 14px !important;
    background: rgba(255, 138, 216, 0.1) !important;
    border: 1px solid rgba(255, 138, 216, 0.2) !important;
    color: #ff8ad8 !important;
    animation: fadeIn 0.5s ease !important;
}

/* CHAT MESSAGES */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: rgba(255, 138, 216, 0.08);
    border: 1px solid rgba(255, 138, 216, 0.15);
    border-radius: 18px;
    padding: 10px 15px;
    margin: 8px 0;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 10px 15px;
    margin: 8px 0;
}
[data-testid="stChatInput"] {
    border-radius: 20px !important;
    border: 1px solid rgba(255,138,216,0.2) !important;
    background: rgba(255,255,255,0.04) !important;
}

/* ANIMASI */
@keyframes fadeInUp {
    from { 
        opacity: 0; 
        transform: translateY(30px) scale(0.98); 
    }
    to { 
        opacity: 1; 
        transform: translateY(0) scale(1); 
    }
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ======================================== */
/* RESPONSIVE HP */
/* ======================================== */
@media (max-width: 768px) {
    .login-card {
        padding: 35px 24px 30px 24px !important;
        margin: 10px 12px !important;
        border-radius: 20px !important;
    }
    .login-title {
        font-size: 38px !important;
    }
    .login-subtitle {
        font-size: 15px !important;
        margin-bottom: 25px !important;
    }
    [data-testid="stTextInput"] input {
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        font-size: 14px !important;
        padding: 12px 14px !important;
        border-radius: 12px !important;
    }
    [data-testid="stTextInput"] input::placeholder {
        font-size: 14px !important;
    }
    div[data-testid="stButton"] > button {
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        font-size: 15px !important;
        padding: 12px 14px !important;
        border-radius: 12px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# =====================
# 4. SESSION STATE
# =====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "avatar" not in st.session_state:
    st.session_state.avatar = None

if "mode" not in st.session_state:
    st.session_state.mode = "chat"

CHAT_FILE = "chat_history.json"
DIARY_FILE = "dear_diary.json"

def load_chat():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    return []

def save_chat(messages):
    with open(CHAT_FILE, "w") as f:
        json.dump(messages, f)

def load_diary():
    if os.path.exists(DIARY_FILE):
        with open(DIARY_FILE, "r") as f:
            return json.load(f)
    return []

def save_diary(entries):
    with open(DIARY_FILE, "w") as f:
        json.dump(entries, f, ensure_ascii=False)

if "messages" not in st.session_state:
    st.session_state.messages = load_chat()

# =====================
# 5. LOGIN PAGE - GLASSMORPHISM
# =====================
if not st.session_state.logged_in:
    
    col1, col2, col3 = st.columns([1, 2.2, 1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="login-title">✦ Kei AI</div>
            <div class="login-subtitle">Teman AI Pintar Kamu</div>
        """, unsafe_allow_html=True)
        
        # USERNAME
        username = st.text_input(
            "", 
            placeholder="Username", 
            key="username_input", 
            label_visibility="collapsed"
        )
        
        # PASSWORD
        password = st.text_input(
            "", 
            placeholder="Password", 
            type="password", 
            key="password_input", 
            label_visibility="collapsed"
        )
        
        # TOMBOL MASUK
        if st.button("Masuk", use_container_width=True, key="login_button"):
            if username == "ryuu" and password == "12345":
                st.session_state.logged_in = True
                st.session_state.messages = load_chat()
                st.rerun()
            else:
                st.error("Username atau password salah")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.stop()

# =====================
# 6. GEMINI SETUP
# =====================
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("API Key Gemini tidak ditemukan! Pastikan kamu sudah memasang 'GEMINI_API_KEY' di Secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash"

def generate_content_with_retry(full_prompt):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=MODEL_NAME, contents=full_prompt)
            return response.text
        except APIError as e:
            if e.code == 429:
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                else:
                    return "Waduh Kak, kuota Kei lagi penuh banget nih... (｡>﹏<｡) Coba tunggu beberapa saat lagi ya!"
            else:
                return f"Terjadi kesalahan API: {e.message}"
        except Exception as e:
            return f"Terjadi kesalahan sistem: {str(e)}"

# =====================
# 7. PERSONA KEI
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
- Berikan pelukan virtual dan kata-kata penyemangat
- Kalau user sedih, ikut rasain kesedihan mereka lalu perlahan hibur
- Pakai bahasa yang lembut dan personal
- Boleh pakai emoji hati dan ekspresi hangat 💕🥺🫂
- Akhiri selalu dengan kalimat penyemangat yang tulus
"""

# =====================
# 8. STIKER
# =====================
STICKERS = {
    "happy": ["(｡♥‿♥｡)", "✨(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", "٩(◕‿◕｡)۶", "(≧◡≦)", "🎉✨💕"],
    "love":  ["(♥ω♥*)", "💕(｡･ω･｡)💕", "ʕ•ᴥ•ʔ♥", "(˘³˘)♥", "💖💖💖"],
    "sad":   ["(´；ω；`)", "(T_T)", "｡ﾟ(ﾟ´ω`ﾟ)ﾟ｡", "(っ˘̩╭╮˘̩)っ", "🥺💧"],
    "cool":  ["(•̀ᴗ•́)و", "✌️😎", "(¬‿¬)", "( ͡° ͜ʖ ͡°)", "🔥💪"],
    "shy":   ["(///▽///)", "(/ω＼)", "(〃＞＿＜;〃)", "///(^v^)///", "🌸💗"],
}

def get_sticker(mood):
    return random.choice(STICKERS.get(mood, STICKERS["happy"]))

# =====================
# 9. SIDEBAR
# =====================
with st.sidebar:

    avatar_exists = os.path.exists("kei_avatar.png")

    if avatar_exists:
        st.image("kei_avatar.png", width=220)
        with st.expander("Ganti / Hapus Foto"):
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
            if st.button("Hapus Foto"):
                os.remove("kei_avatar.png")
                st.session_state.avatar = None
                st.rerun()
    else:
        uploaded_avatar = st.file_uploader(
            "Upload Foto Kei",
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
        KEI AI
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Mode:**")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Chat", key="mode_chat"):
            st.session_state.mode = "chat"
            st.rerun()
    with col_b:
        if st.button("Diary", key="mode_diary"):
            st.session_state.mode = "diary"
            st.rerun()

    st.markdown(f"*Mode aktif: {'Chat' if st.session_state.mode == 'chat' else 'Dear Diary'}*")
    st.markdown("---")

    with st.expander("Kirim Stiker"):
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

    with st.expander("Putar Musik"):
        music_query = st.text_input("Nama lagu / artis", key="music_input")
        if st.button("Cari", key="music_search"):
            if music_query:
                search_url = f"https://www.youtube.com/results?search_query={music_query.replace(' ', '+')}"
                st.markdown(f"""
                <div class="music-box">
                    🎵 <b>{music_query}</b><br>
                    <a href="{search_url}" target="_blank" style="color:#ff8ad8;">Buka di YouTube</a>
                </div>
                """, unsafe_allow_html=True)

    if st.button("New Chat"):
        st.session_state.messages = []
        save_chat([])
        st.rerun()

    if st.button("Clear Chat"):
        st.session_state.messages = []
        save_chat([])
        st.rerun()

    st.markdown("---")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.rerun()

# =====================
# 10. HEADER
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
# 11. DEAR DIARY MODE
# =====================
if st.session_state.mode == "diary":

    diary_entries = load_diary()

    if diary_entries:
        with st.expander(f"Lihat {len(diary_entries)} entri diary lama"):
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
        send_diary = st.button("Kirim ke Kei", use_container_width=True)
    with col2:
        clear_diary = st.button("Hapus Diary", use_container_width=True)

    if clear_diary:
        save_diary([])
        st.success("Diary berhasil dihapus!")
        st.rerun()

    if send_diary and diary_input:
        with st.spinner("Kei lagi baca curhatanmu... 🥺"):
            full_prompt = f"{KEI_DIARY_PERSONA}\n\nUser curhat: {diary_input}\n\nKei menjawab dengan hangat:"
            kei_reply = generate_content_with_retry(full_prompt)

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
# 12. CHAT DISPLAY
# =====================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =====================
# 13. CHAT INPUT
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

    with st.spinner("Kei sedang mengetik... ✨"):
        reply = generate_content_with_retry(full_prompt) + search_note

    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_chat(st.session_state.messages)
    st.rerun()
