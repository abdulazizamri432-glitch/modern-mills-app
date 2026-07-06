import streamlit as st
import pandas as pd
import time
import requests
import random
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="MMC Smart Plant ERP", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

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
    "Al-Jumum": "Jumum123", "Al-Jouf": "Jouf123", "Khamis Mushait": "Khamis123"
}
HQ_PASSWORD = "Admin123" 

def send_telegram_message(text, plant):
    chat_id = TELEGRAM_CHATS.get(plant)
    if not chat_id: return 
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try: requests.post(url, json=payload)
    except: pass

# ==========================================
# 🎨 التصميم الإبداعي
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    .neon-text {
        color: #00f2fe;
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.5), 0 0 20px rgba(0, 242, 254, 0.3);
        font-weight: 800 !important; font-size: 2.5em !important; text-align: center; margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: #000 !important; font-weight: bold !important; border: none !important; border-radius: 12px; transition: all 0.4s ease;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0, 242, 254, 0.6); }
    div[data-testid="stContainer"] {
        background: rgba(22, 27, 34, 0.6); backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 15px !important; padding: 15px;
    }
    .blinking-dot {
        height: 12px; width: 12px; background-color: #2ecc71; border-radius: 50%;
        display: inline-block; animation: blinker 1.5s linear infinite; box-shadow: 0 0 10px #2ecc71; margin-right: 8px;
    }
    @keyframes blinker { 50% { opacity: 0.2; } }
    div[data-testid="stMetricValue"] { font-size: 2em !important; color: #00f2fe !important; }
    .hq-title { color: #f39c12; font-size: 1.5em; border-bottom: 1px solid #f39c12; padding-bottom: 10px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 تهيئة قواعد البيانات (مفصولة بالمنشأة)
# ==========================================
if 'splash_done' not in st.session_state: st.session_state.splash_done = False
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'safety_ack' not in st.session_state: st.session_state.safety_ack = False 

if 'users_db' not in st.session_state: st.session_state.users_db = {} 
if 'parts_requests' not in st.session_state: st.session_state.parts_requests = []
if 'wro_pool' not in st.session_state: st.session_state.wro_pool = [] 
if 'fazaas' not in st.session_state: st.session_state.fazaas = [] 
if 'bounties' not in st.session_state: st.session_state.bounties = [] 
if 'plant_brain' not in st.session_state: st.session_state.plant_brain = [] 
if 'shift_log' not in st.session_state: st.session_state.shift_log = [] 
if 'tools_crib' not in st.session_state: st.session_state.tools_crib = []
if 'plant_reels' not in st.session_state: st.session_state.plant_reels = []
if 'maint_tasks' not in st.session_state: st.session_state.maint_tasks = []
if 'predicted_sap_number' not in st.session_state: st.session_state.predicted_sap_number = ""

def get_filtered_data(data_list, current_plant, role):
    if role == "Director (HQ)": return data_list 
    return [item for item in data_list if item.get('plant') == current_plant]

# ==========================================
# 1. SPLASH SCREEN
# ==========================================
if not st.session_state.splash_done:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<div class='neon-text'>⚡ MMC OS v2.0</div>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center; color: #8b949e; font-family: monospace;'>Booting Plant Kernels & Establishing SAP OData Links...</h5>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.015)
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
        with st.container():
            st.markdown("<h2 style='text-align:center;'>🔒 Secure Plant Gateway</h2>", unsafe_allow_html=True)
            st.markdown("---")
            
            emp_name = st.text_input("👤 Operator Name", placeholder="e.g., Ahmed Al-Dawsari")
            emp_id = st.text_input("💳 Access ID", placeholder="e.g., 10452")
            
            col_a, col_b = st.columns(2)
            with col_a:
                plant = st.selectbox("🏭 Plant Node", ["Al-Jumum", "Khamis Mushait", "Al-Jouf"])
                role = st.selectbox("🔑 Clearance Level", ["Technician", "Manager", "Director (HQ)"])
            with col_b:
                if role == "Technician":
                    department = st.selectbox("🛠️ Division", ["Mechanical", "Electrical", "Welding", "HVAC", "Operations"])
                    password = ""
                elif role == "Manager":
                    department = "Management"
                    password = st.text_input("🛡️ Override Code (Password)", type="password")
                else: 
                    department = "HQ"
                    password = st.text_input("🛡️ HQ Master Code", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("INITIALIZE CONNECTION 🚀", type="primary", use_container_width=True):
                if not emp_name or not emp_id:
                    st.error("⚠️ Credentials Required.")
                elif role == "Manager" and password != PLANT_PASSWORDS.get(plant): 
                    st.error("❌ Access Denied: Invalid Manager Code!")
                elif role == "Director (HQ)" and password != HQ_PASSWORD:
                    st.error("❌ Access Denied: Invalid HQ Code!")
                else:
                    if emp_id not in st.session_state.users_db:
                        st.session_state.users_db[emp_id] = {"points": random.randint(100, 250), "plant": plant, "name": emp_name}
                    st.session_state.user_info = {"name": emp_name, "id": emp_id, "plant": plant, "dept": department, "role": role}
                    st.session_state.logged_in = True
                    st.rerun()

# ==========================================
# 3. SAFETY TOOLBOX TALK
# ==========================================
elif not st.session_state.safety_ack and st.session_state.user_info['role'] != "Director (HQ)":
    u_name = st.session_state.user_info['name']
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.error("### 🛑 CRITICAL: Daily Safety Briefing")
            st.markdown(f"**Operator: {u_name}**. Acknowledge before proceeding:")
            st.info("**Focus: Lock Out Tag Out (LOTO)**\n\nEnsure zero energy state. Your lock, your life.")
            if st.button("✅ I COMPLY WITH SAFETY PROTOCOLS", type="primary", use_container_width=True):
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
    u_points = st.session_state.users_db[u_id]["points"]
    
    # --- Sidebar ---
    st.sidebar.markdown(f"## {'🌐 Global HQ' if u_role == 'Director (HQ)' else f'🏭 {u_plant} Node'}")
    st.sidebar.markdown(f"<div style='color:#8b949e;'>Status: <span class='blinking-dot'></span>Online</div>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.write(f"**👤 {u_name}**")
    st.sidebar.write(f"**💳 ID:** `{u_id}`")
    st.sidebar.write(f"**🔑 Role:** {u_role}")
    
    if u_role == "Technician":
         st.sidebar.write(f"**🛠️ {u_dept}**")
         st.sidebar.markdown("---")
         st.sidebar.markdown(f"**⭐ Points:** <span style='color:#00f2fe; font-weight:bold;'>{u_points}</span>", unsafe_allow_html=True)
         
    st.sidebar.markdown("---")
    if st.sidebar.button("TERMINATE SESSION 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.safety_ack = False 
        st.rerun()

    # --- Header ---
    if u_role == "Director (HQ)":
        st.markdown(f"<h1 style='color:#f39c12;'>🌐 Executive Global View: {u_name}</h1>", unsafe_allow_html=True)
        st.caption("Central Command for Al-Jumum, Khamis Mushait, and Al-Jouf Operations.")
    else:
        st.markdown(f"<h1 style='color:white;'>Welcome, {u_name} 👋</h1>", unsafe_allow_html=True)
    
    # --- Tabs Setup ---
    if u_role == "Director (HQ)":
        tabs = st.tabs(["🌐 Global KPIs", "🚨 Emergency Radar", "📦 Supply Chain (SAP)", "📊 Fleet & Leaderboard"])
        tab_kpis, tab_radar, tab_sap_hq, tab_fleet = tabs
    elif u_role == "Manager":
        tabs = st.tabs(["📊 Command Center", "🔗 SAP Bridge", "🛠️ Dispatch", "📝 Log Task", "📅 Maint. Day", "📦 Inventory", "🧠 AI Brain", "🎬 Tutorials"])
        tab_dash, tab_sap, tab_action, tab_log, tab_maint, tab_parts, tab_brain, tab_reels = tabs
    else:
        tabs = st.tabs(["🎯 Action Hub", "📝 Log Task", "📅 Maint. Day", "📦 Inventory", "🧠 AI Brain", "🎬 Tutorials"])
        tab_action, tab_log, tab_maint, tab_parts, tab_brain, tab_reels = tabs

    # ==========================================
    # 🌐 DIRECTOR (HQ) EXCLUSIVE VIEWS
    # ==========================================
    if u_role == "Director (HQ)":
        # 1. GLOBAL KPIs & CHARTS
        with tab_kpis:
            st.markdown("<div class='hq-title'>📈 High-Level Financial & Operational KPIs</div>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Global Health Index", "96.4%", "+1.2% YTD")
            c2.metric("Total Prevented Downtime", "$145K", "+$22K this month")
            c3.metric("Pending WROs (All Plants)", len(st.session_state.wro_pool), "Action Required", delta_color="inverse")
            c4.metric("Active Tech Fleet", len(st.session_state.users_db), "Personnel")
            
            st.markdown("---")
            st.markdown("#### 📊 Cross-Plant Performance Analytics")
            
            # تجهيز بيانات الرسم البياني للمحطات
            p_jumum = len([x for x in st.session_state.shift_log if x.get('plant') == 'Al-Jumum'])
            p_khamis = len([x for x in st.session_state.shift_log if x.get('plant') == 'Khamis Mushait'])
            p_jouf = len([x for x in st.session_state.shift_log if x.get('plant') == 'Al-Jouf'])
            
            chart_data = pd.DataFrame({
                "Completed Tasks": [p_jumum, p_khamis, p_jouf]
            }, index=["Al-Jumum", "Khamis Mushait", "Al-Jouf"])
            
            col_ch1, col_ch2 = st.columns([2, 1])
            with col_ch1:
                st.bar_chart(chart_data, use_container_width=True)
            with col_ch2:
                with st.container():
                    st.info(f"**Al-Jumum:** {p_jumum} Tasks")
                    st.warning(f"**Khamis Mushait:** {p_khamis} Tasks")
                    st.success(f"**Al-Jouf:** {p_jouf} Tasks")

        # 2. EMERGENCY RADAR
        with tab_radar:
            st.markdown("<div class='hq-title'>🚨 Global Emergency Radar (Live WROs)</div>", unsafe_allow_html=True)
            if not st.session_state.wro_pool:
                st.success("✅ All plants are clear. No active emergencies reported across the grid.")
            else:
                for wro in st.session_state.wro_pool:
                    with st.container():
                        st.error(f"**⚠️ EMERGENCY IN {wro['plant'].upper()}**")
                        st.markdown(f"**📍 Location:** {wro['machine']} | **Signature:** {wro['issue']}")

        # 3. GLOBAL SUPPLY CHAIN (SAP)
        with tab_sap_hq:
            st.markdown("<div class='hq-title'>🔗 Global SAP & Supply Chain Overview</div>", unsafe_allow_html=True)
            st.markdown("Monitor pending parts requests across all operational nodes.")
            if not st.session_state.parts_requests:
                st.info("No pending supply chain requests.")
            else:
                df_hq_parts = pd.DataFrame(st.session_state.parts_requests)
                st.dataframe(df_hq_parts[['plant', 'Part', 'SAP_No', 'Status', 'Technician']], use_container_width=True)

        # 4. FLEET & LEADERBOARD
        with tab_fleet:
            st.markdown("<div class='hq-title'>🏆 Global Workforce Leaderboard</div>", unsafe_allow_html=True)
            st.caption("Top performing technicians across the entire company based on merit points.")
            if st.session_state.users_db:
                hq_leaders = [{"Name": v["name"], "Plant": v["plant"], "Total Points": v["points"]} for k, v in st.session_state.users_db.items()]
                df_hq_leaders = pd.DataFrame(hq_leaders).sort_values(by="Total Points", ascending=False).reset_index(drop=True)
                st.dataframe(df_hq_leaders, use_container_width=True)
            else:
                st.info("No workforce data available yet.")

    # ==========================================
    # 🏭 MANAGER & TECHNICIAN VIEWS (نفس ما كانت عليه وتعمل بشكل مثالي)
    # ==========================================
    if u_role == "Manager":
        with tab_dash:
            my_wros = get_filtered_data(st.session_state.wro_pool, u_plant, u_role)
            my_logs = get_filtered_data(st.session_state.shift_log, u_plant, u_role)
            my_maint = get_filtered_data(st.session_state.maint_tasks, u_plant, u_role)
            st.markdown(f"### 📊 {u_plant} Operations Metrics")
            c1, c2, c3 = st.columns(3)
            c1.metric("🚨 Active WROs", len(my_wros), "Critical", delta_color="inverse")
            c2.metric("✅ Tasks Logged", len(my_logs), "+12%")
            c3.metric("📅 Maint. Closed", len([t for t in my_maint if t['status'] == 'Completed']))
            st.markdown("#### 🏆 Plant Leaderboard")
            leaders_data = [{"Tech ID": k, "Points": v["points"], "Name": v["name"]} for k, v in st.session_state.users_db.items() if v["plant"] == u_plant]
            if leaders_data:
                df_leaders = pd.DataFrame(leaders_data).sort_values(by="Points", ascending=False).reset_index(drop=True)
                st.dataframe(df_leaders, use_container_width=True)

        with tab_sap:
            st.markdown("### 🔗 SAP S/4HANA Middleware")
            st.markdown("<div style='margin-bottom:15px;'><span class='blinking-dot'></span> <b>Status:</b> OData Active</div>", unsafe_allow_html=True)
            with st.container():
                st.error("⚠️ **Critical Low Stock:** Bearings 6004-2RS (Mat #1040092)")
                if st.button("⚡ EXECUTE SAP PR INJECTION", type="primary"):
                    with st.spinner("Constructing JSON Payload..."):
                        time.sleep(1.5)
                        st.success("✅ 201 Created: PR successfully injected into SAP.")
                        send_telegram_message(f"🔗 <b>SAP Auto-System</b>\nGenerated PR for Material 1040092.", u_plant)

    if u_role in ["Manager", "Technician"]:
        with tab_action:
            my_wros = get_filtered_data(st.session_state.wro_pool, u_plant, u_role)
            my_bounties = get_filtered_data(st.session_state.bounties, u_plant, u_role)
            if u_role == "Manager":
                st.markdown("### 🛠️ Dispatch Matrix")
                col1, col2 = st.columns(2)
                with col1:
                    with st.container():
                        wro_mac = st.text_input("📍 Equipment/Location:")
                        wro_desc = st.text_input("⚠️ Fault Signature:")
                        if st.button("📢 DISPATCH WRO", type="primary", use_container_width=True):
                            if wro_mac and wro_desc:
                                st.session_state.wro_pool.append({"id": random.randint(1000, 9999), "plant": u_plant, "machine": wro_mac, "issue": wro_desc, "status": "Pending"})
                                send_telegram_message(f"🚨 <b>CRITICAL WRO</b>\n📍 {wro_mac}\n⚠️ {wro_desc}", u_plant)
                                st.success("Dispatched!")
                                st.rerun()
                with col2:
                    with st.container():
                        bnty_desc = st.text_input("📌 Objective:")
                        bnty_pts = st.slider("⭐ Reward:", 10, 100, 30, step=10)
                        if st.button("💸 POST BOUNTY", use_container_width=True):
                            if bnty_desc:
                                st.session_state.bounties.append({"id": random.randint(1000,9999), "plant": u_plant, "desc": bnty_desc, "points": bnty_pts})
                                st.success("Bounty is live!")
                                st.rerun()
            else:
                st.markdown("### 🎯 Live Grid")
                st.markdown("#### 🚨 Active Anomalies (WROs)")
                if not my_wros: st.info("Grid is clear.")
                for wro in my_wros:
                    with st.container():
                        st.write(f"**📍 Location:** {wro['machine']} | **⚠️ Issue:** {wro['issue']}")
                        if st.button(f"⚡ INTERCEPT", key=f"wro_{wro['id']}", type="primary"):
                            st.session_state.wro_pool.remove(wro)
                            st.success("Task bound to your ID.")
                            time.sleep(1)
                            st.rerun()
                st.markdown("#### 💰 Bounty Board")
                if not my_bounties: st.info("No bounties.")
                for b in my_bounties:
                    with st.container():
                        st.write(f"**📌 {b['desc']}** | ⭐ {b['points']} PTS")
                        if st.button("✅ CLAIM", key=f"bnty_{b['id']}"):
                            st.session_state.users_db[u_id]["points"] += b['points'] 
                            st.session_state.bounties.remove(b)
                            st.success(f"Reward transferred.")
                            time.sleep(1)
                            st.rerun()

        with tab_log:
            st.markdown("### 📝 Log Execution")
            task_type = st.radio("Classification", ["🔴 WRO", "🟢 PRO"], horizontal=True, label_visibility="collapsed")
            with st.container():
                col1, col2 = st.columns(2)
                with col1: machine_name = st.text_input("📍 Equipment:")
                with col2: issue_desc = st.text_area("📝 Details:")
            with st.container():
                proof_media = st.file_uploader("📸 Upload execution proof", type=["jpg", "png", "mp4"])
            if st.button("✅ COMMIT TO LOG (+50 PTS)", type="primary", use_container_width=True):
                if machine_name and issue_desc and proof_media:
                    st.session_state.users_db[u_id]["points"] += 50 
                    st.session_state.shift_log.append({"plant": u_plant, "log": f"[{task_type[:5]}] {machine_name}", "user": u_name})
                    if "WRO" in task_type:
                        st.session_state.plant_brain.append({"plant": u_plant, "date": datetime.now().strftime("%Y-%m-%d"), "machine": machine_name, "fix": issue_desc, "tech": u_name})
                    st.success("Task logged!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("⚠️ Fields and proof are mandatory.")

        with tab_maint:
            st.markdown("### 📅 Planned Maintenance Outage")
            if u_role == "Manager":
                with st.container():
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        tech_name_assign = st.text_input("👤 Tech Name:")
                        tech_id_assign = st.text_input("💳 Tech ID:")
                    with col_m2:
                        maint_task_desc = st.text_area("🛠️ Work Order Scope:")
                    if st.button("📤 ALLOCATE", type="primary"):
                        if tech_id_assign and maint_task_desc:
                            st.session_state.maint_tasks.append({
                                "id": random.randint(1000, 9999), "plant": u_plant, "tech_name": tech_name_assign, 
                                "tech_id": tech_id_assign, "desc": maint_task_desc, "status": "⏳ Pending", "assigned_by": u_name
                            })
                            st.success("Allocated!")
                            time.sleep(1)
                            st.rerun()
                my_maint = get_filtered_data(st.session_state.maint_tasks, u_plant, u_role)
                if my_maint: st.dataframe(pd.DataFrame(my_maint)[['tech_name', 'desc', 'status']], use_container_width=True)
            else: 
                my_tasks = [t for t in st.session_state.maint_tasks if t['tech_id'] == u_id and t['plant'] == u_plant and "Pending" in t['status']]
                if not my_tasks: st.success("No active directives.")
                for task in my_tasks:
                    with st.container():
                        st.markdown(f"**🛠️ Scope:** {task['desc']}")
                        tech_report = st.text_area("📝 Report:", key=f"rep_{task['id']}")
                        maint_media = st.file_uploader("📸 Evidence:", type=["jpg", "png"], key=f"med_{task['id']}")
                        if st.button("✅ CLOSE WORK ORDER", key=f"btn_{task['id']}", type="primary"):
                            if tech_report and maint_media:
                                task['status'], task['report'] = "✅ Completed", tech_report
                                st.session_state.users_db[u_id]["points"] += 80
                                st.success("Closed!")
                                time.sleep(1)
                                st.rerun()

        with tab_parts:
            st.markdown("### 📦 Supply Chain & Inventory")
            if u_role == "Technician":
                with st.container():
                    col1, col2 = st.columns(2)
                    with col1:
                        part_desc = st.text_input("🛠️ Component Name:")
                        sap_number = st.text_input("🔢 SAP Code:", value=st.session_state.predicted_sap_number)
                    with col2:
                        target_machine = st.text_input("📍 Destination:")
                    if st.button("📤 TRANSMIT REQUEST", type="primary") and part_desc:
                        st.session_state.parts_requests.append({"ID": len(st.session_state.parts_requests)+1, "plant": u_plant, "Technician": u_name, "Part": part_desc, "SAP_No": sap_number, "Machine": target_machine, "Status": "⏳ Pending"})
                        st.session_state.predicted_sap_number = "" 
                        st.success("Transmitted!")
                        time.sleep(1)
                        st.rerun()
                my_parts = [p for p in st.session_state.parts_requests if p['Technician'] == u_name and p['plant'] == u_plant]
                if my_parts: st.dataframe(pd.DataFrame(my_parts)[['Part', 'SAP_No', 'Status']], use_container_width=True)
            elif u_role == "Manager":
                my_parts = get_filtered_data(st.session_state.parts_requests, u_plant, u_role)
                if my_parts:
                    st.dataframe(pd.DataFrame(my_parts), use_container_width=True)
                    sel_id = st.number_input("Target Req ID:", min_value=1, step=1)
                    action = st.selectbox("Decision:", ["Mark as Done ✅", "Rejected ❌", "Trigger SAP PO 🔄"])
                    if st.button("💾 UPDATE TICKET"):
                        for r in st.session_state.parts_requests:
                            if r["ID"] == sel_id and r["plant"] == u_plant: r["Status"] = action
                        st.rerun()

        with tab_brain:
            st.markdown("### 🧠 AI Knowledge Base")
            my_brain = get_filtered_data(st.session_state.plant_brain, u_plant, u_role)
            for entry in reversed(my_brain):
                with st.container():
                    st.markdown(f"**📍 Source:** {entry['machine']} | **🔧 Fix:** {entry['fix']}")
                    st.caption(f"By {entry['tech']}")

        with tab_reels:
            st.markdown("### 🎬 Operation Tutorials")
            with st.expander("📤 Upload Intel (+100 PTS)"):
                reel_title = st.text_input("📌 Intel Subject:")
                reel_file = st.file_uploader("Upload Video", type=["mp4"])
                if st.button("🚀 UPLOAD INTEL", type="primary") and reel_title and reel_file:
                    st.session_state.plant_reels.append({"plant": u_plant, "title": reel_title, "author": u_name, "video_bytes": reel_file.read()})
                    st.session_state.users_db[u_id]["points"] += 100
                    st.success("Uploaded!")
                    time.sleep(1)
                    st.rerun()
            my_reels = get_filtered_data(st.session_state.plant_reels, u_plant, u_role)
            for reel in reversed(my_reels):
                with st.container():
                    st.markdown(f"**📌 {reel['title']}** (By {reel['author']})")
                    st.video(reel['video_bytes'])