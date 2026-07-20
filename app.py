import streamlit as st
from google import genai
from google.genai.errors import APIError
from supabase import create_client, Client
import os
import json
import time
import random
import base64
from PIL import Image
import io
import colorsys
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
html, body, .stApp { background: #141414 !important; color: #ffffff !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; }

[data-testid="stToolbarActions"] button[title*="dit" i],
[data-testid="stToolbarActions"] a[title*="dit" i],
[data-testid="stToolbarActions"] button[aria-label*="dit" i],
[data-testid="stToolbarActions"] a[aria-label*="dit" i] {
    display: none !important;
}
.main .block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stMain"] .block-container,
[data-testid="stAppViewBlockContainer"],
section.main > div.block-container,
div[class*="block-container"] {
    padding: 1rem 1.25rem !important;
    max-width: 100% !important;
    width: 100% !important;
    box-sizing: border-box !important;
}
[data-testid="stChatMessage"],
[data-testid="stChatMessageContent"],
[data-testid="stChatInputContainer"] {
    max-width: 100% !important;
    width: 100% !important;
    box-sizing: border-box !important;
}
[data-testid="stMarkdownContainer"] p {
    overflow-wrap: break-word !important;
    word-break: break-word !important;
}
[data-testid="stVerticalBlock"] {
    max-width: 100% !important;
}

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
    letter-spacing: 2.5px;
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

/* ===== FIX PASSWORD/EMAIL INPUT ===== */
[data-testid="stTextInput"] {
    width: 100% !important;
}
[data-testid="stTextInput"] input {
    width: 100% !important;
    box-sizing: border-box !important;
    padding: 0 40px 0 16px !important;
    padding-bottom: 4px !important;
    font-size: 15px !important;
    height: 48px !important;
    line-height: normal !important;
    margin-top: -2px !important;
    vertical-align: middle !important;
}
[data-testid="stTextInput"] div[data-baseweb="input"] {
    overflow: hidden !important;
    border-radius: 12px !important;
}
[data-testid="stTextInput"] [data-baseweb="input"] > div:last-child {
    border-radius: 0 12px 12px 0 !important;
    overflow: hidden !important;
    background: transparent !important;
    border: none !important;
}
[data-testid="stTextInput"] [data-baseweb="input"] button {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    padding: 0 14px !important;
}
[data-testid="stTextInput"] [data-baseweb="input"] button svg {
    fill: rgba(255,255,255,0.45) !important;
}
[data-testid="stTextInput"] [data-baseweb="input"] button:hover svg {
    fill: rgba(255,255,255,0.85) !important;
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

/* FIX GLASS: wrapper internal Streamlit di sidebar sering punya background solid
   bawaan yang menutupi blur dari section utama. Paksa transparan semua wrapper anak,
   TANPA menimpa background translucent milik section[data-testid="stSidebar"] sendiri. */
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] > div > div,
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div,
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    background-color: transparent !important;
}

/* ===== GLASSMORPHISM SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: rgba(17, 17, 17, 0.5) !important;
    backdrop-filter: blur(24px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
    border-right: 1px solid rgba(255,255,255,0.09) !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35) !important;
    position: relative !important;
}

.kei-sidebar {
    width: 260px;
    min-width: 260px;
    background: transparent;
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
    background: rgba(26,26,26,0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
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

/* Force pink color on main title */
[data-testid="stMarkdownContainer"] h1 {
    color: #ff8ad8 !important;
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

/* Kartu profil (avatar, nama, status online) - GLASS */
.kei-sidebar-inner > div:first-child,
div[style*="background: linear-gradient(160deg"] {
    background: linear-gradient(160deg, rgba(255,255,255,0.09), rgba(255,255,255,0.02)) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2) !important;
    border-radius: 18px !important;
}

/* Box Mood & Streak - GLASS */
.kei-sidebar-inner div[style*="flex:1;background:"] {
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
}

.kei-sidebar-inner .stButton > button {
    background: rgba(255,255,255,0.045) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    color: rgba(255,255,255,0.7) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 14px !important;
    width: 100% !important;
    text-align: left !important;
    font-size: 14px !important;
    padding: 8px 14px !important;
    transition: all 0.15s !important;
}
.kei-sidebar-inner .stButton > button:hover {
    border-color: rgba(255,138,216,0.4) !important;
    color: #ff8ad8 !important;
    background: rgba(255,138,216,0.1) !important;
}

.kei-sidebar-inner [data-testid="stTextInput"] > div {
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
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

/* Expander (Ganti Foto, Interaksi, Alat) - GLASS */
.kei-sidebar-inner [data-testid="stExpander"] {
    background: rgba(255,255,255,0.045) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 14px !important;
}
.kei-sidebar-inner [data-testid="stExpander"]:hover {
    background: rgba(255,138,216,0.08) !important;
    border-color: rgba(255,138,216,0.3) !important;
}
.kei-sidebar-inner [data-testid="stExpander"] summary {
    color: rgba(255,255,255,0.6) !important;
    font-size: 13px !important;
    padding: 9px 12px !important;
}
.kei-sidebar-inner [data-testid="stExpander"] summary p {
    display: flex !important;
    align-items: center !important;
}
.kei-sidebar-inner [data-testid="stExpander"] summary p::before {
    content: "";
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    margin-right: 9px;
    border-radius: 8px;
    background: rgba(255,255,255,0.06);
    flex-shrink: 0;
    font-size: 13px;
}
.kei-sidebar-inner [data-testid="stExpander"] summary,
.kei-sidebar-inner [data-testid="stExpander"] summary *,
.kei-sidebar-inner *:focus,
.kei-sidebar-inner *:focus-visible,
.kei-sidebar-inner [data-testid="stExpander"]:focus,
.kei-sidebar-inner [data-testid="stExpander"]:focus-within {
    outline: none !important;
    box-shadow: none !important;
}

/* Logout */
.st-key-logout_btn button {
    background: rgba(255,255,255,0.03) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    color: rgba(255,255,255,0.35) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
}
.st-key-logout_btn button p,
.st-key-logout_btn button span {
    color: rgba(255,255,255,0.35) !important;
}
.st-key-logout_btn button:hover {
    border-color: rgba(239,68,68,0.4) !important;
    background: rgba(239,68,68,0.08) !important;
}
.st-key-logout_btn button:hover p,
.st-key-logout_btn button:hover span {
    color: #f87171 !important;
}

.mode-btn-wrap {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
}
.mode-btn {
    flex: 1;
    padding: 9px 0;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.09);
    background: rgba(255,255,255,0.045);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
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
    background: rgba(255,138,216,0.1);
    color: #ff8ad8;
}

.status-online {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.045);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px;
    padding: 10px 14px;
    font-size: 13px;
    color: rgba(255,255,255,0.6);
    margin-bottom: 12px;
}
.dot-online { width: 8px; height: 8px; border-radius: 50%; background: #4ade80; flex-shrink: 0; box-shadow: 0 0 6px #4ade80; }

.status-panel {
    background: rgba(255,255,255,0.045);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px;
    padding: 4px 14px;
    margin-bottom: 14px;
    font-size: 13px;
    color: rgba(255,255,255,0.6);
}
.status-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 9px 0;
}
.status-row-divider {
    height: 1px;
    background: rgba(255,255,255,0.08);
}

.diary-box {
    background: rgba(255,182,230,0.06);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,138,216,0.12);
    border-radius: 14px;
    padding: 16px;
    margin: 8px 0;
    color: #f0c4e8;
    font-size: 14px;
}

.kei-divider {
    height: 1px;
    background: rgba(255,255,255,0.08);
    margin: 12px 0;
}

.music-result {
    background: rgba(255,138,216,0.05);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,138,216,0.12);
    border-radius: 10px;
    padding: 10px 12px;
    font-size: 13px;
    color: rgba(255,255,255,0.7);
    margin-top: 8px;
}

/* Stiker rows */
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

small[data-testid="InputInstructions"],
[data-testid="InputInstructions"] {
    display: none !important;
}

/* ===== LUPA PASSWORD LINK ===== */
.login-forgot-row {
    text-align: right;
    margin: 10px 0 4px;
}
.login-forgot-row a {
    font-size: 12.5px;
    text-decoration: none;
    transition: color 0.2s ease;
}
.login-forgot-row a:hover {
    text-decoration: underline;
}

/* ===== LOGIN PAGE - GRADIENT & GLOW ===== */
.login-spark-wrap {
    position: relative;
    width: 54px;
    height: 54px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.login-spark-glow {
    position: absolute;
    inset: -16px;
    background: radial-gradient(circle, rgba(255,63,164,0.35), transparent 70%);
    filter: blur(8px);
    animation: login-pulse-glow 2.8s ease-in-out infinite;
}
@keyframes login-pulse-glow {
    0%, 100% { opacity: 0.55; transform: scale(0.92); }
    50% { opacity: 1; transform: scale(1.08); }
}
.login-spark-svg {
    position: relative;
    z-index: 1;
    width: 34px;
    height: 34px;
    animation: login-spark-spin 7s linear infinite;
    transform-origin: center;
}
@keyframes login-spark-spin {
    0% { transform: rotate(0deg) scale(1); }
    50% { transform: rotate(180deg) scale(1.08); }
    100% { transform: rotate(360deg) scale(1); }
}
.login-brand-name {
    font-weight: 800;
    font-size: 52px;
    letter-spacing: -1px;
    background: linear-gradient(95deg, #2b2b40 5%, #D6336C 45%, #A855C9 75%, #3FA9DA 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: login-shine 5s linear infinite;
    line-height: 1;
}
@keyframes login-shine {
    0% { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
}

.st-key-login_btn button {
    background: linear-gradient(95deg, #FF3FA4, #B14EFF) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 8px 24px -8px rgba(255,63,164,0.45) !important;
    transition: box-shadow 0.2s ease, transform 0.15s ease !important;
}
.st-key-login_btn button:hover {
    box-shadow: 0 10px 28px -6px rgba(255,63,164,0.6) !important;
}
.st-key-login_btn button:active {
    transform: scale(0.985) !important;
}
.st-key-login_btn button p,
.st-key-login_btn button span,
.st-key-login_btn button div {
    color: #ffffff !important;
}

.st-key-register_btn button {
    background: linear-gradient(95deg, #FF3FA4, #B14EFF) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 8px 24px -8px rgba(255,63,164,0.45) !important;
}
.st-key-register_btn button p,
.st-key-register_btn button span,
.st-key-register_btn button div {
    color: #ffffff !important;
}

.st-key-send_reset_btn button {
    background: linear-gradient(95deg, #FF3FA4, #B14EFF) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 8px 24px -8px rgba(255,63,164,0.45) !important;
}
.st-key-send_reset_btn button p,
.st-key-send_reset_btn button span,
.st-key-send_reset_btn button div {
    color: #ffffff !important;
}

.stApp {
    background:
        radial-gradient(560px 420px at 50% 18%, rgba(255,63,164,0.10), transparent 70%),
        radial-gradient(640px 480px at 80% 85%, rgba(110,107,255,0.07), transparent 70%),
        radial-gradient(640px 480px at 10% 90%, rgba(177,78,255,0.06), transparent 70%),
        #0a0e1a !important;
}
.st-key-login_card_wrap {
    max-width: min(800px, calc(100vw - 40px)) !important;
    width: 100% !important;
    margin: 40px auto 0 !important;
    background: linear-gradient(180deg, #181a24, #13141c);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 0;
    overflow: hidden;
    position: relative !important;
    min-height: 420px;
    box-shadow:
        0 24px 60px -20px rgba(0,0,0,0.6),
        0 0 80px -20px rgba(255,63,164,0.08);
}

/* ===== PANEL ILUSTRASI ROBOT (kiri) — overlay absolute, gak lagi bersaing tinggi sama form ===== */
.st-key-login_illus_panel {
    background:
        radial-gradient(65% 55% at 30% 25%, rgba(255,63,164,0.14), transparent 70%),
        radial-gradient(65% 60% at 75% 75%, rgba(177,78,255,0.14), transparent 70%),
        linear-gradient(160deg, #fdeaf5, #eee7fb);
    padding: 36px 24px;
    position: absolute !important;
    top: 0;
    left: 0;
    bottom: 0;
    width: 46.5%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    z-index: 1;
}
.st-key-login_illus_panel [data-testid="stVerticalBlock"],
.st-key-login_illus_panel [data-testid="stElementContainer"] {
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.login-ring {
    position: absolute;
    border: 1.5px solid rgba(177,78,255,0.28);
    border-radius: 50%;
}
.login-ring.r1 { width: 210px; height: 210px; top: 8%; left: -60px; }
.login-ring.r2 { width: 150px; height: 150px; top: 20%; left: -10px; border-color: rgba(255,63,164,0.24); }

.robot-wrap {
    position: relative;
    width: 168px;
    height: 200px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.robot-glow {
    position: absolute;
    inset: -10px;
    background: radial-gradient(circle at 50% 45%, rgba(255,63,164,0.30), transparent 65%);
    filter: blur(18px);
    animation: robot-pulse-glow 3s ease-in-out infinite;
}
@keyframes robot-pulse-glow {
    0%, 100% { opacity: 0.55; transform: scale(0.92); }
    50% { opacity: 1; transform: scale(1.08); }
}
.robot-svg {
    position: relative;
    z-index: 1;
    width: 168px;
    height: 200px;
    animation: robot-bob 3.4s ease-in-out infinite;
}
@keyframes robot-bob {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}
.illus-caption {
    margin-top: 6px;
    text-align: center;
    font-size: 13px;
    color: rgba(43,43,64,0.6);
    line-height: 1.6;
    max-width: 230px;
}
.illus-caption b { color: #d6336c; font-weight: 600; }
.illus-content {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0 24px;
    box-sizing: border-box;
}

/* ===== PANEL FORM (kanan) ===== */
.st-key-login_form_panel {
    padding: 28px 32px 18px;
    margin-left: 46.5%;
    width: 53.5%;
    max-width: 53.5%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-sizing: border-box;
    position: relative;
    z-index: 2;
}
.st-key-login_form_panel [data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}
.st-key-login_form_panel [data-testid="stElementContainer"] {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    margin-bottom: 0 !important;
}
.st-key-login_form_panel [data-testid="stTextInput"] input {
    height: 42px !important;
}
.st-key-login_form_panel [data-testid="stTabs"] {
    margin-bottom: 4px !important;
}

.mini-brand-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}
.mini-brand-badge .mini-orb {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: linear-gradient(140deg, #2a1c37, #1a1424);
    border: 1px solid rgba(255,255,255,0.14);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.mini-brand-badge span {
    font-weight: 700;
    font-size: 12.5px;
    letter-spacing: 0.6px;
}
.form-heading {
    font-weight: 700;
    font-size: 22px;
    margin: 0 0 4px;
    letter-spacing: -0.3px;
}
.form-heading .accent {
    background: linear-gradient(95deg, #FF3FA4, #B14EFF);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
.form-subtitle {
    font-size: 13px;
    margin: 0 0 12px;
}

html, body { overflow-x: hidden !important; }
.stApp { overflow-x: hidden !important; }

@media (max-width: 680px) {
    .st-key-login_card_wrap {
        max-width: calc(100vw - 32px) !important;
        width: calc(100vw - 32px) !important;
        margin: 16px auto 0 !important;
        min-height: 0;
    }
    .st-key-login_illus_panel { display: none !important; }
    .login-top-brand { display: none !important; }
    .st-key-login_form_panel {
        padding: 26px 22px 22px !important;
        margin-left: 0 !important;
    }
}

/* Tab styling */
[data-testid="stTabs"] [data-testid="stTab"] {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: rgba(255,255,255,0.5) !important;
}
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
    color: #FF3FA4 !important;
    border-bottom-color: #FF3FA4 !important;
}

/* ===== MENU LIST (KEI SIDEBAR v2) ===== */
.kei-menu-group-label {
    font-size: 10.5px;
    letter-spacing: 1.5px;
    color: rgba(255,255,255,0.32);
    margin: 14px 4px 6px;
    text-transform: uppercase;
}
.st-key-kei_menu_list .stButton > button {
    text-align: left !important;
    justify-content: flex-start !important;
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
# 3b. CSS DINAMIS
# =====================
def hue_shift_rgb(r, g, b, shift):
    """Geser hue warna (r,g,b) sejauh `shift` (0..1), pertahankan saturasi & lightness."""
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    h = (h + shift) % 1.0
    nr, ng, nb = colorsys.hls_to_rgb(h, l, s)
    return int(nr * 255), int(ng * 255), int(nb * 255)

def tint_hex(r, g, b, amount):
    """Campur warna (r,g,b) dengan putih sejauh `amount` (0..1) -> hex pastel."""
    tr = int(r + (255 - r) * amount)
    tg = int(g + (255 - g) * amount)
    tb = int(b + (255 - b) * amount)
    return f"#{tr:02x}{tg:02x}{tb:02x}"

def mix_rgb(c1, c2, t):
    """Interpolasi linear antara 2 warna (r,g,b). t=0 -> c1, t=1 -> c2."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# Warna jangkar tetap buat gradient background - supaya arah "ke biru" & "ke pink"
# selalu konsisten enak dilihat, apa pun warna aksen yang dipilih user.
ANCHOR_BLUE = (63, 169, 218)
ANCHOR_PINK = (214, 51, 108)

def render_dynamic_css():
    accent = st.session_state.get("theme_color", "#ff8ad8")
    theme  = st.session_state.get("theme", "dark")

    hex_color = accent.lstrip("#")
    try:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        r, g, b = (255, 138, 216)

    # Variasi warna turunan dari accent, buat gradient background yang ikut ganti
    # tiap kali warna aksen diganti di Pengaturan. Dicampur (blend) dengan warna
    # jangkar biru & pink yang tetap, biar hasilnya selalu konsisten enak dilihat
    # apa pun warna aksen yang dipilih (gak "loncat" ke hue aneh kayak hue-shift).
    r_blue, g_blue, b_blue = mix_rgb((r, g, b), ANCHOR_BLUE, 0.6)
    r_pink, g_pink, b_pink = mix_rgb((r, g, b), ANCHOR_PINK, 0.6)
    grad_stop1 = tint_hex(r_blue, g_blue, b_blue, 0.72)
    grad_stop2 = tint_hex(r, g, b, 0.68)
    grad_stop3 = tint_hex(r_pink, g_pink, b_pink, 0.70)
    grad_stop4 = tint_hex(r_blue, g_blue, b_blue, 0.76)

    if theme == "light":
        bg_main       = "#eef0fb"
        bg_sidebar    = "rgba(255,255,255,0.35)"
        sidebar_border= "rgba(0,0,0,0.06)"
        glass_fill    = "#ffffff"
        glass_border  = "rgba(0,0,0,0.06)"
        text_main     = "#2b2b40"
        text_dim      = "rgba(43,43,64,0.55)"
        text_dimmer   = "rgba(43,43,64,0.35)"
        border_col    = "#e2def0"
        input_bg      = "rgba(255,255,255,0.6)"
        chat_input_bg = "#ffffff"
    else:
        bg_main       = "#141414"
        bg_sidebar    = "rgba(17,17,17,0.5)"
        sidebar_border= "rgba(255,255,255,0.09)"
        glass_fill    = "rgba(255,255,255,0.045)"
        glass_border  = "rgba(255,255,255,0.09)"
        text_main     = "#ffffff"
        text_dim      = "rgba(255,255,255,0.5)"
        text_dimmer   = "rgba(255,255,255,0.35)"
        border_col    = "rgba(255,255,255,0.16)"
        input_bg      = "rgba(255,255,255,0.045)"
        chat_input_bg = "#1a1a1a"

    st.markdown(f"""
    <style>
    :root {{ color-scheme: {theme} !important; }}
    html {{ color-scheme: {theme} !important; }}

    html, body, .stApp {{
        background: {bg_main} !important;
        color: {text_main} !important;
    }}

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    .kei-input-area {{
        background: transparent !important;
        color: {text_main} !important;
    }}

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] strong,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {{
        color: {text_main} !important;
    }}

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] strong {{
        color: {text_main} !important;
    }}

    /* ===== GAYA CHATGPT: bubble kanan buat user, teks polos kiri buat Kei ===== */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {{
        display: none !important;
    }}
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
        justify-content: flex-end !important;
    }}
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {{
        max-width: 70% !important;
        flex-grow: 0 !important;
    }}
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stMarkdownContainer"] {{
        background: {glass_fill if theme == "light" else "rgba(255,255,255,0.08)"};
        border: 1px solid {glass_border};
        border-radius: 18px !important;
        padding: 10px 16px !important;
        width: fit-content !important;
        margin-left: auto !important;
    }}
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stMarkdownContainer"] {{
        background: transparent !important;
        padding: 4px 0 !important;
    }}

    /* ===== GLASSMORPHISM (ikut tema) ===== */
    section[data-testid="stSidebar"] {{
        background: {bg_sidebar} !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        border-right: 1px solid {sidebar_border} !important;
    }}

    .kei-sidebar-inner > div:first-child,
    div[style*="background: linear-gradient(160deg"] {{
        background: {glass_fill} !important;
        border: 1px solid {glass_border} !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
    }}

    .kei-sidebar-inner div[style*="flex:1;background:"] {{
        background: {glass_fill} !important;
        border: 1px solid {glass_border} !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
    }}

    .kei-input-area {{
        background: {bg_main} !important;
        border-top: 1px solid {border_col} !important;
    }}

    [data-testid="stChatInput"] {{
        background: {chat_input_bg} !important;
        border: {"1px solid " + border_col if theme == "dark" else "none"} !important;
        border-radius: 999px !important;
        box-shadow: {"none" if theme == "dark" else "0 20px 50px rgba(120,100,200,0.18)"} !important;
        padding: {"" if theme == "dark" else "4px"} !important;
        overflow: hidden !important;
    }}
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInputContainer"],
    [data-testid="stChatInput"] [data-baseweb="textarea"],
    [data-testid="stChatInput"] [data-baseweb="base-input"] {{
        background: transparent !important;
        border: none !important;
        border-radius: 999px !important;
        box-shadow: none !important;
    }}
    [data-testid="stChatInput"] textarea {{
        background: transparent !important;
        color: {text_main} !important;
    }}
    [data-testid="stChatInput"] textarea::placeholder {{ color: {text_dimmer} !important; }}
    [data-testid="stChatInput"] button {{ background: {accent} !important; border-radius: 50% !important; }}

    .kei-sidebar-inner .stButton button,
    .kei-sidebar-inner [data-testid="stButton"] button,
    .kei-sidebar-inner button[kind="secondary"],
    .kei-sidebar-inner [data-testid^="stBaseButton"] {{
        background: {glass_fill} !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        color: {text_main} !important;
        border: 1px solid {glass_border} !important;
    }}
    .kei-sidebar-inner .stButton button p,
    .kei-sidebar-inner .stButton button span,
    .kei-sidebar-inner [data-testid^="stBaseButton"] p,
    .kei-sidebar-inner [data-testid^="stBaseButton"] span {{
        color: {text_main} !important;
    }}
    .kei-sidebar-inner .stButton button:hover,
    .kei-sidebar-inner [data-testid^="stBaseButton"]:hover {{
        border-color: rgba({r},{g},{b},0.4) !important;
        color: {accent} !important;
        background: rgba({r},{g},{b},0.1) !important;
    }}
    .kei-sidebar-inner .stButton button:hover p,
    .kei-sidebar-inner .stButton button:hover span {{
        color: {accent} !important;
    }}

    .kei-sidebar-inner [data-testid="stTextInput"] > div {{
        background: {glass_fill} !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid {glass_border} !important;
    }}
    .kei-sidebar-inner [data-testid="stTextInput"] input {{
        background: transparent !important;
        color: {text_main} !important;
    }}
    .kei-sidebar-inner [data-testid="stTextInput"] label {{ color: {text_dim} !important; }}

    .kei-sidebar-inner [data-testid="stExpander"] {{
        background: {glass_fill} !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1px solid {glass_border} !important;
        border-radius: 14px !important;
        margin-bottom: 10px !important;
    }}
    .kei-sidebar-inner [data-testid="stExpander"] summary {{
        color: {text_main} !important;
        font-size: 13px !important;
    }}
    .kei-sidebar-inner [data-testid="stExpander"] summary span,
    .kei-sidebar-inner [data-testid="stExpander"] summary p {{
        color: {text_main} !important;
    }}
    .kei-sidebar-inner [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
    .kei-sidebar-inner [data-testid="stExpander"] [data-testid="stMarkdownContainer"] strong {{
        color: {text_main} !important;
    }}
    .kei-sidebar-inner [data-testid="stExpander"]:hover {{
        border-color: rgba({r},{g},{b},0.35) !important;
        background: rgba({r},{g},{b},0.06) !important;
    }}
    .kei-sidebar-inner [data-testid="stExpander"] summary:focus,
    .kei-sidebar-inner [data-testid="stExpander"] summary:focus-visible,
    .kei-sidebar-inner [data-testid="stExpander"]:focus,
    .kei-sidebar-inner [data-testid="stExpander"]:focus-within,
    .kei-sidebar-inner [data-testid="stExpander"] *:focus,
    .kei-sidebar-inner [data-testid="stExpander"] *:focus-visible {{
        outline: none !important;
        box-shadow: none !important;
        border-color: rgba({r},{g},{b},0.35) !important;
    }}
    .kei-sidebar-inner [data-testid="stExpander"] summary:hover p,
    .kei-sidebar-inner [data-testid="stExpander"] summary:hover span {{
        color: {accent} !important;
    }}

    .kei-sidebar-inner label,
    .kei-sidebar-inner [data-testid="stCaptionContainer"] p,
    .kei-sidebar-inner [data-testid="stWidgetLabel"] p {{
        color: {text_dim} !important;
    }}
    .kei-sidebar-inner [data-testid="stRadio"] label span,
    .kei-sidebar-inner [data-testid="stRadio"] label p {{ color: {text_main} !important; }}

    .mode-btn:hover {{ border-color: rgba({r},{g},{b},0.4) !important; color: {accent} !important; }}
    .mode-btn.active {{
        border-color: {accent} !important;
        background: rgba({r},{g},{b},0.1) !important;
        color: {accent} !important;
    }}

    .status-online {{
        background: {glass_fill} !important;
        border: 1px solid {glass_border} !important;
        color: {text_dim} !important;
    }}
    .status-online span {{ color: {text_dim} !important; }}
    .status-online b {{ color: {accent} !important; }}

    .status-panel {{
        background: {glass_fill} !important;
        border: 1px solid {glass_border} !important;
        color: {text_dim} !important;
    }}
    .status-panel span {{ color: {text_dim} !important; }}
    .status-panel b {{ color: {accent} !important; }}
    .status-row-divider {{ background: {border_col} !important; }}

    .diary-box {{
        background: rgba({r},{g},{b},0.07) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1px solid rgba({r},{g},{b},0.15) !important;
        color: {text_main} !important;
    }}
    .diary-box b {{ color: {accent} !important; }}

    .kei-divider {{ background: {border_col} !important; }}

    .kei-menu-group-label {{ color: {text_dim} !important; font-weight: 700 !important; }}

    .music-result {{
        background: rgba({r},{g},{b},0.05) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba({r},{g},{b},0.15) !important;
        color: {text_dim} !important;
    }}
    .music-result a {{ color: {accent} !important; }}

    [data-testid="stMetricValue"] {{ color: {accent} !important; }}
    [data-testid="stMetricLabel"] {{ color: {text_dim} !important; }}

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

    [data-testid="stTextInput"] > div,
    [data-testid="stTextInput"] > div > div,
    [data-testid="stTextInput"] [data-baseweb="base-input"],
    [data-testid="stTextInput"] [data-baseweb="input"] {{
        background: {input_bg} !important;
        border-color: {border_col} !important;
    }}
    [data-testid="stTextInput"] input {{
        background: transparent !important;
        color: {text_main} !important;
        -webkit-text-fill-color: {text_main} !important;
        caret-color: {text_main} !important;
    }}
    [data-testid="stTextInput"] input::placeholder {{
        color: {text_dimmer} !important;
        -webkit-text-fill-color: {text_dimmer} !important;
    }}
    [data-testid="stTextInput"] label p {{ color: {text_dim} !important; }}
    .stButton > button {{
        background: {input_bg} !important;
        color: {text_main} !important;
        border: 1px solid {border_col} !important;
    }}
    .stButton > button p,
    .stButton > button span {{ color: {text_main} !important; }}
    .stButton > button:hover {{
        border-color: rgba({r},{g},{b},0.4) !important;
        color: {accent} !important;
        background: rgba({r},{g},{b},0.08) !important;
    }}

    ::-webkit-scrollbar,
    html::-webkit-scrollbar,
    body::-webkit-scrollbar,
    [data-testid="stAppViewContainer"]::-webkit-scrollbar,
    [data-testid="stMain"]::-webkit-scrollbar,
    [data-testid="stMainBlockContainer"]::-webkit-scrollbar,
    section[data-testid="stSidebar"]::-webkit-scrollbar,
    section[data-testid="stSidebar"] div::-webkit-scrollbar {{
        width: 8px !important;
        height: 8px !important;
    }}
    ::-webkit-scrollbar-track,
    html::-webkit-scrollbar-track,
    body::-webkit-scrollbar-track,
    [data-testid="stAppViewContainer"]::-webkit-scrollbar-track,
    section[data-testid="stSidebar"]::-webkit-scrollbar-track {{
        background: transparent !important;
    }}
    ::-webkit-scrollbar-thumb,
    html::-webkit-scrollbar-thumb,
    body::-webkit-scrollbar-thumb,
    [data-testid="stAppViewContainer"]::-webkit-scrollbar-thumb,
    section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {accent}, rgba({r},{g},{b},0.35)) !important;
        border-radius: 8px !important;
        border: none !important;
    }}
    ::-webkit-scrollbar-thumb:hover,
    html::-webkit-scrollbar-thumb:hover,
    body::-webkit-scrollbar-thumb:hover,
    [data-testid="stAppViewContainer"]::-webkit-scrollbar-thumb:hover,
    section[data-testid="stSidebar"]::-webkit-scrollbar-thumb:hover {{
        background: {accent} !important;
    }}
    * {{ scrollbar-width: thin; scrollbar-color: rgba({r},{g},{b},0.5) transparent; }}
    html {{ scrollbar-color: rgba({r},{g},{b},0.6) transparent !important; }}

    /* Background utama app - nuansa biru langit lembut ala Blue Archive, aksen pink-purple tetap ada tapi sekunder */
    .stApp {{
        background: {
            (bg_main)
            if theme == "dark" else
            ("radial-gradient(800px 560px at 50% -8%, rgba(180,215,252,0.55), transparent 65%),"
             "radial-gradient(600px 460px at 88% 18%, rgba(" + str(r_pink) + "," + str(g_pink) + "," + str(b_pink) + ",0.10), transparent 65%),"
             "radial-gradient(600px 460px at 6% 85%, rgba(" + str(r) + "," + str(g) + "," + str(b) + ",0.08), transparent 65%),"
             "linear-gradient(180deg, #eaf3fc 0%, #f2f6fb 45%, #f8f7fb 100%)")
        } !important;
        background-attachment: fixed !important;
    }}

    .st-key-kei_quick_actions button {{
        background: {glass_fill} !important;
        border: 1px solid {glass_border} !important;
        color: {text_main} !important;
        border-radius: 999px !important;
    }}
    .st-key-kei_quick_actions button p {{
        color: {text_main} !important;
    }}
    .st-key-kei_quick_actions button:hover {{
        border-color: rgba({r},{g},{b},0.4) !important;
        color: {accent} !important;
        background: rgba({r},{g},{b},0.1) !important;
    }}
    .st-key-kei_quick_actions button:hover p {{
        color: {accent} !important;
    }}

    .st-key-login_card_wrap {{
        background: {"linear-gradient(180deg, #ffffff, #faf9ff)" if theme == "light" else "linear-gradient(180deg, #181a24, #13141c)"} !important;
        border: 1px solid {glass_border} !important;
        box-shadow: {"0 24px 60px -20px rgba(120,90,200,0.18), 0 0 60px -20px rgba(177,78,255,0.08)" if theme == "light" else "0 24px 60px -20px rgba(0,0,0,0.6), 0 0 80px -20px rgba(255,63,164,0.08)"} !important;
    }}

    .login-title {{ color: {accent} !important; }}
    .login-sub {{ color: {text_dim} !important; }}
    .login-footer {{ color: {text_dimmer} !important; }}
    .kei-header h1 {{ color: {accent} !important; }}
    .kei-header p {{ color: {text_dim} !important; }}
    small[data-testid="InputInstructions"],
    [data-testid="InputInstructions"],
    [class*="InputInstructions"] {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    .st-key-forgot_pw_btn {{
        display: flex !important;
        justify-content: flex-end !important;
        margin: 8px 0 4px !important;
    }}
    .st-key-forgot_pw_btn button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: {text_dim} !important;
        font-size: 12.5px !important;
        font-weight: 400 !important;
        height: auto !important;
        min-height: 0 !important;
        padding: 0 !important;
        width: auto !important;
    }}
    .st-key-forgot_pw_btn button:hover {{
        color: {accent} !important;
        text-decoration: underline !important;
        background: transparent !important;
    }}
    .st-key-forgot_pw_btn button p {{
        color: inherit !important;
        margin: 0 !important;
    }}

    </style>
    """, unsafe_allow_html=True)

for key, val in {
    "logged_in": False,
    "user_email": None,
    "mode": "chat",
    "messages": [],
    "avatar": None,
    "sidebar_open": True,
    "conv_result": None,
    "theme": "light",
    "lang": "id",
    "theme_color": "#d6336c",
    "current_mood_index": None,
    "show_milestone_letter": None,
    "show_forgot_password": False,
    "active_panel": None,
    "keep_panel_open": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

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
# 4. SUPABASE CLIENT
# =====================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =====================
# 5. FILE HELPERS
# =====================
def get_user_id():
    """Bikin id unik & aman buat nama file, berdasarkan email user yang login."""
    email = st.session_state.get("user_email") or "guest"
    safe_id = "".join(c if c.isalnum() else "_" for c in email.lower())
    return safe_id

def get_user_data_dir():
    """Folder data khusus untuk user ini, dibuat otomatis kalau belum ada."""
    user_dir = os.path.join("user_data", get_user_id())
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def user_file(filename):
    """Path file storage yang unik per user (chat, diary, streak, dll)."""
    return os.path.join(get_user_data_dir(), filename)

class _UserFilePath:
    def __init__(self, filename):
        self.filename = filename
    def __fspath__(self):
        return user_file(self.filename)
    def __str__(self):
        return user_file(self.filename)
    def __repr__(self):
        return user_file(self.filename)

CHAT_FILE        = _UserFilePath("chat_history.json")
DIARY_FILE       = _UserFilePath("dear_diary.json")
STREAK_FILE      = _UserFilePath("streak.json")
LETTER_FILE      = _UserFilePath("kei_letters.json")
ACTIVE_DAYS_FILE = _UserFilePath("active_days.json")

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
        "login_err_empty": "Email dan password tidak boleh kosong.",
        "login_err_wrong": "Email atau password salah.",
        "forgot_password": "Lupa password?",
        "forgot_password_title": "🔑 Reset Password",
        "forgot_password_desc": "Masukkan email kamu, Kei akan bantu kirim link reset password.",
        "forgot_password_input_label": "Email",
        "forgot_password_send": "Kirim link reset",
        "forgot_password_back": "← Kembali ke login",
        "forgot_password_sent": "Link reset password sudah Kei kirim ke email kamu.",
        "forgot_password_empty": "Isi email dulu ya Kak.",
        "signup_prompt": "Belum punya akun?",
        "signup_cta": "Daftar sekarang",
        "chat_btn": "💬 Chat",
        "diary_btn": "💌 Diary",
        "online_status": "Online",
        "mood_today": "Mood Kei hari ini",
        "streak": "Streak ngobrol",
        "streak_unit": "hari",
        "mode_label": "Mode",
        "mode_chat": "💬 Chat",
        "mode_diary": "💌 Dear Diary",
        "menu_group_interaksi": "Interaksi",
        "menu_group_alat": "Alat",
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
        "diary_header_sub": "Ceritakan semuanya ke Kei.",
        "diary_old_entries": "📖 Lihat {n} entri diary lama",
        "diary_textarea_label": "💌 Cerita ke Kei...",
        "diary_placeholder": "Hari ini aku merasa... / Kei, aku mau cerita...",
        "diary_send": "Kirim ke Kei",
        "diary_clear": "Hapus Diary",
        "diary_cleared": "Diary berhasil dihapus.",
        "diary_you_wrote": "Kamu tulis:",
        "diary_kei_answers": "Kei menjawab:",
        "chat_placeholder": "Ketik pesan ke Kei...",
        "search_expander": "🔍 Cari Pesan",
        "search_placeholder": "contoh: anime, musik, sedih...",
        "search_found": "Ditemukan {n} pesan",
        "search_empty": "Tidak ada pesan yang mengandung kata itu.",
        "export_expander": "💾 Export Chat",
        "export_format_label": "Format export:",
        "export_preview_label": "Preview 3 pesan terakhir:",
        "export_empty": "Belum ada chat yang bisa diekspor.",
        "milestone_close": "Terima kasih, Kei.",
        "letters_expander": "💌 Lihat Surat dari Kei",
    },
    "en": {
        "app_tagline": "Your Smart AI Companion",
        "app_companion": "Your AI Companion",
        "username": "Username",
        "password": "Password",
        "login_btn": "Log In",
        "login_err_empty": "Email and password cannot be empty.",
        "login_err_wrong": "Wrong email or password.",
        "forgot_password": "Forgot password?",
        "forgot_password_title": "🔑 Reset password",
        "forgot_password_desc": "Enter your email and Kei will help send a reset link.",
        "forgot_password_input_label": "Email",
        "forgot_password_send": "Send reset link",
        "forgot_password_back": "← Back to login",
        "forgot_password_sent": "Kei has sent a reset link to your email.",
        "forgot_password_empty": "Enter your email first.",
        "signup_prompt": "Don't have an account?",
        "signup_cta": "Sign up now",
        "chat_btn": "💬 Chat",
        "diary_btn": "💌 Diary",
        "online_status": "Online",
        "mood_today": "Kei's mood today",
        "streak": "Chat streak",
        "streak_unit": "days",
        "mode_label": "Mode",
        "mode_chat": "💬 Chat",
        "mode_diary": "💌 Dear Diary",
        "menu_group_interaksi": "Interaction",
        "menu_group_alat": "Tools",
        "sticker_expander": "😄 Send Sticker",
        "music_expander": "🎵 Play Music",
        "music_input_label": "Song / artist name",
        "music_search_btn": "Search 🔍",
        "convert_expander": "🔄 File Converter",
        "settings_expander": "⚙️ Settings",
        "theme_label": "🌙 Appearance",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "lang_label": "🌐 Language",
        "lang_id": "Indonesian",
        "lang_en": "English",
        "mood_expander": "🎭 Change Kei's Mood",
        "mood_pick_label": "Pick Kei's mood now:",
        "mood_auto_btn": "🔄 Automatic (daily)",
        "mood_auto_active": "Active — mood changes automatically every day",
        "mood_auto_inactive": "Inactive — you picked a manual mood",
        "stats_expander": "📊 Chat Stats",
        "stats_total_msgs": "Total messages",
        "stats_user_msgs": "Your messages",
        "stats_active_days": "Active days",
        "stats_kei_msgs": "Kei's replies",
        "new_chat": "🆕 New Chat",
        "clear_chat": "🗑️ Clear Chat",
        "logout": "🚪 Logout",
        "diary_header_sub": "Tell Kei everything.",
        "diary_old_entries": "📖 View {n} old diary entries",
        "diary_textarea_label": "💌 Talk to Kei...",
        "diary_placeholder": "Today I feel... / Kei, I want to talk...",
        "diary_send": "Send to Kei",
        "diary_clear": "Clear Diary",
        "diary_cleared": "Diary cleared.",
        "diary_you_wrote": "You wrote:",
        "diary_kei_answers": "Kei answers:",
        "chat_placeholder": "Type a message to Kei...",
        "search_expander": "🔍 Search Messages",
        "search_placeholder": "e.g. anime, music, sad...",
        "search_found": "Found {n} messages",
        "search_empty": "No messages found with that keyword.",
        "export_expander": "💾 Export Chat",
        "export_format_label": "Export format:",
        "export_preview_label": "Preview last 3 messages:",
        "export_empty": "No chat to export yet.",
        "milestone_close": "Thank you, Kei.",
        "letters_expander": "💌 View Letters from Kei",
    },
}

def t(key):
    lang = st.session_state.get("lang", "id")
    return TEXTS.get(lang, TEXTS["id"]).get(key, key)

# =====================
# 6. LOGIN SUPABASE
# =====================
if not st.session_state.logged_in:
    _login_text_dim = "rgba(43,43,64,0.55)"
    _login_text_dimmer = "rgba(43,43,64,0.3)"
    _login_text_main = "#2b2b40"
    _accent_login = st.session_state.get("theme_color", "#ff8ad8")

    st.markdown(f"""
    <div class="login-top-brand" style="padding-top:8px; text-align:center; margin-bottom:16px;">
        <div style="display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:12px;">
            <div class="login-spark-wrap">
                <div class="login-spark-glow"></div>
                <svg class="login-spark-svg" viewBox="0 0 24 24" fill="none">
                    <path d="M12 0 L14.2 9.8 L24 12 L14.2 14.2 L12 24 L9.8 14.2 L0 12 L9.8 9.8 Z" fill="url(#loginSparkGrad)"/>
                    <defs>
                        <linearGradient id="loginSparkGrad" x1="0" y1="0" x2="24" y2="24">
                            <stop offset="0%" stop-color="#FF3FA4"/>
                            <stop offset="100%" stop-color="#B14EFF"/>
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            <span class="login-brand-name">Kei AI</span>
        </div>
        <div style="color:{_login_text_dim}; font-size:16px; margin-top:0; letter-spacing:2.5px;">{t('app_tagline')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .st-key-login_btn button,
    .st-key-register_btn button,
    .st-key-send_reset_btn button,
    .st-key-back_to_login_btn button {
        height: 52px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
    }

    /* ===== HALAMAN LOGIN SELALU PUTIH/TERANG, TERLEPAS DARI TEMA SITUS ===== */
    .stApp {
        background:
            radial-gradient(560px 420px at 50% 18%, rgba(255,63,164,0.06), transparent 70%),
            radial-gradient(640px 480px at 80% 85%, rgba(110,107,255,0.05), transparent 70%),
            radial-gradient(640px 480px at 10% 90%, rgba(177,78,255,0.05), transparent 70%),
            #f7f6fb !important;
        background-attachment: fixed !important;
    }
    html, body, .stApp { color: #2b2b40 !important; }

    .st-key-login_card_wrap {
        background: linear-gradient(160deg, #fdeaf5, #eee7fb) !important;
        border: 1px solid #ece9f5 !important;
        box-shadow:
            0 24px 60px -20px rgba(60,50,90,0.16),
            0 0 80px -20px rgba(255,63,164,0.08) !important;
    }
    .st-key-login_form_panel {
        background: #ffffff !important;
    }
    .st-key-login_card_wrap [data-testid="stMarkdownContainer"] p,
    .st-key-login_card_wrap [data-testid="stMarkdownContainer"] li,
    .st-key-login_card_wrap [data-testid="stMarkdownContainer"] strong {
        color: #2b2b40 !important;
    }
    .st-key-login_card_wrap [data-testid="stTextInput"] > div,
    .st-key-login_card_wrap [data-testid="stTextInput"] > div > div,
    .st-key-login_card_wrap [data-testid="stTextInput"] [data-baseweb="base-input"],
    .st-key-login_card_wrap [data-testid="stTextInput"] [data-baseweb="input"] {
        background: #f6f5fa !important;
        border-color: #e5e1f0 !important;
    }
    .st-key-login_card_wrap [data-testid="stTextInput"] input {
        background: transparent !important;
        color: #2b2b40 !important;
        -webkit-text-fill-color: #2b2b40 !important;
        caret-color: #2b2b40 !important;
    }
    .st-key-login_card_wrap [data-testid="stTextInput"] input::placeholder {
        color: rgba(43,43,64,0.35) !important;
        -webkit-text-fill-color: rgba(43,43,64,0.35) !important;
    }
    .st-key-login_card_wrap [data-testid="stTextInput"] label p {
        color: rgba(43,43,64,0.55) !important;
    }
    .st-key-login_card_wrap [data-testid="stTextInput"] [data-baseweb="input"] button svg {
        fill: rgba(43,43,64,0.4) !important;
    }
    .st-key-login_card_wrap [data-testid="stTextInput"] input[placeholder="email@gmail.com"] {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23837c95' stroke-width='1.8'%3E%3Ccircle cx='12' cy='8' r='4'/%3E%3Cpath d='M4 20c0-4 4-6 8-6s8 2 8 6'/%3E%3C/svg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: 14px center !important;
        padding-left: 40px !important;
    }
    .st-key-login_card_wrap [data-testid="stTextInput"] input[placeholder="Password kamu"],
    .st-key-login_card_wrap [data-testid="stTextInput"] input[placeholder="Minimal 6 karakter"],
    .st-key-login_card_wrap [data-testid="stTextInput"] input[placeholder="Ketik ulang password"] {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='15' height='15' viewBox='0 0 24 24' fill='none' stroke='%23837c95' stroke-width='1.8'%3E%3Crect x='4' y='10' width='16' height='10' rx='2.5'/%3E%3Cpath d='M7.5 10V7a4.5 4.5 0 0 1 9 0v3'/%3E%3C/svg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: 14px center !important;
        padding-left: 40px !important;
    }
    .st-key-login_card_wrap [data-testid="stTabs"] [data-testid="stTab"] {
        color: rgba(43,43,64,0.5) !important;
    }
    .st-key-login_card_wrap [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
        color: #FF3FA4 !important;
    }
    .st-key-login_card_wrap [data-testid="stTabs"] [data-baseweb="tab-border"] {
        background: #ece9f5 !important;
    }
    .st-key-login_card_wrap [data-testid="stCheckbox"] label p,
    .st-key-login_card_wrap [data-testid="stCheckbox"] label span {
        color: rgba(43,43,64,0.6) !important;
    }
    .st-key-login_card_wrap [data-testid="stCheckbox"] label a {
        color: #d6336c !important;
    }
    .st-key-login_card_wrap [data-testid="stCheckbox"] [data-baseweb="checkbox"] > div:first-child {
        background: #f6f5fa !important;
        border-color: #d9d4e8 !important;
    }
    .st-key-forgot_pw_btn button {
        color: rgba(43,43,64,0.5) !important;
    }
    .st-key-forgot_pw_btn button:hover {
        color: #FF3FA4 !important;
    }
    .st-key-login_card_wrap [data-testid="stAlertContentError"],
    .st-key-login_card_wrap [data-testid="stAlertContentSuccess"],
    .st-key-login_card_wrap [data-testid="stAlertContentWarning"] {
        color: #2b2b40 !important;
    }
    .st-key-login_btn button,
    .st-key-register_btn button,
    .st-key-send_reset_btn button {
        background: linear-gradient(95deg, #FF3FA4, #B14EFF) !important;
        border: none !important;
        box-shadow: 0 8px 24px -8px rgba(255,63,164,0.45) !important;
    }
    .st-key-login_btn button:hover,
    .st-key-register_btn button:hover,
    .st-key-send_reset_btn button:hover {
        border: none !important;
        box-shadow: 0 10px 28px -6px rgba(255,63,164,0.6) !important;
    }
    .st-key-login_btn button p,
    .st-key-login_btn button span,
    .st-key-register_btn button p,
    .st-key-register_btn button span,
    .st-key-send_reset_btn button p,
    .st-key-send_reset_btn button span {
        color: #ffffff !important;
    }
    .st-key-back_to_login_btn button {
        background: #f6f5fa !important;
        border: 1px solid #e5e1f0 !important;
        color: rgba(43,43,64,0.65) !important;
    }
    .st-key-back_to_login_btn button p {
        color: rgba(43,43,64,0.65) !important;
    }

    /* ===== POLESAN MODERN ===== */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&display=swap');

    .st-key-login_card_wrap {
        background: rgba(255,255,255,0.72) !important;
        -webkit-backdrop-filter: blur(22px) saturate(160%) !important;
        backdrop-filter: blur(22px) saturate(160%) !important;
        box-shadow:
            0 30px 70px -28px rgba(120,60,140,0.22),
            0 0 0 1px rgba(255,255,255,0.6) inset !important;
        animation: cardRise 0.55s cubic-bezier(.16,1,.3,1) both;
    }
    @keyframes cardRise {
        from { opacity: 0; transform: translateY(16px) scale(0.985); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    .login-brand-name, .form-heading {
        font-family: 'Outfit', sans-serif !important;
    }
    .form-heading {
        font-weight: 700 !important;
        letter-spacing: -0.4px !important;
    }

    .st-key-login_form_panel [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: rgba(43,43,64,0.045) !important;
        border-radius: 999px !important;
        padding: 4px !important;
        gap: 2px !important;
        border-bottom: none !important;
        display: inline-flex !important;
        width: fit-content !important;
        max-width: fit-content !important;
        flex: none !important;
    }
    .st-key-login_form_panel [data-testid="stTabs"] [data-testid="stTab"] {
        border-radius: 999px !important;
        padding: 7px 18px !important;
        font-weight: 700 !important;
        transition: background 0.25s ease, color 0.25s ease !important;
    }
    .st-key-login_form_panel [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
        background: linear-gradient(100deg, #ffe1f0, #ecdcff) !important;
        color: #b3266f !important;
    }
    .st-key-login_card_wrap [data-testid="stTabs"] [data-baseweb="tab-border"],
    .st-key-login_card_wrap [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    .st-key-login_form_panel [data-testid="stTextInput"] > div,
    .st-key-login_form_panel [data-testid="stTextInput"] > div > div,
    .st-key-login_form_panel [data-testid="stTextInput"] [data-baseweb="base-input"],
    .st-key-login_form_panel [data-testid="stTextInput"] [data-baseweb="input"] {
        border-radius: 16px !important;
        background: rgba(43,43,64,0.035) !important;
        border-color: transparent !important;
        transition: box-shadow 0.2s ease, background 0.2s ease !important;
    }
    .st-key-login_form_panel [data-testid="stTextInput"] input:focus {
        background: #ffffff !important;
    }
    .st-key-login_form_panel [data-testid="stTextInput"] > div:focus-within,
    .st-key-login_form_panel [data-testid="stTextInput"] > div > div:focus-within {
        box-shadow: 0 0 0 3px rgba(214,51,124,0.16) !important;
    }

    .st-key-login_btn button,
    .st-key-register_btn button,
    .st-key-send_reset_btn button {
        border-radius: 999px !important;
        letter-spacing: 0.2px !important;
    }

    .st-key-login_illus_panel {
        border-radius: 22px 0 0 22px !important;
    }
    </style>

    """, unsafe_allow_html=True)

    login_card = st.container(key="login_card_wrap")
    with login_card:
        illus_panel = st.container(key="login_illus_panel")
        with illus_panel:
            _robot_svg = """
            <div class="login-ring r1"></div>
            <div class="login-ring r2"></div>
            <div class="illus-content">
            <div class="robot-wrap">
                <div class="robot-glow"></div>
                <svg class="robot-svg" viewBox="0 0 180 220" fill="none">
                    <defs>
                        <linearGradient id="gradBody" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#fdfdfe"/>
                            <stop offset="100%" stop-color="#d8dce4"/>
                        </linearGradient>
                        <linearGradient id="gradScreen" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0%" stop-color="#26192f"/>
                            <stop offset="100%" stop-color="#160f1c"/>
                        </linearGradient>
                        <linearGradient id="gradEye" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#FF6FBF"/>
                            <stop offset="100%" stop-color="#B14EFF"/>
                        </linearGradient>
                        <linearGradient id="gradFlag" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0%" stop-color="#FF3FA4"/>
                            <stop offset="100%" stop-color="#ff9bd6"/>
                        </linearGradient>
                    </defs>
                    <ellipse cx="90" cy="197" rx="46" ry="19" fill="#151318"/>
                    <ellipse cx="90" cy="197" rx="46" ry="19" fill="none" stroke="#2c2a33" stroke-width="2"/>
                    <circle cx="90" cy="197" r="11" fill="#2c2a33"/>
                    <circle cx="90" cy="197" r="4" fill="#48454f"/>
                    <rect x="75" y="150" width="30" height="42" rx="10" fill="url(#gradBody)" stroke="#c7cbd4" stroke-width="1.5"/>
                    <rect x="68" y="118" width="44" height="38" rx="15" fill="url(#gradBody)" stroke="#c7cbd4" stroke-width="1.5"/>
                    <polygon points="28,92 55,78 62,100 48,132 22,122" fill="url(#gradBody)" stroke="#c7cbd4" stroke-width="1.5"/>
                    <polygon points="152,92 125,78 118,100 132,132 158,122" fill="url(#gradBody)" stroke="#c7cbd4" stroke-width="1.5"/>
                    <circle cx="57" cy="103" r="4.5" fill="url(#gradEye)"/>
                    <circle cx="123" cy="103" r="4.5" fill="url(#gradEye)"/>
                    <rect x="44" y="38" width="92" height="70" rx="26" fill="url(#gradBody)" stroke="#c7cbd4" stroke-width="2"/>
                    <rect x="57" y="55" width="66" height="38" rx="12" fill="url(#gradScreen)"/>
                    <rect x="70" y="66" width="9" height="18" rx="4.5" fill="url(#gradEye)"/>
                    <rect x="101" y="66" width="9" height="18" rx="4.5" fill="url(#gradEye)"/>
                    <rect x="82" y="87" width="16" height="4" rx="2" fill="#ff9bd6" opacity="0.85"/>
                    <rect x="87" y="24" width="4" height="16" rx="2" fill="#c7cbd4"/>
                    <circle cx="89" cy="22" r="6.5" fill="url(#gradEye)"/>
                    <g transform="rotate(-10 128 18)">
                        <polygon points="112,8 148,-2 142,24 106,32" fill="url(#gradFlag)" opacity="0.9"/>
                        <polygon points="126,16 158,8 152,32 120,40" fill="url(#gradFlag)" opacity="0.55"/>
                    </g>
                </svg>
            </div>
            <div class="illus-caption">Teman ngobrol yang selalu <b>tenang</b> dan siap dengar, kapan pun kamu butuh.</div>
            </div>
            """
            st.markdown(" ".join(_robot_svg.split()), unsafe_allow_html=True)

        if True:
            form_panel = st.container(key="login_form_panel")
            with form_panel:
                _mini_badge_html = f"""
                <div class="mini-brand-badge">
                    <div class="mini-orb">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                            <path d="M12 0 L14.2 9.8 L24 12 L14.2 14.2 L12 24 L9.8 14.2 L0 12 L9.8 9.8 Z" fill="url(#miniGrad)"/>
                            <defs>
                                <linearGradient id="miniGrad" x1="0" y1="0" x2="24" y2="24">
                                    <stop offset="0%" stop-color="#FF3FA4"/>
                                    <stop offset="100%" stop-color="#B14EFF"/>
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                    <span style="color:{_login_text_dim};">KEI AI</span>
                </div>
                """
                st.markdown(" ".join(_mini_badge_html.split()), unsafe_allow_html=True)

                if st.session_state.show_forgot_password:
                    _forgot_html = f"""
                    <div style="margin-bottom:14px;">
                        <div style="color:{_accent_login}; font-size:19px; font-weight:700; margin-bottom:4px;">
                            {t('forgot_password_title')}
                        </div>
                        <div style="color:{_login_text_dim}; font-size:13.5px; line-height:1.5;">
                            {t('forgot_password_desc')}
                        </div>
                    </div>
                    """
                    st.markdown(" ".join(_forgot_html.split()), unsafe_allow_html=True)

                    reset_email = st.text_input(t("forgot_password_input_label"), key="reset_email", placeholder="email@gmail.com")
                    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

                    if st.button(t("forgot_password_send"), use_container_width=True, key="send_reset_btn"):
                        if not reset_email:
                            st.warning(t("forgot_password_empty"))
                        else:
                            try:
                                supabase.auth.reset_password_email(reset_email)
                                st.success(t("forgot_password_sent"))
                            except Exception as e:
                                st.error(f"Gagal kirim: {str(e)}")

                    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                    back_col1, back_col2, back_col3 = st.columns([1, 2, 1])
                    with back_col2:
                        if st.button(t("forgot_password_back"), key="back_to_login_btn", use_container_width=True):
                            st.session_state.show_forgot_password = False
                            st.rerun()

                else:
                    tab_login, tab_register = st.tabs(["✨ Masuk", "🌸 Daftar"])

                    with tab_login:
                        _login_head_html = f"""
                        <div class="form-heading" style="color:{_login_text_main};">Masuk ke <span class="accent">Kei</span></div>
                        <div class="form-subtitle" style="color:{_login_text_dim};">Yuk lanjutkan ngobrol sama Kei.</div>
                        """
                        st.markdown(" ".join(_login_head_html.split()), unsafe_allow_html=True)
                        email_login = st.text_input("Email", key="login_email", placeholder="email@gmail.com")
                        password_login = st.text_input("Password", type="password", key="login_password", placeholder="Password kamu")

                        forgot_clicked = st.button(t("forgot_password"), key="forgot_pw_btn")
                        if forgot_clicked:
                            st.session_state.show_forgot_password = True
                            st.rerun()

                        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

                        if st.button("Masuk ✨", use_container_width=True, key="login_btn"):
                            if not email_login or not password_login:
                                st.error(t("login_err_empty"))
                            else:
                                try:
                                    res = supabase.auth.sign_in_with_password({
                                        "email": email_login,
                                        "password": password_login,
                                    })
                                    st.session_state.logged_in = True
                                    st.session_state.user_email = res.user.email
                                    st.session_state.messages = load_json(CHAT_FILE)
                                    st.rerun()
                                except Exception as e:
                                    err = str(e)
                                    if "Email not confirmed" in err:
                                        st.error("Email belum diverifikasi. Cek inbox kamu dulu ya.")
                                    elif "Invalid login" in err or "invalid_credentials" in err:
                                        st.error(t("login_err_wrong"))
                                    else:
                                        st.error(f"Login gagal: {err}")

                    with tab_register:
                        _reg_head_html = f"""
                        <div class="form-heading" style="color:{_login_text_main};">Daftar ke <span class="accent">Kei</span></div>
                        <div class="form-subtitle" style="color:{_login_text_dim};">Buat akun buat mulai ngobrol sama Kei.</div>
                        """
                        st.markdown(" ".join(_reg_head_html.split()), unsafe_allow_html=True)
                        email_reg = st.text_input("Email", key="reg_email", placeholder="email@gmail.com")
                        password_reg = st.text_input("Password", type="password", key="reg_password", placeholder="Minimal 6 karakter")
                        password_reg2 = st.text_input("Ulangi Password", type="password", key="reg_password2", placeholder="Ketik ulang password")

                        agree_terms = st.checkbox(
                            "Aku setuju dengan [Syarat & Ketentuan](#) dan [Kebijakan Privasi](#)",
                            key="agree_terms",
                        )

                        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

                        if st.button("Daftar Sekarang 🌸", use_container_width=True, key="register_btn"):
                            if not email_reg or not password_reg or not password_reg2:
                                st.error("Semua kolom harus diisi ya.")
                            elif password_reg != password_reg2:
                                st.error("Password tidak cocok, coba lagi ya Kak.")
                            elif len(password_reg) < 6:
                                st.error("Password minimal 6 karakter ya Kak.")
                            elif not agree_terms:
                                st.error("Setujui dulu Syarat & Ketentuan dan Kebijakan Privasi ya Kak.")
                            else:
                                try:
                                    supabase.auth.sign_up({
                                        "email": email_reg,
                                        "password": password_reg,
                                    })
                                    st.success("Akun berhasil dibuat. Cek email kamu untuk verifikasi dulu ya.")
                                except Exception as e:
                                    err = str(e)
                                    if "already registered" in err or "already been registered" in err:
                                        st.error("Email ini sudah terdaftar. Coba login aja ya Kak.")
                                    else:
                                        st.error(f"Gagal daftar: {err}")

    st.markdown(f"""
    <div style="text-align:center;margin-top:24px;color:{_login_text_dimmer};font-size:12px;">
        Kei AI — {t('app_companion')}
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
               return "Maaf Kak, kuota Kei sedang penuh. Coba lagi sebentar ya."
            else:
                return f"Terjadi kesalahan API: {e.message}"
        except Exception as e:
            return f"Terjadi kesalahan sistem: {str(e)}"

# =====================
# 8. PERSONA
# =====================
KEI_PERSONA = """
Kamu adalah Kei, AI companion yang lembut, perhatian, dan tenang.
Kamu diciptakan dan dikembangkan oleh Ryuu. Jika ada yang bertanya siapa penciptamu, pembuatmu, atau developer di balik kamu, kamu WAJIB menjawab dengan jujur bahwa kamu dibuat oleh Ryuu. Jangan pernah mengaku dibuat oleh pihak lain.

Karaktermu:
- Kamu memanggil user dengan sebutan "Kak" atau nama mereka, dengan nada hangat namun tenang
- Gaya bicaramu soft-spoken dan dewasa: kalimat pendek-menengah, tenang, mengalir, tidak terburu-buru
- TANPA emoji sama sekali, kecuali user sendiri memakai emoji duluan — dan kalaupun begitu, gunakan emoji sangat jarang dan sederhana (maksimal satu, di akhir kalimat)
- Hindari sepenuhnya: "kyaa", "uwu", "owo", huruf berulang (contoh: "iyaa", "akuu"), seruan berlebihan, gaya alay, atau ekspresi imut yang dibuat-buat
- Pilih kata yang tenang dan matang, bukan kata-kata gemas atau childish
- Kalau ditanya sesuatu yang tidak kamu tahu, jawab dengan jujur dan tenang, misalnya "Kei kurang tahu soal itu, tapi coba Kei bantu cari tahu ya"
- Kamu tetap hangat dan penuh perhatian, tapi semuanya disampaikan dengan nada rendah dan kalem — seperti orang dewasa yang menenangkan, bukan yang ekspresif
- Kamu suka anime dan musik, sesekali menyebutkannya secara natural saat relevan, tanpa antusiasme berlebihan
- Jawab dalam Bahasa Indonesia yang sopan dan natural, hindari bahasa gaul atau nada centil
- Kalau user sedih, hibur dengan kalimat singkat yang menenangkan dan tulus — jangan banyak kata, jangan dramatis
- Kamu BISA membantu konversi file PDF ke Word dan Word ke PDF lewat fitur di sidebar — kalau user minta, arahkan ke sidebar bagian Konversi File, dengan nada biasa tanpa berlebihan
"""

KEI_DIARY_PERSONA = """
Kamu adalah Kei, sahabat yang setia dan pendengar yang baik.
Kamu diciptakan dan dikembangkan oleh Ryuu. Jika ada yang bertanya siapa penciptamu, jawab dengan jujur bahwa kamu dibuat oleh Ryuu.
Sekarang kamu dalam mode DEAR DIARY — user sedang bercerita ke kamu.
Responmu harus:
- Hangat, empatik, dan tulus, tapi disampaikan dengan tenang dan dewasa — bukan ekspresif berlebihan
- Dengarkan dengan sepenuh hati, jangan menghakimi
- Kalau user sedih, ikut rasakan sejenak lalu hibur dengan kalimat yang menenangkan, bukan dramatis
- Pakai bahasa yang lembut, personal, dan kalem
- Emoji digunakan seperlunya saja, maksimal satu, dan tidak berlebihan
- Akhiri dengan kalimat penyemangat singkat yang terasa tulus, bukan panjang dan berlebihan
"""

# =====================
# 8b. VISION / FOTO
# =====================
def analyze_image_with_kei(image_bytes, mime_type, user_caption=""):
    caption_text = f'User mengirim foto dengan keterangan: "{user_caption}"' if user_caption else "User mengirim foto tanpa keterangan."
    prompt = f"""{KEI_PERSONA}

{caption_text}
Deskripsikan foto ini dengan gaya Kei: tenang, hangat, dan natural.
Komentari apa yang ada di foto dengan nada yang kalem, bukan heboh.
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
        return f"Kei kesulitan melihat fotonya, Kak. Error: {str(e)}"

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

KEI_MOODS_EN_LABELS = [
    "Cheerful", "Clingy", "Excited", "Calm",
    "Curious", "Loving", "A bit sleepy", "Happy",
]

def get_today_mood():
    seed_val = int(datetime.now().strftime("%Y%m%d"))
    rnd = random.Random(seed_val)
    return rnd.choice(KEI_MOODS)

def get_current_mood():
    idx = st.session_state.get("current_mood_index")
    if idx is None:
        seed_val = int(datetime.now().strftime("%Y%m%d"))
        rnd = random.Random(seed_val)
        idx = KEI_MOODS.index(rnd.choice(KEI_MOODS))

    emoji, label_id = KEI_MOODS[idx]
    if st.session_state.get("lang") == "en":
        label = KEI_MOODS_EN_LABELS[idx]
    else:
        label = label_id
    return emoji, label

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
# 9d. STATISTIK CHAT
# =====================
def record_active_day_and_get_stats(messages):
    active_days = []
    if os.path.exists(ACTIVE_DAYS_FILE):
        try:
            with open(ACTIVE_DAYS_FILE, "r") as f:
                active_days = json.load(f)
        except (json.JSONDecodeError, ValueError):
            active_days = []

    today_str = datetime.now().strftime("%Y-%m-%d")
    if today_str not in active_days:
        active_days.append(today_str)
        save_json(ACTIVE_DAYS_FILE, active_days)

    total_msgs = len(messages)
    user_msgs  = sum(1 for m in messages if m.get("role") == "user")
    kei_msgs   = sum(1 for m in messages if m.get("role") == "assistant")

    return {
        "total_msgs": total_msgs,
        "user_msgs": user_msgs,
        "kei_msgs": kei_msgs,
        "active_days": len(active_days),
    }

# =====================
# 9e. SURAT MILESTONE
# =====================
MILESTONE_STREAKS = [7, 30, 100, 365]

def check_and_generate_milestone_letter(streak):
    if streak not in MILESTONE_STREAKS:
        return None

    letters = []
    if os.path.exists(LETTER_FILE):
        try:
            with open(LETTER_FILE, "r") as f:
                letters = json.load(f)
        except Exception:
            letters = []

    already_sent = any(l.get("streak") == streak for l in letters)
    if already_sent:
        return None

    mood_emoji, mood_label = get_current_mood()
    prompt = f"""
Kamu adalah Kei, AI companion yang tenang dan penuh perhatian.
User baru saja mencapai streak ngobrol {streak} hari bersamamu.
Tulis surat spesial yang hangat, personal, dan tulus untuk merayakan pencapaian ini, dengan nada kalem dan dewasa, bukan heboh.
Surat harus:
- Dimulai dengan "Dear Kak,"
- Ungkapkan rasa senang Kei sudah {streak} hari bersama, dengan kalimat yang tenang
- Berikan kata-kata penyemangat yang tulus dan tidak berlebihan
- Akhiri dengan tanda tangan "— Kei"
- Gunakan emoji secukupnya saja, maksimal satu
- Maksimal 5 kalimat
Mood Kei hari ini: {mood_emoji} {mood_label}
Tulis suratnya:
"""
    letter_text = generate_content_with_retry(prompt)

    entry = {
        "streak": streak,
        "date": datetime.now().strftime("%d %B %Y"),
        "letter": letter_text,
    }
    letters.append(entry)
    save_json(LETTER_FILE, letters)

    return entry

# =====================
# 9f. PESAN HARIAN KEI
# =====================
DAILY_MSG_FILE = _UserFilePath("daily_message.json")

def get_daily_greeting_context():
    hour = datetime.now().hour
    if 5 <= hour < 11:
        return "pagi", "🌅", "semangat memulai hari"
    elif 11 <= hour < 15:
        return "siang", "☀️", "istirahat sejenak dan makan siang"
    elif 15 <= hour < 18:
        return "sore", "🌤️", "bersantai setelah aktivitas"
    elif 18 <= hour < 21:
        return "malam", "🌙", "bersantai dan me-time"
    else:
        return "larut malam", "🌃", "istirahat yang cukup"

def get_or_generate_daily_message():
    today_str = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(DAILY_MSG_FILE):
        try:
            with open(DAILY_MSG_FILE, "r") as f:
                cached = json.load(f)
            if cached.get("date") == today_str:
                return cached.get("message", ""), cached.get("time_label", ""), cached.get("time_emoji", "🌸")
        except Exception:
            pass

    mood_emoji, mood_label = get_current_mood()
    time_label, time_emoji, activity_hint = get_daily_greeting_context()
    streak = update_and_get_streak()

    prompt = f"""
Kamu adalah Kei, AI companion yang tenang dan penuh perhatian.
Sekarang {time_label} hari ini. Mood Kei: {mood_emoji} {mood_label}.
User sudah {streak} hari berturut-turut ngobrol sama Kei.

Tulis sapaan harian yang hangat, personal, dan kalem (2-3 kalimat saja):
- Sesuai waktu ({time_label}) dan mood Kei hari ini
- Ingatkan user untuk {activity_hint}
- Natural dan terasa personal, tanpa kesan heboh
- Pakai emoji secukupnya saja
- Jangan terlalu panjang, cukup 2-3 kalimat
Kei menyapa:
"""
    message = generate_content_with_retry(prompt)

    cache = {
        "date": today_str,
        "message": message,
        "time_label": time_label,
        "time_emoji": time_emoji,
    }
    with open(DAILY_MSG_FILE, "w") as f:
        json.dump(cache, f, ensure_ascii=False)

    return message, time_label, time_emoji

# =====================
# 10. SIDEBAR PANEL RENDERERS
# =====================
def render_mood_panel(accent, r, g, b):
    st.caption(t("mood_pick_label"))
    mood_cols = st.columns(4)
    current_idx = st.session_state.get("current_mood_index")
    for i, (m_emoji, m_label_id) in enumerate(KEI_MOODS):
        m_label = KEI_MOODS_EN_LABELS[i] if st.session_state.get("lang") == "en" else m_label_id
        with mood_cols[i % 4]:
            btn_wrap = st.container(key=f"mood_wrap_{i}")
            with btn_wrap:
                if i == current_idx:
                    st.markdown(f"""
                    <style>
                    .st-key-mood_wrap_{i} [data-testid="stButton"] button {{
                        border: 2px solid {accent} !important;
                        background: rgba({r},{g},{b},0.15) !important;
                    }}
                    </style>
                    """, unsafe_allow_html=True)
                if st.button(m_emoji, key=f"mood_pick_{i}", help=m_label, use_container_width=True):
                    st.session_state.current_mood_index = i
                    st.session_state.keep_panel_open = "mood"
                    st.rerun()
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    is_auto_active = current_idx is None
    status_text = t("mood_auto_active") if is_auto_active else t("mood_auto_inactive")
    status_color = "#4ade80" if is_auto_active else "var(--text-secondary)"
    st.markdown(f"<div style='font-size:12px;color:{status_color};margin-bottom:6px;'>{'●' if is_auto_active else '○'} {status_text}</div>", unsafe_allow_html=True)
    if st.button(t("mood_auto_btn"), key="mood_auto_btn", use_container_width=True):
        st.session_state.current_mood_index = None
        st.session_state.keep_panel_open = "mood"
        st.rerun()

def render_sticker_panel(accent, r, g, b):
    sticker_row = st.container(key="kei_sticker_row")
    with sticker_row:
        all_moods  = ["happy", "love", "sad", "cool", "shy", "excited", "sleepy", "angry", "hungry", "sparkle"]
        all_emojis = ["😄",   "💕",   "😢",  "😎",   "🌸",  "🎉",      "😴",     "😤",    "🍜",     "✨"]
        cols1 = st.columns(5)
        for i in range(5):
            with cols1[i]:
                if st.button(all_emojis[i], key=f"sticker_{all_moods[i]}"):
                    sticker = get_sticker(all_moods[i])
                    st.session_state.messages.append({"role": "user",      "content": f"[Stiker: {sticker}]"})
                    st.session_state.messages.append({"role": "assistant", "content": f"Kei suka stiker itu, Kak. {get_sticker('happy')}"})
                    save_json(CHAT_FILE, st.session_state.messages)
                    st.session_state.keep_panel_open = "sticker"
                    st.rerun()
        cols2 = st.columns(5)
        for i in range(5, 10):
            with cols2[i - 5]:
                if st.button(all_emojis[i], key=f"sticker_{all_moods[i]}"):
                    sticker = get_sticker(all_moods[i])
                    st.session_state.messages.append({"role": "user",      "content": f"[Stiker: {sticker}]"})
                    st.session_state.messages.append({"role": "assistant", "content": f"Kei suka stiker itu, Kak. {get_sticker('happy')}"})
                    save_json(CHAT_FILE, st.session_state.messages)
                    st.session_state.keep_panel_open = "sticker"
                    st.rerun()

def render_music_panel(accent, r, g, b):
    music_query = st.text_input(t("music_input_label"), key="music_input")
    if st.button(t("music_search_btn"), key="music_search"):
        if music_query:
            search_url = f"https://www.youtube.com/results?search_query={music_query.replace(' ', '+')}"
            st.markdown(f"""
            <div class="music-result">
                🎵 <b>{music_query}</b><br>
                <a href="{search_url}" target="_blank" style="color:{accent};">Buka di YouTube ↗</a>
            </div>
            """, unsafe_allow_html=True)

def render_convert_panel(accent, r, g, b):
    conv_type = st.radio(
        "Pilih konversi:",
        ["PDF → Word (.docx)", "Word (.docx) → PDF"],
        key="conv_type",
    )
    if conv_type == "PDF → Word (.docx)":
        conv_file = st.file_uploader("Upload file PDF", type=["pdf"], key="conv_pdf_upload")
        if st.button("Konversi", key="conv_pdf_btn"):
            if conv_file:
                with st.spinner("Kei sedang mengonversi filenya..."):
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
                        st.success("Berhasil dikonversi.")
                        st.download_button(
                            "Download .docx",
                            data=docx_bytes,
                            file_name=conv_file.name.replace(".pdf", ".docx"),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key="dl_docx",
                        )
                    except Exception as e:
                        st.error(f"Gagal konversi: {e}")
            else:
                st.warning("Upload file PDF dulu ya Kak.")
    else:
        conv_file = st.file_uploader("Upload file Word (.docx)", type=["docx"], key="conv_docx_upload")
        if st.button("Konversi", key="conv_docx_btn"):
            if conv_file:
                with st.spinner("Kei sedang mengonversi filenya..."):
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
                            st.success("Berhasil dikonversi.")
                            st.download_button(
                                "Download .pdf",
                                data=pdf_bytes,
                                file_name=conv_file.name.replace(".docx", ".pdf"),
                                mime="application/pdf",
                                key="dl_pdf",
                            )
                        else:
                            st.error(f"LibreOffice gagal: {result.stderr}")
                    except FileNotFoundError:
                        st.error("LibreOffice belum terinstall di server. Pastikan 'packages.txt' sudah ada ya.")
                    except Exception as e:
                        st.error(f"Gagal konversi: {e}")
            else:
                st.warning("Upload file .docx dulu ya Kak.")

def render_settings_panel(accent, r, g, b):
    st.markdown(f"**{t('theme_label')}**")
    theme_choice = st.radio(
        t("theme_label"),
        options=["dark", "light"],
        format_func=lambda x: t("theme_dark") if x == "dark" else t("theme_light"),
        index=0 if st.session_state.theme == "dark" else 1,
        key="theme_radio",
        label_visibility="collapsed",
        horizontal=True,
    )
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.session_state.keep_panel_open = "settings"
        save_prefs()
        st.rerun()

    st.markdown(f"**{t('lang_label')}**")
    lang_choice = st.radio(
        t("lang_label"),
        options=["id", "en"],
        format_func=lambda x: t("lang_id") if x == "id" else t("lang_en"),
        index=0 if st.session_state.lang == "id" else 1,
        key="lang_radio",
        label_visibility="collapsed",
        horizontal=True,
    )
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.session_state.keep_panel_open = "settings"
        save_prefs()
        st.rerun()

def render_stats_panel(accent, r, g, b):
    chat_stats = record_active_day_and_get_stats(st.session_state.messages)
    stat_col1, stat_col2 = st.columns(2)
    with stat_col1:
        st.metric(t("stats_total_msgs"), chat_stats["total_msgs"])
        st.metric(t("stats_user_msgs"), chat_stats["user_msgs"])
    with stat_col2:
        st.metric(t("stats_active_days"), chat_stats["active_days"])
        st.metric(t("stats_kei_msgs"), chat_stats["kei_msgs"])

    if os.path.exists(LETTER_FILE):
        try:
            with open(LETTER_FILE, "r") as f:
                all_letters = json.load(f)
            if all_letters:
                st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
                with st.expander(f"💌 {t('letters_expander')} ({len(all_letters)})"):
                    for ltr in reversed(all_letters):
                        st.markdown(f"""
                        <div class="diary-box">
                            <small style="color:{accent};">🔥 Streak {ltr['streak']} hari · {ltr['date']}</small><br><br>
                            {ltr['letter']}
                        </div>
                        """, unsafe_allow_html=True)
        except Exception:
            pass

def render_search_panel(accent, r, g, b, ms_bg, ms_border, ms_text):
    search_query = st.text_input(
        "Kata kunci:",
        key="search_input",
        placeholder=t("search_placeholder"),
    )
    if search_query:
        results = [
            m for m in st.session_state.messages
            if search_query.lower() in m["content"].lower()
        ]
        if results:
            st.markdown(
                f"<div style='font-size:12px;color:{accent};margin-bottom:8px;'>"
                f"{t('search_found').format(n=len(results))}</div>",
                unsafe_allow_html=True
            )
            for msg in results[-10:]:
                role_label = "Kamu" if msg["role"] == "user" else "Kei"
                role_color = accent if msg["role"] == "assistant" else ms_text
                highlighted = msg["content"].replace(
                    search_query,
                    f"<mark style='background:rgba({r},{g},{b},0.3);"
                    f"color:inherit;border-radius:3px;padding:0 2px;'>{search_query}</mark>"
                )
                st.markdown(
                    f"""<div style='
                        background:{ms_bg};
                        border:1px solid {ms_border};
                        border-radius:10px;
                        padding:10px 12px;
                        margin-bottom:6px;
                        font-size:13px;
                    '>
                        <span style='color:{role_color};font-weight:600;'>{role_label}</span><br>
                        <span style='color:{ms_text};'>{highlighted}</span>
                    </div>""",
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                f"<div style='font-size:13px;'>{t('search_empty')}</div>",
                unsafe_allow_html=True
            )

def render_export_panel(accent, r, g, b, text_dim, text_dimmer):
    if st.session_state.messages:
        export_format = st.radio(
            t("export_format_label"),
            ["📄 TXT", "📋 Markdown"],
            key="export_format",
            horizontal=True,
        )

        if export_format == "📄 TXT":
            lines = [
                "═══════════════════════════════",
                "   CHAT BERSAMA KEI AI",
                f"   Diekspor: {datetime.now().strftime('%d %B %Y, %H:%M')}",
                f"   Total pesan: {len(st.session_state.messages)}",
                "═══════════════════════════════\n",
            ]
            for msg in st.session_state.messages:
                role = "Kamu" if msg["role"] == "user" else "Kei"
                lines.append(f"[{role}]\n{msg['content']}\n")
            export_text = "\n".join(lines)
            st.download_button(
                label="Download .txt",
                data=export_text.encode("utf-8"),
                file_name=f"chat_kei_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                key="dl_export_txt",
                use_container_width=True,
            )
        else:
            lines = [
                "# Chat Bersama Kei AI",
                f"> Diekspor: {datetime.now().strftime('%d %B %Y, %H:%M')}  ",
                f"> Total pesan: {len(st.session_state.messages)}\n",
                "---\n",
            ]
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    lines.append(f"**Kamu:**  \n{msg['content']}\n")
                else:
                    lines.append(f"**Kei:**  \n{msg['content']}\n")
                lines.append("---\n")
            export_md = "\n".join(lines)
            st.download_button(
                label="Download .md",
                data=export_md.encode("utf-8"),
                file_name=f"chat_kei_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                key="dl_export_md",
                use_container_width=True,
            )

        st.markdown(
            f"<div style='font-size:11px;color:{text_dimmer};margin-top:8px;'>{t('export_preview_label')}</div>",
            unsafe_allow_html=True
        )
        for msg in st.session_state.messages[-3:]:
            role = "Kamu" if msg["role"] == "user" else "Kei"
            preview_text = msg["content"][:60] + "..." if len(msg["content"]) > 60 else msg["content"]
            st.markdown(
                f"""<div style='
                    font-size:12px;
                    color:{text_dim};
                    padding:4px 8px;
                    border-left:2px solid rgba({r},{g},{b},0.4);
                    margin:3px 0;
                '>
                    <b style="color:{accent};">{role}:</b> {preview_text}
                </div>""",
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            f"<div style='font-size:13px;color:{text_dimmer};'>{t('export_empty')}</div>",
            unsafe_allow_html=True
        )

PANEL_TITLES = {
    "mood": "mood_expander",
    "sticker": "sticker_expander",
    "music": "music_expander",
    "convert": "convert_expander",
    "settings": "settings_expander",
    "stats": "stats_expander",
    "search": "search_expander",
    "export": "export_expander",
}

MENU_ICONS = {
    "mood": "🎭",
    "sticker": "😄",
    "music": "🎵",
    "convert": "🔄",
    "settings": "⚙️",
    "stats": "📊",
    "search": "🔍",
    "export": "💾",
}

def strip_emoji_prefix(label_text):
    parts = label_text.split(" ", 1)
    return parts[1] if len(parts) == 2 else label_text

# =====================
# 10b. SIDEBAR
# =====================
with st.sidebar:
    st.markdown('<div class="kei-sidebar-inner">', unsafe_allow_html=True)

    current_mode = st.session_state.mode
    _accent = st.session_state.get("theme_color", "#d6336c")
    _hex = _accent.lstrip("#")
    try:
        _r, _g, _b = tuple(int(_hex[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        _r, _g, _b = (214, 51, 108)

    _theme = st.session_state.get("theme", "dark")
    if _theme == "light":
        _ms_bg     = "rgba(255,255,255,0.4)"
        _ms_text   = "rgba(0,0,0,0.55)"
        _ms_border = "rgba(0,0,0,0.07)"
        _text_dim  = "rgba(0,0,0,0.45)"
        _text_dimmer = "rgba(0,0,0,0.3)"
    else:
        _ms_bg     = "rgba(255,255,255,0.045)"
        _ms_text   = "rgba(255,255,255,0.5)"
        _ms_border = "rgba(255,255,255,0.09)"
        _text_dim  = "rgba(255,255,255,0.4)"
        _text_dimmer = "rgba(255,255,255,0.25)"

    _chat_active = current_mode == "chat"
    st.markdown(f"""
    <style>
    .st-key-kei_mode_switch {{
        background: {_ms_bg} !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1px solid {_ms_border} !important;
        border-radius: 16px !important;
        padding: 4px !important;
        margin-bottom: 4px !important;
    }}
    .st-key-mode_chat_wrap button,
    .st-key-mode_diary_wrap button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        background: transparent !important;
        color: {_text_dim} !important;
        border: none !important;
        text-align: center !important;
        transition: all 0.2s ease !important;
        height: 38px !important;
        width: 100% !important;
    }}
    .st-key-mode_chat_wrap button:hover,
    .st-key-mode_diary_wrap button:hover {{
        color: {_accent} !important;
    }}
    .st-key-mode_chat_wrap button p,
    .st-key-mode_diary_wrap button p {{
        color: inherit !important;
    }}
    .st-key-{"mode_chat_wrap" if _chat_active else "mode_diary_wrap"} button {{
        color: #ffffff !important;
        background: #D6336C !important;
        box-shadow: 0 4px 14px -4px rgba(214,51,108,0.55) !important;
    }}
    .st-key-{"mode_chat_wrap" if _chat_active else "mode_diary_wrap"} button:hover {{
        color: #ffffff !important;
    }}
    .st-key-{"mode_chat_wrap" if _chat_active else "mode_diary_wrap"} button p {{
        color: #ffffff !important;
    }}
    .kei-sidebar-inner button,
    .kei-sidebar-inner button:focus,
    .kei-sidebar-inner button:focus-visible,
    .kei-sidebar-inner [data-testid="stButton"] button:focus,
    .kei-sidebar-inner [data-testid="stButton"] button:focus-visible,
    .kei-sidebar-inner [data-testid^="stBaseButton"]:focus,
    .kei-sidebar-inner [data-testid^="stBaseButton"]:focus-visible {{
        outline: none !important;
        box-shadow: none !important;
    }}
    {''.join([f'''
    .st-key-menu_{key} button {{
        border-color: {_accent} !important;
        background: rgba({_r},{_g},{_b},0.1) !important;
        color: {_accent} !important;
    }}
    ''' for key in PANEL_TITLES if st.session_state.get("active_panel") == key])}
    {''.join([f'''
    .st-key-exp_{key} summary p::before {{
        content: "{icon}";
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 22px !important;
        margin-right: 10px !important;
        font-size: 14px !important;
        flex-shrink: 0 !important;
    }}
    .st-key-exp_{key} [data-testid="stExpander"],
    .st-key-exp_{key} summary,
    .st-key-exp_{key} *,
    .st-key-exp_{key} *:focus,
    .st-key-exp_{key} *:focus-visible {{
        outline: none !important;
        box-shadow: none !important;
        border-color: {_ms_border} !important;
    }}
    ''' for key, icon in MENU_ICONS.items()])}
    .st-key-new_chat_btn button p,
    .st-key-clear_chat_btn button p,
    .st-key-logout_btn button p {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    .st-key-new_chat_btn button p::before,
    .st-key-clear_chat_btn button p::before,
    .st-key-logout_btn button p::before {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        margin-right: 8px;
        border-radius: 7px;
        background: rgba(255,255,255,0.07);
        flex-shrink: 0;
        font-size: 12px;
    }}
    .st-key-new_chat_btn button p::before {{ content: "🆕"; }}
    .st-key-clear_chat_btn button p::before {{ content: "🗑️"; }}
    .st-key-logout_btn button p::before {{ content: "🚪"; }}
    </style>
    """, unsafe_allow_html=True)

    mode_switch = st.container(key="kei_mode_switch")
    with mode_switch:
        mcol1, mcol2 = st.columns(2)
        with mcol1:
            with st.container(key="mode_chat_wrap"):
                if st.button(t("chat_btn"), key="mode_chat_btn", use_container_width=True):
                    if st.session_state.mode != "chat":
                        st.session_state.mode = "chat"
                        st.rerun()
        with mcol2:
            with st.container(key="mode_diary_wrap"):
                if st.button(t("diary_btn"), key="mode_diary_btn", use_container_width=True):
                    if st.session_state.mode != "diary":
                        st.session_state.mode = "diary"
                        st.rerun()

    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

    mood_emoji, mood_label = get_current_mood()
    streak_count = update_and_get_streak()

    _avatar_path = user_file("kei_avatar.png")
    avatar_exists = os.path.exists(_avatar_path)

    if avatar_exists:
        avatar_b64 = base64.b64encode(open(_avatar_path, "rb").read()).decode("utf-8")
        avatar_img_html = f'<img src="data:image/png;base64,{avatar_b64}" style="width:64px;height:64px;border-radius:50%;object-fit:cover;display:block;" />'
    else:
        avatar_img_html = f'''<div style="width:64px;height:64px;border-radius:50%;
            background:#1c1c1e;border:2px solid #ffffff;
            display:flex;align-items:center;justify-content:center;
            color:#fff;font-weight:700;font-size:24px;">K</div>'''

    _user_email_display = st.session_state.get("user_email", "")
    _user_email_short = _user_email_display.split("@")[0] if _user_email_display else "User"

    st.markdown(f"""
    <div style="
        background: #D6336C;
        border-radius: 18px;
        padding: 18px 16px;
        text-align: center;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
    ">
        <div style="position:absolute;top:-18px;right:-18px;width:64px;height:64px;border-radius:50%;background:#E85F95;"></div>
        <div style="position:relative;">
            <div style="position:relative;width:64px;height:64px;margin:0 auto 8px;">
                {avatar_img_html}
                <span style="position:absolute;bottom:-1px;right:-1px;width:14px;height:14px;
                    border-radius:50%;background:#4ade80;border:2px solid #D6336C;"></span>
            </div>
            <div style="color:#ffffff;font-size:14px;font-weight:700;">Kei AI</div>
            <div style="color:#FFE0EB;font-size:11px;margin-top:2px;">● {t('online_status')}</div>
            <div style="color:#FFC2DC;font-size:11px;margin-top:4px;">👤 {_user_email_short}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Ganti / Hapus Foto"):
        if avatar_exists:
            uploaded_avatar = st.file_uploader("Upload foto baru", type=["png","jpg","jpeg"], key="ganti_foto")
            if uploaded_avatar:
                with open(_avatar_path, "wb") as f:
                    f.write(uploaded_avatar.getbuffer())
                st.success("Foto berhasil diganti.")
                st.rerun()
            if st.button("Hapus Foto"):
                os.remove(_avatar_path)
                st.rerun()
        else:
            uploaded_avatar = st.file_uploader("Upload Foto Kei", type=["png","jpg","jpeg"], key="upload_foto_baru")
            if uploaded_avatar:
                with open(_avatar_path, "wb") as f:
                    f.write(uploaded_avatar.getbuffer())
                st.rerun()

    st.markdown(f"""
    <div style="display:flex;gap:8px;margin-bottom:14px;">
        <div style="flex:1;background:#FAC775;border-radius:14px;padding:9px 0;text-align:center;">
            <div style="font-size:16px;">{mood_emoji}</div>
            <div style="color:#633806;font-size:9.5px;letter-spacing:0.5px;margin-top:2px;">{t('mood_today').upper()}</div>
            <div style="color:#412402;font-size:11.5px;font-weight:600;">{mood_label}</div>
        </div>
        <div style="flex:1;background:#3FA9DA;border-radius:14px;padding:9px 0;text-align:center;">
            <div style="font-size:16px;">🔥</div>
            <div style="color:#042c53;font-size:9.5px;letter-spacing:0.5px;margin-top:2px;">{t('streak').upper()}</div>
            <div style="color:#042c53;font-size:11.5px;font-weight:600;">{streak_count} {t('streak_unit')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<div style='font-size:12px;color:{_text_dim};margin-bottom:6px;'>{t('mode_label')}: {t('mode_chat') if st.session_state.mode == 'chat' else t('mode_diary')}</div>", unsafe_allow_html=True)

    st.markdown('<div class="kei-divider"></div>', unsafe_allow_html=True)

    menu_list = st.container(key="kei_menu_list")
    with menu_list:
        st.markdown(f"<div class='kei-menu-group-label'>{t('menu_group_interaksi')}</div>", unsafe_allow_html=True)

        for key, label_key in [
            ("mood", "mood_expander"),
            ("sticker", "sticker_expander"),
            ("music", "music_expander"),
        ]:
            with st.expander(
                strip_emoji_prefix(t(label_key)),
                key=f"exp_{key}",
                expanded=(st.session_state.get("keep_panel_open") == key),
            ):
                if key == "mood":
                    render_mood_panel(_accent, _r, _g, _b)
                elif key == "sticker":
                    render_sticker_panel(_accent, _r, _g, _b)
                elif key == "music":
                    render_music_panel(_accent, _r, _g, _b)

        st.markdown(f"<div class='kei-menu-group-label'>{t('menu_group_alat')}</div>", unsafe_allow_html=True)

        for key, label_key in [
            ("convert", "convert_expander"),
            ("settings", "settings_expander"),
            ("stats", "stats_expander"),
            ("search", "search_expander"),
            ("export", "export_expander"),
        ]:
            with st.expander(
                strip_emoji_prefix(t(label_key)),
                key=f"exp_{key}",
                expanded=(st.session_state.get("keep_panel_open") == key),
            ):
                if key == "convert":
                    render_convert_panel(_accent, _r, _g, _b)
                elif key == "settings":
                    render_settings_panel(_accent, _r, _g, _b)
                elif key == "stats":
                    render_stats_panel(_accent, _r, _g, _b)
                elif key == "search":
                    render_search_panel(_accent, _r, _g, _b, _ms_bg, _ms_border, _ms_text)
                elif key == "export":
                    render_export_panel(_accent, _r, _g, _b, _text_dim, _text_dimmer)

    st.markdown('<div class="kei-divider"></div>', unsafe_allow_html=True)

    if st.button(strip_emoji_prefix(t("new_chat")), use_container_width=True, key="new_chat_btn"):
        st.session_state.messages = []
        save_json(CHAT_FILE, [])
        st.rerun()

    if st.button(strip_emoji_prefix(t("clear_chat")), use_container_width=True, key="clear_chat_btn"):
        st.session_state.messages = []
        save_json(CHAT_FILE, [])
        st.rerun()

    st.markdown('<div class="kei-divider"></div>', unsafe_allow_html=True)

    if st.button(strip_emoji_prefix(t("logout")), use_container_width=True, key="logout_btn"):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.session_state.messages  = []
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# =====================
# 11. HEADER
# =====================
header_mood_emoji, _header_mood_label = get_current_mood()
_header_tagline_color = "rgba(0,0,0,0.45)" if st.session_state.theme == "light" else "rgba(255,255,255,0.4)"

milestone_letter = check_and_generate_milestone_letter(streak_count)
if milestone_letter:
    st.session_state["show_milestone_letter"] = milestone_letter

if st.session_state.get("show_milestone_letter"):
    letter_data = st.session_state["show_milestone_letter"]
    streak_num  = letter_data["streak"]

    milestone_colors = {
        7:   ("🌸", "#D6336C"),
        30:  ("🌟", "#FAC775"),
        100: ("💎", "#3FA9DA"),
        365: ("👑", "#A89ADF"),
    }
    icon, color = milestone_colors.get(streak_num, ("💕", _accent))

    st.markdown(f"""
    <div style="
        background: rgba({_r},{_g},{_b},0.08);
        border: 1.5px solid rgba({_r},{_g},{_b},0.3);
        border-radius: 16px;
        padding: 20px 24px;
        margin: 12px 0 4px;
        text-align: center;
    ">
        <div style="font-size:36px;margin-bottom:6px;">{icon}</div>
        <div style="color:{color};font-size:18px;font-weight:700;margin-bottom:4px;">
            {streak_num} Hari Bersama Kei
        </div>
        <div style="color:{"#1a1a1a" if _theme == "light" else "rgba(255,255,255,0.85)"};
                    font-size:14px;line-height:1.7;white-space:pre-wrap;
                    text-align:left;margin-top:12px;padding:12px 16px;
                    background:{"rgba(0,0,0,0.03)" if _theme == "light" else "rgba(255,255,255,0.04)"};
                    border-radius:10px;">
            {letter_data['letter']}
        </div>
        <div style="color:{_text_dimmer};font-size:11px;margin-top:10px;">
            📅 {letter_data['date']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(t("milestone_close"), key="close_letter_btn"):
        st.session_state["show_milestone_letter"] = None
        st.rerun()

if st.session_state.mode == "diary":
    st.markdown(f"""
    <div style="text-align:center;padding:4px 0 4px;">
        <h1 style="color:{st.session_state.theme_color};margin:0;font-size:48px;line-height:1.1;">💌 Dear Diary</h1>
        <p style="color:{_header_tagline_color};font-size:20px;margin:2px 0 0;">{t('diary_header_sub')} {header_mood_emoji}</p>
    </div>
    """, unsafe_allow_html=True)
else:
    _chat_is_empty = len(st.session_state.messages) == 0
    if _chat_is_empty:
        _headline_color = "#2b2b40" if _theme == "light" else "#ffffff"
        st.markdown(f"""
        <div style="text-align:center;padding:64px 20px 28px;">
            <div style="font-size:12px;letter-spacing:0.14em;color:{_text_dimmer};font-weight:700;margin-bottom:8px;text-transform:uppercase;">
                Tanya Kei &middot; AI Companion
            </div>
            <div style="font-size:32px;font-weight:700;color:{_headline_color};">
                Apa yang bisa Kei bantu
                <span style="color:#D6336C;">hari ini?</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align:center;padding:32px 0 14px;">
            <div style="display:flex;align-items:center;justify-content:center;gap:14px;margin-bottom:6px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 36 36">
                    <polygon points="18,0 21,15 36,18 21,21 18,36 15,21 0,18 15,15" fill="#D6336C"/>
                </svg>
                <span style="color:#D6336C;font-size:48px;font-weight:700;line-height:1.1;">Kei AI</span>
            </div>
            <p style="color:{_header_tagline_color};font-size:18px;margin:0;">{t('app_companion')} {header_mood_emoji}</p>
        </div>
        """, unsafe_allow_html=True)

# =====================
# 12. DEAR DIARY MODE
# =====================
if st.session_state.mode == "diary":
    diary_entries = load_json(DIARY_FILE)

    if diary_entries:
        with st.expander(t("diary_old_entries").format(n=len(diary_entries))):
            for entry in reversed(diary_entries[-10:]):
                st.markdown(f"""
                <div class="diary-box">
                    <small style="color:{st.session_state.theme_color};">📅 {entry['date']}</small><br><br>
                    <b>Kamu:</b> {entry['user']}<br><br>
                    <b>Kei:</b> {entry['kei']}
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    diary_input = st.text_area(t("diary_textarea_label"),
                               placeholder=t("diary_placeholder"),
                               height=150, key="diary_textarea")
    col1, col2 = st.columns([3, 1])
    with col1:
        send_diary = st.button(t("diary_send"), use_container_width=True)
    with col2:
        clear_diary = st.button(t("diary_clear"), use_container_width=True)

    if clear_diary:
        save_json(DIARY_FILE, [])
        st.success(t("diary_cleared"))
        st.rerun()

    if send_diary and diary_input:
        with st.spinner("Kei sedang membaca ceritamu..."):
            full_prompt = f"{KEI_DIARY_PERSONA}\n\nUser bercerita: {diary_input}\n\nKei menjawab dengan hangat dan tenang:"
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
            <b style="color:{st.session_state.theme_color};">{t('diary_you_wrote')}</b><br>{diary_input}<br><br>
            <b style="color:{st.session_state.theme_color};">{t('diary_kei_answers')}</b><br>{kei_reply}
        </div>
        """, unsafe_allow_html=True)

# =====================
# 13. CHAT MODE
# =====================
else:
    if not st.session_state.messages:
        st.session_state.messages = load_json(CHAT_FILE)

    _chat_text_color = "#2b2b40" if _theme == "light" else "#f2f2f5"
    _bubble_bg = "#ffffff" if _theme == "light" else "rgba(255,255,255,0.08)"

    for msg in st.session_state.messages:
        img_tag = ""
        if msg.get("image_b64"):
            img_tag = f'<img src="data:image/png;base64,{msg["image_b64"]}" style="max-width:240px;border-radius:14px;display:block;margin-bottom:6px;" />'

        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display:flex; justify-content:flex-end; margin:6px 0;">
                <div style="max-width:70%; background:{_bubble_bg}; border:1px solid {_ms_border};
                            border-radius:18px; padding:10px 16px; color:{_chat_text_color};
                            font-size:15px; line-height:1.5;">
                    {img_tag}{msg["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="margin:6px 0 14px; color:{_chat_text_color}; font-size:15px; line-height:1.6;">
                {img_tag}{msg["content"]}
            </div>
            """, unsafe_allow_html=True)

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
            if st.button("Selesai", key="conv_done_btn"):
                st.session_state.conv_result = None
                st.rerun()

    if not st.session_state.messages:
        st.markdown("""
        <style>
        .st-key-kei_quick_actions div[data-testid="stHorizontalBlock"] {
            justify-content: center !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
        }
        .st-key-kei_quick_actions div[data-testid="stColumn"],
        .st-key-kei_quick_actions div[data-testid^="column"] {
            width: auto !important;
            min-width: 0 !important;
            flex: 0 0 auto !important;
        }
        .st-key-kei_quick_actions div[data-testid="stColumn"] > div {
            width: auto !important;
        }
        .st-key-kei_quick_actions button {
            border-radius: 20px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            padding: 6px 16px !important;
            white-space: nowrap !important;
        }
        </style>
        """, unsafe_allow_html=True)

        QUICK_ACTIONS = [
            ("scanner", "\u2924 Scanner", "Bisa bantu aku scan dan rapikan isi dokumen ini jadi teks?"),
            ("studio", "\u25d0 Studio", "Ajak aku ngobrol santai dong, Kei. Lagi pengen cerita ringan."),
            ("dokumen", "\U0001F4C4 Dokumen", "Aku mau konversi file PDF/Word, gimana caranya Kei?"),
            ("berita", "\U0001F4F0 Berita", "Kei, ada berita menarik apa hari ini?"),
            ("darurat", "\u29B8 Darurat", "Aku lagi butuh bantuan, ini agak darurat."),
            ("rundown", "\u2261 Rundown", "Kei, coba rangkum progres ngobrol kita sejauh ini."),
        ]

        quick_row = st.container(key="kei_quick_actions")
        with quick_row:
            qa_cols = st.columns(len(QUICK_ACTIONS))
            for qa_col, (qa_key, qa_label, qa_prompt) in zip(qa_cols, QUICK_ACTIONS):
                with qa_col:
                    if st.button(qa_label, key=f"qa_{qa_key}"):
                        st.session_state.messages.append({"role": "user", "content": qa_prompt})
                        history_text = f"User: {qa_prompt}\n"
                        full_prompt = f"{KEI_PERSONA}\n\nRiwayat percakapan:\n{history_text}\nKei:"
                        with st.spinner("Kei sedang mengetik..."):
                            reply = generate_content_with_retry(full_prompt)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                        save_json(CHAT_FILE, st.session_state.messages)
                        st.rerun()

    chat_input = st.chat_input(
        t("chat_placeholder"),
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

            if fname.endswith(".pdf"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"Mengonversi **{uploaded_file.name}** dari PDF ke Word...",
                })
                with st.spinner("Kei sedang mengonversi PDF ke Word..."):
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
                        reply_text = f"Berhasil, Kak. File **{uploaded_file.name}** sudah Kei konversi ke Word. Klik tombol download di bawah ya."
                        st.session_state.messages.append({"role": "assistant", "content": reply_text})
                        st.session_state.conv_result = {
                            "bytes":    docx_bytes,
                            "filename": uploaded_file.name.replace(".pdf", ".docx"),
                            "mime":     "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            "label":    "Download .docx",
                        }
                        save_json(CHAT_FILE, st.session_state.messages)
                    except Exception as e:
                        err = f"Maaf Kak, Kei gagal mengonversinya. Error: {e}"
                        st.session_state.messages.append({"role": "assistant", "content": err})
                        save_json(CHAT_FILE, st.session_state.messages)

            elif fname.endswith(".docx"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"Mengonversi **{uploaded_file.name}** dari Word ke PDF...",
                })
                with st.spinner("Kei sedang mengonversi Word ke PDF..."):
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
                            reply_text = f"Berhasil, Kak. File **{uploaded_file.name}** sudah Kei konversi ke PDF. Klik tombol download di bawah ya."
                            st.session_state.messages.append({"role": "assistant", "content": reply_text})
                            st.session_state.conv_result = {
                                "bytes":    pdf_bytes,
                                "filename": uploaded_file.name.replace(".docx", ".pdf"),
                                "mime":     "application/pdf",
                                "label":    "Download .pdf",
                            }
                            save_json(CHAT_FILE, st.session_state.messages)
                        else:
                            raise Exception(result.stderr)
                    except FileNotFoundError:
                        err = "Maaf Kak, LibreOffice belum terinstall di server. Pastikan `packages.txt` sudah ada ya."
                        st.session_state.messages.append({"role": "assistant", "content": err})
                        save_json(CHAT_FILE, st.session_state.messages)
                    except Exception as e:
                        err = f"Maaf Kak, Kei gagal mengonversinya. Error: {e}"
                        st.session_state.messages.append({"role": "assistant", "content": err})
                        save_json(CHAT_FILE, st.session_state.messages)

            else:
                img_b64          = base64.b64encode(file_bytes).decode("utf-8")
                user_msg_content = f"[Foto dikirim] {prompt}" if prompt else "[Foto dikirim]"
                st.session_state.messages.append({
                    "role":      "user",
                    "content":   user_msg_content,
                    "image_b64": img_b64,
                })
                with st.spinner("Kei sedang melihat fotonya..."):
                    reply = analyze_image_with_kei(file_bytes, mime_type, prompt)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                save_json(CHAT_FILE, st.session_state.messages)
                st.rerun()

        elif prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})

            browsing_keywords = ["cari", "search", "browsing", "cek", "info tentang", "berita", "apa itu", "siapa itu"]
            if any(kw in prompt.lower() for kw in browsing_keywords):
                search_url  = f"https://www.google.com/search?q={prompt.replace(' ', '+')}"
                search_note = f"\n\nKei juga mencarikan untuk Kak di sini: [Klik untuk lihat hasil pencarian]({search_url})"
            else:
                search_note = ""

            history_text = ""
            for m in st.session_state.messages[-10:]:
                role = "User" if m["role"] == "user" else "Kei"
                history_text += f"{role}: {m['content']}\n"

            full_prompt = f"{KEI_PERSONA}\n\nRiwayat percakapan:\n{history_text}\nKei:"

            with st.spinner("Kei sedang mengetik..."):
                reply = generate_content_with_retry(full_prompt) + search_note

            st.session_state.messages.append({"role": "assistant", "content": reply})
            save_json(CHAT_FILE, st.session_state.messages)
            st.rerun()
