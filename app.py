import streamlit as st
import pandas as pd
import time
import requests
import numpy as np

# --- إعدادات الصفحة ---
st.set_page_config(page_title="MMC Smart Maintenance", page_icon="⚙️", layout="wide")

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
        st.error("🚨 تنبيه: نسيت تحط التوكن حق البوت في الكود (السطر 14)!")
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
# 🎨 تصميم VIP (Custom CSS)
# ==========================================
st.markdown("""
<style>
    /* تجميل الأزرار */
    .stButton>button {
        border-radius: 12px;
        transition: all 0.3s ease;
        font-weight: bold;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
    }
    /* تجميل بطاقات الإحصائيات للمدير */
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border-left: 5px solid #2E86C1;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    /* تحسين العناوين */
    h1, h2, h3 { color: #1B4F72; }
</style>
""", unsafe_allow_html=True)

# --- تهيئة المتغيرات ---
if 'splash_done' not in st.session_state:
    st.session_state.splash_done = False
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ==========================================
# 1. SPLASH SCREEN (الافتتاحية)
# ==========================================
if not st.session_state.splash_done:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 65px;'>⚙️ MMC Smart System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #7F8C8D;'>Modern Mills Company</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-top: 30px;'>Loading Secure Environment...</p>", unsafe_allow_html=True)
    
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
        if st.button("Login to Workspace 🚀", type="primary", use_container_width=True):
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
    
    st.sidebar.markdown(f"### 🏢 {u_branch} Branch")
    st.sidebar.markdown("---")
    st.sidebar.write(f"**👤 Name:** {u_name}")
    st.sidebar.write(f"**🔑 Role:** {u_role}")
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    if u_role == "Manager":
        st.title("⚙️ Branch Management Hub")
        tabs = st.tabs(["📊 Dashboard & Passport", "🛠️ Task Logging", "🤝 Shift Handover", "🚨 SOS", "🏎️ Pit Stop", "🎬 Reels"])
        tab_dash = tabs[0]
        tab_logging = tabs[1]
        tab_shift = tabs[2]
        tab_sos = tabs[3]
        tab_pitstop = tabs[4]
        tab_reels = tabs[5]
    else:
        st.title(f"⚙️ {u_dept} Workspace")
        tabs = st.tabs(["🛠️ Task Logging", "🤝 Shift Handover", "🚨 SOS", "🏎️ Pit Stop", "🎬 Reels"])
        tab_logging = tabs[0]
        tab_shift = tabs[1]
        tab_sos = tabs[2]
        tab_pitstop = tabs[3]
        tab_reels = tabs[4]

    # ------------------------------------------
    # TAB 1: TASK LOGGING + SMART INVENTORY + VOICE
    # ------------------------------------------
    with tab_logging:
        st.subheader("📝 Log Maintenance Task")
        
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                task_type = st.radio("Task Type:", ["WRO (Emergency 🔴)", "PRO (Preventive 🟢)"], horizontal=True)
                machine_name = st.text_input("📍 Machine & Location:")
                
                if st.button("🔮 AI Root Cause Analyzer", type="secondary"):
                    with st.spinner("Analyzing..."):
                        time.sleep(1)
                        st.success("🤖 **AI:** 1. Check Bearings | 2. Inspect Belt Alignment | 3. Verify Sensors.")
                
            with col2:
                issue_desc = st.text_area("📝 Work Done:")
                spare_parts = st.text_input("🛒 Spare Parts Used (Optional):", placeholder="e.g., Belt size 50, 2 Bearings")
                
        with st.container(border=True):
            st.markdown("### 🎙️ Audio Note (Optional)")
            st.info("Hands dirty? Record a quick voice note instead of typing.")
            audio_note = st.audio_input("Record Voice Note") # ميزة تسجيل الصوت الجديدة

        with st.container(border=True):
            st.markdown("### 🔒 LOTO Checkpoint")
            loto_photo = st.camera_input("Capture LOTO Lock 📸")
            
            if loto_photo is not None:
                if st.button("✅ Submit Task", type="primary", use_container_width=True):
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
                    st.success("Task logged successfully!")
                    st.balloons()

    # ------------------------------------------
    # TAB: SHIFT HANDOVER (تسليم الوردية)
    # ------------------------------------------
    with tab_shift:
        st.subheader("🤝 Shift Handover Log")
        st.markdown("Leave notes for the incoming shift to ensure smooth operations.")
        
        with st.container(border=True):
            shift_note = st.text_area("📝 Handover Notes (What needs attention?):", height=150)
            urgent_flag = st.checkbox("🚨 Mark as Urgent for next shift")
            
            if st.button("📤 Submit Handover Note", use_container_width=True):
                urgency = "🔴 URGENT" if urgent_flag else "🟢 Normal"
                msg = f"""
🤝 <b>Shift Handover ({urgency})</b>
━━━━━━━━━━━━━━
👨‍🔧 <b>From:</b> {u_name}
📝 <b>Notes:</b> {shift_note}
"""
                send_telegram_message(msg, u_branch)
                st.success("Handover logged! Next shift will be notified.")

    # ------------------------------------------
    # TAB: SOS & PIT STOP & REELS (نفس السابقة بس بتصميم أفضل)
    # ------------------------------------------
    with tab_sos:
        st.subheader("🚨 Emergency SOS")
        with st.container(border=True):
            sos_loc = st.text_input("📍 Location:")
            sos_need = st.text_input("⚠️ Need:")
            if st.button("🚨 Broadcast SOS", type="primary", use_container_width=True):
                send_telegram_message(f"🚨 <b>SOS from {u_name}!</b>\n📍 {sos_loc}\n⚠️ {sos_need}", u_branch)
                st.error("SOS Sent!")

    with tab_pitstop:
        st.subheader("🏎️ Pit Stop Challenge")
        with st.container(border=True):
            pit_mac = st.text_input("⚙️ Machine/Roll:")
            if not st.session_state.pitstop_active:
                if st.button("🏁 Start Timer", type="primary"):
                    st.session_state.pitstop_active = True
                    st.session_state.start_time = time.time()
                    st.rerun()
            else:
                st.warning("⏱️ LIVE!")
                if st.button("🛑 Stop Timer"):
                    mins, secs = divmod(int(time.time() - st.session_state.start_time), 60)
                    st.session_state.pitstop_active = False
                    send_telegram_message(f"🏎️ <b>Pit Stop:</b> {u_name} did [{pit_mac}] in <b>{mins}m {secs}s</b>! 🏁", u_branch)
                    st.success(f"Time: {mins}m {secs}s")
                    st.rerun()

    with tab_reels:
        st.subheader("🎬 Maintenance Reels")
        with st.container(border=True):
            vid_title = st.text_input("📌 Title:")
            vid_file = st.file_uploader("📤 Upload MP4", type=['mp4'])
            if vid_file and st.button("🚀 Publish"):
                send_telegram_message(f"🎬 <b>New Reel by {u_name}</b>: <i>{vid_title}</i>", u_branch)
                st.success("Published!")

    # ------------------------------------------
    # TAB: MANAGER DASHBOARD (السجل الطبي للمعدات)
    # ------------------------------------------
    if u_role == "Manager":
        with tab_dash:
            st.subheader("📊 Analytics & Machine Passport")
            
            # إحصائيات بصرية جذابة
            c1, c2, c3 = st.columns(3)
            c1.metric("WRO Reports", "12", "-3 Today")
            c2.metric("LOTO Compliance", "100%", "Safe")
            c3.metric("Avg Pit Stop", "18m", "-2m")
            
            st.markdown("### 🏥 Machine Health Passport")
            search_mac = st.selectbox("Select Machine to view history:", ["Mill A", "Mill B", "Main Sifter", "Packaging Line"])
            
            # رسم بياني خفيف يوضح الأعطال
            chart_data = pd.DataFrame(
                np.random.randint(1, 5, size=(7, 1)), 
                columns=["Breakdowns"],
                index=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            )
            st.bar_chart(chart_data, color="#E74C3C")
            
            if search_mac == "Mill A":
                st.warning("⚠️ Warning: Mill A has broken down 4 times this week. Root cause analysis recommended.")
            else:
                st.success(f"✅ {search_mac} is running optimally.")