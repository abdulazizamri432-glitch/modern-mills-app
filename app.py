import streamlit as st
import pandas as pd
import requests
import os
import random
from datetime import datetime

# ==========================================
# 1. System Configuration & CSS
# ==========================================
st.set_page_config(page_title="MMC Smart Maintenance", page_icon="🏭", layout="wide")

st.markdown("""
<style>
    .stButton>button { border-radius: 6px; font-weight: bold; width: 100%; }
    .main-header { text-align: center; color: #2C3E50; margin-bottom: 5px; }
    .sub-header { text-align: center; color: #7F8C8D; margin-bottom: 40px; }
    .warning-box { background-color: #FDEDEC; padding: 15px; border-left: 5px solid #E74C3C; border-radius: 5px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Telegram & Settings
# ==========================================
BOT_TOKEN = "8912670603:AAEr-hufquf8PIxnv-aKv0fz-9WgZa0oRks"
BRANCH_CHATS = {
    "Al-Jumum": "-5159290787", 
    "Al-Jouf": "-5176017884", 
    "Khamis Mushait": "-5104633079"
}
BRANCH_PASSCODES = {
    "Al-Jumum": "2004", 
    "Al-Jouf": "2026", 
    "Khamis Mushait": "1425"
}
DEPARTMENTS = ["Mechanics", "Electrical", "Welding", "HVAC"]

MOTIVATIONS = [
    "Outstanding work! You're the backbone of this factory! 🚀",
    "Brilliant job! Another problem solved like a true pro! 💯",
    "Exceptional effort! You're keeping the gears turning! ⚙️🔥",
    "Fantastic! Your dedication is what makes MMC great! 🌟",
    "Masterful execution! Keep up the incredible momentum! 🏆"
]

def send_telegram(msg, branch):
    chat_id = BRANCH_CHATS.get(branch)
    if chat_id:
        try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": chat_id, "text": f"📍 [{branch} Update]:\n{msg}"})
        except: pass

# ==========================================
# 3. Database Initialization
# ==========================================
files = {
    "tickets_db.csv": ["Date", "Branch", "Dept", "Type", "Device", "Location", "Tech_Name", "Points", "Status"],
    "rolls_db.csv": ["Date", "Branch", "Roll_Type", "Status", "Device", "Start_Time", "End_Time"],
    "users_db.csv": ["Name", "EmpID", "Branch", "Dept", "Total_Points"]
}
for file, cols in files.items():
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)

df_tickets = pd.read_csv("tickets_db.csv")
df_rolls = pd.read_csv("rolls_db.csv")
df_users = pd.read_csv("users_db.csv")

# ==========================================
# 4. Session State Management
# ==========================================
if 'welcome_screen' not in st.session_state: st.session_state.welcome_screen = True
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# ==========================================
# 5. Welcome & Login Screens
# ==========================================
if st.session_state.welcome_screen:
    st.markdown("<h1 class='main-header'>🏭 MMC Smart Maintenance</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='sub-header'>Enterprise Asset & Task Management System</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("Welcome to the centralized maintenance hub. Please proceed to authenticate.")
        if st.button("Access Portal 🔐", type="primary"):
            st.session_state.welcome_screen = False; st.rerun()

elif not st.session_state.logged_in:
    st.markdown("<h2 class='main-header'>System Authentication</h2><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            branch = st.selectbox("Select Branch", list(BRANCH_CHATS.keys()))
            name = st.text_input("Full Name")
            eid = st.text_input("Employee ID")
            dept = st.selectbox("Department", DEPARTMENTS)
            role = st.radio("Access Level", ["Technician", "Manager / Supervisor"])
            passcode = st.text_input("Passcode (Managers Only)", type="password") if "Manager" in role else ""

            st.write("") 
            if st.button("Login", type="primary"):
                if "Manager" in role and passcode != BRANCH_PASSCODES.get(branch):
                    st.error("❌ Invalid Manager Passcode for this branch!")
                elif not name or not eid:
                    st.warning("⚠️ Please fill in your Name and Employee ID.")
                else:
                    st.session_state.update({"logged_in": True, "name": name, "eid": eid, "branch": branch, "dept": dept, "role": role})
                    if eid not in df_users['EmpID'].astype(str).values:
                        pd.concat([df_users, pd.DataFrame([{"Name": name, "EmpID": eid, "Branch": branch, "Dept": dept, "Total_Points": 0}])]).to_csv("users_db.csv", index=False)
                    st.rerun()

# ==========================================
# 6. Main Dashboard
# ==========================================
else:
    st.sidebar.markdown(f"## 👤 {st.session_state.name}")
    st.sidebar.markdown(f"**🏢 Branch:** {st.session_state.branch}")
    st.sidebar.markdown(f"**🛠️ Dept:** {st.session_state.dept}")
    st.sidebar.markdown("---")
    
    user_pts = df_tickets[df_tickets['Tech_Name'] == st.session_state.name]['Points'].sum()
    if st.session_state.role == "Technician":
        rank = "Elite Master 👑" if user_pts >= 100 else "Rising Star ⭐️" if user_pts >= 50 else "Creative Tech 🔧"
        st.sidebar.metric(label="Current Rank", value=rank)
        st.sidebar.metric(label="Total Points", value=f"{user_pts} Pts")
        st.sidebar.markdown("---")

    if st.sidebar.button("Logout 🚪"):
        st.session_state.logged_in = False
        st.session_state.welcome_screen = True
        st.rerun()

    # ------------------------------------------
    # TECHNICIAN DASHBOARD
    # ------------------------------------------
    if st.session_state.role == "Technician":
        t1, t2, t3 = st.tabs(["🛠️ Maintenance Tasks", "📋 Rolls Management", "🏆 Global Leaderboard"])
        
        with t1:
            st.subheader("Submit New Maintenance Record")
            with st.container(border=True):
                task_type = st.radio("Select Task Type:", ["Work Request Order (WRO) - 10 Pts", "Preventative Request Order (PRO) - 20 Pts"])
                c1, c2 = st.columns(2)
                device = c1.text_input("Device Name / ID")
                loc = c2.text_input("Exact Location")
                
                c_start, c_end = st.columns(2)
                start_t = c_start.time_input("Task Start Time")
                end_t = c_end.time_input("Task End Time")
                
                st.write("**Media & Attachments (Optional)**")
                img = st.file_uploader("Upload Work Proof (Image)", type=['png', 'jpg', 'jpeg'])
                aud = st.audio_input("Record Voice Notes")
                
                if st.button("🚀 Submit Task & Earn Points", type="primary"):
                    pts = 10 if "WRO" in task_type else 20
                    short_type = "WRO" if "WRO" in task_type else "PRO"
                    new_t = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Branch": st.session_state.branch, "Dept": st.session_state.dept, "Type": short_type, "Device": device, "Location": loc, "Tech_Name": st.session_state.name, "Points": pts, "Status": "Completed"}])
                    pd.concat([df_tickets, new_t]).to_csv("tickets_db.csv", index=False)
                    send_telegram(f"✅ Task Completed ({short_type})\nTech: {st.session_state.name}\nDevice: {device}\nPoints Earned: +{pts}", st.session_state.branch)
                    st.balloons()
                    st.success(f"**Task Submitted Successfully! (+{pts} Pts)**\n\n💬 *{random.choice(MOTIVATIONS)}*")

        with t2:
            st.subheader("Roll Lifecycle Management")
            roll_action = st.radio("Choose Action:", ["Install/Replace a Roll", "Manage Inventory (Ready Rolls)"])
            
            if "Install" in roll_action:
                with st.container(border=True):
                    r_device = st.text_input("Target Device Name/ID:", key="rd")
                    r_type = st.text_input("Roll Type:", key="rt")
                    c1, c2 = st.columns(2)
                    r_start = c1.time_input("Installation Start Time:", key="rs")
                    r_end = c2.time_input("Installation End Time:", key="re")
                    
                    if st.button("Confirm Installation ⚙️", type="primary"):
                        pd.concat([df_rolls, pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Branch": st.session_state.branch, "Roll_Type": r_type, "Status": "Installed", "Device": r_device, "Start_Time": str(r_start), "End_Time": str(r_end)}])]).to_csv("rolls_db.csv", index=False)
                        df_ready = pd.read_csv("rolls_db.csv")
                        idx_drop = df_ready[(df_ready['Branch'] == st.session_state.branch) & (df_ready['Status'] == "Ready") & (df_ready['Roll_Type'] == r_type)].index
                        if not idx_drop.empty:
                            df_ready = df_ready.drop(idx_drop[0])
                            df_ready.to_csv("rolls_db.csv", index=False)
                        send_telegram(f"⚙️ Roll Installed\nType: {r_type}\nDevice: {r_device}\nTech: {st.session_state.name}", st.session_state.branch)
                        st.success("Roll installation logged perfectly. Inventory updated!")
            else:
                with st.container(border=True):
                    new_ready = st.text_input("Enter New Roll Type:")
                    if st.button("➕ Add to Ready Stock"):
                        pd.concat([df_rolls, pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Branch": st.session_state.branch, "Roll_Type": new_ready, "Status": "Ready", "Device": "N/A", "Start_Time": "N/A", "End_Time": "N/A"}])]).to_csv("rolls_db.csv", index=False)
                        st.rerun()
                    st.dataframe(df_rolls[(df_rolls['Branch'] == st.session_state.branch) & (df_rolls['Status'] == 'Ready')][['Date', 'Roll_Type']], use_container_width=True)

        with t3:
            st.subheader("Wall of Fame 🏆")
            leaderboard = df_tickets.groupby(['Branch', 'Dept', 'Tech_Name'])['Points'].sum().reset_index()
            c_local, c_global = st.columns(2)
            with c_local:
                st.write(f"**🏢 Top in {st.session_state.branch}**")
                branch_lb = leaderboard[leaderboard['Branch'] == st.session_state.branch].sort_values(by='Points', ascending=False)
                for dpt in DEPARTMENTS:
                    dept_top = branch_lb[branch_lb['Dept'] == dpt]
                    if not dept_top.empty: st.info(f"**{dpt}:** {dept_top.iloc[0]['Tech_Name']} ({dept_top.iloc[0]['Points']} pts)")
            with c_global:
                st.write("**🌍 Top 3 Company-Wide**")
                global_lb = df_tickets.groupby('Tech_Name')['Points'].sum().reset_index().sort_values(by='Points', ascending=False).head(3)
                medals = ["🥇", "🥈", "🥉"]
                for i, row in global_lb.reset_index(drop=True).iterrows(): st.success(f"{medals[i]} {row['Tech_Name']} - {row['Points']} pts")

    # ------------------------------------------
    # MANAGER DASHBOARD (Upgraded Intelligence)
    # ------------------------------------------
    elif "Manager" in st.session_state.role:
        st.subheader(f"📊 Command Center - {st.session_state.branch}")
        
        branch_tickets = df_tickets[df_tickets['Branch'] == st.session_state.branch]
        
        tab1, tab2, tab3 = st.tabs(["🔍 Analytics & Filters", "🚨 Predictive Alerts", "🎯 Operations & Export"])
        
        with tab1:
            st.markdown("#### Advanced Search & Logs")
            c1, c2 = st.columns(2)
            filter_dept = c1.multiselect("Filter by Department", DEPARTMENTS, default=DEPARTMENTS)
            
            # Safe check for tech names
            tech_options = branch_tickets['Tech_Name'].unique() if not branch_tickets.empty else []
            filter_tech = c2.multiselect("Filter by Technician", tech_options)
            
            filtered_df = branch_tickets[branch_tickets['Dept'].isin(filter_dept)]
            if filter_tech:
                filtered_df = filtered_df[filtered_df['Tech_Name'].isin(filter_tech)]
                
            st.dataframe(filtered_df, use_container_width=True)
            
        with tab2:
            st.markdown("#### Predictive Maintenance Intelligence")
            if not branch_tickets.empty:
                # Count failures per device
                device_counts = branch_tickets['Device'].value_counts()
                problematic = device_counts[device_counts >= 3]
                
                if problematic.empty:
                    st.success("✅ All systems optimal. No recurring device issues detected.")
                else:
                    for dev, count in problematic.items():
                        st.markdown(f"<div class='warning-box'>⚠️ <b>CRITICAL WARNING:</b> Device '<b>{dev}</b>' has broken down {count} times! Immediate root cause analysis is strongly recommended to prevent further downtime.</div>", unsafe_allow_html=True)
            else:
                st.info("Not enough data to run predictive models yet.")
                
        with tab3:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("#### Dispatch Tasks")
                with st.form("assign_form"):
                    a_type = st.selectbox("Priority & Task Type", ["Emergency Breakdown", "Maintenance Day", "Preventative Care"])
                    a_tech = st.text_input("Assign to (Exact Name)")
                    a_desc = st.text_area("Detailed Instructions")
                    if st.form_submit_button("📤 Dispatch Task", type="primary"):
                        send_telegram(f"🔔 NEW TASK ALERT ({a_type})\nTo: {a_tech}\nDetails: {a_desc}\nFrom: Management", st.session_state.branch)
                        st.success("Task dispatched and Telegram notification sent!")
            with c2:
                st.markdown("#### Generate Reports")
                st.info("Download full maintenance logs for Excel/PDF conversion.")
                if not branch_tickets.empty:
                    csv_data = branch_tickets.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Excel/CSV Report",
                        data=csv_data,
                        file_name=f"MMC_Maintenance_Report_{st.session_state.branch}.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("No records to export.")
