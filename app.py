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
# 🎨 التصميم الإبداعي (الدلع)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    .neon-text {
        color: #00f2fe; text-shadow: 0 0 10px rgba(0, 242, 254, 0.5), 0 0 20px rgba(0, 242, 254, 0.3);
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
# 🧠 تهيئة قواعد البيانات
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
if 'rolls_inventory' not in st.session_state: st.session_state.rolls_inventory = []

def get_filtered_data(data_list, current_plant, role):
    if role == "Director (HQ)": return data_list 
    return [item for item in data_list if item.get('plant') == current_plant]

def calculate_lifespan(install_date_str):
    if not install_date_str: return "N/A"
    install_date = datetime.strptime(install_date_str, "%Y-%m-%d")
    days_active = (datetime.now() - install_date).days
    return f"{days_active} Days"

# ==========================================
# 1. SPLASH SCREEN
# ==========================================
if not st.session_state.splash_done:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<div class='neon-text'>⚡ MMC OS v2.0</div>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center; color: #8b949e;'>Booting Plant Kernels & Establishing SAP OData Links...</h5>", unsafe_allow_html=True)
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
                    department = st.selectbox("🛠️ Division", ["Mechanical", "Electrical", "Welding", "HVAC", "Operations", "Workshop"])
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
    else:
        st.markdown(f"<h1 style='color:white;'>Welcome, {u_name} 👋</h1>", unsafe_allow_html=True)
    
    # --- Tabs Setup ---
    if u_role == "Director (HQ)":
        tabs = st.tabs(["🌐 Global KPIs", "🚨 Radar", "⚙️ Rolls", "🔗 SAP Integration", "📊 Fleet"])
        tab_kpis, tab_radar, tab_rolls_hq, tab_sap_hq, tab_fleet = tabs
    elif u_role == "Manager":
        tabs = st.tabs(["📊 Command Center", "🔗 SAP Bridge", "⚙️ Rolls", "🛠️ Dispatch", "📝 Log Task", "📅 Maint.", "📦 Inventory", "🧠 Brain", "🎬 Reels"])
        tab_dash, tab_sap, tab_rolls, tab_action, tab_log, tab_maint, tab_parts, tab_brain, tab_reels = tabs
    else:
        tabs = st.tabs(["🎯 Action Hub", "📝 Log Task", "⚙️ Rolls", "📅 Maint.", "📦 Inventory", "🧠 Brain", "🎬 Reels"])
        tab_action, tab_log, tab_rolls, tab_maint, tab_parts, tab_brain, tab_reels = tabs

    # ==========================================
    # 🌐 DIRECTOR (HQ) EXCLUSIVE VIEWS
    # ==========================================
    if u_role == "Director (HQ)":
        with tab_kpis:
            st.markdown("<div class='hq-title'>📈 High-Level Operational KPIs</div>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Global Health Index", "96.4%", "+1.2% YTD")
            c2.metric("Prevented Downtime", "$145K", "+$22K this month")
            c3.metric("Pending WROs", len(st.session_state.wro_pool), "Action Required", delta_color="inverse")
            c4.metric("Active Tech Fleet", len(st.session_state.users_db), "Personnel")

        with tab_radar:
            st.markdown("<div class='hq-title'>🚨 Global Emergency Radar</div>", unsafe_allow_html=True)
            if not st.session_state.wro_pool: st.success("✅ All plants are clear.")
            else:
                for wro in st.session_state.wro_pool:
                    with st.container():
                        st.error(f"**⚠️ EMERGENCY IN {wro['plant'].upper()}** | 📍 {wro['machine']} | Signature: {wro['issue']}")

        with tab_rolls_hq:
            st.markdown("<div class='hq-title'>⚙️ Global Milling Rolls Inventory</div>", unsafe_allow_html=True)
            all_rolls = st.session_state.rolls_inventory
            if not all_rolls: st.info("No rolls registered.")
            else:
                for r in all_rolls: r['Age (Days)'] = calculate_lifespan(r['install_date'])
                st.dataframe(pd.DataFrame(all_rolls)[['plant', 'serial', 'type', 'status', 'machine', 'Age (Days)']], use_container_width=True)

        with tab_sap_hq:
            st.markdown("<div class='hq-title'>🔗 Global Supply Chain (SAP OData)</div>", unsafe_allow_html=True)
            if not st.session_state.parts_requests: st.info("No pending requests.")
            else: st.dataframe(pd.DataFrame(st.session_state.parts_requests)[['plant', 'Part', 'SAP_No', 'Status', 'Technician']], use_container_width=True)

        with tab_fleet:
            st.markdown("<div class='hq-title'>🏆 Global Workforce Leaderboard</div>", unsafe_allow_html=True)
            if st.session_state.users_db:
                hq_leaders = [{"Name": v["name"], "Plant": v["plant"], "Points": v["points"]} for k, v in st.session_state.users_db.items()]
                st.dataframe(pd.DataFrame(hq_leaders).sort_values(by="Points", ascending=False).reset_index(drop=True), use_container_width=True)

    # ==========================================
    # 🔗 SAP BRIDGE (دلع المدير)
    # ==========================================
    if u_role == "Manager":
        with tab_sap:
            st.markdown("### 🔗 SAP S/4HANA Middleware")
            st.caption("This hub acts as a middle-layer between Plant Operations and SAP via OData APIs.")
            
            col_s1, col_s2 = st.columns([2, 1])
            with col_s1:
                with st.container():
                    st.markdown("#### ⚠️ Live Inventory Alerts (Synced with SAP)")
                    st.error("📉 **Critical Low Stock:** Bearings 6004-2RS (SAP Material #1040092)")
                    
                    st.markdown("#### 🔄 Auto-Generate Purchase Requisition (PR)")
                    if st.button("⚡ EXECUTE SAP PR INJECTION", type="primary"):
                        with st.spinner("Authenticating with SAP & Generating Payload..."):
                            time.sleep(1.5)
                            sap_payload = {
                                "POST": "/sap/opu/odata/sap/API_PURCHASEREQ_PROCESS_SRV",
                                "Payload": {"PR_Type": "NB", "Plant": u_plant.upper()[:4], "Material": "1040092", "Quantity": 50}
                            }
                            st.json(sap_payload)
                            st.success("✅ 201 Created: PR #500012489 successfully injected into SAP.")
                            send_telegram_message(f"🔗 <b>SAP Alert</b>\nGenerated PR for Material 1040092 (Low Stock).", u_plant)
            with col_s2:
                with st.container():
                    st.markdown("#### 📊 Metrics")
                    st.metric("Avg Part Delivery", "3.2 Days", "-12%")
                    st.metric("Downtime Saved", "$14,500")

    # ==========================================
    # ⚙️ ROLLS WORKSHOP
    # ==========================================
    if u_role in ["Manager", "Technician"]:
        with tab_rolls:
            st.markdown("### ⚙️ Milling Rolls Workshop")
            my_rolls = get_filtered_data(st.session_state.rolls_inventory, u_plant, u_role)
            
            with st.container():
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.markdown("#### ➕ Register Ready Roll")
                    roll_sn = st.text_input("🔢 Roll Serial Number:")
                    roll_type = st.selectbox("🛠️ Roll Type:", ["Break Roll", "Reduction Roll", "Smooth Roll"])
                    if st.button("💾 Add to Inventory", type="primary") and roll_sn:
                        st.session_state.rolls_inventory.append({
                            "id": random.randint(10000, 99999), "plant": u_plant, "serial": roll_sn, 
                            "type": roll_type, "status": "🟢 Ready", "machine": "-", "install_date": None, "added_by": u_name
                        })
                        st.success(f"Added!")
                        st.rerun()
                with col_r2:
                    st.markdown("#### 🔧 Install Roll")
                    ready_rolls = [r for r in my_rolls if r['status'] == '🟢 Ready']
                    if not ready_rolls: st.info("No 'Ready' rolls available.")
                    else:
                        selected_roll_sn = st.selectbox("Select Roll:", [r['serial'] for r in ready_rolls])
                        target_machine = st.text_input("📍 Machine Name (e.g., Mill A):")
                        if st.button("⚙️ Confirm Installation", type="primary") and target_machine:
                            for r in st.session_state.rolls_inventory:
                                if r['serial'] == selected_roll_sn and r['plant'] == u_plant:
                                    r['status'], r['machine'], r['install_date'] = "🔴 Installed", target_machine, datetime.now().strftime("%Y-%m-%d")
                            send_telegram_message(f"⚙️ <b>Roll Installed!</b>\n📍 {target_machine}\n🔢 SN: {selected_roll_sn}", u_plant)
                            st.success(f"Installed successfully!")
                            st.rerun()

            st.markdown("#### 🟢 Ready Rolls")
            df_ready = pd.DataFrame([r for r in my_rolls if r['status'] == '🟢 Ready'])
            if not df_ready.empty: st.dataframe(df_ready[['serial', 'type', 'added_by']], use_container_width=True)
            
            st.markdown("#### 🔴 Active Rolls (Lifespan Tracker)")
            active_rolls = [r for r in my_rolls if r['status'] == '🔴 Installed']
            if active_rolls:
                for r in active_rolls: r['Age (Days)'] = calculate_lifespan(r['install_date'])
                st.dataframe(pd.DataFrame(active_rolls)[['serial', 'type', 'machine', 'install_date', 'Age (Days)']], use_container_width=True)

    # ==========================================
    # 📦 INVENTORY (دلع الذكاء الاصطناعي)
    # ==========================================
    if u_role in ["Manager", "Technician"]:
        with tab_parts:
            st.markdown("### 📦 Supply Chain & Inventory")
            if u_role == "Technician":
                with st.container():
                    st.markdown("#### 🪄 AI SAP Material Predictor")
                    st.caption("Don't know the SAP number? Describe the part and let the AI find it.")
                    col_ai1, col_ai2 = st.columns([3, 1])
                    with col_ai1:
                        ai_desc = st.text_input("Describe component (e.g., Impeller for Pump A):")
                    with col_ai2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🪄 Scan Catalog", use_container_width=True):
                            if ai_desc:
                                with st.spinner("🤖 Scanning 40,000+ SAP Records..."):
                                    time.sleep(1.5)
                                    st.session_state.predicted_sap_number = f"10{random.randint(20000, 99999)}"
                                    st.success(f"✅ Match Found! SAP: **{st.session_state.predicted_sap_number}** (94% Acc)")
                            else: st.warning("Describe part first.")
                
                st.markdown("---")
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

    # ==========================================
    # MANAGER DASHBOARD (Regular)
    # ==========================================
    if u_role == "Manager":
        with tab_dash:
            my_wros = get_filtered_data(st.session_state.wro_pool, u_plant, u_role)
            my_logs = get_filtered_data(st.session_state.shift_log, u_plant, u_role)
            st.markdown(f"### 📊 {u_plant} Metrics")
            c1, c2, c3 = st.columns(3)
            c1.metric("🚨 Active WROs", len(my_wros), "Critical", delta_color="inverse")
            c2.metric("✅ Tasks Logged", len(my_logs), "+12%")
            st.markdown("#### 🏆 Plant Leaderboard")
            leaders_data = [{"Tech ID": k, "Points": v["points"], "Name": v["name"]} for k, v in st.session_state.users_db.items() if v["plant"] == u_plant]
            if leaders_data: st.dataframe(pd.DataFrame(leaders_data).sort_values(by="Points", ascending=False).reset_index(drop=True), use_container_width=True)

    # ==========================================
    # ACTION HUB & LOG TASK (AI Vision)
    # ==========================================
    if u_role in ["Manager", "Technician"]:
        with tab_action:
            my_wros = get_filtered_data(st.session_state.wro_pool, u_plant, u_role)
            my_bounties = get_filtered_data(st.session_state.bounties, u_plant, u_role)
            if u_role == "Manager":
                col1, col2 = st.columns(2)
                with col1:
                    wro_mac = st.text_input("📍 Equipment/Location:")
                    wro_desc = st.text_input("⚠️ Fault Signature:")
                    if st.button("📢 DISPATCH WRO", type="primary") and wro_mac:
                        st.session_state.wro_pool.append({"id": random.randint(1000, 9999), "plant": u_plant, "machine": wro_mac, "issue": wro_desc, "status": "Pending"})
                        st.rerun()
                with col2:
                    bnty_desc = st.text_input("📌 Objective:")
                    bnty_pts = st.slider("⭐ Reward:", 10, 100, 30, step=10)
                    if st.button("💸 POST BOUNTY", type="primary") and bnty_desc:
                        st.session_state.bounties.append({"id": random.randint(1000,9999), "plant": u_plant, "desc": bnty_desc, "points": bnty_pts})
                        st.rerun()
            else:
                for wro in my_wros:
                    with st.container():
                        st.write(f"**📍 Location:** {wro['machine']} | **⚠️ Issue:** {wro['issue']}")
                        if st.button(f"⚡ INTERCEPT", key=f"wro_{wro['id']}", type="primary"):
                            st.session_state.wro_pool.remove(wro)
                            st.rerun()

        with tab_log:
            st.markdown("### 📝 Log Execution")
            task_type = st.radio("Classification", ["🔴 WRO", "🟢 PRO"], horizontal=True, label_visibility="collapsed")
            col1, col2 = st.columns(2)
            with col1: machine_name = st.text_input("📍 Equipment:")
            with col2: issue_desc = st.text_area("📝 Details:")
            proof_media = st.file_uploader("📸 Upload execution proof", type=["jpg", "png", "mp4"])
            if st.button("✅ COMMIT TO LOG (+50 PTS)", type="primary", use_container_width=True):
                if machine_name and issue_desc and proof_media:
                    with st.spinner("🤖 AI Vision analyzing media for LOTO compliance..."):
                        time.sleep(2)
                        st.success("👁️ AI Verification: LOTO Confirmed.")
                        time.sleep(0.5)
                    st.session_state.users_db[u_id]["points"] += 50 
                    st.session_state.shift_log.append({"plant": u_plant, "log": f"[{task_type[:5]}] {machine_name}", "user": u_name})
                    st.rerun()
                else:
                    st.error("⚠️ All fields and proof are mandatory.")

        # MAINTENANCE DAY
        with tab_maint:
            st.markdown("### 📅 Planned Maintenance Outage")
            if u_role == "Manager":
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    tech_name_assign = st.text_input("👤 Tech Name:")
                    tech_id_assign = st.text_input("💳 Tech ID:")
                with col_m2: maint_task_desc = st.text_area("🛠️ Work Order Scope:")
                if st.button("📤 ALLOCATE", type="primary") and tech_id_assign:
                    st.session_state.maint_tasks.append({"id": random.randint(1000, 9999), "plant": u_plant, "tech_name": tech_name_assign, "tech_id": tech_id_assign, "desc": maint_task_desc, "status": "⏳ Pending", "assigned_by": u_name})
                    st.rerun()
            else: 
                my_tasks = [t for t in st.session_state.maint_tasks if t['tech_id'] == u_id and t['plant'] == u_plant and "Pending" in t['status']]
                for task in my_tasks:
                    with st.container():
                        st.markdown(f"**🛠️ Scope:** {task['desc']}")
                        tech_report = st.text_area("📝 Report:", key=f"rep_{task['id']}")
                        maint_media = st.file_uploader("📸 Evidence:", type=["jpg", "png"], key=f"med_{task['id']}")
                        if st.button("✅ CLOSE WORK ORDER", key=f"btn_{task['id']}", type="primary") and tech_report and maint_media:
                            task['status'], task['report'] = "✅ Completed", tech_report
                            st.session_state.users_db[u_id]["points"] += 80
                            st.rerun()

        # AI BRAIN & REELS
        with tab_brain:
            st.markdown("### 🧠 AI Knowledge Base")
            my_brain = get_filtered_data(st.session_state.plant_brain, u_plant, u_role)
            for entry in reversed(my_brain):
                with st.container():
                    st.markdown(f"**📍 Source:** {entry['machine']} | **🔧 Fix:** {entry['fix']}")

        with tab_reels:
            st.markdown("### 🎬 Operation Tutorials")
            with st.expander("📤 Upload Intel (+100 PTS)"):
                reel_title = st.text_input("📌 Intel Subject:")
                reel_file = st.file_uploader("Upload Video", type=["mp4"])
                if st.button("🚀 UPLOAD INTEL", type="primary") and reel_title and reel_file:
                    st.session_state.plant_reels.append({"plant": u_plant, "title": reel_title, "author": u_name, "video_bytes": reel_file.read()})
                    st.session_state.users_db[u_id]["points"] += 100
                    st.rerun()
            my_reels = get_filtered_data(st.session_state.plant_reels, u_plant, u_role)
            for reel in reversed(my_reels):
                with st.container():
                    st.markdown(f"**📌 {reel['title']}** (By {reel['author']})")
                    st.video(reel['video_bytes'])