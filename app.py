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
TELEGRAM_BOT_TOKEN = "هنا_تحط_التوكن_حقك"

TELEGRAM_CHATS = {
    "Al-Jumum": "-5159290787",
    "Al-Jouf": "-5176017884",
    "Khamis Mushait": "-5104633079"
}

PLANT_PASSWORDS = {
    "Al-Jumum": "Jumum123",
    "Al-Jouf": "Jouf123",
    "Khamis Mushait": "Khamis123"
}

def send_telegram_message(text, plant):
    if TELEGRAM_BOT_TOKEN == "هنا_تحط_التوكن_حقك" or not TELEGRAM_BOT_TOKEN:
        # st.error("🚨 تنبيه: نسيت تحط التوكن حق البوت!") # معطلة مؤقتاً لعدم الإزعاج في العرض
        return

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
# 🎨 لمسات بصرية بسيطة 
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
    .stButton>button {
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }
    div.row-widget.stRadio > div {
        flex-direction: row;
        justify-content: center;
        background-color: rgba(0,0,0,0.05);
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 تهيئة المتغيرات وقواعد البيانات الوهمية
# ==========================================
if 'splash_done' not in st.session_state: st.session_state.splash_done = False
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'pitstop_active' not in st.session_state: st.session_state.pitstop_active = False
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'user_points' not in st.session_state: st.session_state.user_points = random.randint(150, 450)
if 'parts_requests' not in st.session_state: st.session_state.parts_requests = []

# قواعد البيانات الجديدة
if 'wro_pool' not in st.session_state: st.session_state.wro_pool = [] # طلبات أوبر للأعطال
if 'fazaas' not in st.session_state: st.session_state.fazaas = [] # طلبات الفزعة
if 'bounties' not in st.session_state: st.session_state.bounties = [] # لوحة المكافآت
if 'plant_brain' not in st.session_state: st.session_state.plant_brain = [] # ذاكرة المحطة
if 'shift_log' not in st.session_state: st.session_state.shift_log = [] # سجل مهام الوردية للتسليم

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
                plant = st.selectbox("🏭 Plant Location", ["Al-Jumum", "Al-Jouf", "Khamis Mushait"])
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
                    st.session_state.user_info = {"name": emp_name, "plant": plant, "dept": department, "role": role}
                    st.session_state.logged_in = True
                    st.rerun()

# ==========================================
# 3. MAIN APPLICATION
# ==========================================
else:
    u_name = st.session_state.user_info['name']
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
    st.sidebar.write(f"**🔑 Role:** {u_role}")
    if u_role == "Technician":
         st.sidebar.write(f"**🛠️ Dept:** {u_dept}")
         st.sidebar.markdown("---")
         st.sidebar.write(f"**⭐ Points:** {u_points}")
         st.sidebar.write(f"**🏅 Rank:** {rank}")
    st.sidebar.markdown("---")
    if st.sidebar.button("Leave Plant 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # --- Header ---
    st.title(f"Welcome to {u_plant} Operations, {u_name}! 👋")
    st.markdown("---")
    
    # --- Tabs Setup بناءً على الصلاحيات ---
    if u_role == "Manager":
        tabs = st.tabs(["📊 Dashboard", "🛠️ Dispatch Hub", "📝 Log Task", "🧠 Plant Brain", "📦 Parts Request", "🤝 Handover", "⚡ Extras"])
        tab_dash, tab_action, tab_log, tab_brain, tab_parts, tab_handover, tab_extras = tabs
    else:
        tabs = st.tabs(["🎯 Action Hub", "📝 Log Task", "🧠 Plant Brain", "📦 Parts Request", "🤝 Handover", "⚡ Extras"])
        tab_action, tab_log, tab_brain, tab_parts, tab_handover, tab_extras = tabs

    # ------------------------------------------
    # MANAGER: DASHBOARD
    # ------------------------------------------
    if u_role == "Manager":
        with tab_dash:
            st.markdown("### 📊 Plant Operations Dashboard")
            c1, c2, c3 = st.columns(3)
            c1.metric("🔴 Active WROs", len(st.session_state.wro_pool), "Pending Tasks")
            c2.metric("🟢 Shift Completed Tasks", len(st.session_state.shift_log), "Good progress")
            c3.metric("🧠 Plant Brain Entries", len(st.session_state.plant_brain), "Knowledge Saved")
            
            st.markdown("#### 🏆 Plant Leaderboard")
            df_leaders = pd.DataFrame({
                "Technician": ["Ahmed (Mech)", "Khalid (Elec)", "Yasser (Weld)", f"{u_name}"],
                "Points": [850, 620, 510, u_points],
                "Rank": ["🏆 Plant Master", "⚡ Senior Tech", "⚡ Senior Tech", rank]
            }).sort_values(by="Points", ascending=False).reset_index(drop=True)
            st.dataframe(df_leaders, use_container_width=True)

    # ------------------------------------------
    # DISPATCH / ACTION HUB (Uber for Maint, Faza'a, Bounties)
    # ------------------------------------------
    with tab_action:
        if u_role == "Manager":
            st.markdown("### 🛠️ Dispatch Hub (Assign Tasks)")
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
                    st.markdown("#### 💰 Post a Bounty (Extra Task)")
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
            
            # 1. Uber WROs
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
                                st.success("You claimed this task! Go fix it and log it later.")
                                time.sleep(1)
                                st.rerun()

            # 2. Faza'a (Quick Assist)
            st.markdown("---")
            st.markdown("#### 🤝 Faza'a (Quick Assist)")
            with st.expander("Need help? Request a Faza'a"):
                fz_loc = st.text_input("📍 Your Location:")
                fz_need = st.text_input("🙋‍♂️ What do you need? (e.g., Lift heavy motor)")
                if st.button("📢 Ask for Faza'a", use_container_width=True):
                    if fz_loc:
                        st.session_state.fazaas.append({"id": random.randint(10,99), "req": u_name, "loc": fz_loc, "need": fz_need})
                        send_telegram_message(f"🤝 <b>Faza'a Needed!</b>\n📍 {fz_loc}\n🙋‍♂️ {u_name} needs: {fz_need}", u_plant)
                        st.success("Faza'a broadcasted!")
                        st.rerun()
            
            if st.session_state.fazaas:
                for fz in st.session_state.fazaas:
                    if fz['req'] != u_name:
                        st.warning(f"**{fz['req']}** at **{fz['loc']}** needs: {fz['need']}")
                        if st.button(f"🏃‍♂️ I'm coming! (+10 pts)", key=f"fz_{fz['id']}"):
                            st.session_state.user_points += 10
                            st.session_state.fazaas.remove(fz)
                            send_telegram_message(f"✅ <b>Faza'a Accepted!</b>\n{u_name} is going to help {fz['req']}.", u_plant)
                            st.success("You got +10 Points for helping a teammate!")
                            time.sleep(1)
                            st.rerun()

            # 3. Bounties
            st.markdown("---")
            st.markdown("#### 💰 Bounty Board (Extra Points)")
            if not st.session_state.bounties:
                st.info("No active bounties right now.")
            else:
                for b in st.session_state.bounties:
                    with st.container(border=True):
                        col_x, col_y = st.columns([3, 1])
                        with col_x:
                            st.write(f"**📌 Task:** {b['desc']}")
                            st.write(f"⭐ **Reward:** {b['points']} Points")
                        with col_y:
                            if st.button("✅ Complete", key=f"bnty_{b['id']}"):
                                st.session_state.user_points += b['points']
                                st.session_state.bounties.remove(b)
                                st.session_state.shift_log.append(f"Completed Bounty: {b['desc']}")
                                st.success(f"Awesome! You earned {b['points']} points.")
                                time.sleep(1)
                                st.rerun()

    # ------------------------------------------
    # TASK LOGGING & PLANT BRAIN
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
            with col_z: ppe_tools = st.checkbox("🔧 LOTO Confirmed")
            
        if st.button("✅ Submit Task (+50 Points)", type="primary", use_container_width=True):
            if not machine_name or not issue_desc:
                st.error("⚠️ Please fill in Machine Location and Description.")
            elif not (ppe_helmet and ppe_gloves and ppe_tools):
                st.error("⚠️ You must check all HSE boxes before submitting!")
            else:
                st.session_state.user_points += 50
                # Add to shift handover log
                st.session_state.shift_log.append(f"[{task_type[:5]}] {machine_name} - By {u_name}")
                
                # Add to Plant Brain if it's WRO
                if "WRO" in task_type:
                    st.session_state.plant_brain.append({
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "machine": machine_name,
                        "fix": issue_desc,
                        "tech": u_name
                    })
                
                send_telegram_message(f"✅ <b>Task Completed</b>\n🏭 <b>Plant:</b> {u_plant}\n📍 <b>Machine:</b> {machine_name}\n👨‍🔧 <b>Tech:</b> {u_name}", u_plant)
                st.success("🎉 Task logged successfully! Saved to Shift Log & Plant Brain.")
                st.balloons()
                time.sleep(2)
                st.rerun()

    with tab_brain:
        st.markdown("### 🧠 Plant Brain (Knowledge Base)")
        st.caption("Search past WRO solutions to fix machines faster.")
        
        search_q = st.text_input("🔍 Search Machine Name (e.g., Pump A):")
        
        if st.session_state.plant_brain:
            for entry in reversed(st.session_state.plant_brain):
                if search_q.lower() in entry['machine'].lower() or search_q == "":
                    with st.container(border=True):
                        st.markdown(f"**📍 Machine:** {entry['machine']} `({entry['date']})`")
                        st.markdown(f"**🔧 Solution:** {entry['fix']}")
                        st.markdown(f"👨‍🔧 *Fixed by: {entry['tech']}*")
        else:
            st.info("The Plant Brain is currently empty. Complete WROs to build knowledge!")

    # ------------------------------------------
    # PARTS REQUEST
    # ------------------------------------------
    with tab_parts:
        st.markdown("### 📦 Spare Parts Request (SAP Integrated)")
        if u_role == "Technician":
            with st.container(border=True):
                col1, col2 = st.columns(2)
                with col1:
                    part_desc = st.text_input("🛠️ Part Description:")
                    sap_number = st.text_input("🔢 SAP Material No:")
                with col2:
                    target_machine = st.text_input("📍 For which Machine?:")
                    urgency = st.selectbox("🚨 Urgency:", ["Normal 🟢", "Urgent 🔴"])
                
                if st.button("📤 Submit Request", type="primary"):
                    if part_desc and target_machine:
                        req_id = len(st.session_state.parts_requests) + 1
                        st.session_state.parts_requests.append({
                            "ID": req_id, "Technician": u_name, "Part": part_desc, 
                            "Machine": target_machine, "Status": "⏳ Pending"
                        })
                        st.session_state.shift_log.append(f"Requested Part: {part_desc}")
                        st.success(f"Request #{req_id} sent!")
                    else:
                        st.warning("Please fill Part and Machine.")
                        
            st.markdown("#### 📋 My Requests")
            df_req = pd.DataFrame(st.session_state.parts_requests)
            if not df_req.empty:
                st.dataframe(df_req[df_req['Technician'] == u_name], use_container_width=True)

        elif u_role == "Manager":
            df_req = pd.DataFrame(st.session_state.parts_requests)
            if not df_req.empty:
                st.dataframe(df_req, use_container_width=True)
                sel_id = st.number_input("Update Req ID:", min_value=1, max_value=len(st.session_state.parts_requests), step=1)
                action = st.selectbox("Action:", ["Mark as Done ✅", "Rejected ❌"])
                if st.button("💾 Update Status"):
                    for r in st.session_state.parts_requests:
                        if r["ID"] == sel_id: r["Status"] = action
                    st.success("Updated!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.info("No parts requests.")

    # ------------------------------------------
    # SHIFT HANDOVER (Auto-Summary)
    # ------------------------------------------
    with tab_handover:
        st.markdown("### 🤝 Smart Shift Handover")
        
        # Auto-generate summary based on session activity
        auto_summary = f"🔄 Shift Summary for {u_name}:\n"
        auto_summary += f"- Tasks & Bounties Completed: {len(st.session_state.shift_log)}\n"
        for log_item in st.session_state.shift_log:
            auto_summary += f"  > {log_item}\n"
            
        with st.container(border=True):
            shift_note = st.text_area("📝 Review & Add Handover Notes:", value=auto_summary, height=200)
            urgent_flag = st.checkbox("🚨 Mark as Urgent for next shift")
            
            if st.button("📤 Submit Shift Handover", use_container_width=True):
                urgency = "🔴 URGENT" if urgent_flag else "🟢 Normal"
                send_telegram_message(f"🤝 <b>Shift Handover ({urgency})</b>\n━━━━━━━━━━━━━━\n👨‍🔧 <b>From:</b> {u_name}\n📝 <b>Notes:</b>\n{shift_note}", u_plant)
                st.success("Handover logged! Next shift will be notified. Have a good rest!")
                # Clear shift log for the next day/shift if needed (optional)
                st.session_state.shift_log = []

    # ------------------------------------------
    # EXTRAS (SOS, Pit Stop, Reels)
    # ------------------------------------------
    with tab_extras:
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("### 🚨 SOS Broadcast")
                sos_loc = st.text_input("📍 Emergency Location:")
                if st.button("🚨 Broadcast SOS Now!", type="primary", use_container_width=True):
                    send_telegram_message(f"🚨 <b>SOS from {u_name}!</b>\n📍 {sos_loc}", u_plant)
                    st.error("🚨 SOS Broadcast Sent!")
                    
        with col2:
            with st.container(border=True):
                st.markdown("### 🏎️ F1 Pit Stop Challenge")
                pit_mac = st.text_input("⚙️ Machine Details:")
                if not st.session_state.pitstop_active:
                    if st.button("🏁 Start Timer"):
                        st.session_state.pitstop_active = True
                        st.session_state.start_time = time.time()
                        st.rerun()
                else:
                    st.warning("⏱️ CHALLENGE IS LIVE!")
                    if st.button("🛑 Stop Timer", type="primary"):
                        mins, secs = divmod(int(time.time() - st.session_state.start_time), 60)
                        st.session_state.pitstop_active = False
                        st.session_state.shift_log.append(f"Pit Stop on {pit_mac}: {mins}m {secs}s")
                        st.success(f"🎉 Time: {mins}m {secs}s")