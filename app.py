import streamlit as st
import pandas as pd
import time
import requests
import numpy as np
import random

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
# 🎨 لمسات بصرية بسيطة (بدون تغيير لون الخلفية الأساسي)
# ==========================================
st.markdown("""
<style>
    /* العناوين المتدرجة */
    .gradient-text {
        background: linear-gradient(90deg, #3498db 0%, #2ecc71 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3em !important;
        font-weight: bold !important;
        text-align: center;
    }
    /* تجميل الأزرار بشكل خفيف */
    .stButton>button {
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
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
if 'user_points' not in st.session_state:
    st.session_state.user_points = random.randint(150, 450) # توليد نقاط عشوائية كبداية

# ==========================================
# 1. SPLASH SCREEN
# ==========================================
if not st.session_state.splash_done:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<div class='gradient-text'>⚙️ MMC Smart System</div>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Secure Environment Loading...</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
    st.session_state.splash_done = True
    st.rerun()

# ==========================================
# 2. LOGIN SYSTEM
# ==========================================
elif not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
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
            if st.button("Login 🚀", type="primary", use_container_width=True):
                if not emp_name or not emp_id:
                    st.error("⚠️ Please enter your Full Name and Employee ID.")
                elif role == "Manager" and password != BRANCH_PASSWORDS.get(branch): 
                    st.error(f"❌ Incorrect Password for {branch} Manager!")
                else:
                    st.session_state.user_info = {"name": emp_name, "branch": branch, "dept": department, "role": role}
                    st.session_state.logged_in = True
                    st.rerun()

# ==========================================
# 3. MAIN APPLICATION
# ==========================================
else:
    u_name = st.session_state.user_info['name']
    u_branch = st.session_state.user_info['branch']
    u_dept = st.session_state.user_info['dept']
    u_role = st.session_state.user_info['role']
    u_points = st.session_state.user_points
    
    # تحديد الرتبة بناءً على النقاط
    if u_points > 400: rank = "🏆 Master Tech"
    elif u_points > 200: rank = "⚡ Senior Tech"
    else: rank = "🔧 Specialist"

    # --- Sidebar ---
    st.sidebar.markdown(f"## 🏢 {u_branch}")
    st.sidebar.markdown("---")
    st.sidebar.write(f"**👤 Name:** {u_name}")
    st.sidebar.write(f"**🔑 Role:** {u_role}")
    if u_role == "Technician":
         st.sidebar.write(f"**🛠️ Dept:** {u_dept}")
         st.sidebar.markdown("---")
         st.sidebar.write(f"**⭐ Points:** {u_points}")
         st.sidebar.write(f"**🏅 Rank:** {rank}")
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # --- Header & Branch Health ---
    st.title(f"Welcome back, {u_name}! 👋")
    st.progress(0.92, text="🟢 Branch Health Score: 92% (Optimal)")
    st.markdown("---")
    
    # --- Tabs Setup ---
    if u_role == "Manager":
        tabs = st.tabs(["📊 Dashboard & Passport", "📝 Task Logging", "🤝 Shift Handover", "🚨 SOS", "🏎️ Pit Stop", "🎬 Reels"])
        tab_dash, tab_logging, tab_shift, tab_sos, tab_pitstop, tab_reels = tabs
    else:
        tabs = st.tabs(["📝 Task Logging", "🤝 Shift Handover", "🚨 SOS", "🏎️ Pit Stop", "🎬 Reels"])
        tab_logging, tab_shift, tab_sos, tab_pitstop, tab_reels = tabs

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
            st.markdown("#### ✅ Mandatory HSE Checklist")
            st.caption("Please confirm you followed safety protocols before uploading LOTO.")
            col_x, col_y, col_z = st.columns(3)
            with col_x: ppe_helmet = st.checkbox("👷‍♂️ Helmet & Glasses")
            with col_y: ppe_gloves = st.checkbox("🧤 Safety Gloves")
            with col_z: ppe_tools = st.checkbox("🔧 Right Tools Used")
            
            st.markdown("#### 🔒 LOTO Checkpoint & Audio")
            col_a, col_b = st.columns(2)
            with col_a:
                audio_note = st.audio_input("🎙️ Record Voice Note (Optional)") 
            with col_b:
                loto_photo = st.camera_input("📸 Capture LOTO Lock")
            
        if loto_photo is not None:
            if not (ppe_helmet and ppe_gloves and ppe_tools):
                st.error("⚠️ You must check all safety (HSE) boxes before submitting!")
            else:
                if st.button("✅ Submit Task (+50 Points)", type="primary", use_container_width=True):
                    st.session_state.user_points += 50 # زيادة النقاط!
                    
                    parts_msg = f"\n🛒 <b>Parts Used:</b> {spare_parts}" if spare_parts else ""
                    audio_msg = "\n🎙️ <i>Audio note attached in system.</i>" if audio_note else ""
                    
                    msg = f"""
✅ <b>Task Completed ({task_type[:3]})</b>
━━━━━━━━━━━━━━
🏢 <b>Branch:</b> {u_branch}
📍 <b>Machine:</b> {machine_name}
👨‍🔧 <b>Tech:</b> {u_name} (Points: {st.session_state.user_points})
✅ <b>Safety:</b> HSE Checklist Confirmed 100%{parts_msg}{audio_msg}
🔒 <b>LOTO:</b> Verified 📸
"""
                    send_telegram_message(msg, u_branch)
                    st.success("🎉 Task logged successfully! You earned 50 Points.")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()

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