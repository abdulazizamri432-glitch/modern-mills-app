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
PLANT_PASSWORDS = {"Al-Jumum": "Jumum123", "Al-Jouf": "Jouf123", "Khamis Mushait": "Khamis123"}
HQ_PASSWORD = "Admin123" 

def send_telegram_message(text, plant):
    chat_id = TELEGRAM_CHATS.get(plant)
    if not chat_id: return 
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try: requests.post(url, json=payload)
    except: pass

# ==========================================
# 🎨 التصميم الإبداعي (Cyberpunk & Glassmorphism)
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
    .ai-alert { border-left: 5px solid #ff4b4b; padding: 15px; background: rgba(255, 75, 75, 0.1); border-radius: 5px; margin-bottom: 15px; }
    .chat-bubble { background: rgba(0, 242, 254, 0.1); border-left: 4px solid #00f2fe; padding: 10px; border-radius: 5px; margin-bottom: 10px; font-family: monospace; }
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
if 'rolls_inventory' not in st.session_state: st.session_state.rolls_inventory = []
if 'plant_reels' not in st.session_state: st.session_state.plant_reels = []
if 'maint_tasks' not in st.session_state: st.session_state.maint_tasks = []
if 'predicted_sap_number' not in st.session_state: st.session_state.predicted_sap_number = ""
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

def get_filtered_data(data_list, current_plant, role):
    if role == "Director (HQ)": return data_list 
    return [item for item in data_list if item.get('plant') == current_plant]

def calculate_lifespan(install_date_str):
    if not install_date_str: return "N/A"
    install_date = datetime.strptime(install_date_str, "%Y-%m-%d")
    return f"{(datetime.now() - install_date).days} Days"

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
            time.sleep(0.01)
            progress_bar.progress(i + 1)
    st.session_state.splash_done = True
    st.rerun()

# ==========================================
# 2. LOGIN SYSTEM (تحديث حفظ الأقسام)
# ==========================================
elif not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container():
            st.markdown("<h2 style='text-align:center;'>🔒 Secure Plant Gateway</h2>", unsafe_allow_html=True)
            st.markdown("---")
            
            emp_name = st.text_input("👤 Operator Name", placeholder="e.g., Ahmed")
            emp_id = st.text_input("💳 Access ID", placeholder="e.g., 10452")
            
            col_a, col_b = st.columns(2)
            with col_a:
                plant = st.selectbox("🏭 Plant Node", ["Al-Jumum", "Khamis Mushait", "Al-Jouf"])
                role = st.selectbox("🔑 Clearance Level", ["Technician", "Manager", "Director (HQ)"])
            with col_b:
                if role == "Technician":
                    department = st.selectbox("🛠️ Division (القسم)", ["Mechanical", "Electrical", "Welding", "Operations", "Workshop"])
                    password = ""
                elif role == "Manager":
                    department = "Management"
                    password = st.text_input("🛡️ Manager Code", type="password")
                else: 
                    department = "HQ"
                    password = st.text_input("🛡️ HQ Master Code", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("INITIALIZE CONNECTION 🚀", type="primary", use_container_width=True):
                if not emp_name or not emp_id:
                    st.error("⚠️ Credentials Required.")
                elif role == "Manager" and password != PLANT_PASSWORDS.get(plant): 
                    st.error("❌ Invalid Manager Code!")
                elif role == "Director (HQ)" and password != HQ_PASSWORD:
                    st.error("❌ Invalid HQ Code!")
                else:
                    # حفظ بيانات الفني مع قسمه
                    if emp_id not in st.session_state.users_db:
                        st.session_state.users_db[emp_id] = {"points": random.randint(100, 250), "plant": plant, "name": emp_name, "dept": department, "role": role}
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
    st.sidebar.write(f"**🏢 Dept:** `{u_dept}`")
    
    if u_role == "Technician":
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
    
    # ==========================================
    # التبويبات المكتملة 
    # ==========================================
    if u_role == "Director (HQ)":
        tabs = st.tabs(["🔮 AI Twin", "🌐 Global KPIs", "🚨 Radar", "⚙️ Rolls", "📦 SAP HQ", "🤖 Plant-GPT"])
        tab_ai, tab_kpis, tab_radar, tab_rolls_hq, tab_sap_hq, tab_gpt = tabs
    elif u_role == "Manager":
        tabs = st.tabs(["🔮 AI Twin", "🤖 Plant-GPT", "📊 Dash", "⚙️ Rolls", "🔗 SAP", "🛠️ Dispatch", "📝 Log", "📅 Maint", "📦 Parts", "🧠 Brain", "🎬 Reels"])
        tab_ai, tab_gpt, tab_dash, tab_rolls, tab_sap, tab_action, tab_log, tab_maint, tab_parts, tab_brain, tab_reels = tabs
    else:
        tabs = st.tabs(["🎯 Action Hub", "🤖 Plant-GPT", "📝 Log", "⚙️ Rolls", "📅 Maint", "📦 Parts", "🧠 Brain", "🎬 Reels"])
        tab_action, tab_gpt, tab_log, tab_rolls, tab_maint, tab_parts, tab_brain, tab_reels = tabs

    # ==========================================
    # 🔮 AI DIGITAL TWIN & AUTOPILOT
    # ==========================================
    if u_role in ["Director (HQ)", "Manager"]:
        with tab_ai:
            st.markdown("### 🔮 Predictive AI Digital Twin")
            col_ai1, col_ai2 = st.columns([2, 1])
            with col_ai1:
                st.markdown("<div class='ai-alert'><b>🚨 CRITICAL PREDICTION:</b> Mill C - Main Shaft<br>Failure Probability: <b>98%</b> within 12 Hours.<br><i>Target Department: Mechanical</i></div>", unsafe_allow_html=True)
            with col_ai2:
                with st.container():
                    st.markdown("#### 🤖 AI AUTOPILOT")
                    if st.button("⚡ ACTIVATE AUTOPILOT", type="primary", use_container_width=True):
                        with st.spinner("AI taking control..."):
                            time.sleep(1)
                            st.session_state.parts_requests.append({"ID": random.randint(100, 999), "plant": u_plant if u_role == "Manager" else "Al-Jumum", "Technician": "AI System", "Part": "Main Shaft Bearing", "SAP_No": "1040092", "Machine": "Mill C", "Status": "SAP PO Triggered 🔄"})
                            # إرسال العطل لقسم الميكانيكا فقط!
                            st.session_state.wro_pool.append({"id": random.randint(1000, 9999), "plant": u_plant if u_role == "Manager" else "Al-Jumum", "target_dept": "Mechanical", "machine": "Mill C", "issue": "PREDICTIVE: Replace Bearing", "status": "Pending"})
                            send_telegram_message(f"🤖 <b>AI AUTOPILOT ACTIVATED</b>\n📍 Mill C\n✅ SAP PR Generated.\n✅ WRO Dispatched to [Mechanical] Dept.", u_plant if u_role == "Manager" else "Al-Jumum")
                            st.success("✅ AI Autopilot executed successfully!")

    # ==========================================
    # 🤖 PLANT-GPT 
    # ==========================================
    if u_role in ["Director (HQ)", "Manager", "Technician"]:
        with tab_gpt:
            st.markdown("### 🤖 Plant-GPT (MMC AI Assistant)")
            st.caption("Ask anything about plant history, SAP stock, or maintenance procedures.")
            for chat in st.session_state.chat_history:
                st.markdown(f"**🧑‍🔧 You:** {chat['user']}")
                st.markdown(f"<div class='chat-bubble'>🤖 <b>Plant-GPT:</b> {chat['ai']}</div>", unsafe_allow_html=True)
            user_q = st.text_input("Type your question here:")
            if st.button("Ask Plant-GPT ✨", type="primary"):
                if user_q:
                    with st.spinner("🧠 Searching Plant Brain & SAP..."):
                        time.sleep(1.5)
                        if "pump" in user_q.lower(): ai_resp = "Based on our records, خالد fixed Pump B 3 months ago by replacing the Mechanical Seal (SAP: 104558). Do you want me to order it for you?"
                        elif "sap" in user_q.lower() or "stock" in user_q.lower(): ai_resp = "I checked S/4HANA. We currently have 15 Thermal Pastes and 2 Bearings (Critical Low)."
                        else: ai_resp = "I have scanned the manuals. Ensure you apply LOTO first, then check the main drive belt tension."
                        st.session_state.chat_history.append({"user": user_q, "ai": ai_resp})
                        st.rerun()

    # ==========================================
    # 🌐 DIRECTOR (HQ) EXCLUSIVE VIEWS
    # ==========================================
    if u_role == "Director (HQ)":
        with tab_kpis:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Global Health", "96.4%", "+1.2% YTD")
            c2.metric("Prevented Downtime", "$145K", "+$22K")
            c3.metric("Pending WROs", len(st.session_state.wro_pool), "-2", delta_color="inverse")
            c4.metric("Active Tech Fleet", len(st.session_state.users_db))

        with tab_radar:
            st.markdown("### 🚨 Global Emergency Radar")
            if not st.session_state.wro_pool: st.success("✅ All plants are clear.")
            else:
                for wro in st.session_state.wro_pool:
                    with st.container():
                        st.error(f"**⚠️ {wro['plant'].upper()} | Dept: {wro.get('target_dept', 'All')}** | Loc: {wro['machine']} | Sig: {wro['issue']}")

        with tab_rolls_hq:
            st.markdown("### ⚙️ Global Milling Rolls")
            if st.session_state.rolls_inventory: st.dataframe(pd.DataFrame(st.session_state.rolls_inventory)[['plant', 'serial', 'type', 'status', 'machine']], use_container_width=True)

        with tab_sap_hq:
            st.markdown("### 📦 Global SAP Requests")
            if st.session_state.parts_requests: st.dataframe(pd.DataFrame(st.session_state.parts_requests)[['plant', 'Part', 'SAP_No', 'Status', 'Technician']], use_container_width=True)

    # ==========================================
    # 🏭 MANAGER VIEWS
    # ==========================================
    if u_role == "Manager":
        with tab_dash:
            my_wros = get_filtered_data(st.session_state.wro_pool, u_plant, u_role)
            my_maint = get_filtered_data(st.session_state.maint_tasks, u_plant, u_role)
            c1, c2, c3 = st.columns(3)
            c1.metric("🚨 Active WROs", len(my_wros), "Critical", delta_color="inverse")
            c2.metric("✅ Tasks Logged", len(get_filtered_data(st.session_state.shift_log, u_plant, u_role)))
            c3.metric("📅 Maint. Closed", len([t for t in my_maint if t['status'] == 'Completed']))

            # --- رادار الأقسام الجديد للمدير ---
            st.markdown("#### 🏢 Department Performance Matrix")
            plant_users = [v for k, v in st.session_state.users_db.items() if v["plant"] == u_plant and v["role"] == "Technician"]
            if plant_users:
                df_depts = pd.DataFrame(plant_users)
                # تجميع البيانات حسب القسم
                dept_stats = df_depts.groupby('dept').agg(Techs=('name', 'count'), Total_Points=('points', 'sum')).reset_index()
                st.dataframe(dept_stats, use_container_width=True)
            else:
                st.info("No technicians registered yet.")

        with tab_sap:
            st.markdown("### 🔗 SAP S/4HANA Middleware")
            with st.container():
                st.error("⚠️ **Critical Low Stock:** Bearings 6004-2RS (Mat #1040092)")
                if st.button("⚡ EXECUTE SAP PR INJECTION", type="primary"):
                    time.sleep(1.5)
                    send_telegram_message(f"🔗 <b>SAP Auto-System</b>\nGenerated PR for Material 1040092.", u_plant)
                    st.success("✅ PR successfully injected into SAP.")

    # ==========================================
    # 🎯 ACTION HUB & DISPATCH (تحديث توجيه الأقسام)
    # ==========================================
    if u_role in ["Manager", "Technician"]:
        with tab_action:
            if u_role == "Manager":
                st.markdown("### 🛠️ Dispatch Matrix")
                col1, col2 = st.columns(2)
                with col1:
                    wro_mac = st.text_input("📍 Equipment/Location:")
                    wro_desc = st.text_input("⚠️ Fault Signature:")
                    # المدير يختار القسم المطلوب
                    wro_target_dept = st.selectbox("🎯 Target Department:", ["All", "Mechanical", "Electrical", "Welding", "Operations", "Workshop"])
                    
                    if st.button("📢 DISPATCH WRO", type="primary", use_container_width=True) and wro_mac:
                        st.session_state.wro_pool.append({"id": random.randint(1000, 9999), "plant": u_plant, "target_dept": wro_target_dept, "machine": wro_mac, "issue": wro_desc, "status": "Pending"})
                        send_telegram_message(f"🚨 <b>CRITICAL WRO [{wro_target_dept}]</b>\n📍 {wro_mac}\n⚠️ {wro_desc}", u_plant)
                        st.success("Dispatched!")
                        time.sleep(1)
                        st.rerun()
                with col2:
                    bnty_desc = st.text_input("📌 Objective:")
                    bnty_pts = st.slider("⭐ Reward:", 10, 100, 30, step=10)
                    if st.button("💸 POST BOUNTY", use_container_width=True) and bnty_desc:
                        st.session_state.bounties.append({"id": random.randint(1000,9999), "plant": u_plant, "desc": bnty_desc, "points": bnty_pts})
                        send_telegram_message(f"💰 <b>NEW BOUNTY</b>\n📌 {bnty_desc} | ⭐ {bnty_pts} PTS", u_plant)
                        st.rerun()
            else:
                st.markdown("### 🎯 Live Grid")
                
                # الفزعة
                st.markdown("#### 🤝 Faza'a (Quick Assist)")
                with st.expander("Need help? Request Backup (+15 PTS)"):
                    fz_loc = st.text_input("📍 Your Location:", key="fz_loc")
                    fz_need = st.text_input("🙋‍♂️ What do you need?", key="fz_need")
                    if st.button("📢 Call for Faza'a", type="primary"):
                        if fz_loc and fz_need:
                            st.session_state.fazaas.append({"id": random.randint(10,99), "plant": u_plant, "req": u_name, "loc": fz_loc, "need": fz_need})
                            send_telegram_message(f"🤝 <b>Faza'a Needed!</b>\n📍 {fz_loc}\n🙋‍♂️ {u_name} needs: {fz_need}", u_plant)
                            st.rerun()
                my_fazaas = get_filtered_data(st.session_state.fazaas, u_plant, u_role)            
                if my_fazaas:
                    for fz in my_fazaas:
                        if fz['req'] != u_name:
                            with st.container():
                                st.warning(f"**{fz['req']}** at **{fz['loc']}** needs: {fz['need']}")
                                if st.button(f"🏃‍♂️ I'm coming! (+15 pts)", key=f"fz_{fz['id']}"):
                                    st.session_state.users_db[u_id]["points"] += 15
                                    st.session_state.fazaas.remove(fz)
                                    send_telegram_message(f"✅ <b>Faza'a Accepted!</b>\n{u_name} is going to help {fz['req']}.", u_plant)
                                    st.rerun()

                # عرض الأعطال المخصصة لقسم الفني فقط أو للجميع!
                st.markdown(f"#### 🚨 Active Anomalies (For Dept: {u_dept})")
                my_wros = [w for w in st.session_state.wro_pool if w['plant'] == u_plant and w.get('target_dept', 'All') in ['All', u_dept]]
                
                if not my_wros: st.info("No WROs assigned to your department right now.")
                for wro in my_wros:
                    with st.container():
                        st.write(f"**📍 Loc:** {wro['machine']} | **⚠️ Issue:** {wro['issue']} | 🏢 Dept: {wro.get('target_dept', 'All')}")
                        if st.button(f"⚡ INTERCEPT", key=f"wro_{wro['id']}", type="primary"):
                            st.session_state.wro_pool.remove(wro)
                            send_telegram_message(f"👨‍🔧 <b>WRO Claimed!</b>\n{u_name} ({u_dept}) is heading to {wro['machine']}.", u_plant)
                            st.rerun()

                st.markdown("#### 💰 Bounty Board")
                my_bounties = get_filtered_data(st.session_state.bounties, u_plant, u_role)
                if not my_bounties: st.info("No bounties.")
                for b in my_bounties:
                    with st.container():
                        st.write(f"**📌 {b['desc']}** | ⭐ {b['points']} PTS")
                        if st.button("✅ CLAIM", key=f"bnty_{b['id']}"):
                            st.session_state.users_db[u_id]["points"] += b['points'] 
                            st.session_state.bounties.remove(b)
                            send_telegram_message(f"✅ <b>Bounty Claimed!</b>\n👨‍🔧 By: {u_name}\n📌 {b['desc']}", u_plant)
                            st.rerun()

        # ==========================================
        # TASK LOGGING
        # ==========================================
        with tab_log:
            st.markdown("### 📝 Log Execution")
            task_type = st.radio("Classification", ["🔴 WRO", "🟢 PRO"], horizontal=True, label_visibility="collapsed")
            col1, col2 = st.columns(2)
            with col1: machine_name = st.text_input("📍 Equipment:")
            with col2: issue_desc = st.text_area("📝 Details:")
            proof_media = st.file_uploader("📸 Upload execution proof", type=["jpg", "png", "mp4"])
            if st.button("✅ COMMIT TO LOG (+50 PTS)", type="primary", use_container_width=True):
                if machine_name and issue_desc and proof_media:
                    st.session_state.users_db[u_id]["points"] += 50 
                    st.session_state.shift_log.append({"plant": u_plant, "log": f"[{task_type[:5]}] {machine_name} ({u_dept})", "user": u_name})
                    if "WRO" in task_type:
                        st.session_state.plant_brain.append({"plant": u_plant, "date": datetime.now().strftime("%Y-%m-%d"), "machine": machine_name, "fix": issue_desc, "tech": u_name})
                    send_telegram_message(f"✅ <b>Task Completed!</b>\n🏭 Plant: {u_plant}\n📍 Machine: {machine_name}\n👨‍🔧 Tech: {u_name} ({u_dept})\n📸 <i>Proof Uploaded</i>", u_plant)
                    st.success("Task logged!")
                    time.sleep(1)
                    st.rerun()
                else: st.error("⚠️ Fields and proof are mandatory.")

        # ==========================================
        # ROLLS WORKSHOP
        # ==========================================
        with tab_rolls:
            st.markdown("### ⚙️ Milling Rolls Workshop")
            my_rolls = get_filtered_data(st.session_state.rolls_inventory, u_plant, u_role)
            with st.container():
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.markdown("#### ➕ Add Ready Roll")
                    roll_sn = st.text_input("🔢 Serial Number:")
                    roll_type = st.selectbox("🛠️ Roll Type:", ["Break Roll", "Reduction Roll", "Smooth Roll"])
                    if st.button("💾 Save Roll", type="primary"):
                        if roll_sn:
                            st.session_state.rolls_inventory.append({"id": random.randint(10000, 99999), "plant": u_plant, "serial": roll_sn, "type": roll_type, "status": "🟢 Ready", "machine": "-", "install_date": None})
                            st.success("Saved!")
                            time.sleep(1)
                            st.rerun()
                with col_r2:
                    st.markdown("#### 🔧 Install Roll")
                    ready_rolls = [r for r in my_rolls if r['status'] == '🟢 Ready']
                    if not ready_rolls: st.info("No ready rolls.")
                    else:
                        selected_roll_sn = st.selectbox("Select Roll:", [r['serial'] for r in ready_rolls])
                        target_machine = st.text_input("📍 Machine Name:", key="roll_mac")
                        if st.button("⚙️ Confirm Install", type="primary") and target_machine:
                            for r in st.session_state.rolls_inventory:
                                if r['serial'] == selected_roll_sn and r['plant'] == u_plant:
                                    r['status'], r['machine'], r['install_date'] = "🔴 Installed", target_machine, datetime.now().strftime("%Y-%m-%d")
                            st.success("Installed!")
                            time.sleep(1)
                            st.rerun()

            st.markdown("#### 🔴 Active Rolls (Lifespan Tracker)")
            active_rolls = [r for r in my_rolls if r['status'] == '🔴 Installed']
            if active_rolls:
                for r in active_rolls: r['Age'] = calculate_lifespan(r['install_date'])
                st.dataframe(pd.DataFrame(active_rolls)[['serial', 'type', 'machine', 'Age']], use_container_width=True)

        # ==========================================
        # MAINTENANCE DAY
        # ==========================================
        with tab_maint:
            st.markdown("### 📅 Planned Maintenance Outage")
            if u_role == "Manager":
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    tech_name_assign = st.text_input("👤 Tech Name:")
                    tech_id_assign = st.text_input("💳 Tech ID:")
                with col_m2:
                    maint_task_desc = st.text_area("🛠️ Work Order Scope:")
                if st.button("📤 ALLOCATE", type="primary") and tech_id_assign:
                    st.session_state.maint_tasks.append({"id": random.randint(1000, 9999), "plant": u_plant, "tech_name": tech_name_assign, "tech_id": tech_id_assign, "desc": maint_task_desc, "status": "⏳ Pending", "assigned_by": u_name})
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
                                st.rerun()

        # ==========================================
        # 📦 INVENTORY 
        # ==========================================
        with tab_parts:
            st.markdown("### 📦 Supply Chain & Inventory")
            if u_role == "Technician":
                col1, col2 = st.columns(2)
                with col1:
                    part_desc = st.text_input("🛠️ Component Name:")
                    sap_number = st.text_input("🔢 SAP Code:", value=st.session_state.predicted_sap_number)
                with col2:
                    target_machine = st.text_input("📍 Destination:", key="dest_mac")
                if st.button("📤 TRANSMIT REQUEST", type="primary") and part_desc:
                    st.session_state.parts_requests.append({"ID": len(st.session_state.parts_requests)+1, "plant": u_plant, "Technician": u_name, "Part": part_desc, "SAP_No": sap_number, "Machine": target_machine, "Status": "⏳ Pending"})
                    st.session_state.predicted_sap_number = "" 
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
                            if r["ID"] == sel_id and r["plant"] == u_plant: 
                                r["Status"] = action
                        st.rerun()

        # ==========================================
        # BRAIN & REELS
        # ==========================================
        if u_role in ["Manager", "Technician"]:
            with tab_brain:
                st.markdown("### 🧠 AI Knowledge Base")
                my_brain = get_filtered_data(st.session_state.plant_brain, u_plant, u_role)
                for entry in reversed(my_brain):
                    with st.container():
                        st.markdown(f"**📍 {entry['machine']}** | 🔧 Fix: {entry['fix']} (By {entry['tech']})")

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