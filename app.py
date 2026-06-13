import streamlit as st
import pandas as pd
import datetime
import requests
import time

# --- إعدادات الصفحة ---
st.set_page_config(page_title="MMC Smart Maintenance", page_icon="⚙️", layout="wide")

# --- المتغيرات الأساسية (الرجاء وضع التوكن الخاص بك هنا) ---
TELEGRAM_BOT_TOKEN = "ضع_التوكن_هنا"
TELEGRAM_CHAT_ID = "ضع_رقم_القروب_هنا"

# --- دوال مساعدة ---
def send_telegram_message(text):
    """دالة لإرسال رسائل فخمة للتليجرام باستخدام Markdown"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        pass # يتجاهل الخطأ لو مافيه إنترنت

# --- قاعدة بيانات تجريبية ---
technicians = ["أحمد الدوسري", "خالد عبدالله", "ياسر محمد", "سعد القحطاني"]
machines = ["طاحونة أ", "طاحونة ب", "سير التغليف", "خزان التعبئة", "الغربال الرئيسي"]

# --- تهيئة متغيرات تحدي البيت ستوب ---
if 'pitstop_active' not in st.session_state:
    st.session_state.pitstop_active = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# --- واجهة الموقع ---
st.title("⚙️ نظام المطاحن الحديثة للصيانة الذكية (MMC)")
st.markdown("---")

# تقسيم الموقع إلى أقسام (Tabs) لسهولة التنقل
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛠️ تسجيل صيانة (LOTO)", 
    "🚨 الفزعة", 
    "🏎️ تحدي البيت ستوب", 
    "🎬 تيك توك الصيانة",
    "📊 لوحة الإدارة"
])

# ==========================================
# التاب الأول: تسجيل الصيانة والورشة المشتركة
# ==========================================
with tab1:
    st.header("🛠️ تسجيل مهمة صيانة جديدة")
    
    col1, col2 = st.columns(2)
    with col1:
        task_type = st.radio("نوع المهمة:", ["WRO (عطل طارئ)", "PRO (صيانة دورية)"])
        machine_name = st.selectbox("المعدة المستهدفة:", machines)
        issue_desc = st.text_area("وصف العمل الذي تم إنجازه:")
        
    with col2:
        main_tech = st.selectbox("الفني المسؤول (قائد المهمة):", technicians)
        co_op_techs = st.multiselect("إضافة زملاء للمهمة (نظام الورشة المشتركة 👥):", technicians)
    
    st.markdown("### 🔒 نقطة التفتيش الإجبارية (LOTO)")
    st.info("⚠️ لن تتمكن من إغلاق المهمة حتى تقوم بتصوير قفل العزل الآمن (LOTO) على المعدة.")
    
    loto_photo = st.camera_input("الرجاء التقاط صورة قفل العزل 📸")
    
    # لا يظهر زر الإغلاق إلا إذا تم التقاط الصورة
    if loto_photo is not None:
        if st.button("✅ إغلاق المهمة واعتماد الشغل", use_container_width=True):
            team = [main_tech] + co_op_techs
            team_str = "، ".join(team)
            
            # رسالة التليجرام الفخمة
            msg = f"""
✅ *تم إنجاز مهمة بنجاح ({task_type[:3]})*
━━━━━━━━━━━━━━
⚙️ *المعدة:* {machine_name}
👨‍🔧 *فريق العمل:* {team_str}
📝 *الوصف:* {issue_desc}
🔒 *السلامة:* تم التأكيد بصورة LOTO الميدانية.
🏆 *النقاط:* تمت إضافة النقاط لرصيد الفريق!
"""
            send_telegram_message(msg)
            st.success("🎉 تم حفظ المهمة وتوزيع النقاط على الفريق وإرسال إشعار للإدارة!")
            st.balloons()

# ==========================================
# التاب الثاني: نظام الفزعة
# ==========================================
with tab2:
    st.header("🚨 نداء فزعة طارئ (SOS Backup)")
    st.markdown("تحتاج مساعدة في رفع قطعة ثقيلة؟ أو واجهتك مشكلة معقدة؟ اطلب الفزعة من زملائك!")
    
    sos_tech = st.selectbox("من أنت؟", technicians, key="sos_tech")
    sos_location = st.selectbox("الموقع الحالي:", machines, key="sos_loc")
    sos_reason = st.text_input("وش المشكلة وتحتاج مين؟ (مثال: أحتاج شباب نرفع ماطور ثقيل)")
    
    if st.button("🚨 أرسل نداء الفزعة للقروب 🚨", type="primary", use_container_width=True):
        sos_msg = f"""
🚨 *نـــداء فـــزعـــة طـــارئ!* 🚨
━━━━━━━━━━━━━━
👨‍🔧 *طالب الفزعة:* {sos_tech}
📍 *الموقع:* {sos_location}
⚠️ *السبب:* {sos_reason}

🏃‍♂️ *يا شباب اللي قريب منه يتوجه له فوراً!*
"""
        send_telegram_message(sos_msg)
        st.error("تم إطلاق صفارة الإنذار في قروب التليجرام! زملاؤك في الطريق إليك 🏃‍♂️💨")

# ==========================================
# التاب الثالث: تحدي البيت ستوب
# ==========================================
with tab3:
    st.header("🏎️ تحدي البيت ستوب (F1 Pit Stop)")
    st.markdown("تحدي أسرع وقت لتغيير الرولات! هل تستطيع كسر الرقم القياسي؟")
    
    pit_tech = st.selectbox("الفني المتحدي:", technicians, key="pit_tech")
    pit_machine = st.selectbox("الماكينة:", ["طاحونة أ", "طاحونة ب"], key="pit_mac")
    
    if not st.session_state.pitstop_active:
        if st.button("🏁 ابدأ التحدي (Start Timer)", type="primary"):
            st.session_state.pitstop_active = True
            st.session_state.start_time = time.time()
            st.rerun()
    else:
        st.warning("⏱️ التحدي جاري الآن... أسرع!")
        if st.button("🛑 تم الانتهاء من تركيب الرول (Stop Timer)"):
            end_time = time.time()
            elapsed_seconds = int(end_time - st.session_state.start_time)
            mins, secs = divmod(elapsed_seconds, 60)
            
            st.session_state.pitstop_active = False
            st.success(f"🎉 تم التغيير في: {mins} دقيقة و {secs} ثانية!")
            
            msg = f"🏎️ *تحدي البيت ستوب!*\nالبطل {pit_tech} قام بتغيير رول {pit_machine} في زمن قياسي: *{mins} دقيقة و {secs} ثانية!* 🏁"
            send_telegram_message(msg)
            st.balloons()
            st.session_state.start_time = None
            st.rerun()

# ==========================================
# التاب الرابع: تيك توك الصيانة
# ==========================================
with tab4:
    st.header("🎬 تيك توك الصيانة (Maintenance Reels)")
    st.markdown("شارك زملائك إبداعك، خبرتك، أو لقطة الأسبوع! (الفيديو يجب أن يكون قصير)")
    
    uploader_tech = st.selectbox("من الناشر؟", technicians + ["المدير العام"], key="tik_tech")
    video_title = st.text_input("عنوان المقطع:")
    video_file = st.file_uploader("ارفع الفيديو (MP4/MOV)", type=['mp4', 'mov'])
    
    if video_file is not None:
        st.video(video_file)
        if st.button("🚀 نشر المقطع للجميع"):
            st.success(f"تم نشر مقطع '{video_title}' بواسطة {uploader_tech} بنجاح!")
            msg = f"🎬 *مقطع جديد في تيك توك الصيانة!*\nنشر {uploader_tech} مقطعاً بعنوان: {video_title}.. ادخلوا النظام لمشاهدته!"
            send_telegram_message(msg)

# ==========================================
# التاب الخامس: لوحة الإدارة
# ==========================================
with tab5:
    st.header("📊 لوحة الإدارة المبسطة")
    st.markdown("هنا تظهر إحصائيات المصنع (مثال تجريبي):")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي البلاغات اليوم", "12", "+2")
    col2.metric("أسرع Pit Stop", "14:30 دقيقة", "-1:20", delta_color="inverse")
    col3.metric("معدل السلامة (LOTO)", "100%", "مثالي")
    
    st.markdown("### 🏆 لوحة الشرف (Top Technicians)")
    df = pd.DataFrame({
        "الفني": ["أحمد الدوسري", "سعد القحطاني", "خالد عبدالله"],
        "النقاط": [450, 320, 290],
        "الأوسمة": ["👑 ملك الميكانيكا", "🦸‍♂️ راعي الفزعات", "⚡ البرق"]
    })
    st.dataframe(df, use_container_width=True)