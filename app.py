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
.stApp {
    background: linear-gradient(135deg, #050816, #081028, #050816);
}

[data-testid="stSidebar"] {
    background: #090F20;
    border-right: 1px solid rgba(255,255,255,0.08);
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

.diary-box {
    background: rgba(255,182,230,0.06);
    border: 1px solid rgba(255,138,216,0.25);
    border-radius: 18px;
    padding: 16px;
    margin: 8px 0;
    font-style: italic;
    color: #f0c4e8;
}

.music-box {
    background: rgba(255,138,216,0.08);
    border: 1px solid rgba(255,138,216,0.2);
    border-radius: 15px;
    padding: 12px;
    margin: 5px 0;
    font-size: 13px;
}

/* ===================== */
/* LOGIN PAGE - SEMPURNA */
/* ===================== */

/* Hilangkan label & icon */
[data-testid="stTextInput"] label { display: none !important; }
[data-testid="stTextInput"] svg   { display: none !important; }

/* Input field */
[data-testid="stTextInput"] input {
    width: 100% !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.07) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    padding: 16px 20px !important;
    font-size: 16px !important;
    box-sizing: border-box !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    text-align: center !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: #ff8ad8 !important;
    box-shadow: 0 0 20px rgba(255, 138, 216, 0.15) !important;
    outline: none !important;
}

[data-testid="stTextInput"] input::placeholder {
    color: rgba(255,255,255,0.35) !important;
    text-align: center !important;
}

/* Tombol Masuk - DIPERLEBAR */
div[data-testid="stButton"] > button {
    width: 100% !important;
    background: white !important;
    color: #07080f !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 16px !important;
    font-size: 16px !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
    margin-top: 8px !important;
    box-sizing: border-box !important;
    min-height: 52px !important;
}

div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(255,255,255,0.15) !important;
    background: #f0f0f0 !important;
}

/* Column jadi stretch */
[data-testid="column"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: stretch !important;
}

.stVerticalBlock { gap: 12px !important; }

.stAlert {
    text-align: center !important;
    border-radius: 12px !important;
}

/* Chat messages */
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

[data-testid="stChatInput"] {
    border-radius: 20px !important;
    border: 1px solid rgba(255,138,216,0.3) !important;
   
