import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime

# --- إعدادات النظام ---
st.set_page_config(page_title="Modern Mills CMMS", page_icon="🏭", layout="wide")
BOT_TOKEN = "8912670603:AAEr-hufquf8PIxnv-aKv0fz-9WgZa0oRks"
BRANCH_CHATS = {"الجموم": "-5159290787", "الجوف": "-5176017884", "خميس مشيط": "-5104633079"}
BRANCH_PASSCODES = {"الجموم": "2004", "الجوف": "2026", "خميس مشيط": "1425"}
DEPARTMENTS = ["ميكانيكا", "كهرباء", "لحام", "تكييف"]

def t(ar, en, lang): return ar if lang == "عربي" else en
def send_telegram(msg, branch):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": BRANCH_CHATS.get(branch), "text": f"📍 [{branch}]:\n{msg}"})
    except: pass

# --- تحميل البيانات ---
if not os.path.exists("smart_factory_db.csv"):
    pd.DataFrame(columns=["Branch", "EmpID", "Dept", "Equipment", "Description", "Status", "Tech_Name", "Points"]).to_csv("smart_factory_db.csv", index=False)
if not os.path.exists("rolls_db.csv"):
    pd.DataFrame(columns=["ID", "Branch", "Status", "Machine", "Install_Date"]).to_csv("rolls_db.csv", index=False)

df = pd.read_csv("smart_factory_db.csv")
df_rolls = pd.read_csv("rolls_db.csv")

# --- تسجيل الدخول ---
if 'lang' not in st.session_state: st.session_state.lang = "عربي"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    if st.button("🌐 En / عربي"): st.session_state.lang = "English" if st.session_state.lang == "عربي" else "عربي"; st.rerun()
    st.title(t("نظام المطاحن الحديثة", "Modern Mills CMMS", st.session_state.lang))
    branch = st.selectbox(t("الفرع:", "Branch:", st.session_state.lang), list(BRANCH_CHATS.keys()))
    name = st.text_input(t("الاسم:", "Name:", st.session_state.lang))
    eid = st.text_input(t("الرقم الوظيفي:", "Employee ID:", st.session_state.lang))
    role = st.radio(t("الصفة:", "Role:", st.session_state.lang), ["مدير", "فني"])
    passcode = st.text_input(t("كلمة السر:", "Passcode:", st.session_state.lang), type="password") if role=="مدير" else ""
    
    if st.button(t("دخول", "Login", st.session_state.lang)):
        if role == "مدير" and passcode != BRANCH_PASSCODES.get(branch): st.error("❌")
        else: st.session_state.update({"logged_in": True, "branch": branch, "name": name, "eid": eid, "role": role}); st.rerun()
else:
    st.sidebar.write(f"👤 {st.session_state.name} | {st.session_state.branch}")
    if st.session_state.role == "فني":
        pts = df[df['Tech_Name'] == st.session_state.name]['Points'].sum()
        rank = "أسطورة 👑" if pts >= 150 else "نجم ⭐️" if pts >= 50 else "فني 🔧"
        st.sidebar.metric(t("نقاطك", "Points", st.session_state.lang), pts, rank)
    if st.sidebar.button(t("خروج", "Logout", st.session_state.lang)): st.session_state.logged_in = False; st.rerun()

    tab1, tab2, tab3 = st.tabs([t("🛠️ البلاغات", "🛠️ Tickets", st.session_state.lang), t("📋 الرولات", "📋 Rolls", st.session_state.lang), t("📊 لوحة", "📊 Dashboard", st.session_state.lang)])

    with tab1:
        if st.session_state.role == "مدير":
            dept = st.selectbox(t("القسم:", "Dept:", st.session_state.lang), DEPARTMENTS)
            equip = st.text_input(t("المعدة:", "Equipment:", st.session_state.lang))
            desc = st.text_area(t("الوصف:", "Description:", st.session_state.lang))
            if st.button(t("إرسال", "Send", st.session_state.lang)):
                pd.concat([df, pd.DataFrame([{"Branch": st.session_state.branch, "Dept": dept, "Equipment": equip, "Description": desc, "Status": "New"}])]).to_csv("smart_factory_db.csv", index=False)
                send_telegram(f"🚨 {dept} - {equip}: {desc}", st.session_state.branch)
                st.success("✅")
        else: st.dataframe(df[(df['Branch'] == st.session_state.branch) & (df['Status'] == 'New')])

    with tab2:
        new_roll = st.text_input(t("إضافة رول:", "Add Roll:", st.session_state.lang))
        if st.button(t("إضافة", "Add", st.session_state.lang)):
            pd.concat([df_rolls, pd.DataFrame([{"ID": new_roll, "Branch": st.session_state.branch, "Status": "جاهز"}])]).to_csv("rolls_db.csv", index=False); st.rerun()
        for idx, row in df_rolls[df_rolls['Branch'] == st.session_state.branch].iterrows():
            with st.expander(f"{row['ID']} - {row['Status']}"):
                if row['Status'] == "جاهز":
                    m = st.text_input(t("الجهاز:", "Machine:", st.session_state.lang), key=f"m{idx}")
                    if st.button(t("تركيب", "Install", st.session_state.lang), key=f"b{idx}"):
                        df_rolls.loc[idx, ['Status', 'Machine', 'Install_Date']] = ["قيد التنفيذ", m, datetime.now().strftime("%Y-%m-%d")]; df_rolls.to_csv("rolls_db.csv", index=False); st.rerun()
                else:
                    st.write(f"{row['Machine']} | {row['Install_Date']}")
                    if st.button(t("إزالة", "Remove", st.session_state.lang), key=f"r{idx}"): df_rolls = df_rolls.drop(idx); df_rolls.to_csv("rolls_db.csv", index=False); st.rerun()

    with tab3:
        st.bar_chart(df_rolls[df_rolls['Branch'] == st.session_state.branch]['Status'].value_counts())
