import streamlit as st
import pandas as pd
import time
import requests

# --- إعدادات الصفحة ---
st.set_page_config(page_title="MMC Smart Maintenance", page_icon="⚙️", layout="wide")

# ==========================================
# ⚠️ إعدادات التليجرام 
# ==========================================
# امسح الكلمة اللي تحت وحط التوكن حقك بين علامات التنصيص
TELEGRAM_BOT_TOKEN = "هنا_تحط_التوكن_حقك"

# أرقام القروبات اللي أرسلتها جاهزة ومربوطة
TELEGRAM_CHATS = {
    "Al-Jumum": "-5159290787",
    "Al-Jouf": "-5176017884",
    "Khamis Mushait": "-5104633079"
}

# كلمات المرور الخاصة بمدير كل فرع
BRANCH_PASSWORDS = {
    "Al-Jumum": "Jumum123",
    "Al-Jouf": "Jouf123",
    "Khamis Mushait": "Khamis123"
}

def send_telegram_message(text, branch):
    """إرسال الإشعار مع نظام كشف الأخطاء الذكي"""
    if TELEGRAM_BOT_TOKEN == "هنا_تحط_التوكن_حقك" or not TELEGRAM_BOT_TOKEN:
        st.error("🚨 تنبيه: نسيت تحط التوكن حق البوت في الكود (السطر 12)!")
        return

    chat_id = TELEGRAM_CHATS.get(branch)
    if not chat_id:
        st.error(f"⚠️ لم يتم العثور على رقم قروب لفرع {branch}")
        return 
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            st.error(f"❌ التليجرام رفض الإرسال! تأكد إن البوت مضاف كأدمن في القروب. (كود الخطأ: {response.text})")
    except Exception as e:
        st.error(f"❌ خطأ في الاتصال بالإنترنت: {e}")

# --- تهيئة متغيرات النظام ---
if 'splash_done' not in st.session_state:
    st.session_state.splash_done = False
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}
if 'pitstop_active' not in st.session_state:
    st.session_state.pitstop_active = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# ==========================================
# 1. SPLASH SCREEN (الافتتاحية)
# ==========================================
if not st.session_state.splash_done:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 60px; color: #2E86C1;'>⚙️ MMC Smart Maintenance</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: gray;'>Modern Mills Company</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Loading System Modules & Safety Protocols...</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
    
    st.session_state.splash_done = True
    st.rerun()

# ==========================================
# 2. LOGIN SYSTEM (تسجيل الدخول)
# ==========================================
elif not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🔒 System Login")
        st.markdown("Please enter your credentials to access the MMC portal.")
        st.markdown("---")
        
        emp_name = st.text_input("👤 Full Name", placeholder="e.g., Ahmed Al-Dawsari")
        emp_id = st.text_input("💳 Employee ID", placeholder="e.g., 10452")
        
        col_a, col_b = st.columns(2)
        with col_a:
            branch = st.selectbox("🏢 Branch", ["Al-Jumum", "Al-Jouf", "Khamis Mushait"])
            role = st.selectbox("🔑 Role", ["Technician", "Manager"])
            
        with col_b:
            if role == "Technician":
                department = st.selectbox("🛠️ Department", ["Mechanical", "Electrical", "Welding", "HVAC", "Operations"])
                password = ""
            else:
                department = "Management"
                password = st.text_input("🛡️ Manager Password", type="password", placeholder=f"Password for {branch}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        remember_me = st.checkbox("💾 Remember Me (Auto-Save Login)")
        
        if st.button("Login to Workspace 🚀", type="primary", use_container_width=True):
            if not emp_name or not emp_id:
                st.error("⚠️ Please enter your Full Name and Employee ID.")
            elif role == "Manager" and password != BRANCH_PASSWORDS.get(branch): 
                st.error(f"❌ Incorrect Password for {branch} Manager!")
            else:
                st.session_state.user_info = {
                    "name": emp_name,
                    "id": emp_id,
                    "branch": branch,
                    "dept": department,
                    "role": role
                }
                st.session_state.logged_in = True
                st.toast(f"Welcome back to {branch}, {emp_name}! 🚀", icon="👋")
                time.sleep(0.5)
                st.rerun()

# ==========================================
# 3. MAIN APPLICATION (النظام الرئيسي)
# ==========================================
else:
    u_name = st.session_state.user_info['name']
    u_branch = st.session_state.user_info['branch']
    u_dept = st.session_state.user_info['dept']
    u_role = st.session_state.user_info['role']
    
    # القائمة الجانبية (Sidebar)
    st.sidebar.markdown(f"### 🏢 {u_branch} Branch")
    st.sidebar.markdown("---")
    st.sidebar.write(f"**👤 Name:** {u_name}")
    if u_role == "Technician":
        st.sidebar.write(f"**🛠️ Dept:** {u_dept}")
    st.sidebar.write(f"**🔑 Role:** {u_role}")
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # العنوان يتغير حسب المنصب
    if u_role == "Manager":
        st.title(f"⚙️ MMC Workspace - Branch Management")
    else:
        st.title(f"⚙️ MMC Workspace - {u_dept} Department")
    st.markdown("---")
    
    # الأقسام (Tabs) حسب المنصب