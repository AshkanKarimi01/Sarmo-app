import streamlit as st
import pandas as pd
import os
import time
import io
import json
import logging
import hashlib
import jdatetime
from datetime import datetime
from zoneinfo import ZoneInfo

# ------------------- تنظیمات لاگینگ -------------------
LOG_DIR = "data"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8')]
)
logger = logging.getLogger(__name__)

def log_action(level: str, message: str, user: str = "system"):
    full_msg = f"[{user}] {message}"
    if level == "INFO":
        logger.info(full_msg)
    elif level == "WARNING":
        logger.warning(full_msg)
    elif level == "ERROR":
        logger.error(full_msg)

# ------------------- تنظیمات صفحه -------------------
st.set_page_config(page_title="Sarmo", layout="wide", page_icon="👕", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700&display=swap');

    *, *::before, *::after { box-sizing: border-box; }
    html, body, .stApp { direction: rtl; font-family: 'Vazirmatn', sans-serif !important; }

    /* ============================================================
       پالت روشن (پیش‌فرض)
    ============================================================ */
    :root {
        --primary:        #1B4F8A;
        --primary-light:  #2563B0;
        --primary-glow:   rgba(27,79,138,0.18);
        --accent:         #E8A020;
        --bg:             #F4F7FB;
        --bg2:            #EBF0F8;
        --surface:        #FFFFFF;
        --surface2:       #F8FAFD;
        --border:         #D8E2F0;
        --text:           #1A2535;
        --text-soft:      #5A6E88;
        --text-inv:       #FFFFFF;
        --success:        #1A7F5A;
        --danger:         #C0392B;
        --warn:           #D97706;
        --code-bg:        #F0F5FC;
        --row-alt:        #EEF3FB;
        --shadow:         rgba(0,0,0,0.06);
        --shadow-lg:      rgba(0,0,0,0.12);
        --edit-bg1:       #FEF3C7;
        --edit-bg2:       #FDE68A;
        --edit-text:      #92400E;
        --slider-track:   #CBD5E1;
    }

    /* ============================================================
       پالت تاریک
    ============================================================ */
    .dark-mode {
        --primary:        #4A90D9;
        --primary-light:  #5BA3E8;
        --primary-glow:   rgba(74,144,217,0.22);
        --accent:         #F5B942;
        --bg:             #0F1923;
        --bg2:            #152030;
        --surface:        #1A2840;
        --surface2:       #1F3050;
        --border:         #2A3F5A;
        --text:           #E2EAF4;
        --text-soft:      #8AADCC;
        --text-inv:       #0F1923;
        --success:        #2ECC87;
        --danger:         #E55A4A;
        --warn:           #F59E0B;
        --code-bg:        #111E2E;
        --row-alt:        #1E3048;
        --shadow:         rgba(0,0,0,0.3);
        --shadow-lg:      rgba(0,0,0,0.5);
        --edit-bg1:       #2D2008;
        --edit-bg2:       #3D2D0A;
        --edit-text:      #F5C842;
        --slider-track:   #2A3F5A;
    }

    /* ---- پس‌زمینه کل اپ ---- */
    .stApp                       { background: var(--bg) !important; color: var(--text) !important; }
    .stApp > div                 { background: transparent !important; }
    .main .block-container       { background: transparent !important; padding-top: 1rem !important; }

    /* ---- همه متن‌های streamlit ---- */
    .stApp p, .stApp span, .stApp div,
    .stApp label, .stApp h1, .stApp h2,
    .stApp h3, .stApp h4, .stApp li  { color: var(--text) !important; }

    /* ---- هدر بالا ---- */
    .sarmo-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        border-radius: 16px; padding: 18px 28px; margin-bottom: 20px;
        display: flex; align-items: center; gap: 16px;
        box-shadow: 0 4px 20px var(--primary-glow);
    }
    .sarmo-title    { color: #fff !important; font-size: 1.6rem; font-weight: 700; margin: 0; }
    .sarmo-subtitle { color: rgba(255,255,255,0.75) !important; font-size: 0.85rem; margin: 0; }

    /* ---- کارت‌های آمار ---- */
    .stat-card {
        background: var(--surface); border-radius: 14px; padding: 18px 22px;
        border: 1.5px solid var(--border); text-align: center;
        box-shadow: 0 2px 8px var(--shadow); transition: box-shadow .2s;
    }
    .stat-card:hover          { box-shadow: 0 6px 18px var(--primary-glow); }
    .stat-card .stat-icon     { font-size: 1.8rem; margin-bottom: 6px; }
    .stat-card .stat-val      { font-size: 1.6rem; font-weight: 700; color: var(--primary) !important; margin: 0; }
    .stat-card .stat-label    { font-size: 0.8rem; color: var(--text-soft) !important; margin: 0; }

    /* ---- تب‌ها ---- */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--surface) !important;
        border-radius: 12px; padding: 6px;
        border: 1.5px solid var(--border); gap: 4px;
        box-shadow: 0 2px 8px var(--shadow); margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important; font-size: 0.9rem !important;
        font-weight: 500 !important; color: var(--text-soft) !important;
        padding: 8px 16px !important; transition: all .2s !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--primary) !important;
        color: #fff !important; font-weight: 600 !important;
    }
    /* panel پشت محتوای تب */
    .stTabs [data-baseweb="tab-panel"] { background: transparent !important; }

    /* ---- section-card ---- */
    .section-card {
        background: var(--surface); border-radius: 16px; padding: 24px;
        border: 1.5px solid var(--border); margin-bottom: 20px;
        box-shadow: 0 2px 10px var(--shadow);
    }
    .section-title {
        font-size: 1.05rem; font-weight: 700; color: var(--primary) !important;
        margin-bottom: 16px; display: flex; align-items: center; gap: 8px;
        border-bottom: 2px solid var(--border); padding-bottom: 10px;
    }

    /* ---- اینپوت‌ها ---- */
    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {
        border-radius: 10px !important;
        border: 1.5px solid var(--border) !important;
        font-family: 'Vazirmatn', sans-serif !important;
        background: var(--bg2) !important;
        color: var(--text) !important;
        transition: border-color .2s, box-shadow .2s !important;
    }
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px var(--primary-glow) !important;
        outline: none !important;
    }
    /* سلکت‌باکس */
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"] > div {
        background: var(--bg2) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
    }
    /* dropdown منوی سلکت */
    [data-baseweb="popover"] [data-baseweb="menu"],
    [data-baseweb="popover"] ul {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
    }
    [data-baseweb="popover"] li,
    [data-baseweb="option"]  { color: var(--text) !important; background: var(--surface) !important; }
    [data-baseweb="option"]:hover { background: var(--bg2) !important; }

    /* label‌ها */
    .stTextInput label, .stSelectbox label, .stTextArea label,
    .stNumberInput label, .stRadio label, .stMultiSelect label,
    .stSlider label, .stCheckbox label {
        font-weight: 600 !important; color: var(--text) !important; font-size: 0.88rem !important;
    }
    /* radio و checkbox */
    .stRadio > div, .stCheckbox > label { color: var(--text) !important; }

    /* multiselect */
    .stMultiSelect [data-baseweb="select"] > div { background: var(--bg2) !important; border-color: var(--border) !important; }
    .stMultiSelect [data-baseweb="tag"] { background: var(--primary) !important; color: #fff !important; }

    /* slider track */
    [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] { background: var(--primary) !important; }
    [data-testid="stSlider"] div[data-baseweb="slider"] > div > div { background: var(--slider-track) !important; }

    /* ---- دکمه‌ها ---- */
    .stButton > button {
        border-radius: 10px !important; font-family: 'Vazirmatn', sans-serif !important;
        font-weight: 600 !important; font-size: 0.88rem !important;
        padding: 10px 20px !important; transition: all .2s !important; border: none !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
        color: #fff !important; box-shadow: 0 4px 12px var(--primary-glow) !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 18px var(--shadow-lg) !important; transform: translateY(-1px) !important;
    }
    .stButton > button[kind="secondary"] {
        background: var(--surface) !important; color: var(--text) !important;
        border: 1.5px solid var(--border) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: var(--primary) !important; color: var(--primary) !important;
    }
    /* download button */
    .stDownloadButton > button {
        border-radius: 10px !important; font-family: 'Vazirmatn', sans-serif !important;
        font-weight: 600 !important; background: var(--surface) !important;
        color: var(--text) !important; border: 1.5px solid var(--border) !important;
    }

    /* ---- اکسپندر ---- */
    [data-testid="stExpander"] {
        background: var(--surface2) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 10px !important; overflow: hidden;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary * {
        background: var(--surface2) !important; color: var(--text) !important;
        font-weight: 600 !important; font-family: 'Vazirmatn', sans-serif !important;
    }
    [data-testid="stExpander"] > div { background: var(--surface2) !important; }

    /* ---- دیتافریم ---- */
    .stDataFrame           { border-radius: 12px !important; overflow: hidden !important; border: 1.5px solid var(--border) !important; }
    .stDataFrame iframe    { background: var(--surface) !important; }
    /* جدول داخل iframe - از طریق CSS متغیر قابل کنترل نیست ولی border کافیه */

    /* ---- کد / pre ---- */
    .stCodeBlock, pre, code {
        background: var(--code-bg) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }

    /* ---- متریک ---- */
    div[data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 700 !important; color: var(--primary) !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.82rem !important; color: var(--text-soft) !important; }
    div[data-testid="metric-container"] { background: var(--surface) !important; border-radius: 12px !important; padding: 12px 16px !important; border: 1.5px solid var(--border) !important; }

    /* ---- پیام‌ها ---- */
    div[data-testid="stAlert"] {
        border-radius: 10px !important; font-family: 'Vazirmatn', sans-serif !important;
        font-size: 0.9rem !important; border-width: 1px !important;
    }
    /* رنگ پس‌زمینه alert در دارک مود */
    .dark-mode div[data-testid="stAlert"][data-baseweb="notification"] { opacity: 0.9; }

    /* ---- جداکننده ---- */
    hr { border-color: var(--border) !important; margin: 20px 0 !important; }

    /* ---- سایدبار ---- */
    section[data-testid="stSidebar"] { display: none !important; }
    .main { margin-right: 0 !important; }

    /* ---- بنر ویرایش ---- */
    .edit-banner {
        background: linear-gradient(90deg, var(--edit-bg1), var(--edit-bg2));
        border: 2px solid var(--accent); border-radius: 12px;
        padding: 14px 20px; margin-bottom: 18px;
        font-weight: 600; color: var(--edit-text) !important;
        display: flex; align-items: center; gap: 10px;
    }

    /* ---- اسکرول‌بار ---- */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--primary); }

    /* ---- کلاس دکمه دارک‌مود ---- */
    .dark-toggle-btn button {
        background: var(--surface) !important; color: var(--text) !important;
        border: 1.5px solid var(--border) !important; border-radius: 20px !important;
        padding: 6px 16px !important; font-size: 0.82rem !important; font-weight: 600 !important;
        transition: all .2s !important;
    }
    .dark-toggle-btn button:hover { border-color: var(--primary) !important; color: var(--primary) !important; }

    /* transition نرم برای تغییر تم */
    .stApp, .section-card, .stat-card, .sarmo-header,
    .stTabs [data-baseweb="tab-list"], div[data-testid="metric-container"] {
        transition: background .25s, border-color .25s, color .25s !important;
    }
</style>
""", unsafe_allow_html=True)

# ------------------- پایداری session -------------------
SESSION_FILE = os.path.join(LOG_DIR, "session.json")

def save_session():
    data = {
        "logged_in": st.session_state.get("logged_in", False),
        "username": st.session_state.get("username", ""),
        "role": st.session_state.get("role", ""),
        "login_time": st.session_state.get("login_time", 0)
    }
    with open(SESSION_FILE, "w", encoding='utf-8') as f:
        json.dump(data, f)

def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
            # اعتبارسنجی: فقط فیلدهای مجاز لود بشن
            allowed = {"logged_in", "username", "role", "login_time"}
            for k, v in data.items():
                if k in allowed:
                    st.session_state[k] = v
        except Exception:
            pass

load_session()

# ------------------- احراز هویت (رمز هش‌شده) -------------------
def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

USERS = {
    "admin": {"password_hash": _hash("admin123@"), "role": "admin"},
    "amir":  {"password_hash": _hash("04700"),     "role": "user"},
    "sara":  {"password_hash": _hash("Ab123456@"), "role": "admin"},
}

def check_login(username: str, password: str) -> bool:
    if username in USERS:
        return USERS[username]["password_hash"] == _hash(password)
    return False

# ------------------- session state اولیه -------------------
for _k, _v in {
    "logged_in": False, "username": None, "role": None,
    "edit_mode": False, "edit_invoice_no": None,
    "edit_cart": None, "edit_notes": "",
    "edit_customer_data": {},
    "delete_confirm": {},
    "dark_mode": False,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ---- اعمال تم از طریق CSS variable injection مستقیم ----
# Streamlit اسکریپت رو فیلتر می‌کنه؛ راه‌حل: override کردن CSS variables در :root
_dm = st.session_state.get("dark_mode", False)
if _dm:
    _theme_css = """
<style>
    .stApp,
    .stApp > div,
    .main .block-container,
    section[data-testid="stMain"],
    div[data-testid="stAppViewContainer"] {
        --primary:        #4A90D9 !important;
        --primary-light:  #5BA3E8 !important;
        --primary-glow:   rgba(74,144,217,0.22) !important;
        --accent:         #F5B942 !important;
        --bg:             #0F1923 !important;
        --bg2:            #152030 !important;
        --surface:        #1A2840 !important;
        --surface2:       #1F3050 !important;
        --border:         #2A3F5A !important;
        --text:           #E2EAF4 !important;
        --text-soft:      #8AADCC !important;
        --success:        #2ECC87 !important;
        --danger:         #E55A4A !important;
        --warn:           #F59E0B !important;
        --code-bg:        #111E2E !important;
        --row-alt:        #1E3048 !important;
        --shadow:         rgba(0,0,0,0.3) !important;
        --shadow-lg:      rgba(0,0,0,0.5) !important;
        --edit-bg1:       #2D2008 !important;
        --edit-bg2:       #3D2D0A !important;
        --edit-text:      #F5C842 !important;
        --slider-track:   #2A3F5A !important;
        background-color: #0F1923 !important;
        color: #E2EAF4 !important;
    }

    /* پس‌زمینه تمام لایه‌های streamlit */
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stHeader"],
    .main,
    .block-container,
    section[data-testid="stMain"] > div,
    div[data-testid="stVerticalBlock"],
    div[data-testid="stHorizontalBlock"],
    div[data-testid="column"] { background-color: #0F1923 !important; }

    /* سطح کارت */
    .section-card, .stat-card, .invoice-card,
    div[data-testid="metric-container"],
    .stTabs [data-baseweb="tab-list"],
    [data-testid="stExpander"],
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] > div,
    .streamlit-expanderHeader,
    .streamlit-expanderContent { background-color: #1A2840 !important; border-color: #2A3F5A !important; }

    /* متن */
    .stApp p, .stApp span, .stApp div, .stApp label,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp li, p, span, label, h1, h2, h3,
    div[data-testid="stText"],
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] span { color: #E2EAF4 !important; }

    /* اینپوت */
    .stTextInput input, .stTextArea textarea, .stNumberInput input,
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #152030 !important;
        color: #E2EAF4 !important;
        border-color: #2A3F5A !important;
    }

    /* placeholder */
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder { color: #8AADCC !important; }

    /* dropdown */
    [data-baseweb="popover"] [data-baseweb="menu"],
    [data-baseweb="popover"] ul,
    [data-baseweb="option"] { background-color: #1A2840 !important; color: #E2EAF4 !important; }
    [data-baseweb="option"]:hover { background-color: #152030 !important; }

    /* تب‌ها */
    .stTabs [data-baseweb="tab"] { color: #8AADCC !important; }
    .stTabs [aria-selected="true"] { background: #4A90D9 !important; color: #fff !important; }
    .stTabs [data-baseweb="tab-panel"] { background-color: #0F1923 !important; }

    /* دکمه secondary */
    .stButton > button[kind="secondary"] {
        background-color: #1A2840 !important;
        color: #E2EAF4 !important;
        border-color: #2A3F5A !important;
    }
    .stDownloadButton > button {
        background-color: #1A2840 !important;
        color: #E2EAF4 !important;
        border-color: #2A3F5A !important;
    }

    /* کد */
    .stCodeBlock, pre, code {
        background-color: #111E2E !important;
        color: #E2EAF4 !important;
        border-color: #2A3F5A !important;
    }

    /* متریک */
    div[data-testid="stMetricValue"] { color: #4A90D9 !important; }
    div[data-testid="stMetricLabel"] { color: #8AADCC !important; }
    div[data-testid="metric-container"] { background-color: #1A2840 !important; border-color: #2A3F5A !important; }

    /* section-title */
    .section-title { color: #4A90D9 !important; border-color: #2A3F5A !important; }
    .stat-card .stat-val { color: #4A90D9 !important; }
    .stat-card .stat-label { color: #8AADCC !important; }

    /* اسکرول‌بار */
    ::-webkit-scrollbar-track { background: #0F1923 !important; }
    ::-webkit-scrollbar-thumb { background: #2A3F5A !important; }

    /* فرم */
    [data-testid="stForm"] { background-color: #1A2840 !important; border-color: #2A3F5A !important; }

    /* hr */
    hr { border-color: #2A3F5A !important; }

    /* radio / checkbox text */
    .stRadio > div label, .stCheckbox > label { color: #E2EAF4 !important; }

    /* caption */
    .stCaption, [data-testid="stCaptionContainer"] { color: #8AADCC !important; }

    /* multiselect */
    .stMultiSelect [data-baseweb="select"] > div { background-color: #152030 !important; border-color: #2A3F5A !important; }
    .stMultiSelect [data-baseweb="tag"] { background-color: #4A90D9 !important; }

    /* بنر ویرایش در دارک مود */
    .edit-banner { background: linear-gradient(90deg,#2D2008,#3D2D0A) !important; color: #F5C842 !important; border-color: #F5B942 !important; }
</style>
"""
else:
    _theme_css = ""

st.markdown(_theme_css, unsafe_allow_html=True)

# ------------------- صفحه لاگین -------------------
def login_form():
    _dm = st.session_state.get("dark_mode", False)
    _title_color  = "#4A90D9" if _dm else "#1B4F8A"
    _sub_color    = "#8AADCC" if _dm else "#5A6E88"

    # دکمه تغییر تم در بالای صفحه لاگین
    _dm_icon = "☀️ روشن" if _dm else "🌙 تاریک"
    t1, t2, t3 = st.columns([1, 0.4, 1])
    with t2:
        if st.button(_dm_icon, key="login_theme_toggle", use_container_width=True):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align:center; margin: 20px 0 30px;">
            <div style="font-size:3.5rem; margin-bottom:10px;">👕</div>
            <h1 style="color:{_title_color}; font-size:2rem; margin:0;">Sarmo</h1>
            <p style="color:{_sub_color}; margin:6px 0 0;">سامانه مدیریت فروش پوشاک</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔐 ورود به سامانه</div>', unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("نام کاربری", placeholder="نام کاربری خود را وارد کنید")
            password = st.text_input("رمز عبور", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("ورود به سامانه ←", use_container_width=True, type="primary")
            if submitted:
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = USERS[username]["role"]
                    st.session_state.login_time = time.time()
                    log_action("INFO", "ورود موفق", username)
                    save_session()
                    st.rerun()
                else:
                    st.error("نام کاربری یا رمز عبور اشتباه است.")
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.get("logged_in", False):
    login_form()
    st.stop()
else:
    if time.time() - st.session_state.get("login_time", 0) > 86400:
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        st.rerun()

# ------------------- مسیرهای فایل -------------------
DATA_DIR    = "data"
CUSTOMERS_DB = os.path.join(DATA_DIR, "customers_db.csv")
ORDERS_DB   = os.path.join(DATA_DIR, "orders_db.csv")
INVENTORY_DB = os.path.join(DATA_DIR, "inventory.csv")
LOGO_FILE   = "logo.png"

COLORS_LIST = [
    "مشکی","سفید","آبی کمرنگ","آبی پررنگ","سبز کمرنگ","سبز پررنگ",
    "کرم","قرمز","طوسی","قهوه ای","بنفش","قهوه ای سنگشور","طوسی سنگشور","نارنجی"
]

# ====================================================
# ------------------- توابع انبار -------------------
# ====================================================
@st.cache_data(ttl=60, show_spinner=False)
def load_inventory():
    if not os.path.exists(INVENTORY_DB):
        return pd.DataFrame(columns=["ProductType","Size","Color","Quantity"])
    df = pd.read_csv(INVENTORY_DB, encoding='utf-8-sig')
    for col in ["ProductType","Size","Color"]:
        if col not in df.columns:
            df[col] = ""
    if "Quantity" not in df.columns:
        df["Quantity"] = 0
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors='coerce').fillna(0).astype(int)
    return df

def save_inventory(df):
    df.to_csv(INVENTORY_DB, index=False, encoding='utf-8-sig')
    st.cache_data.clear()
    return True

def update_inventory_after_order(cart_df, user="system"):
    inv_df = load_inventory()
    for _, item in cart_df.iterrows():
        ptype = item["ProductType"]
        size  = item["Size"]
        color = item["Color"]
        qty   = int(item["Quantity"])
        mask = (inv_df["ProductType"]==ptype) & (inv_df["Size"]==size) & (inv_df["Color"]==color)
        if mask.any():
            idx = inv_df[mask].index[0]
            if inv_df.loc[idx,"Quantity"] >= qty:
                inv_df.loc[idx,"Quantity"] -= qty
            else:
                log_action("ERROR","موجودی کافی نیست",user)
                return False
        else:
            log_action("ERROR","کالا یافت نشد",user)
            return False
    return save_inventory(inv_df)

def restore_inventory_after_deletion(cart_df, user="system"):
    inv_df = load_inventory()
    for _, item in cart_df.iterrows():
        ptype = item["ProductType"]
        size  = item["Size"]
        color = item["Color"]
        qty   = int(item["Quantity"])
        mask = (inv_df["ProductType"]==ptype) & (inv_df["Size"]==size) & (inv_df["Color"]==color)
        if mask.any():
            idx = inv_df[mask].index[0]
            inv_df.loc[idx,"Quantity"] += qty
        else:
            new_row = pd.DataFrame([[ptype,size,color,qty]], columns=["ProductType","Size","Color","Quantity"])
            inv_df = pd.concat([inv_df, new_row], ignore_index=True)
    return save_inventory(inv_df)

def add_inventory(ptype, size, color, qty, user="system"):
    inv_df = load_inventory()
    mask = (inv_df["ProductType"]==ptype) & (inv_df["Size"]==size) & (inv_df["Color"]==color)
    if mask.any():
        idx = inv_df[mask].index[0]
        inv_df.loc[idx,"Quantity"] += qty
    else:
        new_row = pd.DataFrame([[ptype,size,color,qty]], columns=["ProductType","Size","Color","Quantity"])
        inv_df = pd.concat([inv_df, new_row], ignore_index=True)
    return save_inventory(inv_df)

def delete_inventory_row(ptype, size, color, user="system"):
    inv_df = load_inventory()
    mask = (inv_df["ProductType"]==ptype) & (inv_df["Size"]==size) & (inv_df["Color"]==color)
    if mask.any():
        inv_df = inv_df[~mask]
        return save_inventory(inv_df)
    return False

# ====================================================
# ------------------- توابع مشتریان -------------------
# ====================================================
@st.cache_data(ttl=60, show_spinner=False)
def load_customers():
    if not os.path.exists(CUSTOMERS_DB):
        return pd.DataFrame(columns=["Name","Address","Phone","Province"])
    df = pd.read_csv(CUSTOMERS_DB, on_bad_lines='skip', encoding='utf-8-sig')
    for col in ["Name","Address","Phone","Province"]:
        if col not in df.columns:
            df[col] = ""
    return df

def save_customer(name, address, phone, province, user="system"):
    df = load_customers()
    name = name.strip().replace('ك','ک').replace('ي','ی')
    if name in df["Name"].values:
        df.loc[df["Name"]==name, ["Address","Phone","Province"]] = [address, phone, province]
    else:
        new_row = pd.DataFrame([[name,address,phone,province]], columns=["Name","Address","Phone","Province"])
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CUSTOMERS_DB, index=False, encoding='utf-8-sig')
    st.cache_data.clear()
    log_action("INFO", f"مشتری '{name}' ذخیره شد", user)
    return True

def delete_customer(name, user="system"):
    """حذف مشتری از دیتابیس"""
    df = load_customers()
    name = name.strip()
    if name not in df["Name"].values:
        return False, "مشتری یافت نشد"
    df = df[df["Name"] != name]
    df.to_csv(CUSTOMERS_DB, index=False, encoding='utf-8-sig')
    st.cache_data.clear()
    log_action("WARNING", f"مشتری '{name}' حذف شد", user)
    return True, "مشتری با موفقیت حذف شد"

# ====================================================
# ------------------- توابع سفارش -------------------
# ====================================================
def save_order(invoice_no, date, customer_name, items_df, issuer, description="", sale_type=""):
    to_save = items_df.copy()
    to_save["InvoiceNo"]   = invoice_no
    to_save["Date"]        = date
    to_save["Customer"]    = customer_name
    to_save["SaleType"]    = sale_type
    to_save["Issuer"]      = issuer
    to_save["Description"] = description
    if not os.path.exists(ORDERS_DB):
        to_save.to_csv(ORDERS_DB, index=False, encoding='utf-8-sig')
    else:
        to_save.to_csv(ORDERS_DB, mode='a', header=False, index=False, encoding='utf-8-sig')
    log_action("INFO", f"فاکتور {invoice_no} ثبت شد", issuer)
    st.cache_data.clear()
    return True

@st.cache_data(ttl=60, show_spinner=False)
def load_orders():
    if not os.path.exists(ORDERS_DB):
        return pd.DataFrame()
    df = pd.read_csv(ORDERS_DB, encoding='utf-8-sig')
    if "Description" not in df.columns:
        df["Description"] = ""
    return df

def delete_invoice(invoice_no, user="system"):
    """
    حذف فاکتور و بازگردانی موجودی.
    فقط یک‌بار restore صدا می‌زند.
    """
    df = load_orders()
    if df.empty:
        return False, "فاکتوری وجود ندارد"
    mask = df["InvoiceNo"] == invoice_no
    if not mask.any():
        return False, "فاکتور یافت نشد"
    deleted_rows = df[mask].copy()
    # بازگردانی موجودی
    restore_cols = ["ProductType","Size","Color","Quantity"]
    cart_to_restore = deleted_rows[restore_cols].copy()
    cart_to_restore["Quantity"] = cart_to_restore["Quantity"].astype(int)
    if not restore_inventory_after_deletion(cart_to_restore, user):
        return False, "خطا در بازگردانی موجودی"
    # حذف از CSV
    new_df = df[~mask]
    new_df.to_csv(ORDERS_DB, index=False, encoding='utf-8-sig')
    st.cache_data.clear()
    log_action("WARNING", f"فاکتور {invoice_no} حذف شد", user)
    return True, "فاکتور با موفقیت حذف شد"

def edit_invoice(invoice_no, new_cart, new_customer, new_address, new_phone, new_province, new_desc, user):
    """
    ویرایش فاکتور:
    1) موجودی قدیم را برمی‌گردانیم (بدون حذف از CSV)
    2) ردیف‌های قدیمی را از CSV حذف می‌کنیم
    3) فاکتور جدید را ثبت می‌کنیم
    4) موجودی جدید کسر می‌شود
    """
    old_df = load_orders()
    old_items = old_df[old_df["InvoiceNo"] == invoice_no]
    if old_items.empty:
        return False, "فاکتور اصلی یافت نشد"

    # مرحله ۱: بازگردانی موجودی قدیم
    old_cart = old_items[["ProductType","Size","Color","Quantity"]].copy()
    old_cart["Quantity"] = old_cart["Quantity"].astype(int)
    if not restore_inventory_after_deletion(old_cart, user):
        return False, "خطا در بازگردانی موجودی"

    # مرحله ۲: حذف ردیف‌های قدیمی مستقیماً از CSV (بدون restore مجدد)
    new_df = old_df[old_df["InvoiceNo"] != invoice_no]
    new_df.to_csv(ORDERS_DB, index=False, encoding='utf-8-sig')
    st.cache_data.clear()

    # مرحله ۳: ذخیره مشتری و فاکتور جدید
    save_customer(new_customer, new_address, new_phone, new_province, user)
    tehran = ZoneInfo("Asia/Tehran")
    inv_date = jdatetime.datetime.fromgregorian(datetime=datetime.now(tehran)).strftime("%Y/%m/%d %H:%M")
    if not save_order(invoice_no, inv_date, new_customer, new_cart, user, description=new_desc):
        return False, "خطا در ثبت فاکتور جدید"

    # مرحله ۴: کسر موجودی جدید
    if not update_inventory_after_order(new_cart, user):
        # rollback: حذف فاکتوری که تازه ثبت شد
        df2 = load_orders()
        df2[df2["InvoiceNo"] != invoice_no].to_csv(ORDERS_DB, index=False, encoding='utf-8-sig')
        st.cache_data.clear()
        return False, "موجودی کافی نیست"

    log_action("INFO", f"فاکتور {invoice_no} ویرایش شد", user)
    return True, "فاکتور با موفقیت ویرایش شد"

# ====================================================
# ------------------- توابع PDF -------------------
# ====================================================
def _download_font(url, dest):
    if os.path.exists(dest): return True
    try:
        import requests
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        r = requests.get(url, stream=True, timeout=30)
        if r.status_code == 200:
            with open(dest,'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except: pass
    return False

def _reshape_persian(text):
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text))
    except:
        return text

def format_rial(amount):
    return f"{amount:,.0f}"

def format_toman(amount_rial):
    return f"{amount_rial//10:,.0f}"

def generate_invoice_pdf(invoice_no, inv_date, customer_name, phone, address,
                         province, issuer, cart_df, total_invoice, description=""):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT

    font_dir = "fonts"
    os.makedirs(font_dir, exist_ok=True)
    regular_path = os.path.join(font_dir,"Vazirmatn-Regular.ttf")
    bold_path    = os.path.join(font_dir,"Vazirmatn-Bold.ttf")
    if not os.path.exists(regular_path):
        _download_font("https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/Vazirmatn-Regular.ttf", regular_path)
    if not os.path.exists(bold_path):
        _download_font("https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/Vazirmatn-Bold.ttf", bold_path)

    FONT_NAME = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"
    try:
        if os.path.exists(regular_path):
            pdfmetrics.registerFont(TTFont("Vazir", regular_path))
            FONT_NAME = "Vazir"
        if os.path.exists(bold_path):
            pdfmetrics.registerFont(TTFont("Vazir-Bold", bold_path))
            FONT_BOLD = "Vazir-Bold"
    except: pass

    def P(text, size=10, bold=False, align=TA_RIGHT, color=colors.black):
        fn = FONT_BOLD if bold else FONT_NAME
        style = ParagraphStyle(name='p', fontName=fn, fontSize=size, textColor=color,
                               alignment=align, leading=size*1.5)
        return Paragraph(_reshape_persian(str(text)), style)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    story = []
    logo_cell = Image(LOGO_FILE, width=3*cm, height=3*cm) if os.path.exists(LOGO_FILE) else P("👕",20,align=TA_CENTER)
    title = [P("فاکتور فروش",18,bold=True,align=TA_CENTER,color=colors.HexColor("#1B4F8A")),
             P("Sarmo",11,align=TA_CENTER,color=colors.HexColor("#555555"))]
    header = Table([[logo_cell,title,""]], colWidths=[3*cm,None,3*cm])
    header.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(1,0),(1,0),'CENTER')]))
    story.append(header)
    story.append(HRFlowable(width="100%",thickness=2,color=colors.HexColor("#1B4F8A")))
    story.append(Spacer(1,0.3*cm))
    inv_info = [[P(f"شماره: {invoice_no}",9,bold=True), P(f"تاریخ: {inv_date}",9,bold=True)],
                [P(f"ثبت کننده: {issuer}",9), P("",9)]]
    inv_table = Table(inv_info, colWidths=[None,None])
    inv_table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor("#d6eaf8")),
                                   ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#aed6f1"))]))
    story.append(inv_table)
    story.append(Spacer(1,0.3*cm))
    story.append(P("اطلاعات مشتری",12,bold=True,color=colors.HexColor("#1B4F8A")))
    cust_info = [[P(f"نام: {customer_name}",10,bold=True), P(f"استان: {province}",10)],
                 [P(f"تلفن: {phone}",10),               P(f"آدرس: {address}",10)]]
    cust_table = Table(cust_info, colWidths=[None,None])
    cust_table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#aed6f1"))]))
    story.append(cust_table)
    story.append(Spacer(1,0.4*cm))
    story.append(P("اقلام سفارش",12,bold=True,color=colors.HexColor("#1B4F8A")))
    items_header = [P(h,10,bold=True,align=TA_CENTER) for h in ["ردیف","نوع","سایز","رنگ","تعداد","فی (ریال)","جمع (ریال)"]]
    items_data = [items_header]
    for i, row in cart_df.iterrows():
        items_data.append([
            P(str(i+1),9,align=TA_CENTER), P(row["ProductType"],9,align=TA_CENTER),
            P(row["Size"],9,align=TA_CENTER), P(row["Color"],9,align=TA_CENTER),
            P(str(int(row["Quantity"])),9,align=TA_CENTER),
            P(format_rial(row["UnitPrice"]),9,align=TA_CENTER),
            P(format_rial(row["TotalPrice"]),9,align=TA_CENTER)
        ])
    items_data.append(["","","","","",
                       P("جمع کل:",10,bold=True,align=TA_CENTER),
                       P(format_rial(total_invoice),10,bold=True,align=TA_CENTER,color=colors.HexColor("#C0392B"))])
    col_w = [1*cm,3*cm,2*cm,2.5*cm,1.8*cm,2.5*cm,3*cm]
    items_table = Table(items_data, colWidths=col_w, repeatRows=1)
    items_table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#1B4F8A")),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-2),0.5,colors.HexColor("#aed6f1")),
        ('LINEABOVE',(0,-1),(-1,-1),1.5,colors.HexColor("#1B4F8A")),
        ('ROWBACKGROUNDS',(0,1),(-1,-2),[colors.white,colors.HexColor("#eaf4fb")]),
        ('BACKGROUND',(0,-1),(-1,-1),colors.HexColor("#d5f5e3"))
    ]))
    story.append(items_table)
    story.append(Spacer(1,0.3*cm))
    if description.strip():
        story.append(P("توضیحات:",10,bold=True,color=colors.HexColor("#1B4F8A")))
        story.append(P(description,10,align=TA_RIGHT))
        story.append(Spacer(1,0.3*cm))
    from reportlab.lib.styles import ParagraphStyle as PS
    story.append(Paragraph(_reshape_persian("با تشکر از شما"),
                           PS(name='thanks',fontName=FONT_NAME,fontSize=10,alignment=TA_CENTER)))
    story.append(Spacer(1,0.3*cm))
    story.append(HRFlowable(width="100%",thickness=0.5,color=colors.grey))
    doc.build(story)
    return buf.getvalue()

# ====================================================
# ------------------- هدر اصلی -------------------
# ====================================================
role_display = "مدیر فروش" if st.session_state.username=="sara" else ("مدیر" if st.session_state.role=="admin" else "ویزیتور")

orders_data = load_orders()
orders_cnt  = orders_data["InvoiceNo"].nunique() if not orders_data.empty else 0
cust_cnt    = len(load_customers())
inv_total   = load_inventory()["Quantity"].sum() if not load_inventory().empty else 0

_dm_icon  = "☀️ روشن" if st.session_state.dark_mode else "🌙 تاریک"

# هدر
st.markdown(f"""
<div class="sarmo-header">
    <div style="font-size:2rem;">👕</div>
    <div>
        <p class="sarmo-title">Sarmo</p>
        <p class="sarmo-subtitle">سامانه مدیریت فروش پوشاک</p>
    </div>
    <div style="margin-right: auto; display:flex; align-items:center; gap:12px;">
        <div style="text-align:left;">
            <div style="color:rgba(255,255,255,0.8); font-size:0.8rem;">کاربر فعال</div>
            <div style="color:#fff; font-weight:700; font-size:1rem;">{st.session_state.username}</div>
        </div>
        <div style="background:rgba(255,255,255,0.18); border-radius:8px; padding:4px 12px;
                    color:#fff; font-size:0.8rem; font-weight:600;">{role_display}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# کارت‌های آمار + دکمه‌های خروج و تم
c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
with c1:
    st.markdown(f"""<div class="stat-card">
        <div class="stat-icon">👥</div>
        <p class="stat-val">{cust_cnt}</p>
        <p class="stat-label">تعداد مشتریان</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="stat-card">
        <div class="stat-icon">🧾</div>
        <p class="stat-val">{orders_cnt}</p>
        <p class="stat-label">فاکتورهای صادر شده</p>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="stat-card">
        <div class="stat-icon">📦</div>
        <p class="stat-val">{inv_total}</p>
        <p class="stat-label">موجودی انبار</p>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown("<div style='padding-top:12px;'>", unsafe_allow_html=True)
    st.markdown('<div class="dark-toggle-btn">', unsafe_allow_html=True)
    if st.button(_dm_icon, use_container_width=True, key="toggle_theme"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
with c5:
    st.markdown("<div style='padding-top:12px;'>", unsafe_allow_html=True)
    if st.button("🚪 خروج از سامانه", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ====================================================
# ------------------- تب‌ها -------------------
# ====================================================
tabs_list = ["🛒 ثبت سفارش", "📄 فاکتورها", "👥 مشتریان", "📤 گزارش", "📦 انبار"]
if st.session_state.role == "admin":
    tabs_list.append("🔒 لاگ سیستم")
tabs = st.tabs(tabs_list)
tab1, tab2, tab3, tab4, tab5 = tabs[0], tabs[1], tabs[2], tabs[3], tabs[4]
tab6 = tabs[5] if len(tabs) > 5 else None

# ====================================================
# ==================== تب ۱: ثبت سفارش ==============
# ====================================================
with tab1:
    if st.session_state.edit_mode:
        st.markdown(f"""<div class="edit-banner">
            ✏️ در حال ویرایش فاکتور شماره <strong>{st.session_state.edit_invoice_no}</strong>
        </div>""", unsafe_allow_html=True)
        if st.button("❌ انصراف از ویرایش", use_container_width=True):
            st.session_state.edit_mode = False
            st.session_state.edit_invoice_no = None
            st.session_state.edit_cart = None
            st.session_state.edit_notes = ""
            st.session_state.edit_customer_data = {}
            st.rerun()

    # ---- اطلاعات مشتری ----
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👤 اطلاعات مشتری</div>', unsafe_allow_html=True)

    customers_df = load_customers()
    existing = customers_df["Name"].tolist()
    search_mode = st.radio("وضعیت مشتری:", ["مشتری جدید","جستجوی مشتری قدیم"],
                           horizontal=True, key="cust_mode")

    name_input = address_input = phone_input = ""
    province_input = "تهران"
    provinces = ["تهران","اصفهان","خراسان رضوی","فارس","خوزستان",
                 "آذربایجان شرقی","مازندران","گیلان","البرز","قم"]

    if search_mode == "جستجوی مشتری قدیم" and not st.session_state.edit_mode:
        search_q = st.text_input("🔍 جستجوی نام مشتری:", placeholder="بخشی از نام را تایپ کنید...")
        filtered_names = [n for n in existing if search_q.lower() in n.lower()] if search_q else existing
        sel = st.selectbox("انتخاب مشتری:", [""] + filtered_names)
        if sel:
            c = customers_df[customers_df["Name"]==sel].iloc[0]
            name_input, address_input, phone_input, province_input = sel, c["Address"], c["Phone"], c["Province"]

    if st.session_state.edit_mode and st.session_state.edit_customer_data:
        name_input     = st.session_state.edit_customer_data.get("name","")
        address_input  = st.session_state.edit_customer_data.get("address","")
        phone_input    = st.session_state.edit_customer_data.get("phone","")
        province_input = st.session_state.edit_customer_data.get("province","تهران")

    col1, col2 = st.columns(2)
    with col1:
        final_name = st.text_input("نام و نام خانوادگی *", value=name_input, placeholder="مثال: علی محمدی")
        province   = st.selectbox("استان *", provinces,
                                  index=provinces.index(province_input) if province_input in provinces else 0)
    with col2:
        phone   = st.text_input("شماره تلفن", value=phone_input, placeholder="۰۹۱۲...")
    address = st.text_area("آدرس *", value=address_input, placeholder="آدرس کامل...", height=90)
    invoice_desc = st.text_area("📝 توضیحات فاکتور (اختیاری):",
                                value=st.session_state.edit_notes if st.session_state.edit_mode else "",
                                height=70, placeholder="هر توضیحی که لازم است...")
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- اقلام سفارش ----
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📦 اقلام سفارش</div>', unsafe_allow_html=True)

    if st.session_state.edit_mode and st.session_state.edit_cart is not None:
        cart = st.session_state.edit_cart
    else:
        if 'cart' not in st.session_state:
            st.session_state.cart = []
        cart = st.session_state.cart

    product_types = ["تیشرت","هودی","دورس","متفرقه"]
    sizes = ["S","M","L","XL","XXL"]

    with st.expander("➕ افزودن کالا به سبد", expanded=True):
        c1, c2, c3, c4 = st.columns([2,1,2,2])
        with c1: ptype = st.selectbox("نوع:", product_types, key="pt")
        with c2: size  = st.selectbox("سایز:", sizes, key="sz")
        with c3: color = st.selectbox("رنگ:", COLORS_LIST, key="cl")
        with c4: qty   = st.number_input("تعداد:", 1, step=1, key="qt")

        # نمایش موجودی لحظه‌ای
        inv_df_check = load_inventory()
        m_check = (inv_df_check["ProductType"]==ptype) & (inv_df_check["Size"]==size) & (inv_df_check["Color"]==color)
        stock_now = int(inv_df_check[m_check]["Quantity"].sum()) if m_check.any() else 0
        if stock_now > 0:
            st.caption(f"✅ موجودی انبار: **{stock_now}** عدد")
        else:
            st.caption(f"❌ موجودی انبار: **صفر**")

        price = st.number_input("فی (ریال):", 0, step=1000, key="pr")
        if price > 0:
            st.caption(f"💰 معادل تومان: **{format_toman(price):}** تومان")

        if st.button("➕ افزودن به سبد", use_container_width=True, type="primary"):
            if qty <= 0:
                st.error("تعداد باید بیشتر از صفر باشد")
            elif price <= 0:
                st.error("قیمت را وارد کنید")
            elif qty > stock_now:
                st.error(f"موجودی کافی نیست (فقط {stock_now} عدد موجود)")
            else:
                cart.append({"ProductType":ptype,"Size":size,"Color":color,
                             "Quantity":qty,"UnitPrice":price,"TotalPrice":qty*price})
                if st.session_state.edit_mode:
                    st.session_state.edit_cart = cart
                else:
                    st.session_state.cart = cart
                st.toast(f"✅ {ptype} {size} {color} اضافه شد")

    if cart:
        cart_df = pd.DataFrame(cart)
        disp = cart_df[["ProductType","Size","Color","Quantity","UnitPrice","TotalPrice"]].copy()
        disp["UnitPrice_Toman"]  = disp["UnitPrice"]//10
        disp["TotalPrice_Toman"] = disp["TotalPrice"]//10
        disp.columns = ["نوع","سایز","رنگ","تعداد","فی (ریال)","جمع (ریال)","فی (تومان)","جمع (تومان)"]
        for col_f in ["فی (ریال)","جمع (ریال)","فی (تومان)","جمع (تومان)"]:
            disp[col_f] = disp[col_f].apply(lambda x: f"{x:,.0f}")
        st.dataframe(disp, use_container_width=True, hide_index=True)

        col_del1, col_del2 = st.columns([2,1])
        with col_del1:
            del_idx = st.number_input("شماره ردیف برای حذف:", 1, len(cart), 1, key="del_row")
        with col_del2:
            st.markdown("<div style='padding-top:28px;'>", unsafe_allow_html=True)
            if st.button("🗑️ حذف ردیف", use_container_width=True):
                cart.pop(del_idx-1)
                if st.session_state.edit_mode:
                    st.session_state.edit_cart = cart
                else:
                    st.session_state.cart = cart
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        total = cart_df["TotalPrice"].sum()
        mc1, mc2 = st.columns(2)
        with mc1: st.metric("💰 جمع کل (ریال)", f"{format_rial(total)} ﷼")
        with mc2: st.metric("💰 جمع کل (تومان)", f"{format_toman(total)} تومان")

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            btn_label = "✅ ذخیره ویرایش" if st.session_state.edit_mode else "✅ ثبت نهایی فاکتور"
            if st.button(btn_label, type="primary", use_container_width=True):
                if not final_name.strip():
                    st.error("نام مشتری الزامی است")
                elif not address.strip():
                    st.error("آدرس مشتری الزامی است")
                else:
                    if not st.session_state.edit_mode:
                        inv_df2 = load_inventory()
                        ok = True
                        for item in cart:
                            msk = (inv_df2["ProductType"]==item["ProductType"]) & \
                                  (inv_df2["Size"]==item["Size"]) & \
                                  (inv_df2["Color"]==item["Color"])
                            if not msk.any() or inv_df2[msk].iloc[0]["Quantity"] < item["Quantity"]:
                                st.error(f"موجودی ناکافی: {item['ProductType']} {item['Size']} {item['Color']}")
                                ok = False
                                break
                        if not ok: st.stop()

                    tehran   = ZoneInfo("Asia/Tehran")
                    inv_date = jdatetime.datetime.fromgregorian(datetime=datetime.now(tehran)).strftime("%Y/%m/%d %H:%M")

                    if st.session_state.edit_mode:
                        inv_no = st.session_state.edit_invoice_no
                        success, msg = edit_invoice(inv_no, cart_df, final_name, address, phone,
                                                    province, invoice_desc.strip(), st.session_state.username)
                        if success:
                            st.success(msg)
                            st.session_state.edit_mode = False
                            st.session_state.edit_invoice_no = None
                            st.session_state.edit_cart = None
                            st.session_state.edit_notes = ""
                            st.session_state.edit_customer_data = {}
                            st.session_state.cart = []
                            save_session()
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        inv_no   = int(time.time())
                        ok_cust  = save_customer(final_name, address, phone, province, st.session_state.username)
                        ok_order = save_order(inv_no, inv_date, final_name, cart_df,
                                             st.session_state.username, description=invoice_desc.strip())
                        ok_inv   = update_inventory_after_order(cart_df, st.session_state.username)
                        if ok_cust and ok_order and ok_inv:
                            st.success(f"✅ فاکتور شماره {inv_no} با موفقیت ثبت شد")
                            pdf = generate_invoice_pdf(inv_no, inv_date, final_name, phone, address, province,
                                                      st.session_state.username, cart_df, total, invoice_desc.strip())
                            st.download_button("⬇️ دانلود PDF فاکتور", data=pdf,
                                              file_name=f"invoice_{inv_no}.pdf", mime="application/pdf")
                            st.session_state.cart = []
                            save_session()
                            st.rerun()
                        else:
                            st.error("خطا در ثبت فاکتور")
        with col_btn2:
            if st.button("🗑️ پاک کردن سبد", use_container_width=True):
                if st.session_state.edit_mode:
                    st.session_state.edit_cart = []
                else:
                    st.session_state.cart = []
                st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center; padding:30px; color:#5A6E88;">
            <div style="font-size:2.5rem; margin-bottom:10px;">🛒</div>
            <p>سبد خرید خالی است. کالا اضافه کنید.</p>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ====================================================
# ==================== تب ۲: فاکتورها ===============
# ====================================================
with tab2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📄 فاکتورهای صادر شده</div>', unsafe_allow_html=True)
    orders = load_orders()
    if orders.empty:
        st.markdown("""<div style="text-align:center; padding:30px; color:#5A6E88;">
            <div style="font-size:2.5rem;">🧾</div><p>هیچ فاکتوری ثبت نشده است.</p>
        </div>""", unsafe_allow_html=True)
    else:
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            custs = ["همه"] + sorted(orders["Customer"].dropna().unique())
            filter_cust = st.selectbox("🔍 فیلتر مشتری:", custs)
        with col_f2:
            issuers = ["همه"] + sorted(orders["Issuer"].dropna().unique())
            filter_iss = st.selectbox("👤 فیلتر ثبت کننده:", issuers)
        with col_f3:
            search_inv = st.text_input("🔢 جستجوی شماره فاکتور:", placeholder="شماره فاکتور...")

        filtered = orders.copy()
        if filter_cust != "همه":
            filtered = filtered[filtered["Customer"] == filter_cust]
        if filter_iss != "همه":
            filtered = filtered[filtered["Issuer"] == filter_iss]
        if search_inv.strip():
            try:
                filtered = filtered[filtered["InvoiceNo"].astype(str).str.contains(search_inv.strip())]
            except: pass

        total_sum = filtered["TotalPrice"].astype(float).sum() if "TotalPrice" in filtered else 0
        st.metric("💰 مجموع فروش فیلترشده", f"{format_rial(total_sum)} ﷼")
        st.divider()

        unique_invoices = filtered["InvoiceNo"].dropna().unique()
        if len(unique_invoices) == 0:
            st.info("فاکتوری با این فیلتر یافت نشد.")

        for inv in unique_invoices:
            rows = filtered[filtered["InvoiceNo"] == inv]
            if rows.empty: continue
            first_row     = rows.iloc[0]
            customer_name = first_row.get("Customer","نامشخص")
            inv_date      = first_row.get("Date","تاریخ نامشخص")
            issuer_name   = first_row.get("Issuer","نامشخص")
            description_text = first_row.get("Description","")
            total_amount  = rows["TotalPrice"].astype(float).sum()

            with st.expander(f"🧾 #{inv}  |  {customer_name}  |  {inv_date}  |  {format_rial(total_amount)} ﷼"):
                ci1, ci2 = st.columns(2)
                with ci1:
                    st.write(f"**ثبت کننده:** {issuer_name}")
                with ci2:
                    if description_text:
                        st.write(f"**📝 توضیحات:** {description_text}")

                items = rows[["ProductType","Size","Color","Quantity","UnitPrice","TotalPrice"]].copy()
                items["UnitPrice"]  = items["UnitPrice"].apply(lambda x: format_rial(float(x)) if pd.notna(x) else "")
                items["TotalPrice"] = items["TotalPrice"].apply(lambda x: format_rial(float(x)) if pd.notna(x) else "")
                items.columns = ["نوع","سایز","رنگ","تعداد","فی","جمع"]
                st.dataframe(items, use_container_width=True, hide_index=True)
                st.markdown(f"**💰 مجموع: {format_rial(total_amount)} ریال**")

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button("📄 PDF", key=f"pdf_{inv}", use_container_width=True):
                        try:
                            cust = load_customers()
                            cust_row = cust[cust["Name"]==customer_name]
                            ph   = cust_row["Phone"].iloc[0]   if not cust_row.empty else ""
                            addr = cust_row["Address"].iloc[0] if not cust_row.empty else ""
                            prov = cust_row["Province"].iloc[0] if not cust_row.empty else "تهران"
                            cart_pdf = rows[["ProductType","Size","Color","Quantity","UnitPrice","TotalPrice"]].copy()
                            pdf = generate_invoice_pdf(inv, inv_date, customer_name, ph, addr, prov,
                                                      issuer_name, cart_pdf, total_amount, description_text)
                            st.download_button("⬇️ دانلود", data=pdf, file_name=f"invoice_{inv}.pdf",
                                              mime="application/pdf", key=f"down_{inv}")
                        except Exception as e:
                            st.error(f"خطا در PDF: {e}")

                with col_b:
                    if st.button("✏️ ویرایش", key=f"edit_{inv}", use_container_width=True):
                        edit_cart = []
                        for _, r in rows.iterrows():
                            edit_cart.append({
                                "ProductType": r["ProductType"], "Size": r["Size"], "Color": r["Color"],
                                "Quantity": int(r["Quantity"]), "UnitPrice": float(r["UnitPrice"]),
                                "TotalPrice": float(r["TotalPrice"])
                            })
                        cust_df = load_customers()
                        c_info  = cust_df[cust_df["Name"]==customer_name]
                        if not c_info.empty:
                            st.session_state.edit_customer_data = {
                                "name": customer_name, "address": c_info.iloc[0]["Address"],
                                "phone": c_info.iloc[0]["Phone"], "province": c_info.iloc[0]["Province"]
                            }
                        else:
                            st.session_state.edit_customer_data = {
                                "name": customer_name, "address":"", "phone":"", "province":"تهران"
                            }
                        st.session_state.edit_mode       = True
                        st.session_state.edit_invoice_no = inv
                        st.session_state.edit_cart       = edit_cart
                        st.session_state.edit_notes      = description_text
                        st.rerun()

                with col_c:
                    if st.session_state.role == "admin":
                        # --- FIX: استفاده از session_state برای تأیید حذف ---
                        confirm_key = f"del_confirm_{inv}"
                        if confirm_key not in st.session_state:
                            st.session_state[confirm_key] = False

                        if not st.session_state[confirm_key]:
                            if st.button("🗑️ حذف", key=f"del_{inv}", use_container_width=True):
                                st.session_state[confirm_key] = True
                                st.rerun()
                        else:
                            st.warning("مطمئنید؟")
                            ca, cb = st.columns(2)
                            with ca:
                                if st.button("✅ بله، حذف شود", key=f"conf_yes_{inv}", use_container_width=True):
                                    success, msg = delete_invoice(inv, st.session_state.username)
                                    st.session_state[confirm_key] = False
                                    if success:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                            with cb:
                                if st.button("❌ انصراف", key=f"conf_no_{inv}", use_container_width=True):
                                    st.session_state[confirm_key] = False
                                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ====================================================
# ==================== تب ۳: مشتریان ================
# ====================================================
with tab3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👥 مدیریت مشتریان</div>', unsafe_allow_html=True)

    cust_all = load_customers()

    # جستجو
    cust_search = st.text_input("🔍 جستجوی مشتری:", placeholder="نام، تلفن یا استان...")
    if cust_search:
        mask_search = (
            cust_all["Name"].str.contains(cust_search, case=False, na=False) |
            cust_all["Phone"].astype(str).str.contains(cust_search, case=False, na=False) |
            cust_all["Province"].str.contains(cust_search, case=False, na=False)
        )
        cust_display = cust_all[mask_search]
    else:
        cust_display = cust_all

    if not cust_display.empty:
        st.dataframe(
            cust_display.rename(columns={"Name":"نام","Address":"آدرس","Phone":"تلفن","Province":"استان"}),
            use_container_width=True, hide_index=True
        )
        st.caption(f"تعداد مشتریان: {len(cust_display)}")
    else:
        st.info("مشتری‌ای یافت نشد")

    # --- حذف مشتری (فقط ادمین) ---
    if st.session_state.role == "admin":
        st.divider()
        st.markdown('<div class="section-title" style="font-size:0.95rem;">🗑️ حذف مشتری</div>', unsafe_allow_html=True)
        st.warning("⚠️ حذف مشتری تنها اطلاعات پروفایل او را پاک می‌کند و فاکتورهایش باقی می‌ماند.")

        all_names = cust_all["Name"].tolist()
        del_search = st.text_input("جستجو برای حذف:", placeholder="نام مشتری...", key="del_cust_search")
        filtered_for_del = [n for n in all_names if del_search.lower() in n.lower()] if del_search else all_names

        if filtered_for_del:
            cust_to_delete = st.selectbox("انتخاب مشتری برای حذف:", [""] + filtered_for_del, key="cust_del_sel")
            if cust_to_delete:
                if "del_cust_confirm" not in st.session_state:
                    st.session_state.del_cust_confirm = False

                if not st.session_state.del_cust_confirm:
                    if st.button(f"🗑️ حذف «{cust_to_delete}»", use_container_width=True):
                        st.session_state.del_cust_confirm = True
                        st.rerun()
                else:
                    st.error(f"آیا از حذف مشتری «{cust_to_delete}» مطمئنید؟")
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        if st.button("✅ بله، حذف شود", use_container_width=True, key="cust_del_yes"):
                            ok, msg = delete_customer(cust_to_delete, st.session_state.username)
                            st.session_state.del_cust_confirm = False
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                    with dc2:
                        if st.button("❌ انصراف", use_container_width=True, key="cust_del_no"):
                            st.session_state.del_cust_confirm = False
                            st.rerun()
        else:
            st.info("مشتری‌ای با این نام یافت نشد")
    st.markdown('</div>', unsafe_allow_html=True)

# ====================================================
# ==================== تب ۴: گزارش ==================
# ====================================================
with tab4:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📤 خروجی و گزارش</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📄 فاکتورها")
        orders_exp = load_orders()
        if not orders_exp.empty:
            csv_orders = orders_exp.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("⬇️ دانلود CSV فاکتورها", data=csv_orders,
                              file_name=f"orders_{jdatetime.date.today()}.csv", mime="text/csv")
            total_all = orders_exp["TotalPrice"].astype(float).sum() if "TotalPrice" in orders_exp else 0
            st.info(f"مجموع کل فروش: **{format_rial(total_all)}** ریال")
            if "Customer" in orders_exp and "TotalPrice" in orders_exp:
                chart = orders_exp.groupby("Customer")["TotalPrice"].sum().astype(float)\
                        .sort_values(ascending=False).head(10)
                st.bar_chart(chart)
        else:
            st.info("فاکتوری وجود ندارد")
    with col2:
        st.subheader("👥 مشتریان")
        cust_exp = load_customers()
        if not cust_exp.empty:
            csv_cust = cust_exp.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("⬇️ دانلود CSV مشتریان", data=csv_cust,
                              file_name=f"customers_{jdatetime.date.today()}.csv", mime="text/csv")
            st.dataframe(
                cust_exp.rename(columns={"Name":"نام","Address":"آدرس","Phone":"تلفن","Province":"استان"}),
                use_container_width=True, hide_index=True
            )
        else:
            st.info("مشتری ثبت نشده")
    st.markdown('</div>', unsafe_allow_html=True)

# ====================================================
# ==================== تب ۵: انبار ==================
# ====================================================
with tab5:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📦 مدیریت انبار</div>', unsafe_allow_html=True)
    inv_df = load_inventory()
    if not inv_df.empty:
        with st.expander("🔍 فیلترها", expanded=False):
            f_type  = st.selectbox("نوع", ["همه"] + sorted(inv_df["ProductType"].unique()))
            f_size  = st.selectbox("سایز", ["همه"] + sorted(inv_df["Size"].unique()))
            f_color = st.text_input("رنگ (اختیاری)")
        filtered_inv = inv_df.copy()
        if f_type  != "همه": filtered_inv = filtered_inv[filtered_inv["ProductType"]==f_type]
        if f_size  != "همه": filtered_inv = filtered_inv[filtered_inv["Size"]==f_size]
        if f_color: filtered_inv = filtered_inv[filtered_inv["Color"].str.contains(f_color,case=False,na=False)]

        st.info("✏️ برای ویرایش تعداد، روی سلول کلیک کرده و سپس «ذخیره تغییرات» را بزنید")
        edited = st.data_editor(
            filtered_inv.rename(columns={"ProductType":"نوع","Size":"سایز","Color":"رنگ","Quantity":"تعداد"}),
            column_config={
                "نوع":    st.column_config.TextColumn(disabled=True),
                "سایز":   st.column_config.TextColumn(disabled=True),
                "رنگ":    st.column_config.TextColumn(disabled=True),
                "تعداد":  st.column_config.NumberColumn(min_value=0, step=1),
            },
            use_container_width=True, hide_index=True
        )
        col_save, col_del = st.columns(2)
        with col_save:
            if st.button("💾 ذخیره تغییرات", use_container_width=True, type="primary"):
                edited.rename(columns={"نوع":"ProductType","سایز":"Size","رنگ":"Color","تعداد":"Quantity"}, inplace=True)
                edited["Quantity"] = edited["Quantity"].fillna(0).astype(int)
                inv_orig = load_inventory()
                for _, row in edited.iterrows():
                    msk = (inv_orig["ProductType"]==row["ProductType"]) & \
                          (inv_orig["Size"]==row["Size"]) & \
                          (inv_orig["Color"]==row["Color"])
                    if msk.any():
                        inv_orig.loc[msk,"Quantity"] = row["Quantity"]
                    else:
                        inv_orig = pd.concat([inv_orig, pd.DataFrame([row])], ignore_index=True)
                if save_inventory(inv_orig):
                    st.success("تغییرات انبار ذخیره شد ✅")
                    st.rerun()
        with col_del:
            if len(filtered_inv) > 0:
                opts = [f"{r['ProductType']} - {r['Size']} - {r['Color']}" for _,r in filtered_inv.iterrows()]
                sel_del = st.selectbox("انتخاب ردیف برای حذف:", [""] + opts)
                if sel_del and st.button("🗑️ حذف ردیف انتخابی", use_container_width=True):
                    parts = sel_del.split(" - ")
                    if delete_inventory_row(parts[0], parts[1], parts[2], st.session_state.username):
                        st.success("ردیف حذف شد")
                        st.rerun()
                    else:
                        st.error("خطا در حذف")
    else:
        st.markdown("""<div style="text-align:center; padding:30px; color:#5A6E88;">
            <div style="font-size:2.5rem;">📦</div><p>انبار خالی است. از بخش زیر کالا اضافه کنید.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">➕ شارژ انبار</div>', unsafe_allow_html=True)
    with st.form("add_inv"):
        col1, col2, col3, col4 = st.columns(4)
        with col1: ptype_inv = st.selectbox("نوع", ["تیشرت","هودی","دورس","متفرقه"])
        with col2: size_inv  = st.selectbox("سایز", ["S","M","L","XL","XXL"])
        with col3: color_inv = st.selectbox("رنگ", COLORS_LIST)
        with col4: qty_inv   = st.number_input("تعداد", 1, step=1)
        if st.form_submit_button("➕ اضافه کردن به انبار", use_container_width=True, type="primary"):
            if add_inventory(ptype_inv, size_inv, color_inv, qty_inv, st.session_state.username):
                st.success(f"✅ {qty_inv} عدد {ptype_inv} {size_inv} {color_inv} اضافه شد")
                st.rerun()
            else:
                st.error("خطا در ثبت")
    st.markdown('</div>', unsafe_allow_html=True)

# ====================================================
# ==================== تب ۶: لاگ سیستم ==============
# ====================================================
if tab6 is not None:
    with tab6:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔒 لاگ سیستم</div>', unsafe_allow_html=True)
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE,"r",encoding='utf-8') as f:
                log_content = f.read()
            lines = log_content.splitlines()
            if len(lines) == 0:
                st.info("فایل لاگ خالی است.")
            else:
                # slider نیاز دارد min < max — وقتی خطوط کم است مستقیم نمایش می‌دهیم
                total_lines = len(lines)
                if total_lines > 21:
                    n = st.slider("تعداد خطوط نمایش:", 20, min(500, total_lines), min(100, total_lines))
                else:
                    n = total_lines
                    st.caption(f"تعداد کل خطوط: {total_lines}")
                level = st.multiselect("سطح لاگ:", ["INFO","WARNING","ERROR"], default=["INFO","WARNING","ERROR"])
                filtered_log = [l for l in lines if any(lv in l for lv in level)]
                st.code("\n".join(filtered_log[-n:]) if filtered_log else "هیچ رکوردی با این فیلتر یافت نشد.")
            lc1, lc2 = st.columns(2)
            with lc1:
                st.download_button("⬇️ دانلود لاگ", data=log_content,
                                  file_name=f"app_log_{datetime.now().strftime('%Y%m%d')}.txt")
            with lc2:
                if st.button("🗑️ پاک کردن لاگ", type="secondary"):
                    open(LOG_FILE,"w").close()
                    st.rerun()
        else:
            st.info("لاگی وجود ندارد")
        st.markdown('</div>', unsafe_allow_html=True)
