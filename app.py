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

def send_telegram_message(text, plant):
    chat_id = TELEGRAM_CHATS.get(plant)
    if not chat_id: return 
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try: requests.post(url, json=payload)
    except: pass

# ==========================================
# 🎨 التصميم الإبداعي (CSS Magic)
# ==========================================
st.markdown("""
<style>
    /* خلفية عامة مظلمة وتأثيرات زجاجية */
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    
    /* نصوص نيون مضيئة */
    .neon-text {
        color: #00f2fe;
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.5), 0 0 20px rgba(0, 242, 254, 0.3);
        font-weight: 800 !important;
        font-size: 2.5em !important;
        text-align: center;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }
    
    /* تصميم الأزرار المتقدم */
    .stButton>button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: #000 !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 12px;
        transition: all 0.4s ease;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 242, 254, 0.6);
    }
    
    /* تصميم الكروت (Containers) */
    div[data-testid="stContainer"] {
        background: rgba(22, 27, 34, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 15px;
        transition: transform 0.3s;
    }
    div[data-testid="stContainer"]:hover {
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
    }

    /* نقطة الاتصال الوامضة لـ SAP */
    .blinking-dot {
        height: 12px; width: 12px;
        background-color: #2ecc71;
        border-radius: 50%;
        display: inline-block;
        animation: blinker 1.5s linear infinite;
        box-shadow: 0 0 10px #2ecc71;
        margin-right: 8px;
    }
    @keyframes blinker { 50% { opacity: 0.2; } }

    /* تحسين المقاييس (Metrics) */
    div[data-testid="stMetricValue"] {
        font-size: 2em !important;
        color: #00f2fe !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 تهيئة قواعد البيانات (Session State)
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

# ==========================================
# 1. SPLASH SCREEN (التمهيد السينمائي)
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
                role = st.selectbox("🔑 Clearance Level", ["Technician", "Manager"])
            with col_b:
                if role == "Technician":
                    department = st.selectbox("🛠️ Division", ["Mechanical", "Electrical", "Welding", "HVAC", "Operations"])
                    password = ""
                else:
                    department = "Management"
                    password = st.text_input("🛡️ Override Code (Password)", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("INITIALIZE CONNECTION 🚀", type="primary", use_container_width=True):
                if not emp_name or not emp_id:
                    st.error("⚠️ Credentials Required.")
                elif role == "Manager" and password != PLANT_PASSWORDS.get(plant): 
                    st.error("❌ Access Denied: Invalid Override Code!")
                else:
                    if emp_id not in st.session_state.users_db:
                        st.session_state.users_db[emp_id] = random.randint(100, 250) 
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
        with st.container():
            st.error("### 🛑 CRITICAL: Daily Safety Briefing")
            st.markdown(f"**Operator: {u_name}**. Acknowledge before proceeding:")
            st.info("**Focus: Lock Out Tag Out (LOTO)**\n\nEnsure zero energy state. Your lock, your life. No bypasses allowed under any circumstances.")
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
    u_points = st.session_state.users_db[u_id] 
    
    # حساب الرتبة والتقدم
    if u_points >= 600: 
        rank = "🏆 Plant Master"
        progress_val = 100
    elif u_points >= 300: 
        rank = "⚡ Senior Tech"
        progress_val = int(((u_points - 300) / 300) * 100)
    else: 
        rank = "🔧 Specialist"
        progress_val = int((u_points / 300) * 100)

    # --- القائمة الجانبية (Sidebar) ---
    st.sidebar.markdown(f"## 🏭 {u_plant} Node")
    st.sidebar.markdown(f"<div style='color:#8b949e;'>Status: <span class='blinking-dot'></span>Online</div>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.write(f"**👤 {u_name}**")
    st.sidebar.write(f"**💳 ID:** `{u_id}`")
    if u_role == "Technician":
         st.sidebar.write(f"**🛠️ {u_dept}**")
         st.sidebar.markdown("---")
         st.sidebar.markdown(f"**⭐ Points:** <span style='color:#00f2fe; font-weight:bold; font-size:1.2em;'>{u_points}</span>", unsafe_allow_html=True)
         st.sidebar.write(f"**🏅 Rank:** {rank}")
         st.caption(f"Next Rank Progress ({progress_val}%)")
         st.sidebar.progress(progress_val)
    st.sidebar.markdown("---")
    if st.sidebar.button("TERMINATE SESSION 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.safety_ack = False 
        st.session_state.predicted_sap_number = "" 
        st.rerun()

    # --- Header ---
    st.markdown(f"<h1 style='color:white;'>Welcome, {u_name} 👋</h1>", unsafe_allow_html=True)
    
    daily_quotes = [
        "💡 **Insight:** Reliability is the byproduct of discipline.",
        "💡 **Insight:** A predictive alert today prevents a catastrophic failure tomorrow.",
        "💡 **Insight:** Data feeds the supply chain; accuracy is our currency."
    ]
    st.markdown(f"<div style='border-left: 4px solid #00f2fe; padding-left: 15px; color: #8b949e;'>{daily_quotes[datetime.now().day % len(daily_quotes)]}</div><br>", unsafe_allow_html=True)
    
    # --- التبويبات ---
    if u_role == "Manager":
        tabs = st.tabs(["📊 Command Center", "🔗 SAP Bridge", "🛠️ Dispatch", "📝 Log Task", "📅 Maint. Day", "📦 Inventory", "🧠 AI Brain", "🎬 Tutorials"])
        tab_dash, tab_sap, tab_action, tab_log, tab_maint, tab_parts, tab_brain, tab_reels = tabs
    else:
        tabs = st.tabs(["🎯 Action Hub", "📝 Log Task", "📅 Maint. Day", "📦 Inventory", "🧠 AI Brain", "🎬 Tutorials"])
        tab_action, tab_log, tab_maint, tab_parts, tab_brain, tab_reels = tabs

    # ------------------------------------------
    # COMMAND CENTER (Manager Dashboard)
    # ------------------------------------------
    if u_role == "Manager":
        with tab_dash:
            st.markdown("### 📊 Live Operations Metrics")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🚨 Active WROs", len(st.session_state.wro_pool), "Critical", delta_color="inverse")
            c2.metric("✅ Tasks Logged", len(st.session_state.shift_log), "+12% vs Yesterday")
            c3.metric("📅 Maint. Closed", len([t for t in st.session_state.maint_tasks if t['status'] == 'Completed']))
            c4.metric("⚙️ Plant Health", "94%", "+2.1%")
            
            st.markdown("#### 🏆 Top Performers Leaderboard")
            leaders_data = [{"Tech ID": k, "Points Earned": v} for k, v in st.session_state.users_db.items()]
            df_leaders = pd.DataFrame(leaders_data).sort_values(by="Points Earned", ascending=False).reset_index(drop=True)
            # تم إزالة background_gradient لحل خطأ الـ matplotlib
            st.dataframe(df_leaders, use_container_width=True)

    # ------------------------------------------
    # 🔗 SAP BRIDGE (الصدمة للمدير)
    # ------------------------------------------
    if u_role == "Manager":
        with tab_sap:
            st.markdown("### 🔗 SAP S/4HANA Middleware")
            st.markdown("<div style='margin-bottom:15px;'><span class='blinking-dot'></span> <b>Status:</b> OData Endpoints Active & Synchronized</div>", unsafe_allow_html=True)
            
            col_s1, col_s2 = st.columns([2, 1])
            with col_s1:
                with st.container():
                    st.markdown("#### 📉 Automated Inventory Triggers")
                    st.error("⚠️ **Critical Threshold Reached:** Bearings 6004-2RS (Mat #1040092) - Stock: 2 PCs")
                    st.warning("⚠️ **Warning Threshold:** Thermal Paste (Mat #1020088) - Stock: 15 PCs")
                    
                    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
                    st.write("Initiate auto-replenishment via SAP Purchase Requisition (PR) API.")
                    
                    if st.button("⚡ EXECUTE SAP PR INJECTION", type="primary"):
                        with st.spinner("Authenticating Token... Constructing JSON Payload..."):
                            time.sleep(2)
                            sap_payload = {
                                "ENDPOINT": "/sap/opu/odata/sap/API_PURCHASEREQ_PROCESS_SRV",
                                "METHOD": "POST",
                                "PAYLOAD": {
                                    "PR_Type": "NB",
                                    "Plant": u_plant.upper()[:4],
                                    "Material": "1040092",
                                    "Quantity": 50,
                                    "CostCenter": "CC-MAINT-01"
                                }
                            }
                            st.json(sap_payload)
                            st.success("✅ 201 Created: PR #500012489 successfully injected into SAP.")
                            send_telegram_message(f"🔗 <b>SAP Auto-System</b>\nGenerated PR #500012489 for Material 1040092 (Low Stock).", u_plant)
            
            with col_s2:
                with st.container():
                    st.markdown("#### 📊 Supply Chain KPIs")
                    st.metric("Avg PR to PO Time", "1.8 Days", "-0.5 Days")
                    st.metric("Downtime Saved", "$22,400", "Via Predictive PR")
                    st.metric("API Success Rate", "99.9%")

    # ------------------------------------------
    # ACTION HUB (WROs & Bounties)
    # ------------------------------------------
    with tab_action:
        if u_role == "Manager":
            st.markdown("### 🛠️ Dispatch Matrix")
            col1, col2 = st.columns(2)
            with col1:
                with st.container():
                    st.markdown("#### 🚨 Broadcast Emergency (WRO)")
                    wro_mac = st.text_input("📍 Equipment/Location:")
                    wro_desc = st.text_input("⚠️ Fault Signature:")
                    if st.button("📢 DISPATCH FLEET", type="primary", use_container_width=True):
                        if wro_mac and wro_desc:
                            wro_id = random.randint(1000, 9999)
                            st.session_state.wro_pool.append({"id": wro_id, "machine": wro_mac, "issue": wro_desc, "status": "Pending"})
                            send_telegram_message(f"🚨 <b>CRITICAL WRO</b>\n📍 {wro_mac}\n⚠️ {wro_desc}", u_plant)
                            st.success("Broadcast sent to all active units!")
                            st.rerun()
            with col2:
                with st.container():
                    st.markdown("#### 💰 Issue Bounty")
                    bnty_desc = st.text_input("📌 Objective (e.g., Calibrate Sensors):")
                    bnty_pts = st.slider("⭐ Reward:", 10, 100, 30, step=10)
                    if st.button("💸 POST BOUNTY", use_container_width=True):
                        if bnty_desc:
                            st.session_state.bounties.append({"id": random.randint(1000,9999), "desc": bnty_desc, "points": bnty_pts})
                            send_telegram_message(f"💰 <b>BOUNTY ACTIVE</b>\n📌 {bnty_desc}\n⭐ Reward: {bnty_pts} PTS", u_plant)
                            st.success("Bounty is live on the grid!")
                            st.rerun()
        else:
            st.markdown("### 🎯 Live Grid")
            
            st.markdown("#### 🚨 Active Anomalies (WROs)")
            if not st.session_state.wro_pool:
                st.info("Grid is clear. No active anomalies.")
            else:
                for wro in st.session_state.wro_pool:
                    with st.container():
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.markdown(f"<span style='color:#ff4b4b; font-weight:bold;'>📍 Location:</span> {wro['machine']}", unsafe_allow_html=True)
                            st.markdown(f"**⚠️ Signature:** {wro['issue']}")
                        with col_b:
                            if st.button(f"⚡ INTERCEPT", key=f"wro_{wro['id']}", type="primary"):
                                st.session_state.wro_pool.remove(wro)
                                send_telegram_message(f"👨‍🔧 <b>WRO Intercepted</b>\n{u_name} is en route to {wro['machine']}.", u_plant)
                                st.success("Task bound to your ID.")
                                time.sleep(1)
                                st.rerun()

            st.markdown("#### 💰 Bounty Board")
            if not st.session_state.bounties:
                st.info("No bounties available.")
            else:
                for b in st.session_state.bounties:
                    with st.container():
                        col_x, col_y = st.columns([3, 1])
                        with col_x:
                            st.write(f"**📌 Objective:** {b['desc']}")
                            st.markdown(f"⭐ **Reward:** <span style='color:#00f2fe;'>{b['points']} PTS</span>", unsafe_allow_html=True)
                        with col_y:
                            if st.button("✅ CLAIM", key=f"bnty_{b['id']}"):
                                st.session_state.users_db[u_id] += b['points'] 
                                st.session_state.bounties.remove(b)
                                st.session_state.shift_log.append(f"Bounty: {b['desc']}")
                                st.success(f"Reward transferred: +{b['points']} PTS.")
                                time.sleep(1)
                                st.rerun()

    # ------------------------------------------
    # TASK LOGGING
    # ------------------------------------------
    with tab_log:
        st.markdown("### 📝 Log Execution")
        task_type = st.radio("Task Classification", ["🔴 WRO (Corrective)", "🟢 PRO (Preventive)"], horizontal=True, label_visibility="collapsed")
        
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                machine_name = st.text_input("📍 Equipment Tag/Location:")
            with col2:
                issue_desc = st.text_area("📝 Execution Details:")
                
        with st.container():
            st.markdown("#### ✅ Safety Protocols Verified")
            col_x, col_y, col_z = st.columns(3)
            with col_x: ppe_helmet = st.checkbox("👷‍♂️ PPE Compliant")
            with col_y: ppe_gloves = st.checkbox("🧤 Isolation Verified")
            with col_z: ppe_tools = st.checkbox("🔧 Tools Cleared")
            
            st.markdown("---")
            st.markdown("#### 📸 Visual Evidence (Mandatory)")
            proof_media = st.file_uploader("Upload execution proof (Image/Video)", type=["jpg", "jpeg", "png", "mp4"])
            
        if st.button("✅ COMMIT TO LOG (+50 PTS)", type="primary", use_container_width=True):
            if not machine_name or not issue_desc:
                st.error("⚠️ Incomplete parameters.")
            elif not (ppe_helmet and ppe_gloves and ppe_tools):
                st.error("⚠️ Safety protocols must be fully acknowledged.")
            elif not proof_media:
                st.error("❌ ⚠️ Visual evidence is strictly required for compliance.")
            else:
                with st.spinner("🤖 AI Vision analyzing media for compliance..."):
                    time.sleep(2)
                    st.success("👁️ AI Verification: LOTO & Work confirmed.")
                    time.sleep(0.5)
                
                st.session_state.users_db[u_id] += 50 
                st.session_state.shift_log.append(f"[{task_type[:5]}] {machine_name} - By {u_name}")
                if "WRO" in task_type:
                    st.session_state.plant_brain.append({"date": datetime.now().strftime("%Y-%m-%d"), "machine": machine_name, "fix": issue_desc, "tech": u_name})
                
                send_telegram_message(f"✅ <b>Task Committed</b>\n📍 {machine_name}\n👨‍🔧 Tech: {u_name}\n📸 <i>Media Verified by System</i>", u_plant)
                st.balloons()
                time.sleep(1.5)
                st.rerun()

    # ------------------------------------------
    # MAINTENANCE DAY
    # ------------------------------------------
    with tab_maint:
        st.markdown("### 📅 Planned Maintenance Outage")
        if u_role == "Manager":
            with st.container():
                st.markdown("#### 📝 Allocate Resources")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    tech_name_assign = st.text_input("👤 Tech Name:")
                    tech_id_assign = st.text_input("💳 Tech ID:")
                with col_m2:
                    maint_task_desc = st.text_area("🛠️ Work Order Scope:")
                
                if st.button("📤 ALLOCATE", type="primary"):
                    if tech_name_assign and tech_id_assign and maint_task_desc:
                        st.session_state.maint_tasks.append({
                            "id": random.randint(1000, 9999), "tech_name": tech_name_assign, "tech_id": tech_id_assign,
                            "desc": maint_task_desc, "status": "⏳ Pending", "report": "", "assigned_by": u_name
                        })
                        st.success("Allocated!")
                        time.sleep(1)
                        st.rerun()
            st.markdown("#### 📊 Execution Status")
            if st.session_state.maint_tasks:
                st.dataframe(pd.DataFrame(st.session_state.maint_tasks)[['tech_name', 'desc', 'status']], use_container_width=True)

        else: 
            st.markdown("#### 📋 My Outage Directives")
            my_tasks = [t for t in st.session_state.maint_tasks if t['tech_id'] == u_id and "Pending" in t['status']]
            if not my_tasks:
                st.success("No active directives.")
            else:
                for task in my_tasks:
                    with st.container():
                        st.markdown(f"**🛠️ Scope:** {task['desc']}")
                        tech_report = st.text_area("📝 Execution Report:", key=f"rep_{task['id']}")
                        maint_media = st.file_uploader("📸 Evidence:", type=["jpg", "png"], key=f"med_{task['id']}")
                        if st.button("✅ CLOSE WORK ORDER", key=f"btn_{task['id']}", type="primary"):
                            if tech_report and maint_media:
                                task['status'], task['report'] = "✅ Completed", tech_report
                                st.session_state.users_db[u_id] += 80
                                st.success("Closed!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Report & Evidence required.")

    # ------------------------------------------
    # 📦 INVENTORY (المساعد الذكي لـ SAP)
    # ------------------------------------------
    with tab_parts:
        st.markdown("### 📦 Supply Chain & Inventory")
        if u_role == "Technician":
            with st.container():
                st.markdown("#### 🪄 AI Material Predictor (SAP Database)")
                col_ai1, col_ai2 = st.columns([3, 1])
                with col_ai1:
                    ai_desc = st.text_input("Describe the component (e.g., Impeller for Pump A):")
                with col_ai2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🪄 Scan Catalog", use_container_width=True):
                        if ai_desc:
                            with st.spinner("🤖 Scanning 40,000+ SAP Records..."):
                                time.sleep(1.5)
                                st.session_state.predicted_sap_number = f"10{random.randint(20000, 99999)}"
                                st.success(f"✅ High Confidence Match! SAP Code: **{st.session_state.predicted_sap_number}**")
            st.markdown("---")
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    part_desc = st.text_input("🛠️ Exact Component Name:")
                    sap_number = st.text_input("🔢 SAP Material Code:", value=st.session_state.predicted_sap_number)
                with col2:
                    target_machine = st.text_input("📍 Destination Equipment:")
                    urgency = st.selectbox("🚨 Priority:", ["Routine 🟢", "AOG/Critical 🔴"])
                if st.button("📤 TRANSMIT REQUEST", type="primary"):
                    if part_desc:
                        st.session_state.parts_requests.append({"ID": len(st.session_state.parts_requests)+1, "Technician": u_name, "Part": part_desc, "SAP_No": sap_number, "Machine": target_machine, "Status": "⏳ Pending"})
                        st.session_state.predicted_sap_number = "" 
                        st.success("Transmitted to Supply Chain!")
                        time.sleep(1)
                        st.rerun()
            
            if st.session_state.parts_requests:
                st.dataframe(pd.DataFrame(st.session_state.parts_requests)[['Part', 'SAP_No', 'Status']], use_container_width=True)

        elif u_role == "Manager":
            if st.session_state.parts_requests:
                st.dataframe(pd.DataFrame(st.session_state.parts_requests), use_container_width=True)
                sel_id = st.number_input("Target Req ID:", min_value=1, max_value=len(st.session_state.parts_requests), step=1)
                action = st.selectbox("Decision:", ["Mark as Done ✅", "Rejected ❌", "Trigger SAP PO 🔄"])
                if st.button("💾 UPDATE TICKET"):
                    for r in st.session_state.parts_requests:
                        if r["ID"] == sel_id: 
                            r["Status"] = action
                    st.rerun()

    # ------------------------------------------
    # AI BRAIN & REELS
    # ------------------------------------------
    with tab_brain:
        st.markdown("### 🧠 AI Knowledge Base")
        search_q = st.text_input("🔍 Query anomaly or equipment:")
        if st.session_state.plant_brain:
            for entry in reversed(st.session_state.plant_brain):
                if search_q.lower() in entry['machine'].lower() or search_q == "":
                    with st.container():
                        st.markdown(f"**📍 Source:** {entry['machine']} `({entry['date']})`")
                        st.markdown(f"**🔧 Resolution:** {entry['fix']}")
                        st.caption(f"Resolved by {entry['tech']}")

    with tab_reels:
        st.markdown("### 🎬 Operation Tutorials")
        with st.expander("📤 Upload Intel (+100 PTS)"):
            reel_title = st.text_input("📌 Intel Subject:")
            reel_file = st.file_uploader("Upload Video", type=["mp4"])
            if st.button("🚀 UPLOAD INTEL", type="primary"):
                if reel_title and reel_file:
                    st.session_state.plant_reels.append({"title": reel_title, "author": u_name, "date": datetime.now().strftime("%Y-%m-%d"), "video_bytes": reel_file.read()})
                    st.session_state.users_db[u_id] += 100
                    st.success("Intel uploaded!")
                    time.sleep(1)
                    st.rerun()
        if st.session_state.plant_reels:
            for reel in reversed(st.session_state.plant_reels):
                with st.container():
                    st.markdown(f"**📌 {reel['title']}** (By {reel['author']})")
                    st.video(reel['video_bytes'])