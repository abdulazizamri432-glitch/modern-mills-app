import streamlit as st
import pandas as pd
import time
import requests

# --- Page Configuration ---
st.set_page_config(page_title="MMC Smart Maintenance", page_icon="⚙️", layout="wide")

# --- Telegram Settings ---
TELEGRAM_BOT_TOKEN = "YOUR_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"

def send_telegram_message(text):
    """Send Rich Notifications to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        pass

# --- Session State Initialization ---
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
    st.markdown("<h1 style='text-align: center; margin-top: 20%; font-size: 60px;'>⚙️ MMC Smart Maintenance</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: gray;'>Modern Mills Company</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Loading System Modules...</p>", unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.02)
        progress_bar.progress(i + 1)
    
    st.session_state.splash_done = True
    st.rerun()

# ==========================================
# 2. LOGIN SYSTEM (نظام تسجيل الدخول)
# ==========================================
elif not st.session_state.logged_in:
    st.title("🔒 System Login")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        emp_name = st.text_input("Full Name")
        emp_id = st.text_input("Employee ID")
        branch = st.selectbox("Branch", ["Al-Jumum", "Al-Jouf", "Khamis Mushait"])
        department = st.selectbox("Department", ["Mechanical", "Electrical", "Welding", "HVAC"])
        
    with col2:
        role = st.selectbox("Role", ["Technician", "Manager"])
        password = ""
        if role == "Manager":
            password = st.text_input("Manager Password", type="password")
            
        st.markdown("<br>", unsafe_allow_html=True)
        remember_me = st.checkbox("💾 Remember Me (Auto-Save Login)")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Login 🚀", type="primary", use_container_width=True):
            if not emp_name or not emp_id:
                st.error("⚠️ Please enter your Name and Employee ID.")
            elif role == "Manager" and password != "admin123": # كلمة سر المدير هنا
                st.error("❌ Incorrect Manager Password!")
            else:
                st.session_state.user_info = {
                    "name": emp_name,
                    "id": emp_id,
                    "branch": branch,
                    "dept": department,
                    "role": role
                }
                st.session_state.logged_in = True
                st.success("Login Successful!")
                time.sleep(0.5)
                st.rerun()

# ==========================================
# 3. MAIN APPLICATION (النظام الرئيسي)
# ==========================================
else:
    # User info variables for easy access
    u_name = st.session_state.user_info['name']
    u_branch = st.session_state.user_info['branch']
    u_dept = st.session_state.user_info['dept']
    u_role = st.session_state.user_info['role']
    
    # Sidebar Info
    st.sidebar.title("👤 User Profile")
    st.sidebar.write(f"**Name:** {u_name}")
    st.sidebar.write(f"**Branch:** {u_branch}")
    st.sidebar.write(f"**Department:** {u_dept}")
    st.sidebar.write(f"**Role:** {u_role}")
    if st.sidebar.button("Logout 🚪"):
        st.session_state.logged_in = False
        st.rerun()

    st.title(f"⚙️ MMC Smart Maintenance - {u_branch} Branch")
    st.markdown("---")
    
    # Machine List
    machines = ["Mill A", "Mill B", "Packaging Belt", "Main Sifter", "Air Compressor"]
    
    # Establish Tabs based on Role
    if u_role == "Manager":
        tabs = st.tabs(["📊 Dashboard", "🛠️ Task Logging", "🚨 SOS", "🏎️ Pit Stop", "🎬 Maintenance Reels"])
    else:
        tabs = st.tabs(["🛠️ Task Logging", "🚨 SOS", "🏎️ Pit Stop", "🎬 Maintenance Reels"])
        
    tab_logging = tabs[1] if u_role == "Manager" else tabs[0]
    tab_sos = tabs[2] if u_role == "Manager" else tabs[1]
    tab_pitstop = tabs[3] if u_role == "Manager" else tabs[2]
    tab_reels = tabs[4] if u_role == "Manager" else tabs[3]

    # ------------------------------------------
    # TAB: TASK LOGGING & LOTO
    # ------------------------------------------
    with tab_logging:
        st.header("🛠️ Log New Maintenance Task")
        
        col1, col2 = st.columns(2)
        with col1:
            task_type = st.radio("Task Type:", ["WRO (Emergency)", "PRO (Preventive)"])
            machine_name = st.selectbox("Target Machine:", machines)
            
        with col2:
            issue_desc = st.text_area("Task Description & Work Done:")
            co_op_techs = st.text_input("Co-op Technicians (Leave blank if none):", placeholder="e.g., Ahmed (Electrical)")
            
        st.markdown("### 🔒 Mandatory Safety Checkpoint (LOTO)")
        st.info("⚠️ You cannot close this task without capturing the LOTO Lockout on the machine.")
        
        loto_photo = st.camera_input("Capture LOTO Lock 📸")
        
        if loto_photo is not None:
            if st.button("✅ Close Task & Claim Points", use_container_width=True):
                team_str = f"{u_name}" + (f" & {co_op_techs}" if co_op_techs else "")
                
                msg = f"""
✅ *Task Completed Successfully ({task_type[:3]})*
━━━━━━━━━━━━━━
🏢 *Branch:* {u_branch}
⚙️ *Machine:* {machine_name}
👨‍🔧 *Team:* {team_str} ({u_dept})
📝 *Description:* {issue_desc}
🔒 *Safety:* LOTO Verified visually.
"""
                send_telegram_message(msg)
                st.success("🎉 Task saved! Notifications sent to branch management.")
                st.balloons()

    # ------------------------------------------
    # TAB: SOS BACKUP
    # ------------------------------------------
    with tab_sos:
        st.header("🚨 Emergency SOS Backup")
        st.markdown("Need help with a heavy lift or complex issue? Call your branch team!")
        
        sos_location = st.selectbox("Where are you?", machines)
        sos_reason = st.text_input("What do you need?", placeholder="e.g., Need 2 guys to lift a motor")
        
        if st.button("🚨 Broadcast SOS to Branch 🚨", type="primary", use_container_width=True):
            sos_msg = f"""
🚨 *URGENT SOS BACKUP NEEDED!* 🚨
━━━━━━━━━━━━━━
🏢 *Branch:* {u_branch}
👨‍🔧 *Requested by:* {u_name}
📍 *Location:* {sos_location}
⚠️ *Reason:* {sos_reason}

🏃‍♂️ *Available team members, please assist immediately!*
"""
            send_telegram_message(sos_msg)
            st.error("🚨 SOS Broadcast sent to your branch Telegram group!")

    # ------------------------------------------
    # TAB: PIT STOP CHALLENGE
    # ------------------------------------------
    with tab_pitstop:
        st.header("🏎️ F1 Pit Stop Challenge (Roll Replacement)")
        
        pit_machine = st.selectbox("Machine for Roll Replacement:", ["Mill A", "Mill B"])
        
        if not st.session_state.pitstop_active:
            if st.button("🏁 Start Timer", type="primary"):
                st.session_state.pitstop_active = True
                st.session_state.start_time = time.time()
                st.rerun()
        else:
            st.warning("⏱️ Challenge is LIVE! Work safely and quickly.")
            if st.button("🛑 Roll Replaced (Stop Timer)"):
                end_time = time.time()
                elapsed_seconds = int(end_time - st.session_state.start_time)
                mins, secs = divmod(elapsed_seconds, 60)
                
                st.session_state.pitstop_active = False
                st.success(f"🎉 Completed in: {mins} minutes and {secs} seconds!")
                
                msg = f"🏎️ *Pit Stop Challenge - {u_branch}!*\n{u_name} replaced a roll on {pit_machine} in *{mins}m {secs}s*! 🏁"
                send_telegram_message(msg)
                st.balloons()
                st.session_state.start_time = None
                st.rerun()

    # ------------------------------------------
    # TAB: MAINTENANCE REELS (TIKTOK)
    # ------------------------------------------
    with tab_reels:
        st.header("🎬 Maintenance Reels")
        st.markdown("Share your expertise, a quick fix, or a safety tip with the team.")
        
        # Name is automatically pulled from login (no selectbox)
        st.info(f"Posting as: **{u_name}** ({u_role})")
        
        video_title = st.text_input("Reel Title:")
        video_file = st.file_uploader("Upload Video (MP4)", type=['mp4'])
        
        if video_file is not None:
            st.video(video_file)
            if st.button("🚀 Publish Reel"):
                st.success(f"Reel '{video_title}' published successfully by {u_name}!")
                msg = f"🎬 *New Reel Published - {u_branch}!*\n**{u_name}** just posted: '{video_title}'. Check it out on the system!"
                send_telegram_message(msg)

    # ------------------------------------------
    # TAB: MANAGER DASHBOARD (Managers Only)
    # ------------------------------------------
    if u_role == "Manager":
        with tabs[0]:
            st.header(f"📊 {u_branch} Branch - Manager Dashboard")
            
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