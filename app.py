import streamlit as st
import pandas as pd
import time
import requests
import random
import json
import os
from datetime import datetime

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="MMC Smart Plant ERP", page_icon="⚡", layout="wide")

# ==========================================
# ⚠️ TELEGRAM API CONFIGURATION
# ==========================================
TELEGRAM_BOT_TOKEN = "8912670603:AAEr-hufquf8PIxnv-aKv0fz-9WgZa0oRks"
TELEGRAM_CHATS = {
    "Al-Jumum": "-5159290787",
    "Khamis Mushait": "-5104633079",
    "Al-Jouf": "-5176017884"
}
PLANT_PASSWORDS = {"Al-Jumum": "Jumum123", "Al-Jouf": "Jouf123", "Khamis Mushait": "Khamis123"}
HQ_PASSWORD = "Admin123"

# --- SMART ENGLISH NOTIFICATION ENGINE ---
def send_smart_notification(title, message, category, plant, target_dept="All"):
    chat_id = TELEGRAM_CHATS.get(plant)
    if not chat_id: return 
    
    icons = {'CRITICAL': '🚨 CRITICAL ALERT', 'INFO': 'ℹ️ SYSTEM NOTIFICATION', 'TASK': '🛠️ DISPATCH ORDER', 'REWARD': '🏆 ACHIEVEMENT'}
    
    txt = f"<b>{icons.get(category, '🔔')}</b>\n\n"
    txt += f"<b>📌 Title:</b> {title}\n"
    txt += f"<b>📝 Details:</b> {message}\n"
    txt += f"<b>🏢 Dept:</b> {target_dept}\n"
    txt += f"<i>🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": txt, "parse_mode": "HTML"}
    try: 
        response = requests.post(url, json=payload)
        if response.status_code == 200: st.toast(f"📩 Alert sent to {plant}!", icon="✅")
    except Exception: pass

# ==========================================
# 💾 PERSISTENT DATABASE (WITH AUTO-HEAL)
# ==========================================
DB_FILE = "mmc_database.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(st.session_state.db, f, indent=4)

if 'db' not in st.session_state:
    loaded_db = load_db()
    defaults = {
        "users": {}, "wro": [], "parts": [], "rolls": [], "maint": [], 
        "log": [], "bounties": [], "fazaas": [], "reels": [], "brain": [],
        "petty_cash": [] # المخزن الجديد لمشتريات الكاش
    }
    for k, v in defaults.items():
        if k not in loaded_db: loaded_db[k] = v
    # Auto-heal old accounts and fazaas
    for uid, udata in loaded_db['users'].items():
        if 'chat' not in udata: udata['chat'] = []
        if 'points' not in udata: udata['points'] = 0
    for f in loaded_db['fazaas']:
        if 'req_dept' not in f: f['req_dept'] = "Unknown"
        
    st.session_state.db = loaded_db
    save_db()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def get_roll_health(rtype, install_date_str):
    if not install_date_str: return "N/A", "⚪ Unknown"
    install_date = datetime.strptime(install_date_str, "%Y-%m-%d")
    days = (datetime.now() - install_date).days
    
    health = "🟢 Good"
    if rtype == "Break Roll":
        if days >= 150: health = "🔴 CRITICAL (>5 Mo)"
        elif days >= 90: health = "🟡 WARNING (>3 Mo)"
    else:
        if days >= 365: health = "🟡 Check Wear"
        
    return f"{days} Days", health

# ==========================================
# 🎨 CYBERPUNK UI DESIGN
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    .neon-text { color: #00f2fe; text-shadow: 0 0 10px rgba(0, 242, 254, 0.5); font-weight: 800; font-size: 2.5em; text-align: center; margin-bottom: 20px;}
    div[data-testid="stContainer"] { background: rgba(22, 27, 34, 0.6); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 15px; }
    .ai-alert { border-left: 5px solid #ff4b4b; padding: 15px; background: rgba(255, 75, 75, 0.1); border-radius: 5px; margin-bottom: 15px; }
    .cash-alert { border-left: 5px solid #ffaa00; padding: 15px; background: rgba(255, 170, 0, 0.1); border-radius: 5px; margin-bottom: 15px; }
    .chat-bubble { background: rgba(0, 242, 254, 0.1); border-left: 4px solid #00f2fe; padding: 10px; border-radius: 5px; margin-bottom: 10px; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 AUTHENTICATION SYSTEM (With Storekeeper)
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
                    reg_role = st.selectbox("🔑 Role:", ["Technician", "Storekeeper", "Manager", "Director (HQ)"])
                with c_b:
                    if reg_role == "Technician":
                        reg_dept = st.selectbox("🛠️ Dept:", ["Mechanical", "Electrical", "Welding", "Operations", "Workshop"])
                        reg_auth = ""
                    elif reg_role == "Storekeeper":
                        reg_dept = "Warehouse"
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
    
    st.sidebar.markdown(f"## {u['plant']} Node" if u['role'] != 'Director (HQ)' else "## 🌐 Global HQ")
    st.sidebar.write(f"**👤 {u['name']}** ({u['dept']})")
    
    if u['role'] == "Technician":
        st.sidebar.write(f"⭐ Points: **{u['points']}**")
        progress_val = int((u['points'] % 300) / 3)
        st.sidebar.progress(progress_val if progress_val <= 100 else 100, text="Next Rank Progress")
        
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout 🚪"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown(f"<h1 style='color:white;'>Welcome, {u['name']} 👋</h1>", unsafe_allow_html=True)

    # ديناميكية الشاشات حسب المنصب الجديد
    if u['role'] == "Director (HQ)":
        tabs = st.tabs(["🌐 KPIs", "🚨 Radar", "⚙️ Rolls", "📦 Supply Chain & Cash", "🤖 Plant-GPT", "📥 Export"])
        t_dash, t_radar, t_rolls, t_parts, t_gpt, t_export = tabs
    elif u['role'] == "Manager":
        tabs = st.tabs(["🔮 AI Twin", "📊 Dash", "💸 Petty Cash (الكاش)", "🤖 Plant-GPT", "🛠️ Dispatch", "📝 Log", "⚙️ Rolls", "📅 Maint", "📦 Supply Chain", "🎬 Reels", "📥 Export"])
        t_ai, t_dash, t_cash, t_gpt, t_action, t_log, t_rolls, t_maint, t_parts, t_reels, t_export = tabs
    elif u['role'] == "Storekeeper":
        tabs = st.tabs(["📦 Warehouse Management", "🤖 Plant-GPT"])
        t_warehouse, t_gpt = tabs
    else: # Technician
        tabs = st.tabs(["🎯 Tasks", "🤖 Plant-GPT", "📝 Log", "⚙️ Rolls", "📅 Maint", "📦 Material Requests", "🎬 Reels"])
        t_action, t_gpt, t_log, t_rolls, t_maint, t_parts, t_reels = tabs

    # ==========================================
    # 🔮 AI DIGITAL TWIN (Managers)
    # ==========================================
    if u['role'] == "Manager":
        with t_ai:
            st.markdown("### 🔮 Predictive AI Digital Twin")
            st.markdown("<div class='ai-alert'><b>🚨 CRITICAL PREDICTION:</b> Mill C - Main Shaft<br>Failure Probability: <b>98%</b> within 12 Hours.<br><i>Target Department: Mechanical</i></div>", unsafe_allow_html=True)
            if st.button("⚡ ACTIVATE AUTOPILOT", type="primary"):
                st.session_state.db['parts'].append({"ID": random.randint(100, 999), "plant": u['plant'], "Technician": "AI System", "Part": "Main Shaft Bearing", "Machine": "Mill C", "Status": "Pending ⏳"})
                st.session_state.db['wro'].append({"id": random.randint(1000, 9999), "plant": u['plant'], "target_dept": "Mechanical", "machine": "Mill C", "issue": "PREDICTIVE: Replace Bearing", "status": "Pending"})
                save_db()
                send_smart_notification("AI AUTOPILOT INITIATED", "Mill C Predictive Fix - Request sent to Storekeeper.", "CRITICAL", u['plant'], "Mechanical")
                st.success("Autopilot Executed successfully! Notification sent to Warehouse.")

    # ==========================================
    # 🤖 PLANT-GPT 
    # ==========================================
    if u['role'] in ["Manager", "Technician", "Director (HQ)", "Storekeeper"]:
        with t_gpt:
            st.markdown("### 🤖 Plant-GPT (AI Assistant)")
            for chat in u['chat']:
                st.markdown(f"**🧑‍🔧 You:** {chat['user']}")
                st.markdown(f"<div class='chat-bubble'>🤖 <b>Plant-GPT:</b> {chat['ai']}</div>", unsafe_allow_html=True)
            user_q = st.text_input("Ask about SAP stock, manuals, or previous fixes:")
            if st.button("Ask Plant-GPT ✨", type="primary") and user_q:
                with st.spinner("🤖 AI is searching..."):
                    time.sleep(1.5)
                    if "pump" in user_q.lower(): ai_resp = "Based on records, Pump B was fixed 3 months ago (SAP #104558)."
                    else: ai_resp = "SAP Check: We currently have 15 Thermal Pastes and 2 Bearings (Low Stock Warning)."
                    st.session_state.db['users'][u['id']]['chat'].append({"user": user_q, "ai": ai_resp})
                    save_db()
                    st.rerun()

    # ==========================================
    # 📦 WAREHOUSE MANAGEMENT (شاشة أمين المستودع الجديدة)
    # ==========================================
    if u['role'] == "Storekeeper":
        with t_warehouse:
            st.markdown("### 📦 Warehouse Logistics & Parts Allocation")
            st.markdown("---")
            
            # فلترة الطلبات الخاصة بفرع أمين المستودع الحالي
            pending_requests = [p for p in st.session_state.db['parts'] if p['plant'] == u['plant'] and "Pending" in p['Status']]
            
            if not pending_requests:
                st.success("🎉 No pending material requests from maintenance team!")
            else:
                st.write(f"📋 You have **{len(pending_requests)}** pending requests to action:")
                for req in pending_requests:
                    with st.container():
                        st.markdown(f"**🔧 Part:** {req['Part']} | **📍 Destination:** {req['Machine']} | **👤 Requested By:** {req['Technician']}")
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.button(f"✅ Issue from Stock (In Stock)", key=f"issue_{req['ID']}"):
                                req['Status'] = "Issued ✅"
                                save_db()
                                send_smart_notification("MATERIAL ISSUED", f"Part '{req['Part']}' is ready for pickup at Warehouse.", "INFO", u['plant'])
                                st.rerun()
                        with col_b2:
                            if st.button(f"🔄 Trigger SAP Purchase Order (Out of Stock)", key=f"sap_{req['ID']}"):
                                req['Status'] = "Triggered SAP PO 🔄"
                                save_db()
                                send_smart_notification("SAP PO TRIGGERED", f"Part '{req['Part']}' is out of stock. SAP PO initiated by Storekeeper.", "TASK", u['plant'])
                                st.rerun()

    # ==========================================
    # 💸 PETTY CASH MANAGEMENT (حل لخبطة الكاش للمشرف والمدير)
    # ==========================================
    if u['role'] == "Manager":
        with t_cash:
            st.markdown("### 💸 Emergency Petty Cash Registry (مشتريات الطوارئ)")
            st.markdown("<div class='cash-alert'><b>⚠️ ميزة الحوكمة المالية:</b> استخدم هذه الشاشة لتسجيل القطع المششتراة كاش بسبب نفاذها من المستودع. ربط كود الـ SAP إلزامي لضمان عدم ضياع تكلفتها على الماكينة.</div>", unsafe_allow_html=True)
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                cash_part = st.text_input("🛠️ Emergency Part Name:")
                cash_sap = st.text_input("🔢 SAP Part Code (حتى لو الرصيد صفر):")
                cash_price = st.number_input("💰 Price (SAR):", min_value=1.0, step=10.0)
            with col_c2:
                cash_mac = st.text_input("📍 Installed on Machine/Location:")
                cash_invoice = st.file_uploader("📸 Upload Receipt / Invoice Proof", type=['jpg', 'png'])
                
            if st.button("💾 Log Cash Purchase & Reconcile", type="primary"):
                if cash_part and cash_sap and cash_price and cash_mac and cash_invoice:
                    st.session_state.db['petty_cash'].append({
                        "plant": u['plant'],
                        "part": cash_part,
                        "sap_code": cash_sap,
                        "price": cash_price,
                        "machine": cash_mac,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "logged_by": u['name']
                    })
                    save_db()
                    st.success("✅ Cash purchase logged and linked to SAP asset tracker successfully!")
                    send_smart_notification("EMERGENCY CASH PURCHASE", f"Part {cash_part} (SAP #{cash_sap}) bought via Cash for {cash_price} SAR.", "INFO", u['plant'])
                    st.rerun()
                else:
                    st.error("⚠️ جميع الحقول وإثبات الفاتورة إلزامية لربط العهدة!")
            
            st.markdown("#### 📜 Recent Plant Cash Outlays")
            my_plant_cash = [c for c in st.session_state.db['petty_cash'] if c['plant'] == u['plant']]
            if my_plant_cash:
                st.dataframe(pd.DataFrame(my_plant_cash), use_container_width=True)

    # ==========================================
    # 📊 DASHBOARD & KPIs (رادار الهدر والزجاجة)
    # ==========================================
    if u['role'] in ["Manager", "Director (HQ)"]:
        with t_dash:
            if u['role'] == "Director (HQ)":
                st.markdown("### 🌐 Global KPIs")
                c1, c2, c3 = st.columns(3)
                c1.metric("Global Health", "96.4%")
                c2.metric("Pending WROs", len(st.session_state.db['wro']))
                total_cash_spent = sum([float(c['price']) for c in st.session_state.db['petty_cash']])
                c3.metric("🚨 Total Global Emergency Cash Spent", f"{total_cash_spent} SAR")
            else:
                st.markdown(f"### 📊 {u['plant']} Dash")
                c1, c2, c3 = st.columns(3)
                c1.metric("🚨 Active WROs", len([w for w in st.session_state.db['wro'] if w['plant'] == u['plant']]))
                
                # عنق الزجاجة: كم طلب واقف بالمستودع؟
                wh_bottleneck = len([p for p in st.session_state.db['parts'] if p['plant'] == u['plant'] and "SAP" in p['Status']])
                c2.metric("📦 Warehouse Delay (Waiting SAP)", wh_bottleneck)
                
                # مجموع الكاش المستهلك في الفرع
                plant_cash_spent = sum([float(c['price']) for c in st.session_state.db['petty_cash'] if c['plant'] == u['plant']])
                c3.metric("💸 Local Petty Cash Outflow", f"{plant_cash_spent} SAR")
                
                # تحليل هدر قطع غيار الـ SAP عبر الكاش
                st.markdown("#### 🚨 Stockout Cash Leakages (قطع متوفرة بالساب واشتريت كاش بسبب نفاذ المخزون)")
                my_plant_cash = [c for c in st.session_state.db['petty_cash'] if c['plant'] == u['plant']]
                if my_plant_cash:
                    df_cash_leak = pd.DataFrame(my_plant_cash)
                    st.bar_chart(df_cash_leak.set_index('sap_code')['price'], color="#ffaa00")
                    st.caption("الرسم البياني يوضح أكثر أكواد الـ SAP اللي جالس يستنزف فيها الفرع كاش محلي نتيجة سوء تخطيط المخزون.")

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
    # 📦 SUPPLY CHAIN (شاشة عرض اللوجستيات العامة وعرض الفني للطلبات)
    # ==========================================
    with t_parts:
        if u['role'] != "Storekeeper": # شاشة أمين المستودع مفصولة ومستقلة فوق
            st.markdown("### 📦 Material Requests & Logistics Tracker")
            
            st.markdown("#### 🚢 Live Logistics Status Tracker")
            track_col1, track_col2, track_col3 = st.columns(3)
            track_col1.info("🟢 **Delivered / Issued:** 12 Parts")
            track_col2.warning("🟡 **In Transit / SAP PO:** 3 Parts")
            track_col3.error("🔴 **Customs Hold:** 1 Part")
            st.markdown("---")

            if u['role'] == "Technician":
                st.markdown("#### 📥 New Material Request (طلب صرف مواد للماكينة)")
                part_desc = st.text_input("🛠️ Part Name / Description:")
                target_machine = st.text_input("📍 Destination Machine:")
                if st.button("📤 Request Part from Warehouse") and part_desc:
                    st.session_state.db['parts'].append({
                        "ID": len(st.session_state.db['parts'])+1, 
                        "plant": u['plant'], 
                        "Technician": u['name'], 
                        "Part": part_desc, 
                        "Machine": target_machine, 
                        "Status": "Pending ⏳"
                    })
                    save_db()
                    send_smart_notification("NEW MATERIAL REQUEST", f"{u['name']} requested: {part_desc} for {target_machine}", "TASK", u['plant'])
                    st.success("Request sent straight to the Storekeeper dashboard!")
                    st.rerun()
                    
                my_parts = [p for p in st.session_state.db['parts'] if p['Technician'] == u['name']]
                if my_parts: 
                    st.markdown("#### ⏳ Status of Your Requests")
                    st.dataframe(pd.DataFrame(my_parts)[['Part', 'Machine', 'Status']])
            else:
                # العرض للمدير والـ HQ
                p_data = [p for p in st.session_state.db['parts'] if p['plant'] == u['plant'] or u['role'] == 'Director (HQ)']
                if p_data:
                    st.dataframe(pd.DataFrame(p_data)[['ID', 'plant', 'Part', 'Machine', 'Status', 'Technician']])

    # ==========================================
    # 📥 EXPORT REPORTS (Excel)
    # ==========================================
    if u['role'] in ["Manager", "Director (HQ)"]:
        with t_export:
            st.markdown("### 📥 Smart Reporting & Export")
            df_wro = pd.DataFrame(st.session_state.db['wro'])
            if not df_wro.empty:
                st.download_button("📊 Download WRO Tasks (CSV)", data=df_wro.to_csv(index=False).encode('utf-8'), file_name="WRO_Report.csv", mime='text/csv')

    # ==========================================
    # 🎯 ACTION HUB & DISPATCH (الفزعة المعززة)
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
                        send_smart_notification(f"NEW DISPATCH: {wro_mac}", f"Issue: {wro_desc}", "CRITICAL", u['plant'], wro_target_dept)
                with col2:
                    bnty_desc = st.text_input("📌 Bounty Objective:")
                    bnty_pts = st.slider("⭐ Reward:", 10, 100, 30, step=10)
                    if st.button("💸 POST BOUNTY", use_container_width=True):
                        st.session_state.db['bounties'].append({"id": random.randint(1000,9999), "plant": u['plant'], "desc": bnty_desc, "points": bnty_pts})
                        save_db()
                        send_smart_notification("NEW BOUNTY!", f"Task: {bnty_desc} | Reward: {bnty_pts} PTS", "REWARD", u['plant'])
            else:
                st.markdown("### 🎯 Live Grid")
                
                with st.expander("🤝 Faza'a (Request Backup)"):
                    fz_loc = st.text_input("📍 Your Location:")
                    fz_need = st.text_input("🙋‍♂️ What do you need?")
                    if st.button("📢 Call for Faza'a", type="primary") and fz_loc:
                        st.session_state.db['fazaas'].append({"id": random.randint(10,99), "plant": u['plant'], "req": u['name'], "req_dept": u['dept'], "loc": fz_loc, "need": fz_need})
                        save_db()
                        send_smart_notification("FAZA'A REQUESTED!", f"{u['name']} ({u['dept']}) needs help at {fz_loc}.\nReq: {fz_need}", "INFO", u['plant'])
                
                for fz in [f for f in st.session_state.db['fazaas'] if f['plant'] == u['plant'] and f['req'] != u['name']]:
                    st.warning(f"**{fz['req']} ({fz['req_dept']})** at **{fz['loc']}** needs: {fz['need']}")
                    
                    is_cross_dept = (u['dept'] != fz['req_dept'])
                    pts_reward = 30 if is_cross_dept else 15
                    btn_text = f"🏃‍♂️ Help {fz['req']} (+{pts_reward} PTS ✨ Cross-Dept)" if is_cross_dept else f"🏃‍♂️ Help {fz['req']} (+15 PTS)"
                    
                    if st.button(btn_text, key=f"fz_{fz['id']}"):
                        st.session_state.db['users'][u['id']]['points'] += pts_reward
                        st.session_state.db['fazaas'].remove(fz)
                        save_db()
                        send_smart_notification("FAZA'A ACCEPTED", f"{u['name']} ({u['dept']}) is helping {fz['req']} ({fz['req_dept']})", "INFO", u['plant'])
                        st.rerun()

                st.markdown(f"#### 🚨 Active Anomalies (For {u['dept']})")
                my_wros = [w for w in st.session_state.db['wro'] if w['plant'] == u['plant'] and w.get('target_dept', 'All') in ['All', u['dept']]]
                for wro in my_wros:
                    st.write(f"**📍 Loc:** {wro['machine']} | **⚠️ Issue:** {wro['issue']}")
                    if st.button("⚡ INTERCEPT", key=f"wro_{wro['id']}"):
                        st.session_state.db['wro'].remove(wro)
                        save_db()
                        send_smart_notification("WRO INTERCEPTED", f"{u['name']} claimed task at {wro['machine']}", "INFO", u['plant'], u['dept'])
                        st.rerun()

    # ==========================================
    # 📝 TASK LOGGING (أوزان المهام)
    # ==========================================
    if u['role'] in ["Manager", "Technician"]:
        with t_log:
            st.markdown("### 📝 Log Execution & Proof")
            task_type = st.radio("Type", ["WRO", "PRO"], horizontal=True)
            mac = st.text_input("📍 Equipment:", key="log_mac")
            desc = st.text_area("📝 Details:", key="log_desc")
            
            difficulty = st.selectbox("⚖️ Task Complexity:", ["🟢 Light (+20 PTS)", "🟡 Medium (+50 PTS)", "🔴 Heavy (+100 PTS)"])
            pts_map = {"🟢 Light (+20 PTS)": 20, "🟡 Medium (+50 PTS)": 50, "🔴 Heavy (+100 PTS)": 100}
            
            proof = st.file_uploader("📸 Upload LOTO / Proof", type=['jpg', 'png'], key="log_proof")
            
            if st.button("✅ COMMIT TO LOG", type="primary"):
                if mac and desc and proof:
                    with st.spinner("🤖 AI Vision is verifying LOTO Compliance..."):
                        time.sleep(2) 
                    earned_pts = pts_map[difficulty]
                    st.session_state.db['users'][u['id']]['points'] += earned_pts
                    st.session_state.db['log'].append({"plant": u['plant'], "log": f"[{task_type}] {mac}", "user": u['name']})
                    st.session_state.db['brain'].append({"plant": u['plant'], "machine": mac, "fix": desc, "tech": u['name']})
                    save_db()
                    send_smart_notification("TASK VERIFIED", f"Tech: {u['name']} finished {mac} ({difficulty}).\nAI Vision: Approved ✅", "REWARD", u['plant'], u['dept'])
                    st.success(f"AI Verified! {earned_pts} Points Added!")
                else:
                    st.error("⚠️ All fields and Visual Evidence are mandatory.")

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
                    tar_mac = st.text_input("📍 Machine Name:", key="rl_mac")
                    if st.button("⚙️ Confirm Install") and tar_mac:
                        for r in st.session_state.db['rolls']:
                            if r['serial'] == sel_roll:
                                r['status'], r['machine'], r['install_date'] = "🔴 Installed", tar_mac, datetime.now().strftime("%Y-%m-%d")
                        save_db()
                        send_smart_notification("ROLL INSTALLED", f"Roll {sel_roll} installed in {tar_mac}", "INFO", u['plant'])
                        st.rerun()
        
        active = [r for r in st.session_state.db['rolls'] if (r.get('plant') == u['plant'] or u['role'] == 'Director (HQ)') and r['status'] == '🔴 Installed']
        if active:
            for r in active:
                r['Age'], r['Health'] = get_roll_health(r['type'], r['install_date'])
            st.dataframe(pd.DataFrame(active)[['plant', 'serial', 'type', 'machine', 'Age', 'Health']], use_container_width=True)

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
                    send_smart_notification("NEW MAINT DIRECTIVE", f"Assigned to: {tech_id_assign}", "TASK", u['plant'])
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
                        send_smart_notification("MAINTENANCE COMPLETED", f"{u['name']} closed order.", "REWARD", u['plant'])
                        st.rerun()

    # ==========================================
    # 🎬 REELS & TRAINING
    # ==========================================
    if u['role'] in ["Manager", "Technician"]:
        with t_reels:
            st.markdown("### 🎬 Operation Tutorials & Reels")
            with st.expander("📤 Upload Intel (+100 PTS)"):
                reel_title = st.text_input("📌 Intel Subject:")
                st.file_uploader("Upload Video File (MP4)", type=["mp4"])
                if st.button("🚀 UPLOAD INTEL", type="primary") and reel_title:
                    st.session_state.db['reels'].append({"plant": u['plant'], "title": reel_title, "author": u['name'], "date": datetime.now().strftime("%Y-%m-%d")})
                    st.session_state.db['users'][u['id']]['points'] += 100
                    save_db()
                    st.success("Intel Uploaded to Secure Vault!")
            
            my_reels = [r for r in st.session_state.db['reels'] if r['plant'] == u['plant']]
            for reel in reversed(my_reels):
                st.info(f"🎥 **{reel['title']}** (Uploaded by {reel['author']} on {reel['date']})")