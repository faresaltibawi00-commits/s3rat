import streamlit as st
from groq import Groq
import base64
import json
import os

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="faress3rat",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. جلب المفتاح
API_KEY = None
if "GROQ_API_KEY" in st.secrets:
    API_KEY = str(st.secrets["GROQ_API_KEY"]).strip()

# 3. إدارة قاعدة البيانات المحلية
DB_FILE = "users_db.json"

def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users_data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)

users_db = load_users()

# 4. إدارة الجلسة الحالية
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "active_meal_type" not in st.session_state:
    st.session_state["active_meal_type"] = None
if "scanned_result" not in st.session_state:
    st.session_state["scanned_result"] = None

# 5. التنسيق والتصميم (MyFitnessPal Style)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif !important;
        background-color: #121824 !important;
        color: #f1f5f9 !important;
        direction: rtl;
        text-align: right;
    }

    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    .days-bar {
        display: flex;
        justify-content: space-between;
        background-color: #1a2232;
        padding: 12px 18px;
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid #283448;
    }
    .day-item {
        text-align: center;
        color: #64748b;
        font-size: 13px;
        font-weight: 700;
    }
    .day-item.active { color: #38ef7d; }
    .day-circle {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        border: 2px solid #334155;
        margin: 5px auto 0 auto;
    }
    .day-item.active .day-circle {
        border: 2px dashed #38ef7d;
        background-color: rgba(56, 239, 125, 0.1);
    }

    .mfp-card {
        background-color: #1a2232;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 16px;
        border: 1px solid #283448;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .mfp-title { color: #94a3b8; font-size: 15px; font-weight: 700; margin-bottom: 12px; }
    .cals-row { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
    .cals-val { font-size: 26px; font-weight: 900; color: #ffffff; }
    .cals-sub { font-size: 15px; color: #64748b; }
    .cals-left { font-size: 22px; font-weight: 900; color: #38ef7d; }

    .progress-bar-bg { background-color: #283448; border-radius: 8px; height: 8px; width: 100%; overflow: hidden; }
    .progress-bar-fill { background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%); height: 100%; border-radius: 8px; }

    .macros-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; text-align: center; }
    .macro-item-title { font-size: 13px; color: #94a3b8; font-weight: 600;
