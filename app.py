import streamlit as st
from google import genai
from google.genai.errors import APIError
import os
import json
import time
import random
import base64
from PIL import Image
import io
from datetime import datetime, timedelta

# =====================
# 1. CONFIG
# =====================
st.set_page_config(page_title="Kei AI", page_icon="🤖", layout="wide")

# =====================
# 2. ANALYTICS
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
# 3. CSS
# =====================
st.markdown("""
<style>

/* ===== GLOBAL ===== */
html, body, .stApp { background: #0a0e1a !important; color: #ffffff !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; }

[data-testid="stToolbarActions"] button[title*="dit" i],
[data-testid="stToolbarActions"] a[title*="dit" i],
[data-testid="stToolbarActions"] button[aria-label*="dit" i],
[data-testid="stToolbarActions"] a[aria-label*="dit" i] {
    display: none !important;
}
.main .block-container { padding: 0 !important; max-width: 100% !important; }

.login-title {
    color: #ff8ad8;
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    letter-spacing: -1px;
    margin-bottom: 4px;
}
.login-sub {
    color: rgba(255,255,255,0.5);
    font-size: 16px;
    text-align: center;
    margin-bottom: 32px;
}
.login-footer {
    color: rgba(255,255,255,0.2);
    font-size: 12px;
    text-align: center;
    margin-top: 20px;
}

input::-webkit-contacts-auto-fill-button,
input::-webkit-credentials-auto-fill-button {
    visibility: hidden;
    display: none !important;
}
datalist {
    display: none !important;
}

.kei-layout {
    display: flex;
    height: 100vh;
    overflow: hidden;
    position: relative;
}

section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.5rem !important;
}

.kei-sidebar {
    width: 260px;
    min-width: 260px;
    background: #111111;
    border-right: 1px solid rgba(255,255,255,0.07);
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    transition: width 0.25s ease, min-width 0.25s ease, opacity 0.2s ease;
    position: relative;
    z-index: 10;
}
.kei-sidebar.closed {
    width: 0 !important;
    min-width: 0 !important;
    overflow: hidden !important;
    opacity: 0;
}

.sidebar-toggle {
    position: fixed;
    top: 14px;
    left: 14px;
    z-index: 999;
    background: #1a1a1a;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: rgba(255,255,255,0.6);
    font-size: 18px;
    transition: all 0.2s;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}
.sidebar-toggle:hover { border-color: #ff8ad8; color: #ff8ad8; }

.kei-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding-left: 52px;
}

.kei-header {
    text-align: center;
    padding: 20px 0 8px;
    flex-shrink: 0;
}
.kei-header h1 {
    color: #ff8ad8;
    font-size: 36px;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
}
.kei-header p {
    color: rgba(255,255,255,0.4);
    font-size: 14px;
    margin: 4px 0 0;
}

.kei-chat-area {
    flex: 1;
    overflow-y: auto;
    padding: 16px 24px;
}

.kei-input-area {
    flex-shrink: 0;
    padding: 12px 24px 16px;
    border-top: 1px solid rgba(255,255,255,0.06);
    background: #0a0e1a;
}

[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 4px 0 !important;
}

[data-testid="stChatInput"] {
    background: #1a1a1a !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #fff !important;
    font-size: 16px !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: rgba(255,255,255,0.3) !important; }
[data-testid="stChatInput"] button {
    background: #ff8ad8 !important;
    border-radius: 8px !important;
    border: none !important;
}
[data-testid="stChatInput"] button svg { fill: white !important; }

.kei-sidebar-inner .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    color: rgba(255,255,255,0.7) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
    width: 100% !important;
    text-align: left !important;
    font-size: 14px !important;
    padding: 8px 14px !important;
    transition: all 0.15s !important;
}
.kei-sidebar-inner .stButton > button:hover {
    border-color: rgba(255,138,216,0.4) !important;
    color: #ff8ad8 !important;
    background: rgba(255,138,216,0.05) !important;
}

.kei-sidebar-inner [data-testid="stTextInput"] > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}
.kei-sidebar-inner [data-testid="stTextInput"] input {
    background: transparent !important;
    color: #fff !important;
    font-size: 13px !important;
    height: 38px !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 12px !important;
}
.kei-sidebar-inner [data-testid="stTextInput"] label { color: rgba(255,255,255,0.5) !important; font-size: 12px !important; }

.kei-sidebar-inner [data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
}
.kei-sidebar-inner [data-testid="stExpander"] summary {
    color: rgba(255,255,255,0.6) !important;
    font-size: 13px !important;
}

.mode-btn-wrap {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
}
.mode-btn {
    flex: 1;
    padding: 9px 0;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.03);
    color: rgba(255,255,255,0.5);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    text-align: center;
    text-decoration: none;
    display: block;
    transition: all 0.15s;
}
.mode-btn:hover { border-color: rgba(255,138,216,0.4); color: #ff8ad8; }
.mode-btn.active {
    border-color: #ff8ad8;
    background: rgba(255,138,216,0.08);
    color: #ff8ad8;
}

.status-online {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    color: rgba(255,255,255,0.6);
    margin-bottom: 12px;
}
.dot-online { width: 8px; height: 8px; border-radius: 50%; background: #4ade80; flex-shrink: 0; }

.diary-box {
    background: rgba(255,182,230,0.05);
    border: 1px solid rgba(255,138,216,0.1);
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
    color: #f0c4e8;
    font-size: 14px;
}

.kei-divider {
    height: 1px;
    background: rgba(255,255,255,0.06);
    margin: 12px 0;
}

.music-result {
    background: rgba(255,138,216,0.04);
    border: 1px solid rgba(255,138,216,0.1);
    border-radius: 10px;
    padding: 10px 12px;
    font-size: 13px;
    color: rgba(255,255,255,0.7);
    margin-top: 8px;
}

/* Stiker rows — dipusatkan & kompak */
.st-key-kei_sticker_row {
    width: 100% !important;
}
.st-key-kei_sticker_row div[data-testid="stHorizontalBlock"] {
    justify-content: center !important;
    flex-wrap: nowrap !important;
    margin: 0 auto !important;
    width: 100% !important;
}
.st-key-kei_sticker_row div[data-testid^="column"] {
    flex: 1 1 0 !important;
    min-width: 0 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    padding: 0 !important;
}
.st-key-kei_sticker_row [data-testid="stButton"] {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
}
.st-key-kei_sticker_row [data-testid="stButton"] button {
    padding: 6px 0 !important;
    min-width: 0 !important;
    width: 100% !important;
    text-align: center !important;
}

div[data-testid="stTextArea"] label p {
    font-size: 16px !important;
}

@media (max-width: 768px) {
    .kei-sidebar { width: 220px; min-width: 220px; }
    .kei-main { padding-left: 46px; }
    .kei-header h1 { font-size: 28px; }
    .kei-chat-area { padding: 12px 14px; }
    .kei-input-area { padding: 10px 14px 14px; }
}
</style>
""", unsafe_allow_html=True)

# =====================
# 4. SESSION STATE
# =====================
for key, val in {
    "logged_in": False,
    "mode": "chat",
    "messages": [],
    "avatar": None,
    "sidebar_open": True,
    "conv_result": None,   # {"bytes": ..., "filename": ..., "mime": ...}
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# =====================
# 5. FILE HELPERS
# =====================
CHAT_FILE  = "chat_history.json"
DIARY_FILE = "dear_diary.json"
STREAK_FILE = "streak.json"

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False)

# =====================
# 6. LOGIN
# =====================
if not st.session_state.logged_in:
    st.markdown("""
    <div style="padding-top:35px; text-align:center; margin-bottom:12px;">
        <div style="color:#ff8ad8; font-size:50px; font-weight:700; letter-spacing:-1px; margin-bottom:0px; line-height:1.1;">✦ Kei AI</div>
        <div style="color:rgba(255,255,255,0.5); font-size:17px; margin-top:2px;">Teman AI Pintar Kamu</div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.button("Masuk", key="login_btn")

        st.components.v1.html("""
        <script>
        (function setNoAutocomplete() {
            const doc = window.parent.document;
            const inputs = doc.querySelectorAll('[data-testid="stTextInput"] input');
            inputs.forEach(function(el) {
                el.setAttribute('autocomplete', 'off');
                el.setAttribute('autocorrect', 'off');
                el.setAttribute('autocapitalize', 'off');
                el.setAttribute('spellcheck', 'false');
            });
        })();
        </script>
        """, height=0, width=0)

        if submitted:
            if not username or not password:
                st.error("Username dan password tidak boleh kosong.")
            elif username == "ryuu" and password == "12345":
                st.session_state.logged_in = True
                st.session_state.messages = load_json(CHAT_FILE)
                st.rerun()
            else:
                st.error("Username atau password salah.")

    st.markdown("""
    <div style="text-align:center;margin-top:20px;color:rgba(255,255,255,0.18);font-size:12px;">
        Kei AI — Your AI Companion ✦
    </div>
    """, unsafe_allow_html=True)

    st.stop()

# =====================
# 7. GEMINI SETUP
# =====================
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("API Key Gemini tidak ditemukan! Pastikan sudah memasang 'GEMINI_API_KEY' di Secrets.")
    st.stop()

client     = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash"

def generate_content_with_retry(full_prompt):
    for attempt in range(3):
        try:
            response = client.models.generate_content(model=MODEL_NAME, contents=full_prompt)
            return response.text
        except APIError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(5)
            elif e.code == 429:
                return "Waduh Kak, kuota Kei lagi penuh banget nih... (｡>﹏<｡) Coba tunggu sebentar ya!"
            else:
                return f"Terjadi kesalahan API: {e.message}"
        except Exception as e:
            return f"Terjadi kesalahan sistem: {str(e)}"

# =====================
# 8. PERSONA
# =====================
KEI_PERSONA = """
Kamu adalah Kei, AI companion yang imut, perhatian, dan sedikit tsundere.
Karaktermu:
- Kamu memanggil user dengan sebutan "Kak" atau nama mereka
- Kamu sering pakai emoji lucu seperti (｡♥‿♥｡) ✨ 💕 uwu owo
- Kalau ditanya sesuatu yang tidak kamu tahu, bilang dengan manja "Kei gak tau deh... tapi Kei coba bantu ya! 🥺"
- Kamu semangat dan selalu positif
- Sesekali tsundere tapi tetap manis
- Kamu suka anime dan musik
- Jawab dalam Bahasa Indonesia yang santai dan natural
- Kalau user sedih, hibur dengan hangat
- Selalu akhiri jawaban dengan emoji atau ekspresi imut
- Kamu BISA membantu konversi file PDF ke Word dan Word ke PDF lewat fitur di sidebar — kalau user minta, arahkan ke sidebar bagian 🔄 Konversi File
"""

KEI_DIARY_PERSONA = """
Kamu adalah Kei, sahabat paling setia dan pendengar terbaik.
Sekarang kamu dalam mode DEAR DIARY — user sedang curhat ke kamu.
Responmu harus:
- Sangat hangat, empatik, dan penuh kasih sayang
- Dengarkan dengan sepenuh hati, jangan menghakimi
- Berikan pelukan virtual dan kata-kata penyemangat
- Kalau user sedih, ikut rasain lalu perlahan hibur
- Pakai bahasa yang lembut dan personal
- Boleh pakai emoji hati dan ekspresi hangat 💕🥺🫂
- Akhiri selalu dengan kalimat penyemangat yang tulus
"""

# =====================
# 8b. VISION / FOTO
# =====================
def analyze_image_with_kei(image_bytes, mime_type, user_caption=""):
    caption_text = f'User mengirim foto dengan keterangan: "{user_caption}"' if user_caption else "User mengirim foto tanpa keterangan."
    prompt = f"""{KEI_PERSONA}

{caption_text}
Deskripsikan foto ini dengan gaya Kei yang imut dan antusias.
Komentari apa yang ada di foto, berikan reaksi yang hangat dan menyenangkan!
Kei menjawab:"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": base64.b64encode(image_bytes).decode("utf-8"),
                            }
                        },
                        {"text": prompt},
                    ]
                }
            ],
        )
        return response.text
    except Exception as e:
        return f"Eh, Kei susah lihat fotonya nih Kak... (｡>﹏<｡) Error: {str(e)}"

# =====================
# 9. STIKER
# =====================
STICKERS = {
    "happy":   ["(｡♥‿♥｡)", "✨(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", "٩(◕‿◕｡)۶", "(≧◡≦)", "🎉✨💕"],
    "love":    ["(♥ω♥*)", "💕(｡･ω･｡)💕", "ʕ•ᴥ•ʔ♥", "(˘³˘)♥", "💖💖💖"],
    "sad":     ["(´；ω；`)", "(T_T)", "｡ﾟ(ﾟ´ω`ﾟ)ﾟ｡", "(っ˘̩╭╮˘̩)っ", "🥺💧"],
    "cool":    ["(•̀ᴗ•́)و", "✌️😎", "(¬‿¬)", "( ͡° ͜ʖ ͡°)", "🔥💪"],
    "shy":     ["(///▽///)", "(/ω＼)", "(〃＞＿＜;〃)", "///(^v^)///", "🌸💗"],
    "excited": ["(ﾉ≧∀≦)ﾉ", "٩(๑•̀ω•́๑)۶", "ヽ(°〇°)ﾉ", "(灬°‿°灬)", "🎊🎉✨"],
    "sleepy":  ["(－_－) zzZ", "(￣_￣)zzZ", "(-_-)💤", "( ˘ω˘ )スヤァ", "😴💤"],
    "angry":   ["(╬ Ò﹏Ó)", "( ｀皿´)", "٩(ఠ益ఠ)۶", "(￣ヘ￣)", "😤🔥"],
    "hungry":  ["(￣﹃￣)", "( ◕‿◕)🍡", "(*゜▽゜)🍜", "( ˙༥˙ )🍰", "🍣🍜🍡"],
    "sparkle": ["(ﾉ◕ヮ◕)ﾉ:･ﾟ✧", "✧･ﾟ: *✧･ﾟ:*", "☆*:.｡.o(≧▽≦)o.｡.:*☆", "⸜(｡˃ᵕ˂)⸝", "✨🌟💫"],
}

def get_sticker(mood):
    return random.choice(STICKERS.get(mood, STICKERS["happy"]))

# =====================
# 9b. MOOD KEI HARIAN
# =====================
KEI_MOODS = [
    ("😄", "Ceria"),
    ("🥺", "Manja"),
    ("✨", "Semangat"),
    ("😌", "Kalem"),
    ("👀", "Penasaran"),
    ("💕", "Sayang banget"),
    ("😴", "Ngantuk dikit"),
    ("🌸", "Bahagia"),
]

def get_today_mood():
    seed_val = int(datetime.now().strftime("%Y%m%d"))
    rnd = random.Random(seed_val)
    return rnd.choice(KEI_MOODS)

# =====================
# 9c. STREAK NGOBROL
# =====================
def update_and_get_streak():
    data = {}
    if os.path.exists(STREAK_FILE):
        try:
            with open(STREAK_FILE, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            data = {}

    today_str = datetime.now().strftime("%Y-%m-%d")
    last_date = data.get("last_date")
    streak    = data.get("streak", 0)

    if last_date == today_str:
        return streak if streak > 0 else 1

    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if last_date == yesterday_str:
        streak += 1
    else:
        streak = 1

    data["last_date"] = today_str
    data["streak"]    = streak
    save_json(STREAK_FILE, data)
    return streak

# =====================
# 10. SIDEBAR
# =====================
with st.sidebar:
    st.markdown('<div class="kei-sidebar-inner">', unsafe_allow_html=True)

    current_mode = st.session_state.mode

    active_index = 1 if current_mode == "chat" else 2
    st.markdown(f"""
    <style>
    .st-key-kei_mode_switch [data-testid="stButton"] button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        background: rgba(255,255,255,0.03) !important;
        color: rgba(255,255,255,0.5) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        text-align: center !important;
    }}
    .st-key-kei_mode_switch [data-testid="stButton"] button:hover {{
        border-color: rgba(255,138,216,0.4) !important;
        color: #ff8ad8 !important;
    }}
    .st-key-kei_mode_switch div[data-testid^="column"]:nth-of-type({active_index}) button {{
        border-color: #ff8ad8 !important;
        color: #ff8ad8 !important;
        background: rgba(255,138,216,0.08) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    mode_switch = st.container(key="kei_mode_switch")
    with mode_switch:
        mcol1, mcol2 = st.columns(2)
        with mcol1:
            if st.button("💬 Chat", key="mode_chat_btn", use_container_width=True):
                if st.session_state.mode != "chat":
                    st.session_state.mode = "chat"
                    st.rerun()
        with mcol2:
            if st.button("💌 Diary", key="mode_diary_btn", use_container_width=True):
                if st.session_state.mode != "diary":
                    st.session_state.mode = "diary"
                    st.rerun()

    avatar_exists = os.path.exists("kei_avatar.png")
    if avatar_exists:
        st.image("kei_avatar.png", width=200)
        with st.expander("Ganti / Hapus Foto"):
            uploaded_avatar = st.file_uploader("Upload foto baru", type=["png","jpg","jpeg"], key="ganti_foto")
            if uploaded_avatar:
                with open("kei_avatar.png", "wb") as f:
                    f.write(uploaded_avatar.getbuffer())
                st.success("Foto berhasil diganti!")
                st.rerun()
            if st.button("🗑 Hapus Foto"):
                os.remove("kei_avatar.png")
                st.rerun()
    else:
        uploaded_avatar = st.file_uploader("Upload Foto Kei", type=["png","jpg","jpeg"])
        if uploaded_avatar:
            with open("kei_avatar.png", "wb") as f:
                f.write(uploaded_avatar.getbuffer())
            st.rerun()

    st.markdown("""
    <div class="status-online">
        <div class="dot-online"></div>
        <span>Online &nbsp;·&nbsp; KEI AI</span>
    </div>
    """, unsafe_allow_html=True)

    mood_emoji, mood_label = get_today_mood()
    streak_count = update_and_get_streak()

    st.markdown(f"""
    <div class="status-online">
        <span style="font-size:16px;">{mood_emoji}</span>
        <span>Mood Kei hari ini: <b style="color:#ff8ad8;">{mood_label}</b></span>
    </div>
    <div class="status-online">
        <span style="font-size:16px;">🔥</span>
        <span>Streak ngobrol: <b style="color:#ff8ad8;">{streak_count} hari</b></span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<div style='font-size:12px;color:rgba(255,255,255,0.35);margin-bottom:12px;'>Mode: {'💬 Chat' if st.session_state.mode == 'chat' else '💌 Dear Diary'}</div>", unsafe_allow_html=True)

    st.markdown('<div class="kei-divider"></div>', unsafe_allow_html=True)

    with st.expander("😄 Kirim Stiker"):
        sticker_row = st.container(key="kei_sticker_row")
        with sticker_row:
            all_moods  = ["happy", "love", "sad", "cool", "shy", "excited", "sleepy", "angry", "hungry", "sparkle"]
            all_emojis = ["😄",   "💕",   "😢",  "😎",   "🌸",  "🎉",      "😴",     "😤",    "🍜",     "✨"]

            # Baris 1
            cols1 = st.columns(5)
            for i in range(5):
                with cols1[i]:
                    if st.button(all_emojis[i], key=f"sticker_{all_moods[i]}"):
                        sticker = get_sticker(all_moods[i])
                        st.session_state.messages.append({"role": "user",      "content": f"[Stiker: {sticker}]"})
                        st.session_state.messages.append({"role": "assistant", "content": f"Kyaa~! {get_sticker('happy')} Kei suka stiker itu Kak! 💕"})
                        save_json(CHAT_FILE, st.session_state.messages)
                        st.rerun()

            # Baris 2
            cols2 = st.columns(5)
            for i in range(5, 10):
                with cols2[i - 5]:
                    if st.button(all_emojis[i], key=f"sticker_{all_moods[i]}"):
                        sticker = get_sticker(all_moods[i])
                        st.session_state.messages.append({"role": "user",      "content": f"[Stiker: {sticker}]"})
                        st.session_state.messages.append({"role": "assistant", "content": f"Kyaa~! {get_sticker('happy')} Kei suka stiker itu Kak! 💕"})
                        save_json(CHAT_FILE, st.session_state.messages)
                        st.rerun()

    with st.expander("🎵 Putar Musik"):
        music_query = st.text_input("Nama lagu / artis", key="music_input")
        if st.button("Cari 🔍", key="music_search"):
            if music_query:
                search_url = f"https://www.youtube.com/results?search_query={music_query.replace(' ', '+')}"
                st.markdown(f"""
                <div class="music-result">
                    🎵 <b>{music_query}</b><br>
                    <a href="{search_url}" target="_blank" style="color:#ff8ad8;">Buka di YouTube ↗</a>
                </div>
                """, unsafe_allow_html=True)

    with st.expander("🔄 Konversi File"):
        conv_type = st.radio(
            "Pilih konversi:",
            ["PDF → Word (.docx)", "Word (.docx) → PDF"],
            key="conv_type",
        )
        if conv_type == "PDF → Word (.docx)":
            conv_file = st.file_uploader("Upload file PDF", type=["pdf"], key="conv_pdf_upload")
            if st.button("Konversi ✨", key="conv_pdf_btn"):
                if conv_file:
                    with st.spinner("Kei lagi konversi filenya... 🥺"):
                        try:
                            import tempfile
                            from pdf2docx import Converter
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                                tmp_pdf.write(conv_file.read())
                                tmp_pdf_path = tmp_pdf.name
                            out_path = tmp_pdf_path.replace(".pdf", ".docx")
                            cv = Converter(tmp_pdf_path)
                            cv.convert(out_path, start=0, end=None)
                            cv.close()
                            with open(out_path, "rb") as f:
                                docx_bytes = f.read()
                            os.remove(tmp_pdf_path)
                            os.remove(out_path)
                            st.success("Berhasil dikonversi! ✨")
                            st.download_button(
                                "⬇️ Download .docx",
                                data=docx_bytes,
                                file_name=conv_file.name.replace(".pdf", ".docx"),
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key="dl_docx",
                            )
                        except Exception as e:
                            st.error(f"Gagal konversi: {e}")
                else:
                    st.warning("Upload file PDF dulu ya Kak! 🥺")

        else:  # Word → PDF
            conv_file = st.file_uploader("Upload file Word (.docx)", type=["docx"], key="conv_docx_upload")
            if st.button("Konversi ✨", key="conv_docx_btn"):
                if conv_file:
                    with st.spinner("Kei lagi konversi filenya... 🥺"):
                        try:
                            import tempfile, subprocess
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
                                tmp_docx.write(conv_file.read())
                                tmp_docx_path = tmp_docx.name
                            out_dir = tempfile.mkdtemp()
                            result = subprocess.run(
                                ["libreoffice", "--headless", "--convert-to", "pdf",
                                 "--outdir", out_dir, tmp_docx_path],
                                capture_output=True, text=True, timeout=60
                            )
                            base_name = os.path.splitext(os.path.basename(tmp_docx_path))[0]
                            out_pdf = os.path.join(out_dir, base_name + ".pdf")
                            if os.path.exists(out_pdf):
                                with open(out_pdf, "rb") as f:
                                    pdf_bytes = f.read()
                                os.remove(tmp_docx_path)
                                os.remove(out_pdf)
                                st.success("Berhasil dikonversi! ✨")
                                st.download_button(
                                    "⬇️ Download .pdf",
                                    data=pdf_bytes,
                                    file_name=conv_file.name.replace(".docx", ".pdf"),
                                    mime="application/pdf",
                                    key="dl_pdf",
                                )
                            else:
                                st.error(f"LibreOffice gagal: {result.stderr}")
                        except FileNotFoundError:
                            st.error("LibreOffice tidak terinstall. Tambahkan 'libreoffice' ke packages.txt ya Kak!")
                        except Exception as e:
                            st.error(f"Gagal konversi: {e}")
                else:
                    st.warning("Upload file .docx dulu ya Kak! 🥺")

    st.markdown('<div class="kei-divider"></div>', unsafe_allow_html=True)

    if st.button("🆕 New Chat", use_container_width=True):
        st.session_state.messages = []
        save_json(CHAT_FILE, [])
        st.rerun()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        save_json(CHAT_FILE, [])
        st.rerun()

    st.markdown('<div class="kei-divider"></div>', unsafe_allow_html=True)

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.messages  = []
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# =====================
# 11. HEADER
# =====================
header_mood_emoji, _header_mood_label = get_today_mood()

if st.session_state.mode == "diary":
    st.markdown(f"""
    <div style="text-align:center;padding:4px 0 4px;">
        <h1 style="color:#ff8ad8;margin:0;font-size:48px;line-height:1.1;">💌 Dear Diary</h1>
        <p style="color:rgba(255,255,255,0.4);font-size:20px;margin:2px 0 0;">Ceritain semua ke Kei ya~ {header_mood_emoji}</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="text-align:center;padding:4px 0 4px;">
        <h1 style="color:#ff8ad8;margin:0;font-size:48px;line-height:1.1;">✦ Kei AI</h1>
        <p style="color:rgba(255,255,255,0.4);font-size:20px;margin:2px 0 0;">Your AI Companion {header_mood_emoji}</p>
    </div>
    """, unsafe_allow_html=True)

# =====================
# 12. DEAR DIARY MODE
# =====================
if st.session_state.mode == "diary":
    diary_entries = load_json(DIARY_FILE)

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
    diary_input = st.text_area("💌 Cerita ke Kei...",
                               placeholder="Hari ini aku ngerasa... / Kei, aku mau curhat nih...",
                               height=150, key="diary_textarea")
    col1, col2 = st.columns([3, 1])
    with col1:
        send_diary = st.button("Kirim ke Kei 💕", use_container_width=True)
    with col2:
        clear_diary = st.button("Hapus Diary", use_container_width=True)

    if clear_diary:
        save_json(DIARY_FILE, [])
        st.success("Diary berhasil dihapus!")
        st.rerun()

    if send_diary and diary_input:
        with st.spinner("Kei lagi baca curhatanmu... 🥺"):
            full_prompt = f"{KEI_DIARY_PERSONA}\n\nUser curhat: {diary_input}\n\nKei menjawab dengan hangat:"
            kei_reply   = generate_content_with_retry(full_prompt)

        entry = {
            "date": datetime.now().strftime("%d %B %Y, %H:%M"),
            "user": diary_input,
            "kei":  kei_reply,
        }
        diary_entries.append(entry)
        save_json(DIARY_FILE, diary_entries)

        st.markdown(f"""
        <div class="diary-box">
            <b style="color:#ff8ad8;">Kamu tulis:</b><br>{diary_input}<br><br>
            <b style="color:#ff8ad8;">Kei menjawab:</b><br>{kei_reply}
        </div>
        """, unsafe_allow_html=True)

# =====================
# 13. CHAT MODE
# =====================
else:
    if not st.session_state.messages:
        st.session_state.messages = load_json(CHAT_FILE)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("image_b64"):
                img_bytes = base64.b64decode(msg["image_b64"])
                st.image(img_bytes, width=300)
            st.markdown(msg["content"])

    # Tampilkan tombol download hasil konversi kalau ada
    if st.session_state.conv_result:
        cr = st.session_state.conv_result
        with st.chat_message("assistant"):
            st.download_button(
                label=cr["label"],
                data=cr["bytes"],
                file_name=cr["filename"],
                mime=cr["mime"],
                key="dl_conv_persistent",
            )
            if st.button("✅ Selesai", key="conv_done_btn"):
                st.session_state.conv_result = None
                st.rerun()

    # --- Chat Input: foto, PDF, Word, atau teks biasa ---
    chat_input = st.chat_input(
        "Ketik pesan ke Kei... 💕",
        accept_file=True,
        file_type=["jpg", "jpeg", "png", "webp", "pdf", "docx"],
    )

    if chat_input:
        prompt        = chat_input.text or ""
        uploaded_file = chat_input["files"][0] if chat_input["files"] else None

        if uploaded_file:
            file_bytes = uploaded_file.read()
            mime_type  = uploaded_file.type
            fname      = uploaded_file.name.lower()

            # ── PDF → Word ──
            if fname.endswith(".pdf"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"📄 Mengkonversi **{uploaded_file.name}** dari PDF ke Word...",
                })
                with st.spinner("Kei lagi konversi PDF ke Word... 🥺✨"):
                    try:
                        import tempfile
                        from pdf2docx import Converter
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(file_bytes)
                            tmp_path = tmp.name
                        out_path = tmp_path.replace(".pdf", ".docx")
                        cv = Converter(tmp_path)
                        cv.convert(out_path, start=0, end=None)
                        cv.close()
                        with open(out_path, "rb") as f:
                            docx_bytes = f.read()
                        os.remove(tmp_path)
                        os.remove(out_path)
                        reply_text = f"Yeay berhasil Kak! ✨ File **{uploaded_file.name}** sudah Kei konversi ke Word~ (｡♥‿♥｡) Klik tombol download di bawah ya!"
                        st.session_state.messages.append({"role": "assistant", "content": reply_text})
                        st.session_state.conv_result = {
                            "bytes":    docx_bytes,
                            "filename": uploaded_file.name.replace(".pdf", ".docx"),
                            "mime":     "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            "label":    "⬇️ Download .docx",
                        }
                        save_json(CHAT_FILE, st.session_state.messages)
                    except Exception as e:
                        err = f"Aduh Kak, Kei gagal konversinya... (｡>﹏<｡) Error: {e}"
                        st.session_state.messages.append({"role": "assistant", "content": err})
                        save_json(CHAT_FILE, st.session_state.messages)

            # ── Word → PDF ──
            elif fname.endswith(".docx"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"📝 Mengkonversi **{uploaded_file.name}** dari Word ke PDF...",
                })
                with st.spinner("Kei lagi konversi Word ke PDF... 🥺✨"):
                    try:
                        import tempfile, subprocess
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                            tmp.write(file_bytes)
                            tmp_path = tmp.name
                        out_dir = tempfile.mkdtemp()
                        result = subprocess.run(
                            ["libreoffice", "--headless", "--convert-to", "pdf",
                             "--outdir", out_dir, tmp_path],
                            capture_output=True, text=True, timeout=60
                        )
                        base_name = os.path.splitext(os.path.basename(tmp_path))[0]
                        out_pdf   = os.path.join(out_dir, base_name + ".pdf")
                        if os.path.exists(out_pdf):
                            with open(out_pdf, "rb") as f:
                                pdf_bytes = f.read()
                            os.remove(tmp_path)
                            os.remove(out_pdf)
                            reply_text = f"Yeay berhasil Kak! ✨ File **{uploaded_file.name}** sudah Kei konversi ke PDF~ (｡♥‿♥｡) Klik tombol download di bawah ya!"
                            st.session_state.messages.append({"role": "assistant", "content": reply_text})
                            st.session_state.conv_result = {
                                "bytes":    pdf_bytes,
                                "filename": uploaded_file.name.replace(".docx", ".pdf"),
                                "mime":     "application/pdf",
                                "label":    "⬇️ Download .pdf",
                            }
                            save_json(CHAT_FILE, st.session_state.messages)
                        else:
                            raise Exception(result.stderr)
                    except FileNotFoundError:
                        err = "Aduh Kak, LibreOffice belum terinstall di server... (｡>﹏<｡) Pastikan `packages.txt` sudah ada ya!"
                        st.session_state.messages.append({"role": "assistant", "content": err})
                        save_json(CHAT_FILE, st.session_state.messages)
                    except Exception as e:
                        err = f"Aduh Kak, Kei gagal konversinya... (｡>﹏<｡) Error: {e}"
                        st.session_state.messages.append({"role": "assistant", "content": err})
                        save_json(CHAT_FILE, st.session_state.messages)

            # ── Foto / Gambar ──
            else:
                img_b64          = base64.b64encode(file_bytes).decode("utf-8")
                user_msg_content = f"[Foto dikirim] {prompt}" if prompt else "[Foto dikirim]"
                st.session_state.messages.append({
                    "role":      "user",
                    "content":   user_msg_content,
                    "image_b64": img_b64,
                })
                with st.spinner("Kei lagi lihat fotonya... 👀✨"):
                    reply = analyze_image_with_kei(file_bytes, mime_type, prompt)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                save_json(CHAT_FILE, st.session_state.messages)
                st.rerun()

        elif prompt:
            # Teks biasa tanpa file
            st.session_state.messages.append({"role": "user", "content": prompt})

            browsing_keywords = ["cari", "search", "browsing", "cek", "info tentang", "berita", "apa itu", "siapa itu"]
            if any(kw in prompt.lower() for kw in browsing_keywords):
                search_url  = f"https://www.google.com/search?q={prompt.replace(' ', '+')}"
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
            save_json(CHAT_FILE, st.session_state.messages)
            st.rerun()
