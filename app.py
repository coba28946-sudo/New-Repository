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
# 3. CSS
# =====================
st.markdown("""
<style>
/* Global */
.stApp { background: #0a0a0a; }

/* ---- LOGIN ---- */
.login-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 80vh;
    padding: 20px;
}
.login-title {
    color: #ff8ad8;
    font-size: 48px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 4px;
}
.login-subtitle {
    color: rgba(255,255,255,0.5);
    font-size: 18px;
    text-align: center;
    margin-bottom: 36px;
}
.login-footer {
    text-align: center;
    color: rgba(255,255,255,0.25);
    font-size: 13px;
    margin-top: 28px;
}
.login-footer span { color: #ff8ad8; }

/* Card */
[data-testid="stForm"] {
    background: #161616 !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 20px !important;
    padding: 32px 28px !important;
    max-width: 480px !important;
    margin: 0 auto !important;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5) !important;
}

/* Input fields */
[data-testid="stTextInput"] label { display: none !important; }
[data-testid="stTextInput"] svg { display: none !important; }
[data-testid="stTextInput"] > div > div {
    background: #222222 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
[data-testid="stTextInput"] input {
    background: transparent !important;
    color: white !important;
    font-size: 15px !important;
    padding: 14px 16px !important;
    height: 52px !important;
    caret-color: #ff8ad8;
}
[data-testid="stTextInput"] input::placeholder {
    color: rgba(255,255,255,0.3) !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(255,138,216,0.4) !important;
    box-shadow: none !important;
}
/* Password eye toggle */
[data-testid="stTextInput"] button {
    background: transparent !important;
    border: none !important;
    color: rgba(255,255,255,0.4) !important;
}

/* Masuk button */
[data-testid="stForm"] div[data-testid="stButton"] > button {
    width: 100% !important;
    background: #1c1c1c !important;
    color: rgba(255,255,255,0.85) !important;
    font-weight: 600 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    height: 52px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stForm"] div[data-testid="stButton"] > button:hover {
    background: #252525 !important;
    border-color: rgba(255,138,216,0.35) !important;
    color: #ff8ad8 !important;
}

/* ---- CHAT / SIDEBAR ---- */
h1 { color: #ff8ad8; }
[data-testid="stSidebar"] { background: #111111 !important; }
[data-testid="stChatInput"] textarea {
    background: #1a1a1a !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
[data-testid="stChatMessage"] {
    background: transparent !important;
}

/* Alert */
.stAlert { max-width: 480px; margin: 0 auto; border-radius: 10px; }

/* Vertical gap fix */
.stVerticalBlock { gap: 10px !important; }

@media (max-width: 768px) {
    .login-title { font-size: 36px; }
    .login-subtitle { font-size: 16px; margin-bottom: 24px; }
    [data-testid="stForm"] { padding: 24px 18px !important; }
}
</style>
""", unsafe_allow_html=True)

# =====================
# 4. SESSION STATE
# =====================
for key, default in {
    "logged_in": False,
    "avatar": None,
    "mode": "chat",
    "messages": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

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
# 6. LOGIN PAGE
# =====================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-title">✦ Kei AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Teman AI Pintar Kamu</div>', unsafe_allow_html=True)

        with st.form("login_form"):
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

        st.markdown(
            '<div class="login-footer">Kei AI — Your AI Companion <span>✦</span></div>',
            unsafe_allow_html=True,
        )
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
    border-radius:12px;padding:15px;text-align:left;margin:10px 0 20px;color:rgba(255,255,255,0.7);">
        🟢 Online<br>KEI AI
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
                border-radius:12px;padding:12px;margin:5px 0;font-size:13px;color:rgba(255,255,255,0.7);">
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

    # Optional Google search link
    browsing_keywords = ["cari", "search", "browsing", "cek", "info tentang", "berita", "apa itu", "siapa itu"]
    if any(kw in prompt.lower() for kw in browsing_keywords):
        search_url  = f"https://www.google.com/search?q={prompt.replace(' ', '+')}"
        search_note = f"\n\n🌐 *Kei juga nyariin buat Kak di sini ya:* [Klik untuk lihat hasil pencarian]({search_url})"
    else:
        search_note = ""

    # Build history
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
