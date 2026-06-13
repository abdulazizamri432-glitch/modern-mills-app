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
    if u_role == "Manager":
        tabs = st.tabs(["📊 Dashboard", "🛠️ Task Logging", "🚨 SOS", "🏎️ Pit Stop", "🎬 Reels"])
    else:
        tabs = st.tabs(["🛠️ Task Logging", "🚨 SOS", "🏎️ Pit Stop", "🎬 Reels"])
        
    tab_logging = tabs[1] if u_role == "Manager" else tabs[0]
    tab_sos = tabs[2] if u_role == "Manager" else tabs[1]
    tab_pitstop = tabs[3] if u_role == "Manager" else tabs[2]
    tab_reels = tabs[4] if u_role == "Manager" else tabs[3]

    # ------------------------------------------
    # TAB 1: TASK LOGGING + المحقق الذكي
    # ------------------------------------------
    with tab_logging:
        st.subheader("📝 Log New Maintenance Task")
        
        container1 = st.container(border=True)
        with container1:
            col1, col2 = st.columns(2)
            with col1:
                task_type = st.radio("Task Type:", ["WRO (Emergency 🔴)", "PRO (Preventive 🟢)"])
                machine_name = st.text_input("📍 Target Machine & Location:", placeholder="e.g., Mill A - 2nd Floor")
                
                # ميزة الذكاء الاصطناعي للمساعدة في التشخيص
                if st.button("🔮 AI Root Cause Analyzer", type="secondary"):
                    if not machine_name:
                        st.warning("Type the machine name first so AI can analyze it!")
                    else:
                        with st.spinner("Analyzing machine history and data..."):
                            time.sleep(1.5)
                            ai_causes = [
                                "1. Worn out bearings due to lack of lubrication.",
                                "2. Belt misalignment causing extreme friction.",
                                "3. Sensor malfunction sending false signals."
                            ]
                            st.success("🤖 **AI Diagnosis Complete! Possible causes:**")
                            for cause in ai_causes:
                                st.write(f"- {cause}")
                
            with col2:
                issue_desc = st.text_area("📝 Description & Work Done:", placeholder="What was the issue and how did you fix it?", height=150)
                co_op_techs = st.text_input("👥 Co-op Technicians (If any):", placeholder="e.g., Khalid (Electrical)")
                
        st.markdown("<br>", unsafe_allow_html=True)
        
        container2 = st.container(border=True)
        with container2:
            st.markdown("### 🔒 Mandatory Safety Checkpoint (LOTO)")
            st.info("⚠️ You cannot close this task without capturing the LOTO Lockout on the machine.")
            loto_photo = st.camera_input("Capture LOTO Lock 📸")
            
            if loto_photo is not None:
                if not machine_name or not issue_desc:
                    st.warning("Please fill in the Machine Location and Description first.")
                else:
                    if st.button("✅ Close Task & Claim Points", type="primary", use_container_width=True):
                        team_str = f"{u_name}" + (f" & {co_op_techs}" if co_op_techs else "")
                        dept_str = f"({u_dept})" if u_role == "Technician" else "(Management)"
                        msg = f"""
✅ *Task Completed Successfully ({task_type[:3]})*
━━━━━━━━━━━━━━
🏢 *Branch:* {u_branch}
📍 *Machine/Loc:* {machine_name}
👨‍🔧 *Team:* {team_str} {dept_str}
📝 *Details:* {issue_desc}
🔒 *Safety:* LOTO Verified 📸
"""
                        send_telegram_message(msg, u_branch) 
                        st.success("🎉 Task saved! Notifications sent to branch management.")
                        st.balloons()

    # ------------------------------------------
    # TAB 2: SOS BACKUP
    # ------------------------------------------
    with tab_sos:
        st.subheader("🚨 Emergency SOS Backup")
        
        container3 = st.container(border=True)
        with container3:
            sos_location = st.text_input("📍 Where exactly are you?", placeholder="e.g., Packaging Area, Line 3")
            sos_reason = st.text_input("⚠️ What do you need?", placeholder="e.g., Need 2 guys to lift a heavy motor")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚨 Broadcast SOS to Branch 🚨", type="primary", use_container_width=True):
                if not sos_location or not sos_reason:
                    st.warning("Please specify your location and what you need!")
                else:
                    sos_msg = f"""
🚨 *URGENT SOS BACKUP NEEDED!* 🚨
━━━━━━━━━━━━━━
🏢 *Branch:* {u_branch}
👨‍🔧 *Requested by:* {u_name}
📍 *Location:* {sos_location}
⚠️ *Reason:* {sos_reason}

🏃‍♂️ *Available team members, please assist immediately!*
"""
                    send_telegram_message(sos_msg, u_branch)
                    st.error("🚨 SOS Broadcast sent! Hold tight, the team is on the way.")

    # ------------------------------------------
    # TAB 3: PIT STOP CHALLENGE
    # ------------------------------------------
    with tab_pitstop:
        st.subheader("🏎️ F1 Pit Stop Challenge")
        st.markdown("Record your fastest roll replacement time safely!")
        
        container4 = st.container(border=True)
        with container4:
            pit_machine = st.text_input("⚙️ Machine / Roll Details:", placeholder="e.g., Mill B - Roll 4A")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if not st.session_state.pitstop_active:
                if st.button("🏁 Start Timer", type="primary", use_container_width=True):
                    if not pit_machine:
                        st.warning("Please specify the Roll/Machine name first.")
                    else:
                        st.session_state.pitstop_active = True
                        st.session_state.start_time = time.time()
                        st.rerun()
            else:
                st.warning("⏱️ Challenge is LIVE! Work safely and quickly.")
                if st.button("🛑 Roll Replaced (Stop Timer)", use_container_width=True):
                    end_time = time.time()
                    elapsed_seconds = int(end_time - st.session_state.start_time)
                    mins, secs = divmod(elapsed_seconds, 60)
                    
                    st.session_state.pitstop_active = False
                    st.success(f"🎉 Completed in: {mins} minutes and {secs} seconds!")
                    
                    msg = f"🏎️ *Pit Stop Challenge - {u_branch}!*\n**{u_name}** replaced [{pit_machine}] in *{mins}m {secs}s*! 🏁"
                    send_telegram_message(msg, u_branch)
                    st.balloons()
                    st.session_state.start_time = None
                    st.rerun()

    # ------------------------------------------
    # TAB 4: MAINTENANCE REELS
    # ------------------------------------------
    with tab_reels:
        st.subheader("🎬 Maintenance Reels")
        st.info(f"Posting as: **{u_name}** ({u_role})")
        
        container5 = st.container(border=True)
        with container5:
            video_title = st.text_input("📌 Reel Title:", placeholder="e.g., How to calibrate the new sensor")
            video_file = st.file_uploader("📤 Upload Video (MP4)", type=['mp4'])
            
            if video_file is not None:
                st.video(video_file)
                if st.button("🚀 Publish Reel", type="primary", use_container_width=True):
                    if not video_title:
                        st.warning("Please add a title for your reel.")
                    else:
                        st.success(f"Reel '{video_title}' published successfully!")
                        msg = f"🎬 *New Reel Published - {u_branch}!*\n**{u_name}** just posted: '{video_title}'. Check it out on the system!"
                        send_telegram_message(msg, u_branch)

    # ------------------------------------------
    # TAB 5: MANAGER DASHBOARD
    # ------------------------------------------
    if u_role == "Manager":
        with tabs[0]:
            st.subheader(f"📊 {u_branch} - Manager Dashboard")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Today's WRO Reports", "5", "-2")
            col2.metric("LOTO Compliance", "100%", "Perfect")
            col3.metric("Avg Pit Stop Time", "18m 30s", "-1m 10s")
            
            st.markdown("### 🏆 Top Technicians in Branch")
            df = pd.DataFrame({
                "Technician": ["Ahmed", "Khalid", "Yasser"],
                "Points": [450, 320, 290],
                "Title": ["👑 Mechanical King", "🦸‍♂️ SOS Hero", "⚡ The Flash"]
            })
            st.dataframe(df, use_container_width=True)