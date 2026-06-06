import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime

# --- 1. إعدادات النظام ---
st.set_page_config(page_title="Modern Mills CMMS", page_icon="🏭", layout="wide")
BOT_TOKEN = "8912670603:AAEr-hufquf8PIxnv-aKv0fz-9WgZa0oRks"

# معرفات القروبات لكل فرع
BRANCH_CHATS = {
    "الجموم": "-5159290787",
    "الجوف": "-5176017884",
    "خميس مشيط": "-5104633079"
}

def send_telegram(msg, branch):
    chat_id = BRANCH_CHATS.get(branch)
    if chat_id:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": chat_id, "text": f"📍 [تنبيه صيانة - فرع {branch}]\n{msg}"})
        except: pass

# --- 2. تهيئة البيانات ---
if not os.path.exists("smart_factory_db.csv"):
    pd.DataFrame(columns=["Branch", "Dept", "Equipment", "Description", "Status"]).to_csv("smart_factory_db.csv", index=False)
if not os.path.exists("rolls_db.csv"):
    pd.DataFrame(columns=["ID", "Branch", "Status", "Machine", "Install_Date"]).to_csv("rolls_db.csv", index=False)

df = pd.read_csv("smart_factory_db.csv")
df_rolls = pd.read_csv("rolls_db.csv")
DEPARTMENTS = ["ميكانيكا", "كهرباء", "لحام", "تكييف"]

# --- 3. واجهة المستخدم ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🏭 نظام المطاحن الحديثة - CMMS")
    branch = st.selectbox("اختر الفرع:", list(BRANCH_CHATS.keys()))
    name = st.text_input("اسم المستخدم:")
    if st.button("دخول النظام"):
        st.session_state.update({"logged_in": True, "branch": branch, "name": name})
        st.rerun()
else:
    st.sidebar.info(f"مرحباً: {st.session_state.name}\nفرع: {st.session_state.branch}")
    if st.sidebar.button("تسجيل خروج"): st.session_state.logged_in = False; st.rerun()

    tab1, tab2 = st.tabs(["🛠️ البلاغات الفنية", "📋 إدارة الرولات"])

    with tab1:
        st.subheader("إرسال بلاغ صيانة")
        dept = st.selectbox("القسم:", DEPARTMENTS)
        equip = st.text_input("اسم المعدة:")
        desc = st.text_area("وصف العطل:")
        if st.button("إرسال البلاغ لقروب الفرع"):
            send_telegram(f"🚨 عطل جديد في {dept}\nالمعدة: {equip}\nالوصف: {desc}", st.session_state.branch)
            st.success("تم إرسال البلاغ بنجاح!")

    with tab2:
        st.subheader("سجل الرولات")
        col_add, col_list = st.columns([1, 2])
        
        with col_add:
            new_roll = st.text_input("إضافة رول جديد:")
            if st.button("إضافة للمخزون"):
                new_entry = pd.DataFrame([{"ID": new_roll, "Branch": st.session_state.branch, "Status": "جاهز", "Machine": "-", "Install_Date": "-"}])
                df_rolls = pd.concat([df_rolls, new_entry]); df_rolls.to_csv("rolls_db.csv", index=False); st.rerun()

        with col_list:
            branch_rolls = df_rolls[df_rolls['Branch'] == st.session_state.branch]
            for idx, row in branch_rolls.iterrows():
                with st.expander(f"رول: {row['ID']} | الحالة: {row['Status']}"):
                    if row['Status'] == "جاهز":
                        machine = st.text_input("اسم الجهاز:", key=f"m_{idx}")
                        if st.button("تركيب الرول", key=f"btn_{idx}"):
                            df_rolls.loc[idx, ['Status', 'Machine', 'Install_Date']] = ["قيد التنفيذ", machine, datetime.now().strftime("%Y-%m-%d")]
                            df_rolls.to_csv("rolls_db.csv", index=False); st.rerun()
                    else:
                        st.write(f"✅ مركب على: {row['Machine']}")
                        st.write(f"📅 تاريخ التركيب: {row['Install_Date']}")
                        if st.button("إزالة الرول (إنهاء)", key=f"del_{idx}"):
                            df_rolls = df_rolls.drop(idx); df_rolls.to_csv("rolls_db.csv", index=False); st.rerun()