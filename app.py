import streamlit as st
import pandas as pd
import time
import requests
import random
import json
import os
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="MMC Smart Plant ERP", page_icon="⚡", layout="wide")

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

# --- دالة الإشعارات مع نظام التأكيد ---
def send_smart_notification(title, message, category, plant, target_dept="All"):
    chat_id = TELEGRAM_CHATS.get(plant)
    if not chat_id: 
        st.toast("⚠️ لم يتم العثور على جروب لهذا الفرع", icon="⚠️")
        return 
    
    icons = {'CRITICAL': '🚨', 'INFO': 'ℹ️', 'TASK': '🛠️', 'REWARD': '🏆'}
    txt = f"{icons.get(category, '🔔')} <b>{title}</b>\n\n{message}\n\n🏢 القسم: {target_dept}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": txt, "parse_mode": "HTML"}
    
    try: 
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            st.toast(f"📩 تم الإرسال لفرع {plant} بنجاح!", icon="✅")
        else:
            st.toast(f"❌ خطأ تليجرام: تأكد أن البوت أدمن", icon="❌")
    except Exception: 
        st.toast("🔌 لا يوجد اتصال إنترنت", icon="🔌")

# ==========================================
# 💾 قاعدة البيانات الدائمة (JSON)
# ==========================================
DB_FILE = "mmc_database.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"users": {}, "wro": [], "parts": [], "rolls": [], "maint": [], "log": [], "bounties": [], "fazaas": []}

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(st.session_state.db, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = load_db()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def calculate_lifespan(install_date_str):
    if not install_date_str: return "N/A"
    install_date = datetime.strptime(install_date_str, "%Y-%m-%d")
    return f"{(datetime.now() - install_date).days} Days"

# ==========================================
# 🎨 التصميم
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    .neon-text { color: #00f2fe; text-shadow: 0 0 10px rgba(0, 242, 254, 0.5); font-weight: 800; font-size: 2.5em; text-align: center; margin-bottom: 20px;}
    div[data-testid="stContainer"] { background: rgba(22, 27, 34, 0.6); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 15px; }
    .ai-alert { border-left: 5px solid #ff4b4b; padding: 15px; background: rgba(255, 75, 75, 0.1); border-radius: 5px; margin-bottom: 15px; }
    .chat-bubble { background: rgba(0, 242, 254, 0.1); border-left: 4px solid #00f2fe; padding: 10px; border-radius: 5px; margin-bottom: 10px; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 نظام التسجيل والدخول
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<div class='neon-text'>⚡ MMC Smart Plant ERP</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container():
            tab_login, tab_register = st.tabs(["🔑 Login", "📝 Sign Up"])
            
            with tab_register:
                reg_name = st.text_input("👤 Full Name:")
                reg_id = st.text_input("💳 Employee ID:")
                reg_pass = st.text_input("🛡️ Password:", type="password")
                c_a, c_b = st.columns(2)
                with c_a:
                    reg_plant = st.selectbox("🏭 Plant:", ["Al-Jumum", "Khamis Mushait", "Al-Jouf"])
                    reg_role = st.selectbox("🔑 Role:", ["Technician", "Manager", "Director (HQ)"])
                with c_b:
                    if reg_role == "Technician":
                        reg_dept = st.selectbox("🛠️ Dept:", ["Mechanical", "Electrical", "Welding", "Operations", "Workshop"])
                        reg_auth = ""
                    elif reg_role == "Manager":
                        reg_dept = "Management"
                        reg_auth = st.text_input("Manager Code:", type="password")
                    else:
                        reg_dept = "HQ"
                        reg_auth = st.text_input("HQ Code:", type="password")
                
                if st.button("Create Account ✅", use_container_width=True):
                    if not reg_name or not reg_id or not reg_pass:
                        st.error("All fields are mandatory.")
                    elif reg_id in st.session_state.db['users']:
                        st.error("ID already exists!")
                    elif reg_role == "Manager" and reg_auth != PLANT_PASSWORDS.get(reg_plant):
                        st.error("Invalid Manager Code!")
                    elif reg_role == "Director (HQ)" and reg_auth != HQ_PASSWORD:
                        st.error("Invalid HQ Code!")
                    else:
                        st.session_state.db['users'][reg_id] = {
                            "name": reg_name, "password": reg_pass, "plant": reg_plant, 
                            "role": reg_role, "dept": reg_dept, "points": 0, "chat": []
                        }
                        save_db()
                        st.success("Account Created! You can login now.")
            
            with tab_login:
                log_id = st.text_input("💳 ID:", key="log_id")
                log_pass = st.text_input("🛡️ Pass:", type="password", key="log_pass")
                if st.button("LOGIN 🚀", use_container_width=True):
                    if log_id in st.session_state.db['users'] and st.session_state.db['users'][log_id]['password'] == log_pass:
                        st.session_state.user_info = st.session_state.db['users'][log_id]
                        st.session_state.user_info['id'] = log_id
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Invalid ID or Password.")

# ==========================================
# 4. MAIN APPLICATION
# ==========================================
else:
    u = st.session_state.user_info
    
    # القائمة الجانبية
    st.sidebar.markdown(f"## {u['plant']} Node" if u['role'] != 'Director (HQ)' else "## 🌐 Global HQ")
    st.sidebar.write(f"**👤 {u['name']}** ({u['dept']})")
    if u['role'] == "Technician":
        st.sidebar.write(f"⭐ Points: **{u['points']}**")
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout 🚪"):
        st.session_state.logged_in = False
        st.rerun()

    # عبارة كل يوم (Daily Quote)
    st.markdown(f"<h1 style='color:white;'>Welcome, {u['name']} 👋</h1>", unsafe_allow_html=True)
    daily_quotes = [
        "💡 Insight: Reliability is the byproduct of discipline.",
        "💡 Insight: A predictive alert today prevents a catastrophic failure tomorrow.",
        "💡 Insight: Data feeds the supply chain; accuracy is our currency."
    ]
    st.markdown(f"<div style='border-left: 4px solid #00f2fe; padding-left: 15px; color: #8b949e;'>{daily_quotes[datetime.now().day % len(daily_quotes)]}</div><br>", unsafe_allow_html=True)

    # التبويبات حسب الصلاحيات
    if u['role'] == "Director (HQ)":
        tabs = st.tabs(["🔮 AI Twin", "🌐 Global KPIs", "🚨 Radar", "⚙️ Rolls", "📦 SAP", "📥 Export"])
        t_ai, t_dash, t_radar, t_rolls, t_parts, t_export = tabs
    elif u['role'] == "Manager":
        tabs = st.tabs(["🔮 AI Twin", "📊 Dash", "🤖 Plant-GPT", "🛠️ Dispatch", "⚙️ Rolls", "📅 Maint", "📦 SAP", "📥 Export"])
        t_ai, t_dash, t_gpt, t_action, t_rolls, t_maint, t_parts, t_export = tabs
    else:
        tabs = st.tabs(["🎯 Tasks Hub", "🤖 Plant-GPT", "📝 Log", "⚙️ Rolls", "📅 Maint", "📦 Parts"])
        t_action, t_gpt, t_log, t_rolls, t_maint, t_parts = tabs

    # ==========================================
    # 🔮 AI DIGITAL TWIN & AUTOPILOT
    # ==========================================
    if u['role'] in ["Manager", "Director (HQ)"]:
        with t_ai:
            st.markdown("### 🔮 Predictive AI Digital Twin")
            st.markdown("<div class='ai-alert'><b>🚨 CRITICAL PREDICTION:</b> Mill C - Main Shaft<br>Failure Probability: <b>98%</b> within 12 Hours.<br><i>Target Department: Mechanical</i></div>", unsafe_allow_html=True)
            if st.button("⚡ ACTIVATE AUTOPILOT", type="primary"):
                st.session_state.db['parts'].append({"ID": random.randint(100, 999), "plant": u['plant'] if u['role'] == 'Manager' else 'Al-Jumum', "Technician": "AI System", "Part": "Main Shaft Bearing", "Status": "SAP PO Triggered 🔄"})
                st.session_state.db['wro'].append({"id": random.randint(1000, 9999), "plant": u['plant'] if u['role'] == 'Manager' else 'Al-Jumum', "target_dept": "Mechanical", "machine": "Mill C", "issue": "PREDICTIVE: Replace Bearing"})
                save_db()
                send_smart_notification("🤖 AI AUTOPILOT", "Mill C Predictive Fix Initiated", "CRITICAL", u['plant'] if u['role'] == 'Manager' else 'Al-Jumum', "Mechanical")
                st.success("Autopilot Executed successfully!")

    # ==========================================
    # 🤖 PLANT-GPT (AI المستودع/الفرع)
    # ==========================================
    if u['role'] in ["Manager", "Technician"]:
        with t_gpt:
            st.markdown("### 🤖 Plant-GPT (AI Assistant)")
            for chat in u['chat']:
                st.markdown(f"**🧑‍🔧 You:** {chat['user']}")
                st.markdown(f"<div class='chat-bubble'>🤖 <b>Plant-GPT:</b> {chat['ai']}</div>", unsafe_allow_html=True)
            user_q = st.text_input("Type your question here (e.g., sap stock, fix pump):")
            if st.button("Ask Plant-GPT ✨", type="primary") and user_q:
                with st.spinner("Searching..."):
                    time.sleep(1)
                    if "pump" in user_q.lower(): ai_resp = "Records show Pump B was fixed 3 months ago by replacing the Mechanical Seal."
                    elif "sap" in user_q.lower() or "stock" in user_q.lower(): ai_resp = "S/4HANA Check: We have 15 Thermal Pastes and 2 Bearings."
                    else: ai_resp = "Apply LOTO first, then refer to the standard maintenance manual."
                    st.session_state.db['users'][u['id']]['chat'].append({"user": user_q, "ai": ai_resp})
                    save_db()
                    st.rerun()

    # ==========================================
    # 📊 DASHBOARD & KPIs
    # ==========================================
    if u['role'] in ["Manager", "Director (HQ)"]:
        with t_dash:
            if u['role'] == "Director (HQ)":
                st.markdown("### 🌐 Global KPIs")
                c1, c2, c3 = st.columns(3)
                c1.metric("Global Health", "96.4%")
                c2.metric("Pending WROs", len(st.session_state.db['wro']))
                c3.metric("Registered Staff", len(st.session_state.db['users']))
            else:
                st.markdown(f"### 📊 {u['plant']} Dash")
                my_wros = [w for w in st.session_state.db['wro'] if w['plant'] == u['plant']]
                c1, c2 = st.columns(2)
                c1.metric("🚨 Active WROs", len(my_wros))
                c2.metric("✅ Tasks Logged", len([l for l in st.session_state.db['log'] if l['plant'] == u['plant']]))
                
                st.markdown("#### 🏢 Department Matrix")
                plant_users = [v for k, v in st.session_state.db['users'].items() if v["plant"] == u['plant'] and v["role"] == "Technician"]
                if plant_users:
                    df_depts = pd.DataFrame(plant_users).groupby('dept').agg(Techs=('name', 'count'), Total_Points=('points', 'sum')).reset_index()
                    st.dataframe(df_depts, use_container_width=True)

    # ==========================================
    # 🚨 RADAR (HQ ONLY)
    # ==========================================
    if u['role'] == "Director (HQ)":
        with t_radar:
            st.markdown("### 🚨 Global Emergency Radar")
            if not st.session_state.db['wro']: st.success("All plants are clear.")
            for wro in st.session_state.db['wro']:
                st.error(f"**{wro['plant'].upper()} | Dept: {wro.get('target_dept', 'All')}** | Loc: {wro['machine']} | Sig: {wro['issue']}")

    # ==========================================
    # 📥 EXPORT REPORTS (Excel)
    # ==========================================
    if u['role'] in ["Manager", "Director (HQ)"]:
        with t_export:
            st.markdown("### 📥 Export Data to Excel (CSV)")
            df_wro = pd.DataFrame(st.session_state.db['wro'])
            if not df_wro.empty:
                st.download_button("📊 Download WRO Tasks", data=df_wro.to_csv(index=False).encode('utf-8'), file_name="WRO_Report.csv", mime='text/csv')

    # ==========================================
    # 🎯 ACTION HUB & DISPATCH
    # ==========================================
    if u['role'] in ["Manager", "Technician"]:
        with t_action:
            if u['role'] == "Manager":
                st.markdown("### 🛠️ Dispatch Matrix")
                col1, col2 = st.columns(2)
                with col1:
                    wro_mac = st.text_input("📍 Equipment/Location:")
                    wro_desc = st.text_input("⚠️ Fault Signature:")
                    wro_target_dept = st.selectbox("🎯 Target Department:", ["All", "Mechanical", "Electrical", "Welding", "Operations", "Workshop"])
                    if st.button("📢 DISPATCH WRO", type="primary"):
                        st.session_state.db['wro'].append({"id": random.randint(1000, 9999), "plant": u['plant'], "target_dept": wro_target_dept, "machine": wro_mac, "issue": wro_desc})
                        save_db()
                        send_smart_notification(f"عطل جديد!", f"الموقع: {wro_mac}\nالمشكلة: {wro_desc}", "CRITICAL", u['plant'], wro_target_dept)
                with col2:
                    bnty_desc = st.text_input("📌 Bounty Objective:")
                    bnty_pts = st.slider("⭐ Reward:", 10, 100, 30, step=10)
                    if st.button("💸 POST BOUNTY", use_container_width=True):
                        st.session_state.db['bounties'].append({"id": random.randint(1000,9999), "plant": u['plant'], "desc": bnty_desc, "points": bnty_pts})
                        save_db()
                        send_smart_notification("مكافأة جديدة!", f"المهمة: {bnty_desc} | الجائزة: {bnty_pts}", "REWARD", u['plant'])
            else:
                st.markdown("### 🎯 Live Grid")
                
                # Faza'a
                with st.expander("🤝 Faza'a (Request Backup)"):
                    fz_loc = st.text_input("📍 Your Location:", key="fz_loc")
                    fz_need = st.text_input("🙋‍♂️ What do you need?", key="fz_need")
                    if st.button("📢 Call for Faza'a", type="primary") and fz_loc:
                        st.session_state.db['fazaas'].append({"id": random.randint(10,99), "plant": u['plant'], "req": u['name'], "loc": fz_loc, "need": fz_need})
                        save_db()
                        send_smart_notification("فزعة!", f"{u['name']} يطلب المساعدة في {fz_loc}", "INFO", u['plant'])
                
                for fz in [f for f in st.session_state.db['fazaas'] if f['plant'] == u['plant'] and f['req'] != u['name']]:
                    st.warning(f"**{fz['req']}** at **{fz['loc']}** needs: {fz['need']}")
                    if st.button(f"🏃‍♂️ Help {fz['req']} (+15 pts)", key=f"fz_{fz['id']}"):
                        st.session_state.db['users'][u['id']]['points'] += 15
                        st.session_state.db['fazaas'].remove(fz)
                        save_db()
                        send_smart_notification("تم قبول الفزعة", f"{u['name']} في الطريق لمساعدة {fz['req']}", "INFO", u['plant'])
                        st.rerun()

                st.markdown(f"#### 🚨 Active Anomalies (For {u['dept']})")
                my_wros = [w for w in st.session_state.db['wro'] if w['plant'] == u['plant'] and w.get('target_dept', 'All') in ['All', u['dept']]]
                for wro in my_wros:
                    st.write(f"**📍 Loc:** {wro['machine']} | **⚠️ Issue:** {wro['issue']}")
                    if st.button("⚡ INTERCEPT", key=f"wro_{wro['id']}"):
                        st.session_state.db['wro'].remove(wro)
                        save_db()
                        send_smart_notification("مهمة مستلمة", f"{u['name']} استلم مهمة {wro['machine']}", "INFO", u['plant'], u['dept'])
                        st.rerun()
                
                st.markdown("#### 💰 Bounty Board")
                for b in [b for b in st.session_state.db['bounties'] if b['plant'] == u['plant']]:
                    st.write(f"**📌 {b['desc']}** | ⭐ {b['points']} PTS")
                    if st.button("✅ CLAIM", key=f"bnty_{b['id']}"):
                        st.session_state.db['users'][u['id']]['points'] += b['points']
                        st.session_state.db['bounties'].remove(b)
                        save_db()
                        send_smart_notification("مكافأة مكتسبة", f"{u['name']} ربح {b['points']} نقطة", "REWARD", u['plant'])
                        st.rerun()

    # ==========================================
    # 📝 TASK LOGGING (للفني)
    # ==========================================
    if u['role'] == "Technician":
        with t_log:
            st.markdown("### 📝 Log Execution")
            task_type = st.radio("Type", ["WRO", "PRO"], horizontal=True)
            mac = st.text_input("📍 Equipment:")
            desc = st.text_area("📝 Details:")
            if st.button("✅ COMMIT TO LOG (+50 PTS)"):
                if mac and desc:
                    st.session_state.db['users'][u['id']]['points'] += 50
                    st.session_state.db['log'].append({"plant": u['plant'], "log": f"[{task_type}] {mac}", "user": u['name']})
                    save_db()
                    send_smart_notification("مهمة مكتملة", f"المهندس {u['name']} أنهى صيانة {mac}", "REWARD", u['plant'], u['dept'])
                    st.rerun()

    # ==========================================
    # 📅 MAINTENANCE DAY
    # ==========================================
    if u['role'] in ["Manager", "Technician"]:
        with t_maint:
            st.markdown("### 📅 Planned Maintenance Outage")
            if u['role'] == "Manager":
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    tech_id_assign = st.text_input("💳 Tech ID:")
                with col_m2:
                    maint_task_desc = st.text_area("🛠️ Work Order Scope:")
                if st.button("📤 ALLOCATE", type="primary") and tech_id_assign:
                    st.session_state.db['maint'].append({"id": random.randint(1000, 9999), "plant": u['plant'], "tech_id": tech_id_assign, "desc": maint_task_desc, "status": "Pending"})
                    save_db()
                    send_smart_notification("صيانة مبرمجة", f"تم تعيين مهمة جديدة للموظف: {tech_id_assign}", "TASK", u['plant'])
                    st.rerun()
                st.dataframe(pd.DataFrame([m for m in st.session_state.db['maint'] if m['plant'] == u['plant']]))
            else:
                my_tasks = [t for t in st.session_state.db['maint'] if t['tech_id'] == u['id'] and t['status'] == 'Pending']
                for task in my_tasks:
                    st.markdown(f"**🛠️ Scope:** {task['desc']}")
                    if st.button("✅ CLOSE WORK ORDER", key=f"btn_{task['id']}"):
                        task['status'] = "Completed"
                        st.session_state.db['users'][u['id']]['points'] += 80
                        save_db()
                        send_smart_notification("صيانة منجزة", f"{u['name']} أنهى أمر العمل", "REWARD", u['plant'])
                        st.rerun()

    # ==========================================
    # ⚙️ ROLLS WORKSHOP
    # ==========================================
    with t_rolls:
        st.markdown("### ⚙️ Milling Rolls Workshop")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if u['role'] in ["Manager", "Technician"]:
                roll_sn = st.text_input("🔢 Serial Number:")
                roll_type = st.selectbox("🛠️ Roll Type:", ["Break Roll", "Reduction Roll", "Smooth Roll"])
                if st.button("💾 Add Roll") and roll_sn:
                    st.session_state.db['rolls'].append({"plant": u['plant'], "serial": roll_sn, "type": roll_type, "status": "🟢 Ready", "install_date": None})
                    save_db()
                    st.rerun()
        with col_r2:
            if u['role'] in ["Manager", "Technician"]:
                ready = [r for r in st.session_state.db['rolls'] if r['plant'] == u['plant'] and r['status'] == '🟢 Ready']
                if ready:
                    sel_roll = st.selectbox("Install Roll:", [r['serial'] for r in ready])
                    tar_mac = st.text_input("📍 Machine Name:")
                    if st.button("⚙️ Confirm Install") and tar_mac:
                        for r in st.session_state.db['rolls']:
                            if r['serial'] == sel_roll:
                                r['status'], r['machine'], r['install_date'] = "🔴 Installed", tar_mac, datetime.now().strftime("%Y-%m-%d")
                        save_db()
                        send_smart_notification("تركيب رول", f"تم تركيب رول {sel_roll} في {tar_mac}", "INFO", u['plant'])
                        st.rerun()
        
        active = [r for r in st.session_state.db['rolls'] if (r.get('plant') == u['plant'] or u['role'] == 'Director (HQ)') and r['status'] == '🔴 Installed']
        if active:
            for r in active: r['Age'] = calculate_lifespan(r['install_date'])
            st.dataframe(pd.DataFrame(active)[['plant', 'serial', 'type', 'machine', 'Age']], use_container_width=True)

    # ==========================================
    # 📦 INVENTORY / SAP
    # ==========================================
    with t_parts:
        st.markdown("### 📦 Supply Chain & SAP")
        if u['role'] == "Technician":
            part_desc = st.text_input("🛠️ Part Name:")
            target_machine = st.text_input("📍 Destination:")
            if st.button("📤 Request Part") and part_desc:
                st.session_state.db['parts'].append({"ID": len(st.session_state.db['parts'])+1, "plant": u['plant'], "Technician": u['name'], "Part": part_desc, "Machine": target_machine, "Status": "Pending"})
                save_db()
                send_smart_notification("طلب قطعة غيار", f"{u['name']} طلب قطعة: {part_desc}", "TASK", u['plant'])
                st.rerun()
            my_parts = [p for p in st.session_state.db['parts'] if p['Technician'] == u['name']]
            if my_parts: st.dataframe(pd.DataFrame(my_parts)[['Part', 'Machine', 'Status']])
        else:
            p_data = [p for p in st.session_state.db['parts'] if p['plant'] == u['plant'] or u['role'] == 'Director (HQ)']
            if p_data:
                st.dataframe(pd.DataFrame(p_data)[['ID', 'plant', 'Part', 'Status', 'Technician']])
                if u['role'] == "Manager":
                    sel_id = st.number_input("Update Req ID:", min_value=1, step=1)
                    action = st.selectbox("Action:", ["Done ✅", "Rejected ❌", "Trigger SAP PO 🔄"])
                    if st.button("Update Ticket"):
                        for r in st.session_state.db['parts']:
                            if r["ID"] == sel_id: r["Status"] = action
                        save_db()
                        send_smart_notification("تحديث طلب SAP", f"الطلب رقم {sel_id} صار: {action}", "INFO", u['plant'])
                        st.rerun()