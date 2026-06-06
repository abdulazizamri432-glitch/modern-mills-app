import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime

# --- إعدادات النظام ---
st.set_page_config(page_title="MMC Smart CMMS", page_icon="🏭", layout="wide")
BOT_TOKEN = "8912670603:AAEr-hufquf8PIxnv-aKv0fz-9WgZa0oRks"
BRANCH_CHATS = {"الجموم": "-5159290787", "الجوف": "-5176017884", "خميس مشيط": "-5104633079"}
BRANCH_NAMES = {"الجموم": "Al-Jumum", "الجوف": "Al-Jouf", "خميس مشيط": "Khamis Mushait"}
BRANCH_PASSCODES = {"الجموم": "2004", "الجوف": "2026", "خميس مشيط": "1425"}

def t(ar, en, lang): return ar if lang == "عربي" else en

def send_alert(msg, branch):
    chat_id = BRANCH_CHATS.get(branch)
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": chat_id, "text": f"🏭 {branch} Update:\n{msg}"})
    except: pass

# --- تحميل/تهيئة البيانات ---
db_path, rolls_path = "smart_factory_db.csv", "rolls_db.csv"
if not os.path.exists(db_path): pd.DataFrame(columns=["Branch", "EmpID", "Dept", "Equip", "Desc", "Status", "Tech"]).to_csv(db_path, index=False)
if not os.path.exists(rolls_path): pd.DataFrame(columns=["ID", "Branch", "Status", "Machine", "Date"]).to_csv(rolls_path, index=False)

df, df_rolls = pd.read_csv(db_path), pd.read_csv(rolls_path)

# --- واجهة الدخول ---
if 'lang' not in st.session_state: st.session_state.lang = "عربي"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    if st.button("🌐 Switch Language"): st.session_state.lang = "English" if st.session_state.lang == "عربي" else "عربي"; st.rerun()
    st.title("🏭 Modern Mills Smart CMMS")
    branch = st.selectbox("Select Branch / الفرع", list(BRANCH_CHATS.keys()))
    name, eid = st.text_input("Name / الاسم"), st.text_input("Emp ID / الرقم الوظيفي")
    role = st.radio("Role / الصفة", ["Manager", "Technician"])
    passcode = st.text_input("Passcode", type="password") if role == "Manager" else ""
    
    if st.button("Login / دخول"):
        if role == "Manager" and passcode != BRANCH_PASSCODES.get(branch): st.error("Wrong Passcode!")
        else: st.session_state.update({"logged_in": True, "branch": branch, "name": name, "role": role}); st.rerun()
else:
    # --- اللوحة الإبداعية ---
    st.sidebar.subheader(f"👋 {st.session_state.name}")
    if st.sidebar.button("Logout"): st.session_state.logged_in = False; st.rerun()

    c1, c2, c3 = st.columns(3)
    c1.metric("Branch", st.session_state.branch)
    c2.metric("Tickets", len(df[df['Branch'] == st.session_state.branch]))
    c3.metric("Ready Rolls", len(df_rolls[(df_rolls['Branch'] == st.session_state.branch) & (df_rolls['Status'] == 'جاهز')]))

    t1, t2 = st.tabs(["🛠️ Maintenance Management", "⚙️ Roll Lifecycle"])

    with t1:
        if st.session_state.role == "Manager":
            with st.form("ticket"):
                eq, desc = st.text_input("Equipment"), st.text_area("Details")
                if st.form_submit_button("Create Ticket"):
                    pd.concat([df, pd.DataFrame([{"Branch": st.session_state.branch, "Equip": eq, "Desc": desc, "Status": "New", "Tech": st.session_state.name}])]).to_csv(db_path, index=False)
                    send_alert(f"🚨 New Work Order:\n{eq}\n{desc}", st.session_state.branch)
        st.dataframe(df[df['Branch'] == st.session_state.branch])

    with t2:
        new_r = st.text_input("Enter New Roll ID")
        if st.button("Add Roll"):
            pd.concat([df_rolls, pd.DataFrame([{"ID": new_r, "Branch": st.session_state.branch, "Status": "جاهز"}])]).to_csv(rolls_path, index=False); st.rerun()
        
        for idx, row in df_rolls[df_rolls['Branch'] == st.session_state.branch].iterrows():
            with st.expander(f"Roll: {row['ID']} - {row['Status']}"):
                if row['Status'] == "جاهز":
                    mach = st.text_input("Machine Name", key=f"m{idx}")
                    if st.button("Install Roll", key=f"b{idx}"):
                        df_rolls.loc[idx, ['Status', 'Machine', 'Date']] = ["قيد التنفيذ", mach, datetime.now().strftime("%Y-%m-%d")]
                        df_rolls.to_csv(rolls_path, index=False); send_alert(f"✅ Roll {row['ID']} installed on {mach}", st.session_state.branch); st.rerun()
