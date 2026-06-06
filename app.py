import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="Modern Mills CMMS", page_icon="🏭", layout="wide")

st.markdown("""
<style>
    .reportview-container { background: #0e1117; color: #fafafa; }
    .stButton>button { border-radius: 8px; font-weight: bold; transition: 0.3s; border: 1px solid #4CAF50; }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4); }
    .glass-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 10px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 15px; }
    .rank-text { font-size: 24px; font-weight: bold; color: #FFD700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.5); }
    .mission-box { border-left: 5px solid #FF5722; padding: 10px; background: rgba(255,87,34,0.1); margin-bottom:10px; border-radius: 5px;}
</style>
""", unsafe_allow_html=True)

# --- 2. إعدادات تليجرام ---
BOT_TOKEN = "8912670603:AAEr-hufquf8PIxnv-aKv0fz-9WgZa0oRks"
CHAT_ID = "-5159290787"

def send_telegram_alert(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        if res.status_code != 200:
            st.error(f"خطأ تليجرام: {res.text}")
    except Exception as e:
        st.error(f"خطأ في الاتصال: {e}")

# --- 3. تهيئة قاعدة البيانات ---
DATA_FILE = "smart_factory_db.csv"
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        "ID", "Date", "Branch", "Dept", "Type", "Equipment", "Description", 
        "Spares", "Status", "Assigned_By", "Assigned_To", "Tech_Name", "Points", "Has_Image"
    ])
    df_init.to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)

# --- 4. نظام اللغات ---
if 'lang' not in st.session_state:
    st.session_state.lang = "عربي"

def t(ar_text, en_text):
    return ar_text if st.session_state.lang == "عربي" else en_text

BRANCHES = {"الجموم": "Jamoum", "الجوف": "Al Jouf", "خميس مشيط": "Khamis Mushait"}
DEPTS = {"مطاحن الدقيق": "Flour Mills", "مصنع الأعلاف": "Feed Mill", "التعبئة": "Packing", "الصوامع": "Silos"}

# --- 5. نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    lang_col1, lang_col2 = st.columns([9, 1])
    with lang_col2:
        if st.button("🌐 En / عربي"):
            st.session_state.lang = "English" if st.session_state.lang == "عربي" else "عربي"
            st.rerun()

    st.markdown(f"<h1 style='text-align: center;'>🏭 {t('المطاحن الحديثة | نظام الصيانة الذكي', 'MODERN MILLS | Smart Maintenance')}</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<div class='glass-card'>", unsafe_allow_html=True)
        branch_login = st.selectbox(t("📍 اختر الفرع:", "📍 Select Branch:"), options=list(BRANCHES.keys()), format_func=lambda x: x if st.session_state.lang == "عربي" else BRANCHES[x])
        emp_name = st.text_input(t("👤 الاسم الكامل:", "👤 Full Name:"))
        emp_id = st.text_input(t("🔢 الرقم الوظيفي:", "🔢 Employee ID:"))
        
        role_options = {"مدير": "Manager / Supervisor", "فني": "Technician"}
        role = st.radio(t("🛡️ صفة الدخول:", "🛡️ Role:"), options=list(role_options.keys()), format_func=lambda x: "مدير / مشرف" if x=="مدير" and st.session_state.lang=="عربي" else role_options[x] if st.session_state.lang=="English" else "فني صيانة")
        
        passcode = ""
        if role == "مدير":
            passcode = st.text_input(t("🔑 الرمز السري للمدير:", "🔑 Manager Passcode:"), type="password")
        
        if st.button(t("تسجيل الدخول 🚀", "Login 🚀"), use_container_width=True):
            if emp_name and emp_id:
                if role == "مدير" and passcode not in ["2004", "2026", "1425"]:
                    st.error(t("❌ الرمز السري خاطئ!", "❌ Invalid Passcode!"))
                    st.stop()
                st.session_state.logged_in = True
                st.session_state.branch = branch_login
                st.session_state.emp_name = emp_name
                st.session_state.role = role
                st.rerun()
            else:
                st.error(t("الرجاء إدخال الاسم والرقم الوظيفي!", "Please enter Name and ID!"))
        st.markdown("</div>", unsafe_allow_html=True)

else:
    col_w1, col_w2 = st.columns([8, 2])
    display_branch = st.session_state.branch if st.session_state.lang == "عربي" else BRANCHES[st.session_state.branch]
    
    col_w1.success(f"{t('أهلاً بك', 'Welcome')} {st.session_state.emp_name} | {display_branch}")
    if col_w2.button(t("تسجيل خروج 🚪", "Logout 🚪")):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown("---")

    raw_eq = df[(df['Branch'] == st.session_state.branch)]['Equipment'].dropna().unique().tolist()
    existing_eq = [e for e in raw_eq if e not in ["+", "-", "+ جديد (+ New)"]]
    
    raw_sp = df[(df['Branch'] == st.session_state.branch)]['Spares'].dropna().unique().tolist()
    existing_sp = [s for s in raw_sp if s not in ["+", "-", "+ جديد (+ New)"]]

    # ========================================
    # واجهة المدير
    # ========================================
    if st.session_state.role == "مدير":
        tab1, tab2 = st.tabs([t("📊 لوحة القيادة", "📊 Dashboard"), t("🚨 توجيه أمر عمل", "🚨 Assign Task")])
        with tab1:
            branch_df = df[df['Branch'] == st.session_state.branch]
            c1, c2, c3 = st.columns(3)
            c1.metric(t("إجمالي البلاغات", "Total Tickets"), len(branch_df))
            c2.metric(t("أعطال طارئة (WRO)", "Emergency (WRO)"), len(branch_df[branch_df['Type'] == 'WRO']))
            c3.metric(t("صيانة وقائية (PRO)", "Preventive (PRO)"), len(branch_df[branch_df['Type'] == 'PRO']))
            
            st.markdown(f"### 🏆 {t('أبطال الصيانة', 'Maintenance Heroes')}")
            if not branch_df.empty:
                leaderboard = branch_df.groupby("Tech_Name")["Points"].sum().reset_index().sort_values(by="Points", ascending=False)
                leaderboard.index = leaderboard.index + 1
                st.dataframe(leaderboard, use_container_width=True)
                
        with tab2:
            st.markdown(f"<div class='glass-card'>", unsafe_allow_html=True)
            dept = st.selectbox(t("القسم", "Department"), list(DEPTS.keys()), format_func=lambda x: x if st.session_state.lang == "عربي" else DEPTS[x], key="mgr_dept")
            
            equip = st.selectbox(t("المعدة", "Equipment"), ["+"] + existing_eq, key="mgr_eq")
            if equip == "+": equip = st.text_input(t("اكتب اسم المعدة:", "Enter Equipment Name:"), key="mgr_eq_new")
                
            desc = st.text_area(t("وصف المشكلة", "Problem Description"), key="mgr_desc")
            tech_assign = st.text_input(t("توجيه إلى الفني (الاسم):", "Assign to Tech:"), key="mgr_tech")
            
            if st.button(t("إرسال استنفار 🚨", "Send Alert 🚨")):
                if equip and desc and tech_assign:
                    new_task = pd.DataFrame({
                        "ID": [f"WRO-{len(df)+1}"], "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")],
                        "Branch": [st.session_state.branch], "Dept": [dept], "Type": ["WRO"],
                        "Equipment": [equip], "Description": [desc], "Spares": ["-"],
                        "Status": ["New"], "Assigned_By": [st.session_state.emp_name],
                        "Assigned_To": [tech_assign], "Tech_Name": ["-"], "Points": [0], "Has_Image": [False]
                    })
                    df = pd.concat([df, new_task], ignore_index=True)
                    df.to_csv(DATA_FILE, index=False)
                    send_telegram_alert(f"🚨 أمر موجه!\nإلى: {tech_assign}\nالفرع: {display_branch}\nالمعدة: {equip}\nمن: {st.session_state.emp_name}")
                    st.success(t("تم التوجيه بنجاح!", "Assigned successfully!"))
                else:
                    st.error(t("الرجاء إكمال جميع البيانات", "Please fill all fields"))
            st.markdown("</div>", unsafe_allow_html=True)

    # ========================================
    # واجهة الفني
    # ========================================
    else:
        my_data = df[df['Tech_Name'] == st.session_state.emp_name]
        my_points = my_data['Points'].sum() if not my_data.empty else 0
        
        # ربط الرتبة بنظام اللغات
        rank_ar = "أسطورة المصنع 👑" if my_points >= 150 else "نجم الصيانة ⭐️" if my_points >= 50 else "فني مبدع 🔧"
        rank_en = "Factory Legend 👑" if my_points >= 150 else "Maintenance Star ⭐️" if my_points >= 50 else "Creative Tech 🔧"
        rank = t(rank_ar, rank_en)
        
        next_target = 150 if my_points < 150 else my_points + 100
            
        st.markdown(f"<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown(f"<h3>{t('رصيد نقاطك الحالي', 'Your Points')}</h3>", unsafe_allow_html=True)
        st.markdown(f"<span class='rank-text'>{my_points} {t('نقطة', 'Pts')}</span> | <span style='font-size:20px;'>{t('الرتبة:', 'Rank:')} {rank}</span>", unsafe_allow_html=True)
        st.progress(min(my_points / next_target, 1.0))
        st.markdown("</div>", unsafe_allow_html=True)

        tab_work, tab_missions, tab_library, tab_backup = st.tabs([
            t("🛠️ إغلاق بلاغ", "🛠️ Close Task"), 
            t("🎯 مهام اليوم", "🎯 Daily Missions"),
            t("📚 المكتبة الفنية", "📚 Library"),
            t("🆘 طلب فزعة", "🆘 Ask for Backup")
        ])
        
        with tab_work:
            st.markdown(f"<div class='glass-card'>", unsafe_allow_html=True)
            dept = st.selectbox(t("القسم", "Department"), list(DEPTS.keys()), format_func=lambda x: x if st.session_state.lang == "عربي" else DEPTS[x])
            req_type = st.radio(t("نوع الطلب", "Request Type"), ["WRO", "PRO"])
            
            equip = st.selectbox(t("المعدة", "Equipment"), ["+"] + existing_eq)
            if equip == "+": equip = st.text_input(t("اكتب اسم المعدة:", "Enter Equipment Name:"))
                
            desc = st.text_area(t("وصف العمل المنجز", "Work Description"))
            
            spare = st.selectbox(t("قطع الغيار", "Spares"), ["+", "-"] + existing_sp)
            if spare == "+": spare = st.text_input(t("القطعة ورقم SAP:", "Spare & SAP:"))
            
            photo = st.camera_input(t("📸 إرفاق صورة العطل", "📸 Attach Image"))
            
            if st.button(t("✅ إغلاق البلاغ وحصد النقاط", "✅ Close Task & Earn Points"), use_container_width=True):
                if req_type == "WRO" and photo is None:
                    st.error(t("الصورة إلزامية للأعطال الطارئة!", "Image is mandatory for WRO!"))
                elif equip and desc:
                    pts = 20 if req_type == "PRO" else 10
                    new_data = pd.DataFrame({
                        "ID": [f"TKT-{len(df)+1}"], "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")],
                        "Branch": [st.session_state.branch], "Dept": [dept], "Type": [req_type],
                        "Equipment": [equip], "Description": [desc], "Spares": [spare],
                        "Status": ["Closed"], "Assigned_By": ["-"], "Assigned_To": ["-"],
                        "Tech_Name": [st.session_state.emp_name], "Points": [pts], "Has_Image": [photo is not None]
                    })
                    df = pd.concat([df, new_data], ignore_index=True)
                    df.to_csv(DATA_FILE, index=False)
                    send_telegram_alert(f"🌟 إنجاز جديد!\nالفني: {st.session_state.emp_name}\nالفرع: {display_branch}\nالمعدة: {equip}\nالنقاط المكتسبة: {pts} نقطة 🚀")
                    st.success(t("كفو يا بطل! تمت إضافة النقاط إلى رصيدك", "Great job hero! Points added to your balance!"))
                    st.balloons()
                else:
                    st.error(t("الرجاء إكمال جميع البيانات المطلوبة", "Please fill all required fields"))
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_missions:
            st.markdown(f"### 🎯 {t('تحديات تنتظرك!', 'Challenges waiting for you!')}")
            my_tasks = df[(df['Assigned_To'] == st.session_state.emp_name) & (df['Status'] == 'New')]
            if not my_tasks.empty:
                for idx, row in my_tasks.iterrows():
                    st.markdown(f"<div class='mission-box'><b>🚨 {row['Equipment']}</b><br>{row['Description']}<br><i>من: {row['Assigned_By']}</i></div>", unsafe_allow_html=True)
            else:
                st.info(t("لا توجد مهام طارئة موجهة لك حالياً. ممتاز!", "No assigned emergency tasks right now. Great!"))
                
        with tab_library:
            st.markdown(f"### 📚 {t('الكتالوجات والأدلة الفنية', 'Manuals & Technical Guides')}")
            st.write(t("سيتم ربط ملفات الكتالوجات قريباً...", "Catalog files will be linked soon..."))

        with tab_backup:
            st.markdown(f"### 🆘 {t('تحتاج مساعدة؟ اطلب فزعة', 'Need help? Ask for backup')}")
            sos_eq = st.selectbox(t("أين أنت الآن؟ (اختر المعدة)", "Where are you? (Select Machine)"), existing_eq if existing_eq else ["-"])
            sos_msg = st.text_area(t("ما هي المشكلة؟", "What is the problem?"))
            
            if st.button(t("🚨 إرسال نداء للفريق", "🚨 Send SOS to Team"), use_container_width=True):
                send_telegram_alert(f"🆘 نداء فزعة عاجل!\nالفني: {st.session_state.emp_name}\nالفرع: {display_branch}\nالمعدة: {sos_eq}\nالتفاصيل: {sos_msg}")
                st.success(t("تم إرسال النداء! فريق الدعم في الطريق إليك 🏃‍♂️", "SOS sent! Support team is on the way 🏃‍♂️"))
