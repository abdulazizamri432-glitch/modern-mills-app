import streamlit as st
import pandas as pd
import time
import requests
import random
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="MMC Smart Plant System", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# ⚠️ إعدادات التليجرام 
# ==========================================
TELEGRAM_BOT_TOKEN = "8912670603:AAEr-hufquf8PIxnv-aKv0fz-9WgZa0oRks"

TELEGRAM_CHATS = {
    "Al-Jumum": "-5159290787",
    "Khamis Mushait": "-5104633079",
    "Al-Jouf": "-5176017884"
}

PLANT_PASSWORDS = {
    "Al-Jumum": "Jumum123",
    "Al-Jouf": "Jouf123",
    "Khamis Mushait": "Khamis123"
}

def send_telegram_message(text, plant):
    chat_id = TELEGRAM_CHATS.get(plant)
    if not chat_id:
        return 
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        pass

# ==========================================
# 🎨 لمسات بصرية 
# ==========================================
st.markdown("""
<style>
    .gradient-text {
        background: linear-gradient(90deg, #e67e22 0%, #d35400 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3em !important;
        font-weight: bold !important;
        text-align: center;
    }
    .stButton>button { border-radius: 8px; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 تهيئة قواعد البيانات الوهمية
# ==========================================
if 'splash_done' not in st.session_state: st.session_state.splash_done = False
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'safety_ack' not in st.session_state: st.session_state.safety_ack = False 
if 'user_points' not in st.session_state: st.session_state.user_points = random.randint(150, 450)
if 'parts_requests' not in st.session_state: st.session_state.parts_requests = []
if 'wro_pool' not in st.session_state: st.session_state.wro_pool = [] 
if 'fazaas' not in st.session_state: st.session_state.fazaas = [] 
if 'bounties' not in st.session_state: st.session_state.bounties = [] 
if 'plant_brain' not in st.session_state: st.session_state.plant_brain = [] 
if 'shift_log' not in st.session_state: st.session_state.shift_log = [] 
if 'tools_crib' not in st.session_state: st.session_state.tools_crib = []
if 'plant_reels' not in st.session_state: st.session_state.plant_reels = []
# قاعدة بيانات مهام "يوم الصيانة"
if 'maint_tasks' not in st.session_state: st.session_state.maint_tasks = []

if 'pitstop_active' not in st.session_state: st.session_state.pitstop_active = False
if 'start_time' not in st.session_state: st.session_state.start_time = None

# ==========================================
# 1. SPLASH SCREEN
# ==========================================
if not st.session_state.splash_done:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<div class='gradient-text'>🏭 MMC Smart Plant System</div>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Initializing Plant Operations...</h4>", unsafe_allow_html=True)
    
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
            st.title("🔒 Plant Access Login")
            st.markdown("---")
            
            emp_name = st.text_input("👤 Full Name", placeholder="e.g., Ahmed Al-Dawsari")
            emp_id = st.text_input("💳 Employee ID", placeholder="e.g., 10452")
            
            col_a, col_b = st.columns(2)
            with col_a:
                plant = st.selectbox("🏭 Plant Location", ["Al-Jumum", "Khamis Mushait", "Al-Jouf"])
                role = st.selectbox("🔑 Role", ["Technician", "Manager"])
            with col_b:
                if role == "Technician":
                    department = st.selectbox("🛠️ Department", ["Mechanical", "Electrical", "Welding", "HVAC", "Operations"])
                    password = ""
                else:
                    department = "Management"
                    password = st.text_input("🛡️ Manager Password", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Access Plant 🚀", type="primary", use_container_width=True):
                if not emp_name or not emp_id:
                    st.error("⚠️ Please enter your Full Name and Employee ID.")
                elif role == "Manager" and password != PLANT_PASSWORDS.get(plant): 
                    st.error(f"❌ Incorrect Password for {plant} Manager!")
                else:
                    st.session_state.user_info = {"name": emp_name, "id": emp_id, "plant": plant, "dept": department, "role": role}
                    st.session_state.logged_in = True
                    st.rerun()

# ==========================================
# 3. SAFETY TOOLBOX TALK
# ==========================================
elif not st.session_state.safety_ack:
    u_name = st.session_state.user_info['name']
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.warning("### 🛑 Daily Toolbox Talk")
            st.markdown(f"Welcome to shift, **{u_name}**. Before starting work, please read today's safety focus:")
            st.info("**Today's Focus: Lock Out Tag Out (LOTO)**\n\nAlways ensure equipment is fully de-energized and your personal lock is applied before performing maintenance. Do not rely on someone else's lock.")
            if st.button("✅ I Acknowledge & Commit to Safety", type="primary", use_container_width=True):
                st.session_state.safety_ack = True
                st.rerun()

# ==========================================
# 4. MAIN APPLICATION
# ==========================================
else:
    u_name = st.session_state.user_info['name']
    u_id = st.session_state.user_info['id']
    u_plant = st.session_state.user_info['plant']
    u_dept = st.session_state.user_info['dept']
    u_role = st.session_state.user_info['role']
    u_points = st.session_state.user_points
    
    if u_points > 600: rank = "🏆 Plant Master"
    elif u_points > 300: rank = "⚡ Senior Tech"
    else: rank = "🔧 Specialist"

    # --- Sidebar ---
    st.sidebar.markdown(f"## 🏭 {u_plant} Plant")
    st.sidebar.markdown("---")
    st.sidebar.write(f"**👤 Name:** {u_name}")
    st.sidebar.write(f"**💳 ID:** {u_id}")
    st.sidebar.write(f"**🔑 Role:** {u_role}")
    if u_role == "Technician":
         st.sidebar.write(f"**🛠️ Dept:** {u_dept}")
         st.sidebar.markdown("---")
         st.sidebar.write(f"**⭐ Points:** {u_points}")
         st.sidebar.write(f"**🏅 Rank:** {rank}")
    st.sidebar.markdown("---")
    if st.sidebar.button("Leave Plant 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.safety_ack = False 
        st.rerun()

    # --- Header ---
    st.title(f"Welcome to {u_plant} Operations 👋")
    st.markdown("---")
    
    # --- Tabs Setup ---
    if u_role == "Manager":
        tabs = st.tabs(["📊 Dashboard", "🛠️ Dispatch", "📝 Log Task", "📅 Maint. Day", "🔧 Tool Crib", "🧠 Plant Brain", "🎬 Reels", "📦 Parts", "🤝 Handover", "⚡ Extras"])
        tab_dash, tab_action, tab_log, tab_maint, tab_tools, tab_brain, tab_reels, tab_parts, tab_handover, tab_extras = tabs
    else:
        tabs = st.tabs(["🎯 Action Hub", "📝 Log Task", "📅 Maint. Day", "🔧 Tool Crib", "🧠 Plant Brain", "🎬 Reels", "📦 Parts", "🤝 Handover", "⚡ Extras"])
        tab_action, tab_log, tab_maint, tab_tools, tab_brain, tab_reels, tab_parts, tab_handover, tab_extras = tabs

    # ------------------------------------------
    # MANAGER: DASHBOARD
    # ------------------------------------------
    if u_role == "Manager":
        with tab_dash:
            st.markdown("### 📊 Plant Operations Dashboard")
            c1, c2, c3 = st.columns(3)
            c1.metric("🔴 Active WROs", len(st.session_state.wro_pool), "Pending Tasks")
            c2.metric("🟢 Shift Tasks Logged", len(st.session_state.shift_log), "Completed")
            c3.metric("📅 Maint. Tasks", len([t for t in st.session_state.maint_tasks if t['status'] == 'Completed']), "Completed")
            
            st.markdown("#### 🏆 Plant Leaderboard")
            df_leaders = pd.DataFrame({
                "Technician": ["Ahmed (Mech)", "Khalid (Elec)", "Yasser (Weld)", f"{u_name}"],
                "Points": [850, 620, 510, u_points],
                "Rank": ["🏆 Plant Master", "⚡ Senior Tech", "⚡ Senior Tech", rank]
            }).sort_values(by="Points", ascending=False).reset_index(drop=True)
            st.dataframe(df_leaders, use_container_width=True)

    # ------------------------------------------
    # DISPATCH / ACTION HUB
    # ------------------------------------------
    with tab_action:
        if u_role == "Manager":
            st.markdown("### 🛠️ Dispatch Hub (Assign WROs)")
            col1, col2 = st.columns(2)
            with col1:
                with st.container(border=True):
                    st.markdown("#### 🚨 Dispatch WRO (Emergency)")
                    wro_mac = st.text_input("📍 Machine Location:")
                    wro_desc = st.text_input("⚠️ Issue Description:")
                    if st.button("📢 Broadcast WRO", type="primary", use_container_width=True):
                        if wro_mac and wro_desc:
                            wro_id = random.randint(1000, 9999)
                            st.session_state.wro_pool.append({"id": wro_id, "machine": wro_mac, "issue": wro_desc, "status": "Pending"})
                            send_telegram_message(f"🚨 <b>NEW WRO DISPATCHED!</b>\n📍 {wro_mac}\n⚠️ {wro_desc}\n\n<i>Login to claim it!</i>", u_plant)
                            st.success("WRO Dispatched to all technicians!")
                            st.rerun()
            with col2:
                with st.container(border=True):
                    st.markdown("#### 💰 Post a Bounty")
                    bnty_desc = st.text_input("📌 Task (e.g., Clean Pump Room):")
                    bnty_pts = st.slider("⭐ Reward Points:", 10, 100, 30, step=10)
                    if st.button("💸 Post Bounty", use_container_width=True):
                        if bnty_desc:
                            st.session_state.bounties.append({"id": random.randint(1000,9999), "desc": bnty_desc, "points": bnty_pts})
                            send_telegram_message(f"💰 <b>NEW BOUNTY POSTED!</b>\n📌 {bnty_desc}\n⭐ Reward: {bnty_pts} Points", u_plant)
                            st.success("Bounty posted successfully!")
                            st.rerun()
        else:
            st.markdown("### 🎯 Live Action Hub")
            
            st.markdown("#### 🚨 Available WROs (Claim to Fix)")
            if not st.session_state.wro_pool:
                st.info("No pending WROs right now. Good job team!")
            else:
                for wro in st.session_state.wro_pool:
                    with st.container(border=True):
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.write(f"**📍 Machine:** {wro['machine']}")
                            st.write(f"**⚠️ Issue:** {wro['issue']}")
                        with col_b:
                            if st.button(f"🙋‍♂️ Claim Task!", key=f"wro_{wro['id']}", type="primary"):
                                st.session_state.wro_pool.remove(wro)
                                send_telegram_message(f"👨‍🔧 <b>WRO Claimed!</b>\n{u_name} is heading to {wro['machine']}.", u_plant)
                                st.success("You claimed this task!")
                                time.sleep(1)
                                st.rerun()

            st.markdown("---")
            st.markdown("#### 🤝 Faza'a (Quick Assist)")
            with st.expander("Need help? Request a Faza'a"):
                fz_loc = st.text_input("📍 Your Location:")
                fz_need = st.text_input("🙋‍♂️ What do you need?")
                if st.button("📢 Ask for Faza'a", use_container_width=True):
                    if fz_loc:
                        st.session_state.fazaas.append({"id": random.randint(10,99), "req": u_name, "loc": fz_loc, "need": fz_need})
                        send_telegram_message(f"🤝 <b>Faza'a Needed!</b>\n📍 {fz_loc}\n🙋‍♂️ {u_name} needs: {fz_need}", u_plant)
                        st.success("Faza'a broadcasted!")
                        st.rerun()

    # ------------------------------------------
    # TASK LOGGING (توثيق المهام العام)
    # ------------------------------------------
    with tab_log:
        st.markdown("### 📝 Log Completed Task")
        task_type = st.radio("Task Type", ["🔴 WRO (Emergency)", "🟢 PRO (Preventive)"], horizontal=True, label_visibility="collapsed")
        
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                machine_name = st.text_input("📍 Machine Name & Location:")
            with col2:
                issue_desc = st.text_area("📝 Work Done & How it was fixed:")
                
        with st.container(border=True):
            st.markdown("#### ✅ Mandatory HSE Checklist")
            col_x, col_y, col_z = st.columns(3)
            with col_x: ppe_helmet = st.checkbox("👷‍♂️ Helmet & Glasses")
            with col_y: ppe_gloves = st.checkbox("🧤 Safety Gloves")
            with col_z: ppe_tools = st.checkbox("🔧 Right Tools Used")
            
            st.markdown("---")
            st.markdown("#### 📸/🎥 Mandatory Proof of Completion")
            st.caption("You MUST upload a photo or video showing the completed work to submit this task.")
            proof_media = st.file_uploader("Upload Photo or Video", type=["jpg", "jpeg", "png", "mp4", "mov"])
            
        if st.button("✅ Submit Task (+50 Points)", type="primary", use_container_width=True):
            if not machine_name or not issue_desc:
                st.error("⚠️ Please fill in Machine Location and Description.")
            elif not (ppe_helmet and ppe_gloves and ppe_tools):
                st.error("⚠️ You must check all HSE boxes before submitting!")
            elif not proof_media:
                st.error("❌ ⚠️ Proof Required: You cannot submit without uploading a photo or video of the work!")
            else:
                st.session_state.user_points += 50
                st.session_state.shift_log.append(f"[{task_type[:5]}] {machine_name} - By {u_name}")
                
                if "WRO" in task_type:
                    st.session_state.plant_brain.append({
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "machine": machine_name,
                        "fix": issue_desc,
                        "tech": u_name
                    })
                
                send_telegram_message(f"✅ <b>Task Completed & Verified!</b>\n🏭 <b>Plant:</b> {u_plant}\n📍 <b>Machine:</b> {machine_name}\n👨‍🔧 <b>Tech:</b> {u_name}\n📸 <i>Media Proof Uploaded in System</i>", u_plant)
                
                st.success("🎉 Task logged and verified successfully! Saved to Shift Log.")
                st.balloons()
                time.sleep(2)
                st.rerun()

    # ------------------------------------------
    # MAINTENANCE DAY (يوم الصيانة)
    # ------------------------------------------
    with tab_maint:
        st.markdown("### 📅 Maintenance Day (يوم الصيانة)")
        
        if u_role == "Manager":
            with st.container(border=True):
                st.markdown("#### 📝 Assign Maintenance Task")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    tech_name_assign = st.text_input("👤 Technician Name:")
                    tech_id_assign = st.text_input("💳 Technician ID (Mandatory):")
                with col_m2:
                    maint_task_desc = st.text_area("🛠️ Task Details:")
                
                if st.button("📤 Assign Task", type="primary"):
                    if tech_name_assign and tech_id_assign and maint_task_desc:
                        task_id = random.randint(1000, 9999)
                        st.session_state.maint_tasks.append({
                            "id": task_id,
                            "tech_name": tech_name_assign,
                            "tech_id": tech_id_assign,
                            "desc": maint_task_desc,
                            "status": "⏳ Pending",
                            "report": "",
                            "assigned_by": u_name
                        })
                        send_telegram_message(f"📅 <b>New Maint. Day Task!</b>\n👨‍🔧 <b>To:</b> {tech_name_assign}\n🔢 <b>ID:</b> {tech_id_assign}\n🛠️ <b>Task:</b> {maint_task_desc}", u_plant)
                        st.success(f"Task assigned to {tech_name_assign} successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("⚠️ Please fill all fields.")
            
            st.markdown("#### 📊 Maintenance Tasks Overview")
            if not st.session_state.maint_tasks:
                st.info("No tasks assigned yet.")
            else:
                df_maint = pd.DataFrame(st.session_state.maint_tasks)
                st.dataframe(df_maint[['tech_name', 'tech_id', 'desc', 'status', 'report']], use_container_width=True)

        else: # Technician View
            st.markdown("#### 📋 My Assigned Maintenance Tasks")
            # تصفية المهام بناءً على الرقم الوظيفي للموظف وحالة المهمة
            my_maint_tasks = [t for t in st.session_state.maint_tasks if t['tech_id'] == u_id and "Pending" in t['status']]
            
            if not my_maint_tasks:
                st.success("🎉 You have no pending Maintenance Day tasks!")
            else:
                for task in my_maint_tasks:
                    with st.container(border=True):
                        st.warning(f"**🛠️ Required Task:** {task['desc']}")
                        st.caption(f"👤 Assigned by: Manager {task['assigned_by']}")
                        
                        tech_report = st.text_area("📝 What did you do to complete this?", key=f"report_{task['id']}")
                        maint_media = st.file_uploader("📸/🎥 Upload Proof (Mandatory)", type=["jpg", "png", "mp4", "mov"], key=f"media_{task['id']}")
                        
                        if st.button("✅ Submit Work", key=f"btn_maint_{task['id']}", type="primary"):
                            if not tech_report or not maint_media:
                                st.error("❌ ⚠️ You MUST write a report AND upload media proof to complete this task!")
                            else:
                                task['status'] = "✅ Completed"
                                task['report'] = tech_report
                                st.session_state.user_points += 80
                                st.session_state.shift_log.append(f"[Maint. Day] {task['desc'][:20]}...")
                                send_telegram_message(f"✅ <b>Maint. Day Task Completed!</b>\n👨‍🔧 <b>By:</b> {u_name} ({u_id})\n🛠️ <b>Task:</b> {task['desc']}\n📝 <b>Report:</b> {tech_report}", u_plant)
                                st.success("Awesome! Task completed and verified.")
                                time.sleep(2)
                                st.rerun()

    # ------------------------------------------
    # TOOL CRIB
    # ------------------------------------------
    with tab_tools:
        st.markdown("### 🔧 Tool Crib (Equipment Checkout)")
        if u_role == "Manager":
            with st.expander("➕ Add New Tool to Crib", expanded=False):
                new_tool_name = st.text_input("Tool Name & Model:")
                if st.button("Add Tool", type="primary"):
                    if new_tool_name:
                        st.session_state.tools_crib.append({"id": len(st.session_state.tools_crib)+1, "name": new_tool_name, "status": "Available", "user": ""})
                        st.success("Tool added!")
                        time.sleep(1)
                        st.rerun()

        if not st.session_state.tools_crib:
            st.info("The Tool Crib is empty.")
        else:
            df_tools = pd.DataFrame(st.session_state.tools_crib)
            def color_status(val):
                return f'color: {"#2ecc71" if val == "Available" else "#e74c3c"}; font-weight: bold'
            st.dataframe(df_tools.style.map(color_status, subset=['status']), use_container_width=True, hide_index=True)
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                avail_tools = [t['name'] for t in st.session_state.tools_crib if t['status'] == 'Available']
                if avail_tools:
                    sel_tool = st.selectbox("Select Tool to Borrow:", avail_tools)
                    if st.button("Borrow"):
                        for t in st.session_state.tools_crib:
                            if t['name'] == sel_tool:
                                t['status'], t['user'] = 'In Use', u_name
                        st.rerun()
            with col_t2:
                my_tools = [t['name'] for t in st.session_state.tools_crib if t['user'] == u_name]
                if my_tools:
                    ret_tool = st.selectbox("Select Tool to Return:", my_tools)
                    if st.button("Return"):
                        for t in st.session_state.tools_crib:
                            if t['name'] == ret_tool:
                                t['status'], t['user'] = 'Available', ''
                        st.rerun()

    # ------------------------------------------
    # PLANT BRAIN 
    # ------------------------------------------
    with tab_brain:
        st.markdown("### 🧠 Plant Brain (Knowledge Base)")
        search_q = st.text_input("🔍 Search Machine Name:")
        if st.session_state.plant_brain:
            for entry in reversed(st.session_state.plant_brain):
                if search_q.lower() in entry['machine'].lower() or search_q == "":
                    with st.container(border=True):
                        st.markdown(f"**📍 Machine:** {entry['machine']} `({entry['date']})`")
                        st.markdown(f"**🔧 Solution:** {entry['fix']}")
                        st.markdown(f"👨‍🔧 *Fixed by: {entry['tech']}*")
        else:
            st.info("The Plant Brain is empty.")

    # ------------------------------------------
    # 🎬 PLANT REELS 
    # ------------------------------------------
    with tab_reels:
        st.markdown("### 🎬 Plant Reels (Tutorials & Guides)")
        with st.expander("📤 Upload a New Reel (+100 Points)", expanded=False):
            reel_title = st.text_input("📌 Reel Title:")
            reel_file = st.file_uploader("Upload Video", type=["mp4", "mov"])
            if st.button("🚀 Publish Reel", type="primary"):
                if reel_title and reel_file:
                    st.session_state.plant_reels.append({
                        "title": reel_title, "author": u_name, "date": datetime.now().strftime("%Y-%m-%d"), "video_bytes": reel_file.read()
                    })
                    st.session_state.user_points += 100
                    st.success("Reel published!")
                    time.sleep(1)
                    st.rerun()
        st.markdown("---")
        if st.session_state.plant_reels:
            for reel in reversed(st.session_state.plant_reels):
                with st.container(border=True):
                    st.markdown(f"**📌 {reel['title']}**")
                    st.caption(f"👨‍🔧 By: {reel['author']} | 📅 {reel['date']}")
                    st.video(reel['video_bytes'])

    # ------------------------------------------
    # PARTS REQUEST
    # ------------------------------------------
    with tab_parts:
        st.markdown("### 📦 Spare Parts Request")
        if u_role == "Technician":
            with st.container(border=True):
                col1, col2 = st.columns(2)
                with col1:
                    part_desc = st.text_input("🛠️ Part Description:")
                with col2:
                    target_machine = st.text_input("📍 Machine?:")
                if st.button("📤 Submit Request", type="primary") and part_desc:
                    st.session_state.parts_requests.append({"ID": len(st.session_state.parts_requests)+1, "Technician": u_name, "Part": part_desc, "Machine": target_machine, "Status": "⏳ Pending"})
                    st.success("Request sent!")
            df_req = pd.DataFrame(st.session_state.parts_requests)
            if not df_req.empty: st.dataframe(df_req[df_req['Technician'] == u_name], use_container_width=True)

        elif u_role == "Manager":
            df_req = pd.DataFrame(st.session_state.parts_requests)
            if not df_req.empty:
                st.dataframe(df_req, use_container_width=True)
                sel_id = st.number_input("Update Req ID:", min_value=1, max_value=len(st.session_state.parts_requests), step=1)
                action = st.selectbox("Action:", ["Mark as Done ✅", "Rejected ❌"])
                if st.button("💾 Update Status"):
                    for r in st.session_state.parts_requests:
                        if r["ID"] == sel_id: r["Status"] = action
                    st.rerun()

    # ------------------------------------------
    # SHIFT HANDOVER
    # ------------------------------------------
    with tab_handover:
        st.markdown("### 🤝 Smart Shift Handover")
        auto_summary = f"🔄 Shift Summary for {u_name}:\n- Tasks Completed: {len(st.session_state.shift_log)}\n"
        for log_item in st.session_state.shift_log: auto_summary += f"  > {log_item}\n"
        with st.container(border=True):
            shift_note = st.text_area("📝 Notes:", value=auto_summary, height=150)
            if st.button("📤 Submit Handover", use_container_width=True):
                send_telegram_message(f"🤝 <b>Shift Handover</b>\n👨‍🔧 {u_name}\n{shift_note}", u_plant)
                st.success("Handover logged!")
                st.session_state.shift_log = []

    # ------------------------------------------
    # EXTRAS
    # ------------------------------------------
    with tab_extras:
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("### 🚨 SOS Broadcast")
                sos_loc = st.text_input("📍 Location:")
                if st.button("🚨 Broadcast SOS", type="primary", use_container_width=True):
                    send_telegram_message(f"🚨 <b>SOS from {u_name}!</b>\n📍 {sos_loc}", u_plant)
                    st.error("Sent!")
        with col2:
            with st.container(border=True):
                st.markdown("### 🏎️ Pit Stop Timer")
                if not st.session_state.pitstop_active:
                    if st.button("🏁 Start"):
                        st.session_state.pitstop_active = True
                        st.session_state.start_time = time.time()
                        st.rerun()
                else:
                    if st.button("🛑 Stop", type="primary"):
                        mins, secs = divmod(int(time.time() - st.session_state.start_time), 60)
                        st.session_state.pitstop_active = False
                        st.success(f"🎉 Time: {mins}m {secs}s")