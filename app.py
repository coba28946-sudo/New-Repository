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
# 3. CSS
# =====================
st.markdown("""
<style>
/* ===== GLOBAL ===== */
html, body, .stApp {
    background-color: #0a0a0a !important;
    color: white !important;
}

/* Hide streamlit default chrome on login */
#MainMenu, footer, header { visibility: hidden; }

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
    color: rgba(255,255,255,0.4);
    font-size: 17px;
    text-align: center;
    margin-bottom: 36px;
}
.login-footer {
    color: rgba(255,255,255,0.2);
    font-size: 13px;
    text-align: center;
    margin-top: 24px;
}
.login-footer b { color: #ff8ad8; }

/* Form card */
div[data-testid="stForm"] {
    background: #161616 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 20px !important;
    padding: 32px 28px 28px !important;
    box-shadow: 0 24px 64px rgba(0,0,0,0.7) !important;
}

/* Input wrapper */
div[data-testid="stTextInput"] > div {
    background: #202020 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 0 !important;
}
div[data-testid="stTextInput"] > div:focus-within {
    border-color: rgba(255,138,216,0.45) !important;
    box-shadow: 0 0 0 2px rgba(255,138,216,0.08) !important;
}

/* Input element */
div[data-testid="stTextInput"] input {
    background: transparent !important;
    color: white !important;
    font-size: 15px !important;
    padding: 0 16px !important;
    border: none !important;
    box-shadow: none !important;
    height: 50px !important;
    line-height: normal !important;
    padding-bottom: 16px !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: rgba(255,255,255,0.28) !important;
}

/* Hide label & icon */
div[data-testid="stTextInput"] label,
div[data-testid="stTextInput"] svg { display: none !important; }

/* Password toggle eye */
div[data-testid="stTextInput"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: rgba(255,255,255,0.35) !important;
    padding-right: 12px !important;
}

/* Submit button inside form */
div[data-testid="stForm"] div[data-testid="stButton"] > button {
    width: 100% !important;
    background: #1e1e1e !important;
    color: rgba(255,255,255,0.8) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 13px !important;
    height: 50px !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
}
div[data-testid="stForm"] div[data-testid="stButton"] > button:hover {
    background: #262626 !important;
    border-color: rgba(255,138,216,0.4) !important;
    color: #ff8ad8 !important;
}

/* Error box */
div[data-testid="stAlert"] {
    background: rgba(255,70,70,0.08) !important;
    border: 1px solid rgba(255,70,70,0.2) !important;
    border-radius: 10px !important;
    color: #ff6b6b !important;
    font-size: 14px !important;
}

/* ===== CHAT / APP ===== */
[data-testid="stSidebar"] { background: #111111 !important; }
[data-testid="stChatMessage"] { background: transparent !important; }
[data-testid="stChatInput"] textarea {
    background: #1a1a1a !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
h1 { color: #ff8ad8 !important; }
</style>
""", unsafe_allow_html=True)

# =====================
# 4. SESSION STATE
# =====================
for key, val in {"logged_in": False, "mode": "chat", "messages": [], "avatar": None}.items():
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
# 10. SIDEBAR
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
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
    border-radius:12px;padding:15px;margin:10px 0 20px;color:rgba(255,255,255,0.7);">
        🟢 Online &nbsp; KEI AI
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Mode:**")
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
                <div style="background:rgba(255,138,216,0.04);border:1px solid rgba(255,138,216,0.08);
                border-radius:12px;padding:12px;font-size:13px;color:rgba(255,255,255,0.7);">
                    🎵 <b>{music_query}</b><br>
                    <a href="{search_url}" target="_blank" style="color:#ff8ad8;">Buka di YouTube</a>
                </div>
                """, unsafe_allow_html=True)

    if st.button("🆕 New Chat"):
        st.session_state.messages = []
        save_json(CHAT_FILE, [])
        st.rerun()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        save_json(CHAT_FILE, [])
        st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.messages  = []
        st.rerun()

# =====================
# 11. HEADER
# =====================
if st.session_state.mode == "diary":
    st.markdown("""
    <div style="text-align:center;">
        <h1 style="color:#ff8ad8;margin-bottom:0;">💌 Dear Diary</h1>
        <p style="color:#bdbdbd;font-size:18px;margin-top:0;">Ceritain semua ke Kei ya~ 🥺</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align:center;">
        <h1 style="color:#ff8ad8;margin-bottom:0;">✦ Kei AI</h1>
        <p style="color:#bdbdbd;font-size:18px;margin-top:0;">Your AI Companion</p>
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
                <div style="background:rgba(255,182,230,0.05);border:1px solid rgba(255,138,216,0.1);
                border-radius:12px;padding:16px;margin:8px 0;color:#f0c4e8;">
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
        <div style="background:rgba(255,182,230,0.05);border:1px solid rgba(255,138,216,0.1);
        border-radius:12px;padding:16px;margin:8px 0;color:#f0c4e8;">
            <b style="color:#ff8ad8;">Kamu tulis:</b><br>{diary_input}<br><br>
            <b style="color:#ff8ad8;">Kei menjawab:</b><br>{kei_reply}
        </div>
        """, unsafe_allow_html=True)

    st.stop()

# =====================
# 13. CHAT DISPLAY
# =====================
if not st.session_state.messages:
    st.session_state.messages = load_json(CHAT_FILE)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =====================
# 14. CHAT INPUT
# =====================
prompt = st.chat_input("Ketik pesan ke Kei...")
if prompt:
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
