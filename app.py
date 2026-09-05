import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import random
import requests

# ==========================================
# 🔒 SECURE
# ==========================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ==========================================
# 🛡️ FIXED: DELETE WITH WHERE CLAUSE (db_delete_all)
# ==========================================
def db_get(table, select="*", match=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}?select={select}"
    if match:
        for key, value in match.items():
            url += f"&{key}=eq.{value}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return []

def db_post(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    response = requests.post(url, headers=HEADERS, json=data)
    return response.status_code == 201

def db_delete_all(table):
    """FIXED: Supabase requires a WHERE clause. Adding ?id=neq.0 to delete all."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=neq.0"
    response = requests.delete(url, headers=HEADERS)
    return response.status_code in [200, 204]

def save_data(table, data):
    # 1. DELETE (Ab with WHERE clause, isliye chalega)
    del_resp = requests.delete(f"{SUPABASE_URL}/rest/v1/{table}?id=neq.0", headers=HEADERS)
    if del_resp.status_code not in [200, 204]:
        st.error(f"❌ DELETE FAILED for {table}!\nStatus: {del_resp.status_code}\nMessage: {del_resp.text[:200]}")
        return False
    
    # 2. INSERT
    for item in data:
        post_resp = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=item)
        if post_resp.status_code != 201:
            st.error(f"❌ INSERT FAILED for {table}!\nStatus: {post_resp.status_code}\nMessage: {post_resp.text[:200]}")
            return False
    
    st.success(f"✅ Data saved successfully for {table}!")
    return True

# ==========================================
# DATA LOAD FUNCTIONS
# ==========================================
def load_factories():
    data = db_get("factories")
    if data:
        for item in data:
            if "verified" not in item: item["verified"] = False
            if "manual_score" not in item: item["manual_score"] = 0
            if "manual_status" not in item: item["manual_status"] = "Green"
            if "manual_reason" not in item: item["manual_reason"] = "No reason"
            if "country" not in item: item["country"] = "Pakistan"
        return data
    return [{"id": 1, "name": "Saga Sports", "client": "Nike", "country": "Pakistan", "status": "Green", "risk": "Low", "manual_score": 85, "manual_status": "Green", "manual_reason": "Verified safe", "verified": False, "history": []}]

def save_factories(data):
    save_data("factories", data)

def load_mnc_clients():
    data = db_get("mnc_clients")
    if data:
        return {item["name"]: {"password": item["password"], "active": item["active"]} for item in data}
    return {"Nike": {"password": "Nike@2026", "active": True}, "Adidas": {"password": "Adidas@2026", "active": True}}

def save_mnc_clients(data):
    transformed = [{"name": k, "password": v["password"], "active": v["active"]} for k, v in data.items()]
    save_data("mnc_clients", transformed)

def load_agencies():
    data = db_get("agencies")
    if data:
        return {item["name"]: {"password": item["password"], "helpline": item["helpline"], "active": item["active"]} for item in data}
    return {"Pakistan": {"password": "Pak@1799", "helpline": "1799", "active": True}, "USA": {"password": "FBI@911", "helpline": "911", "active": True}}

def save_agencies(data):
    transformed = [{"name": k, "password": v["password"], "helpline": v["helpline"], "active": v["active"]} for k, v in data.items()]
    save_data("agencies", transformed)

def load_alerts():
    data = db_get("cyber_alerts")
    if data:
        for item in data:
            if "priority" not in item: item["priority"] = "Medium"
            if "notes" not in item: item["notes"] = ""
        return data
    return []

def save_alerts(data):
    save_data("cyber_alerts", data)

def load_audit():
    data = db_get("audit_logs")
    return data if data else []

def save_audit(data):
    save_data("audit_logs", data)

def load_views():
    data = db_get("views_data")
    if data:
        return data[0]
    return {"total": 0, "today": 0, "last_date": None}

def save_views(data):
    db_delete_all("views_data")
    db_post("views_data", data)

# ==========================================
# SESSION STATE INIT
# ==========================================
if "factories" not in st.session_state:
    st.session_state.factories = load_factories()
if "mnc_clients" not in st.session_state:
    st.session_state.mnc_clients = load_mnc_clients()
if "agencies" not in st.session_state:
    st.session_state.agencies = load_agencies()
if "cyber_alerts" not in st.session_state:
    st.session_state.cyber_alerts = load_alerts()
if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = load_audit()
if "views_data" not in st.session_state:
    views = load_views()
    today_str = datetime.now().strftime("%Y-%m-%d")
    if views.get("last_date") != today_str:
        views["today"] = 0
        views["last_date"] = today_str
    views["total"] += 1
    views["today"] += 1
    st.session_state.views_data = views
    save_views(views)

def log_audit(action, user="System"):
    st.session_state.audit_logs.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
        "action": action
    })
    save_audit(st.session_state.audit_logs)

def save_all():
    save_factories(st.session_state.factories)
    save_mnc_clients(st.session_state.mnc_clients)
    save_agencies(st.session_state.agencies)
    save_alerts(st.session_state.cyber_alerts)

# ==========================================
# HELPERS
# ==========================================
def generate_timeline(current_status):
    steps = ["New", "Under Review", "Resolved", "Closed"]
    status_map = {"New": 0, "Under Review": 1, "Resolved": 2, "Closed": 3}
    active_index = status_map.get(current_status, 0)
    html = '<div class="timeline-container">'
    for i, step in enumerate(steps):
        is_active = i <= active_index
        is_current = i == active_index
        dot_color = "#fbbf24" if is_active else "#334155"
        label_class = "active" if is_current else ""
        html += f"""<div class="timeline-step"><div class="timeline-dot" style="background:{dot_color};"></div><span class="timeline-label {label_class}">{step}</span></div>"""
        if i < len(steps)-1:
            line_class = "done" if i < active_index else ""
            html += f'<div class="timeline-line {line_class}"></div>'
    html += '</div>'
    return html

def generate_tracking_id(country):
    code = country[:2].upper()
    year = datetime.now().year
    rand_num = str(random.randint(10000, 99999))
    return f"{code}-{year}-{rand_num}"

DATA_DIR = "data"
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
# PAGE CONFIG & CSS
# ==========================================
st.set_page_config(page_title="E4GRID - Global Shield", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Inter', sans-serif; }
        .stApp { background: #0a0f1e; }
        .stMetric { background: rgba(30, 41, 59, 0.5); backdrop-filter: blur(5px); border-radius: 12px; border-left: 4px solid #fbbf24; padding: 10px; }
        .stButton > button { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #0a0f1e; font-weight: 700; border: none; border-radius: 12px; padding: 0.6rem 1.5rem; transition: 0.3s; }
        .stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 30px rgba(251, 191, 36, 0.3); }
        .footer { text-align: center; padding: 30px 0 10px 0; color: #475569; font-size: 0.9rem; border-top: 1px solid #1e293b; margin-top: 40px; }
        .footer a { color: #fbbf24; text-decoration: none; }
        .tagline-gold { color: #fbbf24; font-weight: 600; letter-spacing: 2px; }
        .timeline-container { display: flex; align-items: center; gap: 5px; margin: 10px 0; flex-wrap: wrap; }
        .timeline-step { display: flex; align-items: center; gap: 5px; }
        .timeline-dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
        .timeline-line { width: 30px; height: 2px; background: #334155; }
        .timeline-line.done { background: #fbbf24; }
        .timeline-label { font-size: 0.7rem; color: #94a3b8; }
        .timeline-label.active { color: #fbbf24; font-weight: 600; }
        .health-score { font-size: 2.5rem; font-weight: 800; color: #fbbf24; text-align: center; }
        .notif-bell { position: relative; display: inline-block; }
        .notif-badge { position: absolute; top: -5px; right: -10px; background: #ef4444; color: white; border-radius: 50%; padding: 2px 6px; font-size: 10px; font-weight: 700; }
        .verified-badge { background: #22c55e; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
        .boss-badge { background: #fbbf24; color: black; padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
        .ai-suggestion-box { background: rgba(30, 41, 59, 0.5); border-left: 4px solid #fbbf24; padding: 10px; border-radius: 8px; margin: 5px 0; }
        .ai-reason-text { color: #94a3b8; font-size: 0.8rem; margin-top: 4px; }
    </style>
""", unsafe_allow_html=True)

DEMO_FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSf6dliM5l1-dg34Uj_4MWwbJOLDiI7DuUnDxG9M-gBdvYxNyA/viewform?usp=header"

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=150)
    else: st.markdown("<h2 style='color:#fbbf24;'>⚡ E4GRID</h2>", unsafe_allow_html=True)
    st.caption("Cyber · Compliance · Trust")
    st.divider()
    st.markdown("### 🚀 Interested in E4GRID?")
    st.link_button("📌 Book a Demo", DEMO_FORM_LINK, use_container_width=True)
    st.caption("For Agencies, MNCs, and Enterprises.")
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
# LANDING PAGE
# ==========================================
def landing_page():
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists("logo.png"): st.image("logo.png", width=120)
        else: st.markdown("<h1 style='color:#fbbf24;'>⚡</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style="padding-top: 15px;">
                <div style="font-size: 2.8rem; font-weight: 800; color: #fbbf24;">E4GRID</div>
                <div class="tagline-gold" style="font-size: 1.1rem; letter-spacing: 2px;">See Risk · Build Trust · Stay Compliant</div>
                <div style="color: #64748b; font-size: 0.8rem; letter-spacing: 3px;">BUILDING A SAFER DIGITAL WORLD</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 🌐 A Unified Grid for Global Security")
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown("""<div style="background:#1e293b; padding:20px; border-radius:12px; border-top:4px solid #fbbf24;"><h4 style="color:#fbbf24;">🛡️ Public</h4><p style="color:#94a3b8; font-size:0.9rem;">Report cybercrime, upload evidence, and track status.</p></div>""", unsafe_allow_html=True)
    with col2: st.markdown("""<div style="background:#1e293b; padding:20px; border-radius:12px; border-top:4px solid #3b82f6;"><h4 style="color:#3b82f6;">🏢 Enterprise</h4><p style="color:#94a3b8; font-size:0.9rem;">Monitor compliance, risk scores, and supply chain health.</p></div>""", unsafe_allow_html=True)
    with col3: st.markdown("""<div style="background:#1e293b; padding:20px; border-radius:12px; border-top:4px solid #22c55e;"><h4 style="color:#22c55e;">🛡️ Agency</h4><p style="color:#94a3b8; font-size:0.9rem;">Investigate assigned cases with full evidence.</p></div>""", unsafe_allow_html=True)
    
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("🌍 Public", use_container_width=True): st.session_state.role = "public"; st.session_state.logged_in = True; st.rerun()
    if col2.button("🏢 Enterprise", use_container_width=True): st.session_state.landing_target = "mnc"; st.rerun()
    if col3.button("🛡️ Agency", use_container_width=True): st.session_state.landing_target = "agency"; st.rerun()
    if col4.button("👑 Owner", use_container_width=True): st.session_state.landing_target = "admin"; st.rerun()

    target = st.session_state.get("landing_target")
    if target:
        st.divider()
        with st.container():
            st.subheader(f"Login: {target.title()}")
            identifier = st.text_input("Username/Country")
            password = st.text_input("Password", type="password")
            if st.button("Authenticate"):
                if target == "admin" and password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.role = "admin"
                    log_audit("Admin Login")
                    st.rerun()
                elif target == "mnc" and identifier in st.session_state.mnc_clients:
                    if st.session_state.mnc_clients[identifier]["password"] == password and st.session_state.mnc_clients[identifier]["active"]:
                        st.session_state.logged_in = True
                        st.session_state.role = "mnc"
                        st.session_state.client = identifier
                        log_audit(f"MNC Login: {identifier}")
                        st.rerun()
                elif target == "agency" and identifier in st.session_state.agencies:
                    if st.session_state.agencies[identifier]["password"] == password and st.session_state.agencies[identifier]["active"]:
                        st.session_state.logged_in = True
                        st.session_state.role = "agency"
                        st.session_state.client = identifier
                        log_audit(f"Agency Login: {identifier}")
                        st.rerun()
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
            email = st.text_input("Email")
            country = st.selectbox("Country", list(st.session_state.agencies.keys()) + ["Other"])
            city = st.text_input("City")
        with col2:
            category = st.selectbox("Category", ["Cyber Blackmail", "Hacking", "Data Breach", "Compliance", "Other"])
            incident_date = st.date_input("Date", datetime.now())
            website = st.text_input("Website/URL")
        complaint = st.text_area("Description", height=150)
        evidence = st.file_uploader("Upload Evidence", type=['png', 'jpg', 'pdf', 'txt'])
        anonymous = st.checkbox("Submit Anonymously")
        
        if st.form_submit_button("🚔 Submit"):
            if complaint:
                file_name = save_uploaded_file(evidence)
                tracking_id = generate_tracking_id(country)
                new_alert = {
                    "id": len(st.session_state.cyber_alerts)+1,
                    "tracking_id": tracking_id,
                    "name": name or "Anonymous",
                    "email": email,
                    "country": country,
                    "city": city,
                    "category": category,
                    "text": complaint,
                    "website": website,
                    "evidence_file": file_name,
                    "status": "New",
                    "priority": "Medium",
                    "assigned_to": "Unassigned",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "notes": "",
                    "timeline": ["New"]
                }
                st.session_state.cyber_alerts.append(new_alert)
                save_all()
                log_audit(f"Public Report Submitted: {tracking_id}")
                st.success(f"✅ Report Submitted! Tracking ID: **{tracking_id}**")
            else:
                st.error("Please describe the incident.")

    st.divider()
    st.subheader("🔍 Track")
    track = st.text_input("Enter Tracking ID")
    if st.button("Check Status"):
        found = [a for a in st.session_state.cyber_alerts if a.get("tracking_id") == track]
        if found:
            st.success(f"Status: {found[0]['status']} | Assigned to: {found[0].get('assigned_to', 'Pending')}")
            st.markdown(generate_timeline(found[0]['status']), unsafe_allow_html=True)

# ==========================================
# ADMIN DASHBOARD (FIXED)
# ==========================================
def admin_dashboard():
    st.header("👑 Command Center")
    
    total = len(st.session_state.cyber_alerts)
    pending = len([a for a in st.session_state.cyber_alerts if a['status'] not in ['Resolved', 'Closed', 'Archived']])
    resolved = len([a for a in st.session_state.cyber_alerts if a['status'] == 'Resolved'])
    views = st.session_state.views_data
    total_factories = len(st.session_state.factories)
    verified_factories = len([f for f in st.session_state.factories if f.get('verified', False)])
    
    col1, col2, col3, col4, col5, col6 = st.columns([2,1,1,1,1,1])
    col1.metric("📊 Cyber Reports", total)
    col2.metric("⏳ Pending", pending)
    col3.metric("✅ Resolved", resolved)
    col4.metric("🏭 Factories", total_factories)
    col5.metric("✅ Verified", verified_factories)
    col6.metric("👁️ Views", views["total"])
    
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

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Cyber Reports", "🏭 Factories", "🏢 MNCs", "🌍 Agencies", "📜 Audit Logs"])
    
    with tab1:
        search = st.text_input("🔍 Search")
        filtered = st.session_state.cyber_alerts
        if search:
            filtered = [a for a in filtered if search.lower() in str(a.get('tracking_id', '')).lower() or search.lower() in a.get('name', '').lower()]
        active = [a for a in filtered if a.get('status') != 'Archived']
        if active:
            df = pd.DataFrame(active)
            st.dataframe(df[['tracking_id', 'name', 'country', 'category', 'status', 'priority', 'assigned_to', 'time']], use_container_width=True)
            for alert in active:
                with st.expander(f"📌 {alert.get('tracking_id')}"):
                    st.markdown(generate_timeline(alert.get('status')), unsafe_allow_html=True)
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.write(f"**Details:** {alert.get('text')}")
                        if alert.get('evidence_file'):
                            fp = os.path.join(UPLOAD_DIR, alert['evidence_file'])
                            if os.path.exists(fp):
                                if alert['evidence_file'].lower().endswith(('png','jpg','jpeg')):
                                    st.image(fp, width=300)
                                else:
                                    with open(fp, "rb") as f:
                                        st.download_button("📥 Download", f, file_name=alert['evidence_file'])
                        
                        priority = st.selectbox(
                            "Priority",
                            ["Low", "Medium", "High"],
                            index=["Low", "Medium", "High"].index(alert.get('priority', 'Medium')),
                            key=f"pri_{alert['id']}"
                        )
                        if priority != alert.get('priority'):
                            alert['priority'] = priority
                            save_all()
                            log_audit(f"Priority updated for {alert.get('tracking_id')}")
                        
                        notes = st.text_area("Internal Notes", value=alert.get('notes', ''), key=f"notes_{alert['id']}")
                        if notes != alert.get('notes'):
                            alert['notes'] = notes
                            save_all()
                            log_audit(f"Notes updated for {alert.get('tracking_id')}")
                    with col_b:
                        agency_list = list(st.session_state.agencies.keys())
                        assigned = st.selectbox(
                            "Assign to Agency",
                            agency_list,
                            index=agency_list.index(alert.get('assigned_to')) if alert.get('assigned_to') in agency_list else 0,
                            key=f"assign_{alert['id']}"
                        )
                        if assigned != alert.get('assigned_to'):
                            alert['assigned_to'] = assigned
                            if "Assigned" not in alert.get('timeline', []):
                                alert['timeline'] = alert.get('timeline', ["New"]) + [f"Assigned to {assigned}"]
                            save_all()
                            log_audit(f"Assigned {alert.get('tracking_id')} to {assigned}")
                        
                        new_status = st.selectbox(
                            "Status",
                            ["New", "Under Review", "Resolved", "Closed", "Archived"],
                            index=["New", "Under Review", "Resolved", "Closed", "Archived"].index(alert.get('status')),
                            key=f"st_{alert['id']}"
                        )
                        if new_status != alert.get('status'):
                            alert['status'] = new_status
                            if new_status not in alert.get('timeline', []):
                                alert['timeline'] = alert.get('timeline', ["New"]) + [new_status]
                            save_all()
                            log_audit(f"Status changed to {new_status} for {alert.get('tracking_id')}")
        else:
            st.success("✅ No active reports.")
    
    with tab2:
        st.subheader("🏭 Factory Compliance (Manual Mode)")
        st.caption("Add factories, set status/score/reason manually, and verify for MNCs.")
        
        total_f = len(st.session_state.factories)
        verified = len([f for f in st.session_state.factories if f.get('verified', False)])
        green = len([f for f in st.session_state.factories if f.get('verified', False) and f.get('manual_status', 'Green') == 'Green'])
        yellow = len([f for f in st.session_state.factories if f.get('verified', False) and f.get('manual_status', 'Green') == 'Yellow'])
        red = len([f for f in st.session_state.factories if f.get('verified', False) and f.get('manual_status', 'Green') == 'Red'])
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📊 Total", total_f)
        col2.metric("✅ Verified", verified)
        col3.metric("🟢 Verified Green", green)
        col4.metric("🔴 Verified Red", red)
        
        st.divider()
        
        with st.expander("➕ Add New Factory", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                new_name = st.text_input("Factory Name", key="new_fact_name")
                new_client = st.selectbox("Assign to MNC", list(st.session_state.mnc_clients.keys()), key="new_fact_client")
            with col_b:
                new_country = st.text_input("Country", "Pakistan", key="new_fact_country")
                new_status = st.selectbox("Initial Status", ["Green", "Yellow", "Red"], key="new_fact_status")
                if st.button("Add Factory", key="add_fact_btn", use_container_width=True):
                    if new_name:
                        new_factory = {
                            "id": len(st.session_state.factories) + 1,
                            "name": new_name,
                            "client": new_client,
                            "country": new_country,
                            "status": new_status,
                            "risk": "Low" if new_status == "Green" else "Medium" if new_status == "Yellow" else "High",
                            "manual_score": 0,
                            "manual_status": new_status,
                            "manual_reason": "New factory added",
                            "verified": False,
                            "history": [f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Factory Added"]
                        }
                        st.session_state.factories.append(new_factory)
                        save_all()
                        log_audit(f"Factory Added: {new_name}")
                        st.success(f"✅ Factory added: {new_name}")
                        st.rerun()
                    else:
                        st.error("❌ Please enter a factory name.")
        
        st.divider()
        
        for idx, factory in enumerate(st.session_state.factories):
            with st.expander(f"🏭 {factory['name']} ({factory['country']}) - {factory['client']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if factory.get('verified', False):
                        st.markdown('<span class="verified-badge">✅ VERIFIED (Sent to MNCs)</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span style="color:#eab308;">⏳ Pending Verification</span>', unsafe_allow_html=True)
                    
                    st.write(f"**Current Status:** {factory.get('status', 'Green')}")
                    
                    st.subheader("✏️ Manual Edit")
                    col_edit1, col_edit2 = st.columns(2)
                    with col_edit1:
                        current_status = factory.get('manual_status', factory.get('status', 'Green'))
                        status_options = ["Green", "Yellow", "Red"]
                        status_index = status_options.index(current_status) if current_status in status_options else 0
                        new_status = st.selectbox(
                            "Status",
                            status_options,
                            index=status_index,
                            key=f"fact_status_{factory['id']}"
                        )
                        new_score = st.number_input(
                            "Score (0-100)",
                            min_value=0,
                            max_value=100,
                            value=factory.get('manual_score', 0),
                            key=f"fact_score_{factory['id']}"
                        )
                    with col_edit2:
                        new_reason = st.text_area(
                            "Reason",
                            value=factory.get('manual_reason', ''),
                            key=f"fact_reason_{factory['id']}",
                            height=80
                        )
                    
                    if st.button(f"💾 Save Changes", key=f"save_fact_{factory['id']}"):
                        factory['manual_status'] = new_status
                        factory['manual_score'] = new_score
                        factory['manual_reason'] = new_reason
                        factory['status'] = new_status
                        if 'history' not in factory:
                            factory['history'] = []
                        factory['history'].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Manual update: {new_status}, Score: {new_score}")
                        save_all()
                        log_audit(f"Manual update for {factory['name']}: {new_status}")
                        st.success("✅ Changes saved!")
                        st.rerun()
                    
                    if factory.get('history'):
                        with st.expander("📜 History"):
                            for h in factory['history'][-5:]:
                                st.caption(f"- {h}")
                
                with col2:
                    if not factory.get('verified', False):
                        if st.button(f"🔒 Verify & Publish to MNCs", key=f"verify_{factory['id']}", use_container_width=True):
                            factory['verified'] = True
                            if 'history' not in factory:
                                factory['history'] = []
                            factory['history'].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Verified & Published")
                            save_all()
                            log_audit(f"Factory Verified: {factory['name']}")
                            st.success(f"✅ {factory['name']} Published to MNCs!")
                            st.rerun()
                    else:
                        st.success("✅ Published to MNCs")
                        if st.button(f"🔓 Unverify", key=f"unverify_{factory['id']}", use_container_width=True):
                            factory['verified'] = False
                            save_all()
                            log_audit(f"Factory Unverified: {factory['name']}")
                            st.rerun()
                    
                    st.divider()
                    
                    if st.button(f"🗑️ Delete {factory['name']}", key=f"del_fact_{factory['id']}", use_container_width=True):
                        st.session_state.factories = [f for f in st.session_state.factories if f["id"] != factory["id"]]
                        save_all()
                        log_audit(f"Factory Deleted: {factory['name']}")
                        st.success(f"✅ Deleted {factory['name']}")
                        st.rerun()
    
    with tab3:
        for name, data in st.session_state.mnc_clients.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{name}**")
            with col2:
                np = st.text_input(f"Pass", value=data["password"], key=f"mp_{name}")
                if np != data["password"]:
                    st.session_state.mnc_clients[name]["password"] = np
                    save_all()
                    log_audit(f"MNC Pass changed: {name}")
            with col3:
                active = st.checkbox("Active", value=data["active"], key=f"ma_{name}")
                if active != data["active"]:
                    st.session_state.mnc_clients[name]["active"] = active
                    save_all()
                    st.rerun()
        new_mnc = st.text_input("New MNC Name")
        new_pass = st.text_input("Set Password")
        if st.button("Add MNC"):
            if new_mnc and new_pass:
                st.session_state.mnc_clients[new_mnc] = {"password": new_pass, "active": True}
                save_all()
                log_audit(f"MNC Added: {new_mnc}")
                st.rerun()
    
    with tab4:
        for name, data in st.session_state.agencies.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{name}**")
            with col2:
                np = st.text_input(f"Pass", value=data["password"], key=f"ap_{name}")
                if np != data["password"]:
                    st.session_state.agencies[name]["password"] = np
                    save_all()
                    log_audit(f"Agency Pass changed: {name}")
            with col3:
                active = st.checkbox("Active", value=data["active"], key=f"aa_{name}")
                if active != data["active"]:
                    st.session_state.agencies[name]["active"] = active
                    save_all()
                    st.rerun()
        n_ag = st.text_input("New Country")
        n_pass = st.text_input("Pass")
        n_hl = st.text_input("Helpline")
        if st.button("Add Agency"):
            if n_ag and n_pass:
                st.session_state.agencies[n_ag] = {"password": n_pass, "helpline": n_hl, "active": True}
                save_all()
                log_audit(f"Agency Added: {n_ag}")
                st.rerun()
    
    with tab5:
        st.subheader("📜 Complete Activity Trail")
        if st.session_state.audit_logs:
            df_audit = pd.DataFrame(st.session_state.audit_logs[::-1])
            st.dataframe(df_audit, use_container_width=True)
            if st.button("🗑️ Clear All Logs"):
                st.session_state.audit_logs.clear()
                save_audit([])
                st.rerun()
        else:
            st.info("No activities recorded yet.")

# ==========================================
# MNC DASHBOARD
# ==========================================
def mnc_dashboard(client):
    st.header(f"🏢 {client} - Verified Compliance Dashboard")
    st.caption("✅ Only VERIFIED factories are shown here.")
    
    df = pd.DataFrame([
        f for f in st.session_state.factories
        if f["client"] == client and f.get("verified", False)
    ])
    
    if not df.empty:
        total = len(df)
        green = len([f for f in df if f.get('manual_status', f.get('status', 'Green')) == 'Green'])
        yellow = len([f for f in df if f.get('manual_status', f.get('status', 'Green')) == 'Yellow'])
        red = len([f for f in df if f.get('manual_status', f.get('status', 'Green')) == 'Red'])
        
        scores = [f.get('manual_score', 0) for f in df]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("🏭 Total Verified", total)
        col2.metric("🟢 Green", green)
        col3.metric("🟡 Yellow", yellow)
        col4.metric("🔴 Red", red)
        col5.metric("📊 Avg Score", f"{avg_score:.1f}")
        
        st.markdown(f"""
        <div style="text-align:center;padding:20px;background:#1e293b;border-radius:12px;margin:10px 0;">
            <p style="color:#94a3b8;">Overall Compliance Health Score</p>
            <div class="health-score">{round(avg_score)}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        display_df = df[['id', 'name', 'country', 'manual_status', 'manual_score', 'manual_reason']].rename(
            columns={'manual_status': 'Status', 'manual_score': 'Score', 'manual_reason': 'Reason'}
        )
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info(f"No verified factories for {client} yet.")

# ==========================================
# AGENCY DASHBOARD
# ==========================================
def agency_dashboard(agency):
    st.header(f"🛡️ {agency} - Cyber Crime Dashboard")
    
    my_reports = [
        a for a in st.session_state.cyber_alerts
        if a.get("assigned_to") == agency and a.get('status') not in ['Resolved', 'Closed', 'Archived']
    ]
    
    if not my_reports:
        st.success(f"✅ No pending cases for **{agency}**.")
        return
    
    st.subheader(f"📋 Pending Cases ({len(my_reports)})")
    df = pd.DataFrame(my_reports)
    st.dataframe(df[['tracking_id', 'category', 'status', 'priority', 'time']], use_container_width=True)
    
    if not df.empty and 'category' in df.columns:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Category Breakdown")
            st.bar_chart(df['category'].value_counts())
        with col2:
            st.subheader("Status Distribution")
            st.bar_chart(df['status'].value_counts())
    
    st.divider()
    st.subheader("📂 Case Files (Full Details)")
    
    for alert in my_reports:
        with st.expander(f"🔍 Case: {alert.get('tracking_id')} - {alert.get('name')} ({alert.get('status')})"):
            st.markdown(generate_timeline(alert.get('status')), unsafe_allow_html=True)
            
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown(f"**👤 Name:** {alert.get('name')}")
                st.markdown(f"**📧 Email:** {alert.get('email', 'N/A')}")
                st.markdown(f"**🌍 Country:** {alert.get('country')} | **🏙️ City:** {alert.get('city', 'N/A')}")
                st.markdown(f"**📂 Category:** {alert.get('category')}")
                st.markdown(f"**📝 Description:**")
                st.info(alert.get('text'))
                
                if alert.get('evidence_file'):
                    fp = os.path.join(UPLOAD_DIR, alert['evidence_file'])
                    if os.path.exists(fp):
                        st.markdown("**📎 Evidence Uploaded:**")
                        if alert['evidence_file'].lower().endswith(('png', 'jpg', 'jpeg')):
                            st.image(fp, caption="Evidence Image", width=300)
                        else:
                            with open(fp, "rb") as f:
                                st.download_button("📥 Download Evidence", f, file_name=alert['evidence_file'])
                
                notes = st.text_area("📝 Internal Notes", value=alert.get('notes', ''), key=f"ag_notes_{alert['id']}")
                if notes != alert.get('notes'):
                    alert['notes'] = notes
                    save_all()
                    st.success("✅ Notes updated!")
            
            with col_b:
                st.markdown("**⚙️ Update Case**")
                new_status = st.selectbox(
                    "Status",
                    ["New", "Under Review", "Resolved", "Closed"],
                    index=["New", "Under Review", "Resolved", "Closed"].index(alert.get('status')) if alert.get('status') in ["New", "Under Review", "Resolved", "Closed"] else 0,
                    key=f"ag_st_{alert['id']}"
                )
                if new_status != alert.get('status'):
                    alert['status'] = new_status
                    if new_status not in alert.get('timeline', []):
                        alert['timeline'] = alert.get('timeline', ["New"]) + [new_status]
                    save_all()
                    log_audit(f"Agency {agency} changed status to {new_status} for {alert.get('tracking_id')}")
                    st.rerun()
                
                st.caption(f"🕒 Reported: {alert.get('time')}")

# ==========================================
# MAIN ROUTER
# ==========================================
if "landing_target" not in st.session_state:
    st.session_state.landing_target = None

if not st.session_state.get("logged_in", False):
    landing_page()
else:
    if st.session_state.role == "public":
        public_dashboard()
    elif st.session_state.role == "admin":
        admin_dashboard()
    elif st.session_state.role == "mnc":
        mnc_dashboard(st.session_state.client)
    elif st.session_state.role == "agency":
        agency_dashboard(st.session_state.client)

st.markdown("""
<div class="footer">
    © 2026 E4GRID. Built with ❤️ for Global Security.
    <br>
    <a href="#">Privacy Policy</a> · <a href="#">Contact</a> · <a href="https://linkedin.com/company/e4grid" target="_blank">LinkedIn</a>
</div>
""", unsafe_allow_html=True)
