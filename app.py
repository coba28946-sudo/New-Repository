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
# 3. CSS — Tema Gelap/Terang Otomatis + Mobile Fix
# =====================
st.markdown("""
<style>
/* ===== TEMA GELAP (DEFAULT) ===== */
:root {
    --bg-primary: #0a0a0a;
    --bg-secondary: #111111;
    --bg-card: #161616;
    --bg-input: #202020;
    --text-primary: #ffffff;
    --text-secondary: rgba(255,255,255,0.7);
    --text-muted: rgba(255,255,255,0.4);
    --border-color: rgba(255,255,255,0.08);
    --border-hover: rgba(255,138,216,0.45);
    --chat-bg: #2b2b2b;
    --shadow: rgba(0,0,0,0.7);
    --msg-user: rgba(255,138,216,0.15);
    --msg-assistant: rgba(255,255,255,0.05);
    --diary-bg: rgba(255,182,230,0.05);
    --diary-border: rgba(255,138,216,0.1);
    --diary-text: #f0c4e8;
    --music-bg: rgba(255,138,216,0.04);
    --music-border: rgba(255,138,216,0.08);
}

/* ===== TEMA TERANG (otomatis ikut setting perangkat) ===== */
@media (prefers-color-scheme: light) {
    :root {
        --bg-primary: #f5f5f7;
        --bg-secondary: #ffffff;
        --bg-card: #ffffff;
        --bg-input: #f0f0f0;
        --text-primary: #1a1a1a;
        --text-secondary: rgba(0,0,0,0.7);
        --text-muted: rgba(0,0,0,0.45);
        --border-color: rgba(0,0,0,0.1);
        --border-hover: rgba(255,138,216,0.6);
        --chat-bg: #ffffff;
        --shadow: rgba(0,0,0,0.1);
        --msg-user: rgba(255,138,216,0.14);
        --msg-assistant: rgba(0,0,0,0.045);
        --diary-bg: rgba(255,138,216,0.07);
        --diary-border: rgba(255,138,216,0.18);
        --diary-text: #7a3d63;
        --music-bg: rgba(255,138,216,0.07);
        --music-border: rgba(255,138,216,0.15);
    }
}

/* ===== GLOBAL ===== */
html, body, .stApp {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    transition: background-color 0.3s ease, color 0.3s ease;
}

/* Sembunyikan chrome bawaan Streamlit */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] {
    background: transparent !important;
    box-shadow: none !important;
}
header[data-testid="stHeader"] [data-testid="stToolbar"] {
    display: none !important;
}

/* Tombol toggle sidebar custom (gak gantung ke elemen internal Streamlit) */
#kei-sidebar-toggle {
    position: fixed;
    top: 0.6rem;
    left: 0.6rem;
    z-index: 999999;
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 2px 8px var(--shadow);
}
#kei-sidebar-toggle svg {
    width: 18px;
    height: 18px;
    stroke: var(--text-primary);
}

/* ===== LOGIN PAGE ===== */
.login-title {
    color: #ff8ad8;
    font-size: 46px;
    font-weight: 700;
    text-align: center;
    letter-spacing: -1px;
    margin-bottom: 4px;
}
.login-sub {
    color: var(--text-muted);
    font-size: 17px;
    text-align: center;
    margin-bottom: 36px;
}
.login-footer {
    color: var(--text-muted);
    font-size: 13px;
    text-align: center;
    margin-top: 24px;
}
.login-footer b { color: #ff8ad8; }

/* Form card */
div[data-testid="stForm"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 20px !important;
    padding: 32px 28px 28px !important;
    box-shadow: 0 24px 64px var(--shadow) !important;
}

/* Input wrapper */
div[data-testid="stTextInput"] > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    padding: 0 !important;
}
div[data-testid="stTextInput"] > div:focus-within {
    border-color: var(--border-hover) !important;
    box-shadow: 0 0 0 2px rgba(255,138,216,0.08) !important;
}

/* Input element */
div[data-testid="stTextInput"] input {
    background: transparent !important;
    color: var(--text-primary) !important;
    font-size: 15px !important;
    padding: 0 16px !important;
    border: none !important;
    box-shadow: none !important;
    height: 50px !important;
    line-height: normal !important;
    padding-bottom: 10px !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: var(--text-muted) !important;
}

/* Sembunyikan label & ikon default */
div[data-testid="stTextInput"] label,
div[data-testid="stTextInput"] svg { display: none !important; }

/* Tombol mata show/hide password */
div[data-testid="stTextInput"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--text-muted) !important;
    padding-right: 12px !important;
}

/* Tombol submit form login */
div[data-testid="stForm"] div[data-testid="stButton"] > button {
    width: 100% !important;
    background: var(--bg-input) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 13px !important;
    height: 50px !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
}
div[data-testid="stForm"] div[data-testid="stButton"] > button:hover {
    background: var(--bg-card) !important;
    border-color: var(--border-hover) !important;
    color: #ff8ad8 !important;
}

/* Kotak error */
div[data-testid="stAlert"] {
    background: rgba(255,70,70,0.08) !important;
    border: 1px solid rgba(255,70,70,0.2) !important;
    border-radius: 10px !important;
    color: #ff6b6b !important;
    font-size: 14px !important;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-color) !important;
    transition: background-color 0.3s ease;
}
[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] .stButton button {
    background: var(--bg-input) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    border-color: var(--border-hover) !important;
    color: #ff8ad8 !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
}

/* ===== CHAT MESSAGES ===== */
[data-testid="stChatMessage"] {
    background: transparent !important;
}
[data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] {
    background: var(--msg-assistant) !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
    border-radius: 12px !important;
}

/* Pesan user */
[data-testid="stChatMessage"][data-testid*="user"] div[data-testid="stMarkdownContainer"] {
    background: var(--msg-user) !important;
}

/* ===== CHAT INPUT ===== */
[data-testid="stChatInput"] {
    background: var(--chat-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 16px !important;
    padding: 4px 8px !important;
    box-shadow: 0 2px 12px var(--shadow) !important;
    margin-bottom: 20px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--text-primary) !important;
    border: none !important;
    border-radius: 16px !important;
    font-size: 15px !important;
    padding: 12px 16px !important;
    line-height: 1.5 !important;
    resize: none !important;
    min-height: 50px !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
}
[data-testid="stChatInput"] button {
    background: #ff8ad8 !important;
    border-radius: 10px !important;
    border: none !important;
    width: 34px !important;
    height: 34px !important;
    color: white !important;
    margin: 4px !important;
}
[data-testid="stChatInput"] button:hover {
    background: #ff6cc8 !important;
}
[data-testid="stChatInput"] button svg {
    fill: white !important;
    color: white !important;
}

h1 { color: #ff8ad8 !important; }
p, span, label, div { color: inherit; }

/* ===== TOMBOL GANTI MODE (CHAT / DIARY) ===== */
.mode-switcher {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin: 10px 0 20px 0;
    flex-wrap: wrap;
}

.mode-btn {
    background: var(--bg-card);
    border: 2px solid var(--border-color);
    border-radius: 16px;
    padding: 10px 28px;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
}

.mode-btn:hover {
    border-color: var(--border-hover);
    color: #ff8ad8;
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(255,138,216,0.15);
}

.mode-btn.active {
    border-color: #ff8ad8;
    color: #ff8ad8;
    background: rgba(255,138,216,0.08);
}

/* ===== KOTAK DIARY & MUSIK (pakai variabel tema) ===== */
.diary-box {
    background: var(--diary-bg) !important;
    border: 1px solid var(--diary-border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin: 8px 0 !important;
    color: var(--diary-text) !important;
}
.music-box {
    background: var(--music-bg) !important;
    border: 1px solid var(--music-border) !important;
    border-radius: 12px !important;
    padding: 12px !important;
    font-size: 13px !important;
    color: var(--text-secondary) !important;
}
.status-box {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    padding: 15px !important;
    margin: 10px 0 20px !important;
    color: var(--text-secondary) !important;
}

/* ===== RESPONSIVE MOBILE ===== */
@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        min-width: 200px !important;
        max-width: 280px !important;
    }

    [data-testid="stSidebar"] .stButton button {
        font-size: 14px !important;
        padding: 8px 12px !important;
        width: 100% !important;
    }

    .login-title {
        font-size: 32px !important;
    }
    div[data-testid="stForm"] {
        padding: 20px 16px !important;
    }

    .mode-switcher {
        gap: 8px;
        margin: 8px 0 16px 0;
    }
    .mode-btn {
        padding: 8px 16px;
        font-size: 14px;
        border-radius: 12px;
        flex: 1;
        justify-content: center;
        min-width: 80px;
    }

    [data-testid="stChatInput"] {
        position: sticky !important;
        bottom: 0 !important;
        background: var(--bg-primary) !important;
        z-index: 100 !important;
        border-top: 1px solid var(--border-color) !important;
        border-radius: 0 !important;
        padding: 8px 12px !important;
        margin: 0 !important;
    }
    [data-testid="stChatInput"] textarea {
        font-size: 14px !important;
        min-height: 44px !important;
        padding: 8px 12px !important;
    }

    .main > div {
        padding-bottom: 80px !important;
    }
}

/* Tablet */
@media (max-width: 1024px) and (min-width: 769px) {
    [data-testid="stSidebar"] {
        min-width: 240px !important;
        max-width: 300px !important;
    }
}

/* Iframe dari components.html (tombol toggle) jangan sampai keblok ukurannya */
iframe.kei-toggle-frame {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 60px !important;
    height: 60px !important;
    z-index: 999999 !important;
    border: none !important;
    background: transparent !important;
}

/* Batasi lebar konten utama biar simetris (layout wide tapi konten center) */
.main .block-container {
    max-width: 800px !important;
    margin: 0 auto !important;
    padding-top: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

# =====================
# 3b. TOMBOL TOGGLE SIDEBAR CUSTOM
# =====================
import streamlit.components.v1 as components

components.html("""
<style>
  html, body { margin:0; padding:0; background: transparent; }
  #kei-sidebar-toggle {
      position: fixed;
      top: 0.6rem;
      left: 0.6rem;
      z-index: 999999;
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: #161616;
      border: 1px solid rgba(255,255,255,0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(0,0,0,0.5);
  }
  #kei-sidebar-toggle svg {
      width: 18px;
      height: 18px;
      stroke: #ffffff;
  }
</style>
<div id="kei-sidebar-toggle" title="Buka/Tutup menu">
    <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
    </svg>
</div>
<script>
function findToggle() {
    const doc = window.parent.document;
    return doc.querySelector('[data-testid="collapsedControl"] button')
        || doc.querySelector('[data-testid="collapsedControl"]')
        || doc.querySelector('button[kind="header"]')
        || doc.querySelector('[data-testid="stSidebarCollapseButton"] button');
}

const myBtn = document.getElementById('kei-sidebar-toggle');
myBtn.addEventListener('click', function() {
    const target = findToggle();
    if (target) {
        target.click();
    } else {
        const doc = window.parent.document;
        const sidebar = doc.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.display = (sidebar.style.display === 'none') ? '' : 'none';
        }
    }
});

// Tandai iframe pembungkus widget ini sendiri agar bisa ditarget CSS global
(function markFrame() {
    try {
        const myFrame = window.frameElement;
        if (myFrame) {
            myFrame.classList.add('kei-toggle-frame');
        }
    } catch (e) {}
})();
</script>
""", height=0, width=0)


for key, val in {"logged_in": False, "mode": "chat", "messages": [], "avatar": None, "input_text": ""}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# =====================
# 5. FILE HELPERS
# =====================
CHAT_FILE  = "chat_history.json"
DIARY_FILE = "dear_diary.json"

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
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown('<div class="login-title">✦ Kei AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Teman AI Pintar Kamu</div>', unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("u", placeholder="Username", label_visibility="collapsed")
            password = st.text_input("p", placeholder="Password", type="password", label_visibility="collapsed")
            submitted = st.form_submit_button("Masuk", use_container_width=True)

        if submitted:
            if username == "ryuu" and password == "12345":
                st.session_state.logged_in = True
                st.session_state.messages = load_json(CHAT_FILE)
                st.rerun()
            else:
                st.error("Username atau password salah")

        st.markdown('<div class="login-footer">Kei AI — Your AI Companion <b>✦</b></div>', unsafe_allow_html=True)

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
# 9. STIKER
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
# 10. MODE SWITCHER (FLOATING BUTTONS)
# =====================
current_mode = st.session_state.mode

chat_class = "mode-btn active" if current_mode == "chat" else "mode-btn"
diary_class = "mode-btn active" if current_mode == "diary" else "mode-btn"

st.markdown(f"""
<div class="mode-switcher">
    <a href="#" onclick="window.location.href='?mode=chat'" class="{chat_class}" style="text-decoration:none;">
        💬 Chat
    </a>
    <a href="#" onclick="window.location.href='?mode=diary'" class="{diary_class}" style="text-decoration:none;">
        💌 Diary
    </a>
</div>
""", unsafe_allow_html=True)

# Handle mode switching via query params
query_params = st.query_params
if "mode" in query_params:
    new_mode = query_params["mode"]
    if new_mode in ["chat", "diary"] and new_mode != st.session_state.mode:
        st.session_state.mode = new_mode
        st.rerun()

# =====================
# 11. SIDEBAR
# =====================
with st.sidebar:
    avatar_exists = os.path.exists("kei_avatar.png")
    if avatar_exists:
        st.image("kei_avatar.png", width=220)
        with st.expander("Ganti / Hapus Foto"):
            uploaded_avatar = st.file_uploader("Upload foto baru", type=["png","jpg","jpeg"], key="ganti_foto")
            if uploaded_avatar:
                with open("kei_avatar.png", "wb") as f:
                    f.write(uploaded_avatar.getbuffer())
                st.success("Foto berhasil diganti!")
                st.rerun()
            if st.button("Hapus Foto"):
                os.remove("kei_avatar.png")
                st.session_state.avatar = None
                st.rerun()
    else:
        uploaded_avatar = st.file_uploader("Upload Foto Kei", type=["png","jpg","jpeg"])
        if uploaded_avatar:
            with open("kei_avatar.png", "wb") as f:
                f.write(uploaded_avatar.getbuffer())
            st.rerun()

    st.markdown("""
    <div class="status-box">
        🟢 Online &nbsp; KEI AI
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"*Mode aktif: {'💬 Chat' if st.session_state.mode == 'chat' else '💌 Dear Diary'}*")
    st.markdown("---")

    with st.expander("Kirim Stiker"):
        cols = st.columns(5)
        moods  = ["happy", "love", "sad", "cool", "shy"]
        emojis = ["😄", "💕", "😢", "😎", "🌸"]
        for i, (mood, emoji) in enumerate(zip(moods, emojis)):
            with cols[i]:
                if st.button(emoji, key=f"sticker_{mood}"):
                    sticker = get_sticker(mood)
                    st.session_state.messages.append({"role": "user",      "content": f"[Stiker: {sticker}]"})
                    st.session_state.messages.append({"role": "assistant", "content": f"Kyaa~! {get_sticker('happy')} Kei suka stiker itu Kak! 💕"})
                    save_json(CHAT_FILE, st.session_state.messages)
                    st.rerun()

    with st.expander("🎵 Putar Musik"):
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

    if st.button("🆕 New Chat", use_container_width=True):
        st.session_state.messages = []
        save_json(CHAT_FILE, [])
        st.rerun()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        save_json(CHAT_FILE, [])
        st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.messages  = []
        st.rerun()

# =====================
# 12. HEADER
# =====================
if st.session_state.mode == "diary":
    st.markdown("""
    <div style="text-align:center;margin-top:-10px;">
        <h1 style="color:#ff8ad8;margin-bottom:0;">💌 Dear Diary</h1>
        <p style="color:var(--text-secondary);font-size:18px;margin-top:0;">Ceritain semua ke Kei ya~ 🥺</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align:center;margin-top:-10px;">
        <h1 style="color:#ff8ad8;margin-bottom:0;">✦ Kei AI</h1>
        <p style="color:var(--text-secondary);font-size:18px;margin-top:0;">Your AI Companion</p>
    </div>
    """, unsafe_allow_html=True)

# =====================
# 13. DEAR DIARY MODE
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
    diary_input = st.text_area("💌 Cerita ke Kei...", placeholder="Hari ini aku ngerasa... / Kei, aku mau curhat nih...", height=150)

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

    st.stop()

# =====================
# 14. CHAT DISPLAY & INPUT (DIPERBAIKI)
# =====================
# Load chat history
if not st.session_state.messages:
    st.session_state.messages = load_json(CHAT_FILE)

# Tampilkan pesan
chat_container = st.container()
with chat_container:
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ===== CHAT INPUT =====
# st.chat_input mengembalikan None setiap saat sampai user benar-benar
# mengirim pesan — ini normal, BUKAN tanda bahwa input gagal render.
# Fallback manual sebelumnya selalu ikut muncul karena salah membaca None
# sebagai "input tidak muncul", makanya jadi dobel. Sekarang dihapus.
prompt = st.chat_input("Ketik pesan ke Kei...", key="chat_input_main")

if prompt:
    # Proses pesan
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
