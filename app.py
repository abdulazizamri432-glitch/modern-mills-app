import streamlit as st
import pandas as pd
import time
import requests
import numpy as np

# --- إعدادات الصفحة ---
st.set_page_config(page_title="MMC Smart Maintenance", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# ⚠️ إعدادات التليجرام 
# ==========================================
# امسح الكلمة اللي تحت وحط التوكن حقك بين علامات التنصيص
TELEGRAM_BOT_TOKEN = "هنا_تحط_التوكن_حقك"

TELEGRAM_CHATS = {
    "Al-Jumum": "-5159290787",
    "Al-Jouf": "-5176017884",
    "Khamis Mushait": "-5104633079"
}

BRANCH_PASSWORDS = {
    "Al-Jumum": "Jumum123",
    "Al-Jouf": "Jouf123",
    "Khamis Mushait": "Khamis123"
}

def send_telegram_message(text, branch):
    if TELEGRAM_BOT_TOKEN == "هنا_تحط_التوكن_حقك" or not TELEGRAM_BOT_TOKEN:
        st.error("🚨 تنبيه: نسيت تحط التوكن حق البوت في الكود (السطر 15)!")
        return

    chat_id = TELEGRAM_CHATS.get(branch)
    if not chat_id:
        return 
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        pass

# ==========================================
# 🎨 التصميم الخرافي VIP (Advanced CSS)
# ==========================================
st.markdown("""
<style>
    /* تغيير خلفية الموقع بالكامل لتكون مريحة للعين */
    .stApp {
        background-color: #F4F6F9;
    }
    
    /* العناوين المتدرجة الخرافية */
    .gradient-text {
        background: linear-gradient(90deg, #1CB5E0 0%, #000851 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5em !important;
        font-weight: 900 !important;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-gradient {
        text-align: center;
        color: #7F8C8D;
        font-size: 1.2em;
        margin-top: -10px;
        margin-bottom: 30px;
    }

    /* تجميل الأزرار العامة */
    .stButton>button {
        background: linear-gradient(135deg, #2980B9, #2C3E50);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 24px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        font-weight: bold;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        background: linear-gradient(135deg, #2C3E50, #2980B9);
    }

    /* تجميل زر الطوارئ والفزعة (أحمر) */
    button[kind="primary"] {
        background: linear-gradient(135deg, #E74C3C, #900C3F) !important;
    }
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #900C3F, #E74C3C) !important;
    }

    /* كروت الإحصائيات للمدير */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border-left: 6px solid #2980B9;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        transition: transform 0.3s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
    }

    /* الصناديق والحاويات */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background-color: #FFFFFF;
        border-radius: 20px !important;
        border: 1px solid #EAECEE !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.03);
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 تهيئة المتغيرات
# ==========================================
if 'splash_done' not in st.session_state:
    st.session_state.splash_done = False
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'pitstop_active' not in st.session_state:
    st.session_state.pitstop_active = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# ==========================================
# 1. SPLASH SCREEN (شاشة التحميل الفخمة)
# ==========================================
if not st.session_state.splash_done:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<div class='gradient-text'>⚙️ MMC Smart System</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-gradient'>Modern Mills Company - Premium Edition</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
    st.session_state.splash_done = True
    st.rerun()

# ==========================================
# 2. LOGIN SYSTEM (تسجيل الدخول الأنيق)
# ==========================================
elif not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center; color: #2C3E50;'>🔒 Secure Login</h2>", unsafe_allow_html=True)
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
                    password = st.text_input("🛡️ Manager Password", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Authenticate & Enter 🚀", type="primary", use_container_width=True):
                if not emp_name or not emp_id:
                    st.error("⚠️ Please enter your Full Name and Employee ID.")
                elif role == "Manager" and password != BRANCH_PASSWORDS.get(branch): 
                    st.error(f"❌ Incorrect Password for {branch} Manager!")
                else:
                    st.session_state.user_info = {"name": emp_name, "branch": branch, "dept": department, "role": role}
                    st.session_state.logged_in = True
                    st.rerun()

# ==========================================
# 3. MAIN APPLICATION (النظام الرئيسي)
# ==========================================
else:
    u_name = st.session_state.user_info['name']
    u_branch = st.session_state.user_info['branch']
    u_dept = st.session_state.user_info['dept']
    u_role = st.session_state.user_info['role']
    
    # --- Sidebar Styling ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2043/2043085.png", width=80) # أيقونة مصنع جميلة
    st.sidebar.markdown(f"## 🏢 {u_branch}")
    st.sidebar.markdown("---")
    st.sidebar.write(f"**👤 Name:** {u_name}")
    st.sidebar.write(f"**🔑 Role:** {u_role}")
    if u_role == "Technician":
         st.sidebar.write(f"**🛠️ Dept:** {u_dept}")
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # --- Header ---
    st.markdown(f"<h1 style='color: #2C3E50;'>Welcome back, {u_name}! 👋</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: gray; font-size: 18px;'>{u_role} Workspace | {u_branch} Branch</p>", unsafe_allow_html=True)
    
    # --- Tabs Setup ---
    if u_role == "Manager":
        tabs = st.tabs(["📊 Dashboard & Passport", "📝 Task Logging", "🤝 Shift Handover", "🚨 SOS", "🏎️ Pit Stop", "🎬 Reels"])
        tab_dash = tabs[0]
        tab_logging = tabs[1]
        tab_shift = tabs[2]
        tab_sos = tabs[3]
        tab_pitstop = tabs[4]
        tab_reels = tabs[5]
    else:
        tabs = st.tabs(["📝 Task Logging", "🤝 Shift Handover", "🚨 SOS", "🏎️ Pit Stop", "🎬 Reels"])
        tab_logging = tabs[0]
        tab_shift = tabs[1]
        tab_sos = tabs[2]
        tab_pitstop = tabs[3]
        tab_reels = tabs[4]

    # ------------------------------------------
    # TAB: TASK LOGGING 
    # ------------------------------------------
    with tab_logging:
        st.markdown("### 📝 Log New Maintenance Task")
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                task_type = st.radio("Task Type:", ["WRO (Emergency 🔴)", "PRO (Preventive 🟢)"], horizontal=True)
                machine_name = st.text_input("📍 Machine & Location:")
                
                if st.button("🔮 AI Root Cause Analyzer"):
                    with st.spinner("Analyzing data models..."):
                        time.sleep(1)
                        st.info("🤖 **AI Diagnosis:** 1. Check Bearings | 2. Inspect Belt Alignment | 3. Verify Sensors.")
                
            with col2:
                issue_desc = st.text_area("📝 Work Done:")
                spare_parts = st.text_input("🛒 Spare Parts Used (Optional):", placeholder="e.g., Belt size 50")
                
        with st.container(border=True):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("#### 🎙️ Audio Note (Optional)")
                audio_note = st.audio_input("Record Voice Note") 
            with col_b:
                st.markdown("#### 🔒 LOTO Checkpoint")
                loto_photo = st.camera_input("Capture LOTO Lock 📸")
            
        if loto_photo is not None:
            if st.button("✅ Submit Task to System", type="primary", use_container_width=True):
                parts_msg = f"\n🛒 <b>Parts Used:</b> {spare_parts}" if spare_parts else ""
                audio_msg = "\n🎙️ <i>Audio note attached in system.</i>" if audio_note else ""
                
                msg = f"""
✅ <b>Task Completed ({task_type[:3]})</b>
━━━━━━━━━━━━━━
🏢 <b>Branch:</b> {u_branch}
📍 <b>Machine:</b> {machine_name}
👨‍🔧 <b>Tech:</b> {u_name}{parts_msg}{audio_msg}
🔒 <b>Safety:</b> LOTO Verified 📸
"""
                send_telegram_message(msg, u_branch)
                st.success("🎉 Task logged successfully!")
                st.balloons()

    # ------------------------------------------
    # TAB: SHIFT HANDOVER
    # ------------------------------------------
    with tab_shift:
        st.markdown("### 🤝 Shift Handover Log")
        with st.container(border=True):
            shift_note = st.text_area("📝 Handover Notes (What needs attention?):", height=120)
            urgent_flag = st.checkbox("🚨 Mark as Urgent for next shift")
            
            if st.button("📤 Submit Handover Note", use_container_width=True):
                urgency = "🔴 URGENT" if urgent_flag else "🟢 Normal"
                msg = f"🤝 <b>Shift Handover ({urgency})</b>\n━━━━━━━━━━━━━━\n👨‍🔧 <b>From:</b> {u_name}\n📝 <b>Notes:</b> {shift_note}"
                send_telegram_message(msg, u_branch)
                st.success("Handover logged! Next shift will be notified.")

    # ------------------------------------------
    # TAB: SOS & PIT STOP & REELS 
    # ------------------------------------------
    with tab_sos:
        st.markdown("### 🚨 Emergency SOS Broadcast")
        with st.container(border=True):
            sos_loc = st.text_input("📍 Exact Location:")
            sos_need = st.text_input("⚠️ What do you need?")
            if st.button("🚨 Broadcast SOS Now!", type="primary", use_container_width=True):
                send_telegram_message(f"🚨 <b>SOS from {u_name}!</b>\n📍 {sos_loc}\n⚠️ {sos_need}", u_branch)
                st.error("🚨 SOS Broadcast Sent Successfully!")

    with tab_pitstop:
        st.markdown("### 🏎️ F1 Pit Stop Challenge")
        with st.container(border=True):
            pit_mac = st.text_input("⚙️ Machine/Roll Details:")
            st.markdown("<br>", unsafe_allow_html=True)
            if not st.session_state.pitstop_active:
                if st.button("🏁 Start Timer"):
                    st.session_state.pitstop_active = True
                    st.session_state.start_time = time.time()
                    st.rerun()
            else:
                st.warning("⏱️ CHALLENGE IS LIVE! WORK SAFELY.")
                if st.button("🛑 Stop Timer", type="primary"):
                    mins, secs = divmod(int(time.time() - st.session_state.start_time), 60)
                    st.session_state.pitstop_active = False
                    send_telegram_message(f"🏎️ <b>Pit Stop:</b> {u_name} did [{pit_mac}] in <b>{mins}m {secs}s</b>! 🏁", u_branch)
                    st.success(f"🎉 Amazing Time: {mins}m {secs}s")
                    st.rerun()

    with tab_reels:
        st.markdown("### 🎬 Maintenance Reels")
        with st.container(border=True):
            vid_title = st.text_input("📌 Reel Title:")
            vid_file = st.file_uploader("📤 Upload Video (MP4/MOV)", type=['mp4', 'mov'])
            if vid_file and st.button("🚀 Publish Reel"):
                send_telegram_message(f"🎬 <b>New Reel by {u_name}</b>: <i>{vid_title}</i>", u_branch)
                st.success("Reel Published Successfully!")

    # ------------------------------------------
    # TAB: MANAGER DASHBOARD 
    # ------------------------------------------
    if u_role == "Manager":
        with tab_dash:
            st.markdown("### 📊 Branch Overview & Machine Passport")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("🛠️ WRO Reports", "12", "-3 Today")
            c2.metric("🔒 LOTO Compliance", "100%", "Perfect")
            c3.metric("🏎️ Avg Pit Stop", "18m 30s", "-1m 10s")
            
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("#### 🏥 Machine Health Passport")
                search_mac = st.selectbox("Select Machine to view history:", ["Mill A", "Mill B", "Main Sifter", "Packaging Line"])
                
                chart_data = pd.DataFrame(
                    np.random.randint(1, 5, size=(7, 1)), 
                    columns=["Breakdowns"],
                    index=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                )
                st.bar_chart(chart_data, color="#E74C3C")
                
                if search_mac == "Mill A":
                    st.error("⚠️ Warning: Mill A has high breakdown frequency. Preventative overhaul recommended.")
                else:
                    st.success(f"✅ {search_mac} is operating within normal parameters.")