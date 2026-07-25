import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import random

# ==========================================
# CONFIG & CSS
# ==========================================
st.set_page_config(page_title="E4GRID - Global Shield", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Inter', sans-serif; }
        .stApp { background: #0a0f1e; }
        .main-header { text-align: center; padding: 30px 20px 20px 20px; background: linear-gradient(135deg, #0a0f1e 0%, #1a2a4a 100%); border-radius: 30px; margin-bottom: 30px; border: 1px solid rgba(251, 191, 36, 0.15); }
        .main-header .logo-text { font-size: 4.2rem; font-weight: 800; background: linear-gradient(135deg, #fbbf24, #f59e0b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .main-header .tagline { color: #94a3b8; font-size: 1.1rem; letter-spacing: 2px; -webkit-text-fill-color: #94a3b8; }
        .main-header .sub-tagline { color: #64748b; font-size: 0.9rem; letter-spacing: 4px; -webkit-text-fill-color: #64748b; margin-top: 5px; }
        .glass-card { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; transition: 0.3s; }
        .glass-card:hover { border-color: #fbbf24; transform: translateY(-3px); box-shadow: 0 10px 30px rgba(251, 191, 36, 0.05); }
        .stButton > button { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #0a0f1e; font-weight: 700; border: none; border-radius: 12px; padding: 0.6rem 1.5rem; transition: 0.3s; }
        .stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 30px rgba(251, 191, 36, 0.3); }
        .stMetric { background: rgba(30, 41, 59, 0.5); backdrop-filter: blur(5px); border-radius: 12px; border-left: 4px solid #fbbf24; padding: 10px; }
        .footer { text-align: center; padding: 30px 0 10px 0; color: #475569; font-size: 0.9rem; border-top: 1px solid #1e293b; margin-top: 40px; }
        .footer a { color: #fbbf24; text-decoration: none; }
        .sidebar-logo { text-align: center; padding: 10px 0; border-bottom: 1px solid #1e293b; margin-bottom: 15px; }
        .sidebar-logo h2 { color: #fbbf24; font-weight: 700; margin: 0; }
        .sidebar-logo small { color: #64748b; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# DATA FOLDERS
# ==========================================
DATA_DIR = "data"
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

def load_json(filename, default):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ==========================================
# MASTER DATA
# ==========================================
if "factories" not in st.session_state:
    st.session_state.factories = load_json("factories.json", [
        {"id": 1, "name": "Saga Sports", "status": "Green", "risk": "Low", "client": "Nike"},
        {"id": 2, "name": "Forward Sports", "status": "Green", "risk": "Low", "client": "Nike"},
    ])

if "mnc_clients" not in st.session_state:
    st.session_state.mnc_clients = load_json("mnc_clients.json", {
        "Nike": {"password": "Nike@2026", "active": True},
        "Adidas": {"password": "Adidas@2026", "active": True}
    })

if "agencies" not in st.session_state:
    st.session_state.agencies = load_json("agencies.json", {
        "Pakistan": {"password": "Pak@1799", "helpline": "1799", "active": True},
        "USA": {"password": "FBI@911", "helpline": "911", "active": True}
    })

if "cyber_alerts" not in st.session_state:
    st.session_state.cyber_alerts = load_json("alerts.json", [])

if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = load_json("audit.json", [])

if "views_data" not in st.session_state:
    views_data = load_json("views.json", {"total": 0, "today": 0, "last_date": None})
    today_str = datetime.now().strftime("%Y-%m-%d")
    if views_data.get("last_date") != today_str:
        views_data["today"] = 0
        views_data["last_date"] = today_str
    views_data["total"] += 1
    views_data["today"] += 1
    st.session_state.views_data = views_data
    save_json("views.json", views_data)

ADMIN_PASSWORD = "esha4t4boss"

def log_audit(action, user="System"):
    st.session_state.audit_logs.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
        "action": action
    })
    save_json("audit.json", st.session_state.audit_logs)

def save_all():
    save_json("factories.json", st.session_state.factories)
    save_json("mnc_clients.json", st.session_state.mnc_clients)
    save_json("agencies.json", st.session_state.agencies)
    save_json("alerts.json", st.session_state.cyber_alerts)

def generate_tracking_id(country):
    code = country[:2].upper()
    year = datetime.now().year
    rand_num = str(random.randint(10000, 99999))
    return f"{code}-{year}-{rand_num}"

def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{timestamp}_{uploaded_file.name}"
        file_path = os.path.join(UPLOAD_DIR, safe_name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return safe_name
    return None

# ==========================================
# LANDING PAGE
# ==========================================
def landing_page():
    logo_col, text_col = st.columns([1, 4])
    with logo_col:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=120)
        else:
            st.markdown("<h1 style='color:#fbbf24;'>⚡</h1>", unsafe_allow_html=True)
    with text_col:
        st.markdown(
            """
            <div style="padding-top: 15px;">
                <div style="font-size: 2.8rem; font-weight: 800; background: linear-gradient(135deg, #fbbf24, #f59e0b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">E4GRID</div>
                <div style="color: #94a3b8; font-size: 1rem; letter-spacing: 2px;">INTELLIGENCE · COMPLIANCE · PROTECTION · TRUST</div>
                <div style="color: #64748b; font-size: 0.8rem; letter-spacing: 3px;">BUILDING A SAFER DIGITAL WORLD</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🌍 Public Reporting", use_container_width=True):
            st.session_state.role = "public"; st.session_state.logged_in = True; st.rerun()
    with col2:
        if st.button("🏢 Enterprise (MNC)", use_container_width=True):
            st.session_state.landing_target = "mnc"; st.rerun()
    with col3:
        if st.button("🛡️ Agency (Police)", use_container_width=True):
            st.session_state.landing_target = "agency"; st.rerun()
    with col4:
        if st.button("👑 Owner (Admin)", use_container_width=True):
            st.session_state.landing_target = "admin"; st.rerun()

    if "landing_target" in st.session_state:
        target = st.session_state.landing_target
        st.divider()
        with st.container():
            st.subheader(f"Login: {target.title()}")
            identifier = st.text_input("Username/Country")
            password = st.text_input("Password", type="password")
            if st.button("Authenticate"):
                if target == "admin" and password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True; st.session_state.role = "admin"; log_audit("Admin Login"); st.rerun()
                elif target == "mnc" and identifier in st.session_state.mnc_clients:
                    if st.session_state.mnc_clients[identifier]["password"] == password and st.session_state.mnc_clients[identifier]["active"]:
                        st.session_state.logged_in = True; st.session_state.role = "mnc"; st.session_state.client = identifier; log_audit(f"MNC Login: {identifier}"); st.rerun()
                elif target == "agency" and identifier in st.session_state.agencies:
                    if st.session_state.agencies[identifier]["password"] == password and st.session_state.agencies[identifier]["active"]:
                        st.session_state.logged_in = True; st.session_state.role = "agency"; st.session_state.client = identifier; log_audit(f"Agency Login: {identifier}"); st.rerun()
                else:
                    st.error("Invalid credentials")

# ==========================================
# PUBLIC DASHBOARD
# ==========================================
def public_dashboard():
    st.header("🌍 Report Incident")
    with st.form("report_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your Name")
            email = st.text_input("Email (for tracking)")
            country = st.selectbox("Country", list(st.session_state.agencies.keys()) + ["Other"])
            city = st.text_input("City")
        with col2:
            category = st.selectbox("Category", ["Cyber Blackmail", "Hacking", "Data Breach", "Compliance", "Other"])
            incident_date = st.date_input("Incident Date", datetime.now())
            website = st.text_input("Website/URL")
        complaint = st.text_area("Description", height=150)
        evidence = st.file_uploader("Upload Evidence", type=['png', 'jpg', 'pdf', 'txt'])
        anonymous = st.checkbox("Submit Anonymously")
        
        if st.form_submit_button("🚔 Submit Report", use_container_width=True):
            if complaint:
                file_name = save_uploaded_file(evidence)
                tracking_id = generate_tracking_id(country)
                new_alert = {
                    "id": len(st.session_state.cyber_alerts)+1,
                    "tracking_id": tracking_id, "name": name if name else "Anonymous",
                    "email": email, "country": country, "city": city,
                    "category": category, "text": complaint, "website": website,
                    "evidence_file": file_name, "status": "New", "priority": "Medium",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"), "notes": ""
                }
                st.session_state.cyber_alerts.append(new_alert)
                save_all()
                log_audit(f"Public Report Submitted: {tracking_id}")
                st.success(f"✅ Report Submitted! Tracking ID: **{tracking_id}**")
            else:
                st.error("Please describe the incident.")

    st.divider()
    st.subheader("🔍 Track Complaint")
    track = st.text_input("Enter Tracking ID")
    if st.button("Check Status"):
        found = [a for a in st.session_state.cyber_alerts if a.get("tracking_id") == track]
        if found:
            st.success(f"Status: {found[0]['status']}")

# ==========================================
# ADMIN DASHBOARD
# ==========================================
def admin_dashboard():
    st.header("👑 Command Center")
    
    total = len(st.session_state.cyber_alerts)
    pending = len([a for a in st.session_state.cyber_alerts if a['status'] not in ['Resolved', 'Closed', 'Archived']])
    resolved = len([a for a in st.session_state.cyber_alerts if a['status'] == 'Resolved'])
    views = st.session_state.views_data
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📊 Reports", total)
    col2.metric("⏳ Pending", pending)
    col3.metric("✅ Resolved", resolved)
    col4.metric("👁️ Total Views", views["total"])
    col5.metric("📆 Today", views["today"])
    
    if st.session_state.cyber_alerts:
        df = pd.DataFrame(st.session_state.cyber_alerts)
        if not df.empty and 'category' in df.columns:
            col_ch1, col_ch2 = st.columns(2)
            with col_ch1:
                st.subheader("Category Breakdown")
                st.bar_chart(df['category'].value_counts())
            with col_ch2:
                st.subheader("Status Distribution")
                st.bar_chart(df['status'].value_counts())

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Reports", "🏭 Factory", "🌍 Agencies", "📜 Audit Logs"])
    
    with tab1:
        search = st.text_input("🔍 Search")
        filtered = st.session_state.cyber_alerts
        if search:
            filtered = [a for a in filtered if search.lower() in str(a.get('tracking_id', '')).lower() or search.lower() in a.get('name', '').lower()]
        active_reports = [a for a in filtered if a.get('status') != 'Archived']
        if active_reports:
            df = pd.DataFrame(active_reports)
            st.dataframe(df[['tracking_id', 'name', 'country', 'category', 'status', 'priority', 'time']], use_container_width=True)
            for alert in active_reports:
                with st.expander(f"📌 {alert.get('tracking_id')} - {alert.get('name')}"):
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.write(f"**Details:** {alert.get('text')}")
                        if alert.get('evidence_file'):
                            file_path = os.path.join(UPLOAD_DIR, alert['evidence_file'])
                            if os.path.exists(file_path):
                                if alert['evidence_file'].lower().endswith(('png', 'jpg', 'jpeg')):
                                    st.image(file_path, caption="Evidence", width=300)
                                else:
                                    with open(file_path, "rb") as f:
                                        st.download_button("📥 Download Evidence", f, file_name=alert['evidence_file'])
                        notes = st.text_area("Internal Notes", value=alert.get('notes', ''), key=f"notes_{alert['id']}")
                        if notes != alert.get('notes'):
                            alert['notes'] = notes
                            save_all()
                            log_audit(f"Notes updated for {alert.get('tracking_id')}")
                    with col_b:
                        new_status = st.selectbox("Status", ["New", "Under Review", "Resolved", "Closed", "Archived"], index=["New","Under Review","Resolved","Closed","Archived"].index(alert.get('status')), key=f"st_{alert['id']}")
                        if new_status != alert.get('status'):
                            alert['status'] = new_status
                            save_all()
                            log_audit(f"Status changed to {new_status} for {alert.get('tracking_id')}")
                        priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=["Low","Medium","High"].index(alert.get('priority', 'Medium')), key=f"pr_{alert['id']}")
                        if priority != alert.get('priority'):
                            alert['priority'] = priority
                            save_all()
        else:
            st.success("✅ No active reports.")
    
    with tab2:
        st.dataframe(pd.DataFrame(st.session_state.factories))
        col1, col2 = st.columns(2)
        with col1:
            n = st.text_input("Factory Name")
            c = st.selectbox("Assign", list(st.session_state.mnc_clients.keys()))
            s = st.selectbox("Status", ["Green", "Yellow", "Red"])
            if st.button("Add"):
                if n:
                    st.session_state.factories.append({"id": len(st.session_state.factories)+1, "name": n, "status": s, "risk": "Low" if s=="Green" else "Medium", "client": c})
                    save_all(); log_audit(f"Factory Added: {n}"); st.rerun()
        with col2:
            d = st.number_input("Delete ID", min_value=1, step=1)
            if st.button("Delete"):
                st.session_state.factories = [f for f in st.session_state.factories if f["id"] != d]
                save_all(); log_audit(f"Factory Deleted: ID {d}"); st.rerun()

    with tab3:
        for name, data in st.session_state.agencies.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1: st.write(f"**{name}**")
            with col2:
                np = st.text_input(f"Pass", value=data["password"], key=f"ap_{name}")
                if np != data["password"]: st.session_state.agencies[name]["password"] = np; save_all(); log_audit(f"Agency Pass changed: {name}")
            with col3:
                active = st.checkbox("Active", value=data["active"], key=f"aa_{name}")
                if active != data["active"]: st.session_state.agencies[name]["active"] = active; save_all(); st.rerun()
        n_ag = st.text_input("New Country"); n_pass = st.text_input("Pass"); n_hl = st.text_input("Helpline")
        if st.button("Add Agency"):
            st.session_state.agencies[n_ag] = {"password": n_pass, "helpline": n_hl, "active": True}
            save_all(); log_audit(f"Agency Added: {n_ag}"); st.rerun()

    with tab4:
        st.subheader("📜 Complete Activity Trail")
        if st.session_state.audit_logs:
            df_audit = pd.DataFrame(st.session_state.audit_logs[::-1])
            st.dataframe(df_audit, use_container_width=True)
        else:
            st.info("No activities recorded yet.")

# ==========================================
# MNC & AGENCY
# ==========================================
def mnc_dashboard(client):
    st.header(f"🏢 {client} - Compliance")
    df = pd.DataFrame([f for f in st.session_state.factories if f["client"] == client])
    st.dataframe(df)

def agency_dashboard(agency):
    st.header(f"🛡️ {agency} - Cases")
    my_reports = [a for a in st.session_state.cyber_alerts if a.get("country") == agency and a.get('status') != 'Archived']
    if my_reports:
        st.dataframe(pd.DataFrame(my_reports)[['tracking_id', 'category', 'status', 'priority', 'notes']])
        if st.button("📥 Export CSV"):
            df = pd.DataFrame(my_reports)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download", csv, "report.csv", "text/csv")
    else:
        st.success("✅ No cases.")

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    else:
        st.markdown("<h2 style='color:#fbbf24;'>⚡ E4GRID</h2>", unsafe_allow_html=True)
    st.caption("Intelligence · Compliance · Protection · Trust")
    st.divider()
    if st.session_state.get("logged_in", False):
        st.write(f"**User:** `{st.session_state.role}`")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.client = None
            st.session_state.landing_target = None
            st.rerun()

# ==========================================
# MAIN ROUTER
# ==========================================
if "landing_target" not in st.session_state: st.session_state.landing_target = None

if not st.session_state.get("logged_in", False):
    landing_page()
else:
    if st.session_state.role == "public": public_dashboard()
    elif st.session_state.role == "admin": admin_dashboard()
    elif st.session_state.role == "mnc": mnc_dashboard(st.session_state.client)
    elif st.session_state.role == "agency": agency_dashboard(st.session_state.client)

# ==========================================
# FOOTER
# ==========================================
st.markdown("""
<div class="footer">
    © 2026 E4GRID. Built with ❤️ for Global Security.
    <br>
    <a href="#">Privacy Policy</a> · <a href="#">Contact</a> · <a href="https://linkedin.com/comp
