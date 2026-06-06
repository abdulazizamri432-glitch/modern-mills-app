import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime

# --- 1. إعدادات النظام ---
st.set_page_config(page_title="Modern Mills CMMS", page_icon="🏭", layout="wide")
BOT_TOKEN = "8912670603:AAEr-hufquf8PIxnv-aKv0fz-9WgZa0oRks"
BRANCH_CHATS = {
    "الجموم": "-5159290787",
    "الجوف": "-5176017884",
    "خميس مشيط": "-5104633079"
}

# كلمات السر الخاصة بكل فرع
BRANCH_PASSCODES = {
    "الجموم": "2004",
    "الجوف": "2026",
    "خميس مشيط": "1425"
}

def send_telegram(msg, branch):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try: requests.post(url, data={"chat_id": BRANCH_CHATS.get(branch), "text": f"📍 [تنبيه {branch}]\n{msg}"})
    except: pass

# --- 2. إدارة البيانات ---
if not os.path.exists("smart_factory_db.csv"):
    pd.DataFrame(columns=["Branch", "Equipment", "Description", "Status", "Assigned_To", "Tech_Name", "Points"]).to_csv("smart_factory_db.csv", index=False)
if not os.path.exists("rolls_db.csv"):
    pd.DataFrame(columns=["ID", "Branch", "Status", "Machine", "Install_Date"]).to_csv("rolls_db.csv", index=False)

df = pd.read_csv("smart_factory_db.csv")
df_rolls = pd.read_csv("rolls_db.csv")

# --- 3. واجهة الدخول ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🏭 نظام المطاحن الحديثة - CMMS")
    branch = st.selectbox("اختر الفرع:", list(BRANCH_CHATS.keys()))
    name = st.text_input("اسمك:")
    role = st.radio("الصفة:", ["مدير", "فني"])
    
    passcode = ""
    if role == "مدير":
        passcode = st.text_input("كلمة سر المدير:", type="password")

    if st.button("دخول النظام"):
        if role == "مدير" and passcode != BRANCH_PASSCODES.get(branch):
            st.error("❌ كلمة السر غير صحيحة!")
        else:
            st.session_state.update({"logged_in": True, "branch": branch, "name": name, "role": role})
            st.rerun()
else:
    st.sidebar.header(f"مرحباً {st.session_state.name}")
    st.sidebar.info(f"فرع: {st.session_state.branch}")
    if st.sidebar.button("تسجيل خروج"): st.session_state.logged_in = False; st.rerun()

    tab1, tab2, tab3 = st.tabs(["🛠️ البلاغات", "📋 إدارة الرولات", "📊 إحصائيات الفرع"])

    with tab1:
        if st.session_state.role == "مدير":
            with st.form("new_task"):
                equip = st.text_input("اسم المعدة:")
                desc = st.text_area("تفاصيل العطل:")
                if st.form_submit_button("إرسال أمر عمل"):
                    new_row = pd.DataFrame([{"Branch": st.session_state.branch, "Equipment": equip, "Description": desc, "Status": "New"}])
                    df = pd.concat([df, new_row]); df.to_csv("smart_factory_db.csv", index=False)
                    send_telegram(f"🚨 أمر عمل جديد:\nالمعدة: {equip}\nالوصف: {desc}", st.session_state.branch)
                    st.success("تم إرسال البلاغ!")
        else:
            st.write("البلاغات المفتوحة في فرعك:")
            st.dataframe(df[df['Status'] == 'New'])

    with tab2:
        new_roll = st.text_input("إضافة رول جديد للمخزون:")
        if st.button("إضافة"):
            pd.concat([df_rolls, pd.DataFrame([{"ID": new_roll, "Branch": st.session_state.branch, "Status": "جاهز"}])]).to_csv("rolls_db.csv", index=False); st.rerun()
        
        branch_rolls = df_rolls[df_rolls['Branch'] == st.session_state.branch]
        for idx, row in branch_rolls.iterrows():
            with st.expander(f"رول {row['ID']} - حالة: {row['Status']}"):
                if row['Status'] == "جاهز":
                    mach = st.text_input("اسم الجهاز:", key=f"m_{idx}")
                    if st.button("تركيب الرول", key=f"i_{idx}"):
                        df_rolls.loc[idx, ['Status', 'Machine', 'Install_Date']] = ["قيد التنفيذ", mach, datetime.now().strftime("%Y-%m-%d")]
                        df_rolls.to_csv("rolls_db.csv", index=False)
                        send_telegram(f"✅ تم تركيب رول {row['ID']} على جهاز {mach}", st.session_state.branch)
                        st.rerun()
                else:
                    st.write(f"المعدة: {row['Machine']} | تاريخ: {row['Install_Date']}")
                    if st.button("إزالة الرول", key=f"d_{idx}"):
                        df_rolls = df_rolls.drop(idx); df_rolls.to_csv("rolls_db.csv", index=False); st.rerun()

    with tab3:
        st.subheader(f"مؤشرات الأداء - فرع {st.session_state.branch}")
        col1, col2 = st.columns(2)
        branch_rolls = df_rolls[df_rolls['Branch'] == st.session_state.branch]
        col1.metric("رولات جاهزة", len(branch_rolls[branch_rolls['Status'] == "جاهز"]))
        col2.metric("رولات مركبة", len(branch_rolls[branch_rolls['Status'] == "قيد التنفيذ"]))
