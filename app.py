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
# 3. CSS DASAR (base)
# =====================
st.markdown("""
<style>
/* ===== GLOBAL ===== */
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
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    letter-spacing: -1px;
    margin-bottom: 4px;
}
.login-sub {
    font-size: 16px;
    text-align: center;
    margin-bottom: 32px;
}
.login-footer {
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
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 18px;
    transition: all 0.2s;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    background: #1a1a1a;
    color: rgba(255,255,255,0.6);
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
    font-size: 36px;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
}
.kei-header p {
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
}

[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 4px 0 !important;
}

[data-testid="stChatInput"] {
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    font-size: 16px !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: rgba(255,255,255,0.3) !important; }
[data-testid="stChatInput"] button {
    border-radius: 8px !important;
    border: none !important;
}
[data-testid="stChatInput"] button svg { fill: white !important; }

.kei-sidebar-inner .stButton > button {
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
    width: 100% !important;
    text-align: left !important;
    font-size: 14px !important;
    padding: 8px 14px !important;
    transition: all 0.15s !important;
    background: rgba(255,255,255,0.04) !important;
    color: rgba(255,255,255,0.7) !important;
}
.kei-sidebar-inner .stButton > button:hover {
    border-color: rgba(255,138,216,0.4) !important;
    color: #ff8ad8 !important;
    background: rgba(255,138,216,0.05) !important;
}

.kei-sidebar-inner [data-testid="stTextInput"] > div {
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    background: rgba(255,255,255,0.04) !important;
}
.kei-sidebar-inner [data-testid="stTextInput"] input {
    background: transparent !important;
    font-size: 13px !important;
    height: 38px !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 12px !important;
    color: #fff !important;
}
.kei-sidebar-inner [data-testid="stTextInput"] label { font-size: 12px !important; }

.kei-sidebar-inner [data-testid="stExpander"] {
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
    background: rgba(255,255,255,0.02) !important;
}
.kei-sidebar-inner [data-testid="stExpander"] summary {
    font-size: 13px !important;
    color: rgba(255,255,255,0.6) !important;
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
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    background: rgba(255,255,255,0.03);
    color: rgba(255,255,255,0.6);
    margin-bottom: 12px;
}
.dot-online { width: 8px; height: 8px; border-radius: 50%; background: #4ade80; flex-shrink: 0; }

.diary-box {
    border: 1px solid rgba(255,138,216,0.1);
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
    font-size: 14px;
    background: rgba(255,182,230,0.05);
    color: #f0c4e8;
}

.kei-divider {
    height: 1px;
    margin: 12px 0;
    background: rgba(255,255,255,0.06);
}

.music-result {
    border: 1px solid rgba(255,138,216,0.1);
    border-radius: 10px;
    padding: 10px 12px;
    font-size: 13px;
    margin-top: 8px;
    background: rgba(255,138,216,0.04);
    color: rgba(255,255,255,0.7);
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

/* Sembunyikan "Press Enter to apply" hanya di login */
small[data-testid="InputInstructions"] {
    display: none !important;
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
# 3b. CSS DINAMIS (Tema & Warna)
# =====================
def render_dynamic_css():
    accent = st.session_state.get("theme_color", "#ff8ad8")
    theme  = st.session_state.get("theme", "dark")

    hex_color = accent.lstrip("#")
    try:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        r, g, b = (255, 138, 216)

    if theme == "light":
        # Light mode colors
        bg_main      = "#f5f3f8"
        bg_sidebar   = "#ffffff"
        bg_input     = "#ffffff"
        bg_chat_bubble_user = "#e8e0f0"
        bg_chat_bubble_kei  = "#f0edf5"
        text_main    = "#1a1a2e"
        text_dim     = "rgba(0,0,0,0.55)"
        text_dimmer  = "rgba(0,0,0,0.35)"
        border_col   = "rgba(0,0,0,0.12)"
        border_col_light = "rgba(0,0,0,0.08)"
        input_bg     = "rgba(0,0,0,0.03)"
        shadow_color = "rgba(0,0,0,0.08)"
        scrollbar_bg = "rgba(0,0,0,0.05)"
        scrollbar_thumb = "rgba(0,0,0,0.15)"
        mode_btn_bg  = "rgba(0,0,0,0.03)"
        mode_btn_border = "rgba(0,0,0,0.1)"
        mode_btn_color = "rgba(0,0,0,0.5)"
        status_bg    = "rgba(0,0,0,0.02)"
        status_border = "rgba(0,0,0,0.08)"
        status_color = "rgba(0,0,0,0.5)"
        expander_bg  = "rgba(0,0,0,0.02)"
        expander_border = "rgba(0,0,0,0.08)"
        expander_color = "rgba(0,0,0,0.5)"
        music_bg     = "rgba(255,138,216,0.04)"
        music_border = "rgba(255,138,216,0.12)"
        music_color  = "rgba(0,0,0,0.6)"
        diary_box_bg = "rgba(255,138,216,0.04)"
        diary_box_border = "rgba(255,138,216,0.12)"
        diary_box_color = "#2a1a2e"
        button_hover_bg = "rgba(255,138,216,0.08)"
        chat_input_bg = "#ffffff"
        chat_input_border = "rgba(0,0,0,0.15)"
        chat_placeholder = "rgba(0,0,0,0.35)"
        sidebar_toggle_bg = "#ffffff"
        sidebar_toggle_color = "rgba(0,0,0,0.5)"
        sidebar_toggle_border = "rgba(0,0,0,0.12)"
        login_title_color = "#2a1a2e"
        login_sub_color = "rgba(0,0,0,0.4)"
        login_footer_color = "rgba(0,0,0,0.2)"
        # tambahan untuk chat message
        chat_msg_bg_user = "#e8e0f0"
        chat_msg_bg_kei = "#f0edf5"
    else:
        # Dark mode colors (existing)
        bg_main      = "#0a0e1a"
        bg_sidebar   = "#111111"
        bg_input     = "#1a1a1a"
        bg_chat_bubble_user = "transparent"
        bg_chat_bubble_kei  = "transparent"
        text_main    = "#ffffff"
        text_dim     = "rgba(255,255,255,0.5)"
        text_dimmer  = "rgba(255,255,255,0.35)"
        border_col   = "rgba(255,255,255,0.07)"
        border_col_light = "rgba(255,255,255,0.04)"
        input_bg     = "rgba(255,255,255,0.04)"
        shadow_color = "rgba(0,0,0,0.4)"
        scrollbar_bg = "rgba(255,255,255,0.05)"
        scrollbar_thumb = "rgba(255,255,255,0.15)"
        mode_btn_bg  = "rgba(255,255,255,0.03)"
        mode_btn_border = "rgba(255,255,255,0.08)"
        mode_btn_color = "rgba(255,255,255,0.5)"
        status_bg    = "rgba(255,255,255,0.03)"
        status_border = "rgba(255,255,255,0.06)"
        status_color = "rgba(255,255,255,0.6)"
        expander_bg  = "rgba(255,255,255,0.02)"
        expander_border = "rgba(255,255,255,0.06)"
        expander_color = "rgba(255,255,255,0.6)"
        music_bg     = "rgba(255,138,216,0.04)"
        music_border = "rgba(255,138,216,0.1)"
        music_color  = "rgba(255,255,255,0.7)"
        diary_box_bg = "rgba(255,182,230,0.05)"
        diary_box_border = "rgba(255,138,216,0.1)"
        diary_box_color = "#f0c4e8"
        button_hover_bg = "rgba(255,138,216,0.05)"
        chat_input_bg = "#1a1a1a"
        chat_input_border = "rgba(255,255,255,0.1)"
        chat_placeholder = "rgba(255,255,255,0.3)"
        sidebar_toggle_bg = "#1a1a1a"
        sidebar_toggle_color = "rgba(255,255,255,0.6)"
        sidebar_toggle_border = "rgba(255,255,255,0.1)"
        login_title_color = "#ff8ad8"
        login_sub_color = "rgba(255,255,255,0.5)"
        login_footer_color = "rgba(255,255,255,0.2)"
        chat_msg_bg_user = "transparent"
        chat_msg_bg_kei = "transparent"

    # Build CSS
    st.markdown(f"""
    <style>
    /* === BASE LAYOUT === */
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"],
    .main, .main .block-container,
    section.main {{
        background: {bg_main} !important;
        color: {text_main} !important;
    }}

    /* === SCROLLBAR === */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: {scrollbar_bg}; border-radius: 10px; }}
    ::-webkit-scrollbar-thumb {{ background: {scrollbar_thumb}; border-radius: 10px; }}

    /* === LOGIN === */
    .login-title {{ color: {accent} !important; }}
    .login-sub {{ color: {login_sub_color} !important; }}
    .login-footer {{ color: {login_footer_color} !important; }}

    /* === SIDEBAR === */
    .kei-sidebar,
    section[data-testid="stSidebar"],
    [data-testid="stSidebarContent"] {{
        background: {bg_sidebar} !important;
        border-right: 1px solid {border_col} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {text_main} !important;
    }}

    /* === HEADER === */
    .kei-header h1 {{ color: {accent} !important; }}
    .kei-header p {{ color: {text_dim} !important; }}

    /* === INPUT AREA === */
    .kei-input-area,
    [data-testid="stBottom"] > div,
    [data-testid="stBottomBlockContainer"] {{
        background: {bg_main} !important;
        border-top: 1px solid {border_col} !important;
    }}

    /* === CHAT INPUT === */
    [data-testid="stChatInput"] {{
        background: {chat_input_bg} !important;
        border: 1px solid {chat_input_border} !important;
    }}
    [data-testid="stChatInput"] textarea {{
        background: transparent !important;
        color: {text_main} !important;
    }}
    [data-testid="stChatInput"] textarea::placeholder {{
        color: {chat_placeholder} !important;
    }}
    [data-testid="stChatInput"] button {{
        background: {accent} !important;
    }}

    /* === SIDEBAR BUTTONS === */
    .kei-sidebar-inner .stButton > button,
    .kei-sidebar-inner [data-testid="stBaseButton-secondary"] {{
        background: {input_bg} !important;
        color: {text_main} !important;
        border: 1px solid {border_col} !important;
    }}
    .kei-sidebar-inner .stButton > button p,
    .kei-sidebar-inner .stButton > button span,
    .kei-sidebar-inner .stButton > button div {{
        color: {text_main} !important;
    }}
    .kei-sidebar-inner .stButton > button:hover {{
        border-color: rgba({r},{g},{b},0.4) !important;
        color: {accent} !important;
        background: {button_hover_bg} !important;
    }}
    .kei-sidebar-inner .stButton > button:hover p,
    .kei-sidebar-inner .stButton > button:hover span {{
        color: {accent} !important;
    }}

    /* === SIDEBAR TEXT INPUT === */
    .kei-sidebar-inner [data-testid="stTextInput"] > div {{
        background: {input_bg} !important;
        border: 1px solid {border_col} !important;
    }}
    .kei-sidebar-inner [data-testid="stTextInput"] input {{
        background: transparent !important;
        color: {text_main} !important;
    }}
    .kei-sidebar-inner [data-testid="stTextInput"] label {{
        color: {text_dim} !important;
    }}

    /* === SIDEBAR EXPANDER === */
    .kei-sidebar-inner [data-testid="stExpander"],
    .kei-sidebar-inner details {{
        background: {expander_bg} !important;
        border-width: 1px !important;
        border-style: solid !important;
        border-color: {expander_border} !important;
        border-radius: 10px !important;
        box-shadow: 0 0 0 1px {expander_border} !important;
        margin-bottom: 8px !important;
        overflow: hidden !important;
    }}
    .kei-sidebar-inner [data-testid="stExpander"] summary,
    .kei-sidebar-inner [data-testid="stExpanderHeader"],
    .kei-sidebar-inner summary {{
        background: transparent !important;
        color: {text_main} !important;
        font-size: 13px !important;
        border: none !important;
    }}
    .kei-sidebar-inner [data-testid="stExpander"] summary *,
    .kei-sidebar-inner [data-testid="stExpanderHeader"] *,
    .kei-sidebar-inner summary * {{
        color: {text_main} !important;
        fill: {text_main} !important;
    }}
    .kei-sidebar-inner [data-testid="stExpanderDetails"],
    .kei-sidebar-inner [data-testid="stExpander"] > div:not(summary) {{
        background: transparent !important;
        border: none !important;
    }}

    /* === SIDEBAR LABELS === */
    .kei-sidebar-inner label,
    .kei-sidebar-inner [data-testid="stCaptionContainer"],
    .kei-sidebar-inner [data-testid="stCaptionContainer"] p,
    .kei-sidebar-inner [data-testid="stWidgetLabel"] p {{
        color: {text_dim} !important;
    }}
    .kei-sidebar-inner [data-testid="stRadio"] label span,
    .kei-sidebar-inner [data-testid="stRadio"] label p {{
        color: {text_main} !important;
    }}
    .kei-sidebar-inner [data-testid="stMarkdownContainer"] p,
    .kei-sidebar-inner [data-testid="stMarkdownContainer"] strong {{
        color: {text_main} !important;
    }}

    /* === MODE BUTTONS === */
    .mode-btn:hover {{
        border-color: rgba({r},{g},{b},0.4) !important;
        color: {accent} !important;
    }}
    .mode-btn.active {{
        border-color: {accent} !important;
        background: rgba({r},{g},{b},0.08) !important;
        color: {accent} !important;
    }}

    /* === STATUS === */
    .status-online {{
        background: {status_bg} !important;
        border: 1px solid {status_border} !important;
        color: {status_color} !important;
    }}
    .status-online * {{ color: {status_color} !important; }}

    /* === DIARY BOX === */
    .diary-box {{
        background: {diary_box_bg} !important;
        border: 1px solid {diary_box_border} !important;
        color: {diary_box_color} !important;
    }}
    .diary-box b {{ color: {accent} !important; }}

    /* === DIVIDER === */
    .kei-divider {{ background: {border_col} !important; }}

    /* === MUSIC RESULT === */
    .music-result {{
        background: {music_bg} !important;
        border: 1px solid {music_border} !important;
        color: {music_color} !important;
    }}
    .music-result a {{ color: {accent} !important; }}

    /* === CHAT MESSAGES === */
    [data-testid="stChatMessage"],
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] strong,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {{
        color: {text_main} !important;
    }}
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {{
        background: {input_bg} !important;
    }}
    
    /* === CHAT BUBBLE BACKGROUND (only for light mode) === */
    {f'''
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {{
        background: {chat_msg_bg_user} !important;
        border-radius: 12px !important;
        padding: 8px 12px !important;
    }}
    [data-testid="stChatMessage"][data-testid="stChatMessageAssistant"] [data-testid="stMarkdownContainer"] {{
        background: {chat_msg_bg_kei} !important;
    }}
    ''' if theme == "light" else ''}

    /* === GENERAL MARKDOWN === */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] strong,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {{
        color: {text_main} !important;
    }}

    /* === METRICS === */
    [data-testid="stMetricValue"] {{ color: {accent} !important; }}
    [data-testid="stMetricLabel"] {{ color: {text_dim} !important; }}

    /* === ALERTS === */
    [data-testid="stAlertContentInfo"],
    [data-testid="stAlertContentSuccess"],
    [data-testid="stAlertContentWarning"],
    [data-testid="stAlertContentError"] {{
        color: {text_main} !important;
    }}
    .stDownloadButton button {{
        background: rgba({r},{g},{b},0.12) !important;
        color: {accent} !important;
        border: 1px solid rgba({r},{g},{b},0.3) !important;
    }}

    /* === SIDEBAR TOGGLE === */
    .sidebar-toggle {{
        background: {sidebar_toggle_bg} !important;
        color: {sidebar_toggle_color} !important;
        border: 1px solid {sidebar_toggle_border} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# =====================
# 4. INISIALISASI SESSION STATE
# =====================
for key, val in {
    "logged_in": False,
    "mode": "chat",
    "messages": [],
    "avatar": None,
    "sidebar_open": True,
    "conv_result": None,
    "theme": "dark",
    "lang": "id",
    "theme_color": "#ff8ad8",
    "current_mood_index": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# =====================
# 4b. PREFERENSI PERSISTEN
# =====================
PREFS_FILE = "kei_prefs.json"

def load_prefs():
    if os.path.exists(PREFS_FILE):
        try:
            with open(PREFS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}

def save_prefs():
    prefs = {
        "theme": st.session_state.theme,
        "lang": st.session_state.lang,
        "theme_color": st.session_state.theme_color,
    }
    with open(PREFS_FILE, "w") as f:
        json.dump(prefs, f, ensure_ascii=False)

if "_prefs_loaded" not in st.session_state:
    _prefs = load_prefs()
    st.session_state.theme = _prefs.get("theme", st.session_state.theme)
    st.session_state.lang = _prefs.get("lang", st.session_state.lang)
    st.session_state.theme_color = _prefs.get("theme_color", st.session_state.theme_color)
    st.session_state._prefs_loaded = True

render_dynamic_css()

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
# 5b. BAHASA (i18n)
# =====================
TEXTS = {
    "id": {
        "app_tagline": "Teman AI Pintar Kamu",
        "app_companion": "Your AI Companion",
        "username": "Username",
        "password": "Password",
        "login_btn": "Masuk",
        "login_err_empty": "Username dan password tidak boleh kosong.",
        "login_err_wrong": "Username atau password salah.",
        "chat_btn": "💬 Chat",
        "diary_btn": "💌 Diary",
        "online_status": "Online",
        "mood_today": "Mood Kei hari ini",
        "streak": "Streak ngobrol",
        "streak_unit": "hari",
        "mode_label": "Mode",
        "mode_chat": "💬 Chat",
        "mode_diary": "💌 Dear Diary",
        "sticker_expander": "😄 Kirim Stiker",
        "music_expander": "🎵 Putar Musik",
        "music_input_label": "Nama lagu / artis",
        "music_search_btn": "Cari 🔍",
        "convert_expander": "🔄 Konversi File",
        "settings_expander": "⚙️ Pengaturan",
        "theme_label": "🌙 Tampilan",
        "theme_dark": "Gelap",
        "theme_light": "Terang",
        "lang_label": "🌐 Bahasa",
        "lang_id": "Indonesia",
        "lang_en": "English",
        "mood_expander": "🎭 Ubah Mood Kei",
        "mood_pick_label": "Pilih mood Kei sekarang:",
        "mood_auto_btn": "🔄 Otomatis (harian)",
        "mood_auto_active": "Aktif — mood berganti otomatis tiap hari",
        "mood_auto_inactive": "Nonaktif — kamu pilih mood manual",
        "stats_expander": "📊 Statistik Chat",
        "stats_total_msgs": "Total pesan",
        "stats_user_msgs": "Pesan kamu",
        "stats_kei_msgs": "Balasan Kei",
        "stats_active_days": "Hari aktif",
        "new_chat": "🆕 New Chat",
        "clear_chat": "🗑️ Clear Chat",
        "logout": "🚪 Logout",
        "diary_header_sub": "Ceritain semua ke Kei ya~",
        "diary_old_entries": "📖 Lihat {n} entri diary lama",
        "diary_textarea_label": "💌 Cerita ke Kei...",
        "diary_placeholder": "Hari ini aku ngerasa... / Kei, aku mau curhat nih...",
        "diary_send": "Kirim ke Kei 💕",
        "diary_clear": "Hapus Diary",
        "diary_cleared": "Diary berhasil dihapus!",
        "diary_you_wrote": "Kamu tulis:",
        "diary_kei_answers": "Kei menjawab:",
        "chat_placeholder": "Ketik
