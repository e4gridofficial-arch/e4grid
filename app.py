import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import random
import requests

# ==========================================
# 🔒 SECURE: Passwords ab Secrets mein
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
# 2. DATABASE HELPERS (Permanent Save)
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

def db_put(table, match, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = []
    for key, value in match.items():
        params.append(f"{key}=eq.{value}")
    url += "?" + "&".join(params)
    response = requests.patch(url, headers=HEADERS, json=data)
    return response.status_code == 200

def db_delete(table, match):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = []
    for key, value in match.items():
        params.append(f"{key}=eq.{value}")
    url += "?" + "&".join(params)
    response = requests.delete(url, headers=HEADERS)
    return response.status_code == 204

# ==========================================
# 3. DATA LOAD FUNCTIONS
# ==========================================
def load_factories():
    data = db_get("factories")
    if data:
        # Ensure new fields exist for old data
        for item in data:
            if "verified" not in item:
                item["verified"] = False
            if "manual_score" not in item:
                item["manual_score"] = None
            if "manual_status" not in item:
                item["manual_status"] = None
            if "manual_reason" not in item:
                item["manual_reason"] = None
            if "ai_score" not in item:
                item["ai_score"] = 0
            if "ai_status" not in item:
                item["ai_status"] = "Green"
            if "ai_reason" not in item:
                item["ai_reason"] = "No data"
            if "env_score" not in item:
                item["env_score"] = 0
            if "labor_score" not in item:
                item["labor_score"] = 0
            if "safety_score" not in item:
                item["safety_score"] = 0
            if "mgmt_score" not in item:
                item["mgmt_score"] = 0
            if "trans_score" not in item:
                item["trans_score"] = 0
        return data
    return [{"id": 1, "name": "Saga Sports", "client": "Nike", "country": "Pakistan", "status": "Green", "risk": "Low", "human_override": False, "history": [], "verified": False, "ai_score": 0, "ai_status": "Green", "ai_reason": "No data", "manual_score": None, "manual_status": None, "manual_reason": None, "env_score": 0, "labor_score": 0, "safety_score": 0, "mgmt_score": 0, "trans_score": 0}]

def save_factories(data):
    db_delete("factories", {})
    for item in data:
        db_post("factories", item)

def load_mnc_clients():
    data = db_get("mnc_clients")
    if data:
        return {item["name"]: {"password": item["password"], "active": item["active"]} for item in data}
    return {"Nike": {"password": "Nike@2026", "active": True}, "Adidas": {"password": "Adidas@2026", "active": True}}

def save_mnc_clients(data):
    db_delete("mnc_clients", {})
    for name, values in data.items():
        db_post("mnc_clients", {"name": name, "password": values["password"], "active": values["active"]})

def load_agencies():
    data = db_get("agencies")
    if data:
        return {item["name"]: {"password": item["password"], "helpline": item["helpline"], "active": item["active"]} for item in data}
    return {"Pakistan": {"password": "Pak@1799", "helpline": "1799", "active": True}, "USA": {"password": "FBI@911", "helpline": "911", "active": True}}

def save_agencies(data):
    db_delete("agencies", {})
    for name, values in data.items():
        db_post("agencies", {"name": name, "password": values["password"], "helpline": values["helpline"], "active": values["active"]})

def load_alerts():
    data = db_get("cyber_alerts")
    return data if data else []

def save_alerts(data):
    db_delete("cyber_alerts", {})
    for item in data:
        db_post("cyber_alerts", item)

def load_audit():
    data = db_get("audit_logs")
    return data if data else []

def save_audit(data):
    db_delete("audit_logs", {})
    for item in data:
        db_post("audit_logs", item)

def load_views():
    data = db_get("views_data")
    if data:
        return data[0]
    return {"total": 0, "today": 0, "last_date": None}

def save_views(data):
    db_delete("views_data", {})
    db_post("views_data", data)

# ==========================================
# 4. SESSION STATE INIT
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
# 5. GLOBAL COMPLIANCE AI ENGINE (New)
# ==========================================
def calculate_compliance(env, labor, safety, mgmt, trans):
    """
    Weighted Scoring Formula:
    Env 30%, Labor 25%, Safety 20%, Mgmt 15%, Trans 10%
    """
    score = (env * 0.30) + (labor * 0.25) + (safety * 0.20) + (mgmt * 0.15) + (trans * 0.10)
    score = round(score, 1)
    
    if score >= 80:
        status = "Green"
        reason = "✅ Excellent compliance. All standards met."
    elif score >= 50:
        status = "Yellow"
        reason = "🟡 Moderate compliance. Some improvements needed."
    else:
        status = "Red"
        reason = "🔴 High risk. Immediate action required."
    
    return score, status, reason

def generate_reason_smart(env, labor, safety, mgmt, trans):
    reasons = []
    if env < 50: reasons.append("Environment: Poor (Needs EPA/ISO check)")
    elif env < 80: reasons.append("Environment: Average")
    else: reasons.append("Environment: Excellent")
    
    if labor < 50: reasons.append("Labor: High risk (Wages/Child labor)")
    elif labor < 80: reasons.append("Labor: Needs review")
    else: reasons.append("Labor: Compliant")
    
    if safety < 50: reasons.append("Safety: Critical issues")
    elif safety < 80: reasons.append("Safety: Minor issues")
    else: reasons.append("Safety: Safe")
    
    if mgmt < 50: reasons.append("Mgmt: Poor documentation")
    elif mgmt < 80: reasons.append("Mgmt: Needs update")
    else: reasons.append("Mgmt: Strong")
    
    if trans < 50: reasons.append("Transparency: Hidden")
    elif trans < 80: reasons.append("Transparency: Partial")
    else: reasons.append("Transparency: Open")
    
    return " | ".join(reasons)

# ==========================================
# 6. HELPER FUNCTIONS
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
# 7. PAGE CONFIG & CSS
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
        .ai-badge { background: #3b82f6; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
        .boss-badge { background: #fbbf24; color: black; padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
        .verified-badge { background: #22c55e; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
        .ai-suggestion-box { background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 10px; border-radius: 8px; margin: 5px 0; }
        .ai-reason-text { color: #94a3b8; font-size: 0.8rem; margin-top: 4px; }
        .score-badge { font-weight: 600; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; }
    </style>
""", unsafe_allow_html=True)

DEMO_FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSf6dliM5l1-dg34Uj_4MWwbJOLDiI7DuUnDxG9M-gBdvYxNyA/viewform?usp=header"

# ==========================================
# 8. SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=150)
    else: st.markdown("<h2 style='color:#fbbf24;'>⚡ E4GRID</h2>", unsafe_allow_html=True)
    st.caption("Cyber · Compliance · Global")
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
# 9. LANDING PAGE
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
# 10. PUBLIC DASHBOARD (Unchanged)
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
                    "tracking_id": tracking_id, "name": name or "Anonymous",
                    "email": email, "country": country, "city": city,
                    "category": category, "text": complaint, "website": website,
                    "evidence_file": file_name, "status": "New", "priority": "Medium",
                    "assigned_to": "Unassigned", "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "notes": "", "timeline": ["New"]
                }
                st.session_state.cyber_alerts.append(new_alert)
                save_all()
                log_audit(f"Report Submitted: {tracking_id}")
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
# 11. ADMIN DASHBOARD (UPGRADED: Verified System)
# ==========================================
def admin_dashboard():
    st.header("👑 Command Center")
    total = len(st.session_state.cyber_alerts)
    pending = len([a for a in st.session_state.cyber_alerts if a['status'] not in ['Resolved', 'Closed', 'Archived']])
    resolved = len([a for a in st.session_state.cyber_alerts if a['status'] == 'Resolved'])
    views = st.session_state.views_data
    
    col1, col2, col3, col4, col5, col6 = st.columns([2,1,1,1,1,1])
    col1.metric("📊 Cyber Reports", total)
    col2.metric("⏳ Pending", pending)
    col3.metric("✅ Resolved", resolved)
    col4.metric("👁️ Views", views["total"])
    col5.metric("📆 Today", views["today"])
    with col6:
        st.markdown(f"""<div style="text-align: center; padding-top: 10px;"><span class="notif-bell" style="font-size: 2rem;">🔔</span><span class="notif-badge" style="position: relative; top: -15px; left: -10px; background: #ef4444; color: white; border-radius: 50%; padding: 2px 8px; font-size: 14px;">{pending}</span></div>""", unsafe_allow_html=True)
    
    if st.session_state.cyber_alerts:
        df = pd.DataFrame(st.session_state.cyber_alerts)
        if not df.empty and 'category' in df.columns:
            col_ch1, col_ch2 = st.columns(2)
            with col_ch1: st.subheader("Category Breakdown"); st.bar_chart(df['category'].value_counts())
            with col_ch2: st.subheader("Status Distribution"); st.bar_chart(df['status'].value_counts())

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Cyber Reports", "🏭 Factories (Verified)", "🏢 MNCs", "🌍 Agencies", "📜 Audit Logs", "📊 Compliance"])
    
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
                    col_a, col_b = st.columns([2,1])
                    with col_a:
                        st.write(f"**Details:** {alert.get('text')}")
                        if alert.get('evidence_file'):
                            fp = os.path.join(UPLOAD_DIR, alert['evidence_file'])
                            if os.path.exists(fp):
                                if alert['evidence_file'].lower().endswith(('png','jpg','jpeg')): st.image(fp, width=300)
                                else:
                                    with open(fp, "rb") as f: st.download_button("📥 Download", f, file_name=alert['evidence_file'])
                        notes = st.text_area("Notes", value=alert.get('notes',''), key=f"notes_{alert['id']}")
                        if notes != alert.get('notes'): alert['notes'] = notes; save_all(); log_audit(f"Notes updated {alert.get('tracking_id')}")
                    with col_b:
                        agency_list = list(st.session_state.agencies.keys())
                        assigned = st.selectbox("Assign", agency_list, index=agency_list.index(alert.get('assigned_to')) if alert.get('assigned_to') in agency_list else 0, key=f"assign_{alert['id']}")
                        if assigned != alert.get('assigned_to'):
                            alert['assigned_to'] = assigned
                            if "Assigned" not in alert.get('timeline', []): alert['timeline'] = alert.get('timeline', ["New"]) + [f"Assigned to {assigned}"]
                            save_all()
                        new_status = st.selectbox("Status", ["New","Under Review","Resolved","Closed","Archived"], index=["New","Under Review","Resolved","Closed","Archived"].index(alert.get('status')), key=f"st_{alert['id']}")
                        if new_status != alert.get('status'):
                            alert['status'] = new_status
                            if new_status not in alert.get('timeline', []): alert['timeline'] = alert.get('timeline', ["New"]) + [new_status]
                            save_all()
                        priority = st.selectbox("Priority", ["Low","Medium","High"], index=["Low","Medium","High"].index(alert.get('priority','Medium')), key=f"pr_{alert['id']}")
                        if priority != alert.get('priority'): alert['priority'] = priority; save_all()
        else: st.success("✅ No active reports.")
    
    with tab2:
        st.subheader("🏭 Global Factory Compliance (Verified System)")
        st.caption("🔬 Admin researches data -> AI calculates -> Admin Verifies -> MNCs see verified data.")
        
        # Stats
        total_f = len(st.session_state.factories)
        verified = len([f for f in st.session_state.factories if f.get('verified', False)])
        green = len([f for f in st.session_state.factories if f.get('verified', False) and f.get('manual_status', f.get('status')) == 'Green'])
        yellow = len([f for f in st.session_state.factories if f.get('verified', False) and f.get('manual_status', f.get('status')) == 'Yellow'])
        red = len([f for f in st.session_state.factories if f.get('verified', False) and f.get('manual_status', f.get('status')) == 'Red'])
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📊 Total Factories", total_f)
        col2.metric("✅ Verified", verified)
        col3.metric("🟢 Verified Green", green)
        col4.metric("🔴 Verified Red", red)
        
        st.divider()
        
        # Add New Factory
        with st.expander("➕ Add New Factory", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                new_name = st.text_input("Factory Name")
                new_client = st.selectbox("Assign to MNC", list(st.session_state.mnc_clients.keys()))
                new_country = st.text_input("Country")
            with col_b:
                if st.button("Add Factory & Start Compliance", use_container_width=True):
                    if new_name:
                        new_factory = {
                            "id": len(st.session_state.factories)+1,
                            "name": new_name,
                            "client": new_client,
                            "country": new_country,
                            "status": "Green",
                            "risk": "Low",
                            "human_override": False,
                            "history": [f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Factory Added"],
                            "verified": False,
                            "ai_score": 0,
                            "ai_status": "Green",
                            "ai_reason": "No data",
                            "manual_score": None,
                            "manual_status": None,
                            "manual_reason": None,
                            "env_score": 0,
                            "labor_score": 0,
                            "safety_score": 0,
                            "mgmt_score": 0,
                            "trans_score": 0
                        }
                        st.session_state.factories.append(new_factory)
                        save_all()
                        log_audit(f"Factory Added: {new_name}")
                        st.success(f"✅ Factory added! Now go to the list and enter compliance data.")
                        st.rerun()
        
        st.divider()
        
        # Factory List with Compliance Panel
        for idx, factory in enumerate(st.session_state.factories):
            with st.expander(f"🏭 {factory['name']} ({factory['country']}) - {factory['client']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Current Status:** {factory.get('status', 'Green')}")
                    
                    # Verified Status Badge
                    if factory.get('verified', False):
                        st.markdown('<span class="verified-badge">✅ VERIFIED (Sent to MNCs)</span>', unsafe_allow_html=True)
                        st.write(f"**Verified Score:** {factory.get('manual_score', factory.get('ai_score', 0))}")
                        st.write(f"**Verified Status:** {factory.get('manual_status', factory.get('ai_status', 'Green'))}")
                        st.write(f"**Verified Reason:** {factory.get('manual_reason', factory.get('ai_reason', 'N/A'))}")
                    else:
                        st.markdown('<span style="color:#eab308;">⏳ Pending Verification (MNCs cannot see yet)</span>', unsafe_allow_html=True)
                        
                with col2:
                    # Delete Button
                    if st.button(f"🗑️ Delete {factory['name']}", key=f"del_fact_{factory['id']}"):
                        st.session_state.factories = [f for f in st.session_state.factories if f["id"] != factory["id"]]
                        save_all()
                        st.rerun()
                
                st.divider()
                
                # --- COMPLIANCE VERIFICATION PANEL ---
                st.subheader("📊 Compliance Scoring (Global Formula)")
                st.caption("Input the 5 pillars (0-100) based on your research (Open Supply Hub, Google, etc.). AI will calculate the total score.")
                
                # Sliders for 5 pillars
                col_e, col_l, col_s, col_m, col_t = st.columns(5)
                with col_e:
                    env = st.number_input("🌍 Env", min_value=0, max_value=100, value=factory.get('env_score', 0), key=f"env_{factory['id']}")
                with col_l:
                    labor = st.number_input("👷 Labor", min_value=0, max_value=100, value=factory.get('labor_score', 0), key=f"labor_{factory['id']}")
                with col_s:
                    safety = st.number_input("🛡️ Safety", min_value=0, max_value=100, value=factory.get('safety_score', 0), key=f"safety_{factory['id']}")
                with col_m:
                    mgmt = st.number_input("📋 Mgmt", min_value=0, max_value=100, value=factory.get('mgmt_score', 0), key=f"mgmt_{factory['id']}")
                with col_t:
                    trans = st.number_input("🔍 Trans", min_value=0, max_value=100, value=factory.get('trans_score', 0), key=f"trans_{factory['id']}")
                
                # Calculate AI Score
                if st.button(f"🤖 Compute AI Score", key=f"compute_{factory['id']}"):
                    score, status, reason = calculate_compliance(env, labor, safety, mgmt, trans)
                    smart_reason = generate_reason_smart(env, labor, safety, mgmt, trans)
                    
                    factory['ai_score'] = score
                    factory['ai_status'] = status
                    factory['ai_reason'] = f"{reason} | Details: {smart_reason}"
                    factory['env_score'] = env
                    factory['labor_score'] = labor
                    factory['safety_score'] = safety
                    factory['mgmt_score'] = mgmt
                    factory['trans_score'] = trans
                    
                    # If not verified, update current status too
                    if not factory.get('verified', False):
                        factory['status'] = status
                    
                    save_all()
                    st.success(f"✅ AI Score computed: {score} ({status})")
                    st.rerun()
                
                # Display current AI Scores
                st.markdown(f"""
                <div class="ai-suggestion-box">
                    <span class="ai-badge">🤖 AI SUGGESTION</span>
                    <span style="color:#3b82f6;font-weight:600;margin-left:10px;">Score: {factory.get('ai_score', 0)} | Status: {factory.get('ai_status', 'Green')}</span>
                    <div class="ai-reason-text">📌 {factory.get('ai_reason', 'No data')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Manual Override Section
                st.subheader("✏️ Manual Override (Boss Verification)")
                col_ov1, col_ov2 = st.columns(2)
                with col_ov1:
                    manual_score = st.number_input("Override Score", min_value=0, max_value=100, value=factory.get('manual_score', factory.get('ai_score', 0)), key=f"m_score_{factory['id']}")
                    manual_status = st.selectbox("Override Status", ["Green", "Yellow", "Red"], index=["Green", "Yellow", "Red"].index(factory.get('manual_status', factory.get('ai_status', 'Green'))), key=f"m_status_{factory['id']}")
                with col_ov2:
                    manual_reason = st.text_area("Override Reason (Detailed)", value=factory.get('manual_reason', factory.get('ai_reason', '')), key=f"m_reason_{factory['id']}", height=100)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(f"💾 Save Manual Override", key=f"save_manual_{factory['id']}"):
                        factory['manual_score'] = manual_score
                        factory['manual_status'] = manual_status
                        factory['manual_reason'] = manual_reason
                        factory['status'] = manual_status
                        save_all()
                        st.success("✅ Manual override saved!")
                        st.rerun()
                
                with col_btn2:
                    if not factory.get('verified', False):
                        if st.button(f"🔒 Verify & Publish to MNCs", key=f"verify_{factory['id']}", use_container_width=True):
                            # Set verified flag
                            factory['verified'] = True
                            # Lock the current manual/ai data as official
                            if factory.get('manual_score') is not None:
                                factory['status'] = factory['manual_status']
                            else:
                                factory['manual_score'] = factory['ai_score']
                                factory['manual_status'] = factory['ai_status']
                                factory['manual_reason'] = factory['ai_reason']
                            save_all()
                            log_audit(f"Factory Verified: {factory['name']}")
                            st.success(f"✅ {factory['name']} Verified & Published to MNCs!")
                            st.rerun()
                    else:
                        st.success("✅ Already Verified")
                        if st.button(f"🔓 Unverify", key=f"unverify_{factory['id']}"):
                            factory['verified'] = False
                            save_all()
                            st.rerun()
                
                # History
                if factory.get('history'):
                    with st.expander("📜 History"):
                        for h in factory['history'][-5:]:
                            st.caption(f"- {h}")

    with tab3:
        for name, data in st.session_state.mnc_clients.items():
            col1, col2, col3 = st.columns([2,2,1])
            with col1: st.write(f"**{name}**")
            with col2:
                np = st.text_input(f"Pass", value=data["password"], key=f"mp_{name}")
                if np != data["password"]: st.session_state.mnc_clients[name]["password"] = np; save_all(); log_audit(f"MNC Pass changed: {name}")
            with col3:
                active = st.checkbox("Active", value=data["active"], key=f"ma_{name}")
                if active != data["active"]: st.session_state.mnc_clients[name]["active"] = active; save_all(); st.rerun()
        new_mnc = st.text_input("New MNC Name"); new_pass = st.text_input("Set Password")
        if st.button("Add MNC"):
            if new_mnc and new_pass: st.session_state.mnc_clients[new_mnc] = {"password": new_pass, "active": True}; save_all(); log_audit(f"MNC Added: {new_mnc}"); st.rerun()

    with tab4:
        for name, data in st.session_state.agencies.items():
            col1, col2, col3 = st.columns([2,2,1])
            with col1: st.write(f"**{name}**")
            with col2:
                np = st.text_input(f"Pass", value=data["password"], key=f"ap_{name}")
                if np != data["password"]: st.session_state.agencies[name]["password"] = np; save_all(); log_audit(f"Agency Pass changed: {name}")
            with col3:
                active = st.checkbox("Active", value=data["active"], key=f"aa_{name}")
                if active != data["active"]: st.session_state.agencies[name]["active"] = active; save_all(); st.rerun()
        n_ag = st.text_input("New Country"); n_pass = st.text_input("Pass"); n_hl = st.text_input("Helpline")
        if st.button("Add Agency"):
            if n_ag and n_pass: st.session_state.agencies[n_ag] = {"password": n_pass, "helpline": n_hl, "active": True}; save_all(); log_audit(f"Agency Added: {n_ag}"); st.rerun()

    with tab5:
        if st.session_state.audit_logs:
            df_audit = pd.DataFrame(st.session_state.audit_logs[::-1])
            st.dataframe(df_audit, use_container_width=True)
            if st.button("🗑️ Clear All Logs"):
                st.session_state.audit_logs.clear(); save_audit([]); st.rerun()
        else: st.info("No logs.")

    with tab6:
        st.subheader("📊 Compliance Analytics")
        st.caption("Verified factories data summary.")
        verified_factories = [f for f in st.session_state.factories if f.get('verified', False)]
        if verified_factories:
            df = pd.DataFrame(verified_factories)
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Status Distribution")
                st.bar_chart(df['status'].value_counts())
            with col2:
                st.subheader("Score Distribution")
                st.bar_chart(df['manual_score'] if 'manual_score' in df.columns else df['ai_score'])
        else:
            st.info("No verified factories yet. Verify a factory to see analytics.")

def mnc_dashboard(client):
    st.header(f"🏢 {client} - Verified Compliance Dashboard")
    st.caption("Only VERIFIED factories are shown here. Unverified factories are hidden.")
    
    # Filter ONLY verified factories
    df = pd.DataFrame([f for f in st.session_state.factories if f["client"] == client and f.get("verified", False)])
    if not df.empty:
        total = len(df)
        # Use manual_status if exists, else fallback to status
        df['display_status'] = df.apply(lambda row: row.get('manual_status', row.get('status', 'Green')), axis=1)
        green = len(df[df['display_status'] == 'Green'])
        yellow = len(df[df['display_status'] == 'Yellow'])
        red = len(df[df['display_status'] == 'Red'])
        
        # Calculate average score
        scores = df.apply(lambda row: row.get('manual_score', row.get('ai_score', 0)), axis=1)
        avg_score = scores.mean() if not scores.empty else 0
        score = (green/total)*100 if total > 0 else 0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("🏭 Total Verified", total)
        col2.metric("🟢 Green", green)
        col3.metric("🟡 Yellow", yellow)
        col4.metric("🔴 Red", red)
        col5.metric("📊 Avg Score", f"{avg_score:.1f}")
        
        st.markdown(f"""<div style="text-align:center;padding:20px;background:#1e293b;border-radius:12px;"><p style="color:#94a3b8;">Overall Compliance Health Score</p><div class="health-score">{round(avg_score)}%</div></div>""", unsafe_allow_html=True)
        
        # Show detailed table
        display_df = df[['id', 'name', 'country', 'display_status', 'manual_score', 'manual_reason']].rename(columns={'display_status': 'Status', 'manual_score': 'Score', 'manual_reason': 'Reason'})
        st.dataframe(display_df)
    else:
        st.info(f"No verified factories assigned to {client} yet. Factories are verified by the Admin before they appear here.")

def agency_dashboard(agency):
    st.header(f"🛡️ {agency} - Cyber Crime Dashboard")
    
    my_reports = [
        a for a in st.session_state.cyber_alerts 
        if a.get("country", "").strip() == agency.strip() 
        and a.get('status') not in ['Resolved', 'Closed', 'Archived']
    ]
    
    if not my_reports:
        st.success(f"✅ No pending cases for **{agency}**.")
        return

    st.subheader(f"📋 Pending Cases ({len(my_reports)})")
    df = pd.DataFrame(my_reports)
    st.dataframe(df[['tracking_id', 'category', 'status', 'priority', 'time']], use_container_width=True)
    
    if not df.empty and 'category' in df.columns:
        col1, col2 = st.columns(2)
        with col1: st.subheader("Category Breakdown"); st.bar_chart(df['category'].value_counts())
        with col2: st.subheader("Status Distribution"); st.bar_chart(df['status'].value_counts())

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
                                st.download_button("📥 Download Evidence File", f, file_name=alert['evidence_file'])
                else:
                    st.caption("No evidence attached.")
                
                notes = st.text_area("📝 Internal Notes (Visible to Admin & Agency)", value=alert.get('notes', ''), key=f"ag_notes_{alert['id']}")
                if notes != alert.get('notes'):
                    alert['notes'] = notes
                    save_all()
                    log_audit(f"Agency {agency} updated notes for {alert.get('tracking_id')}")
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
# 12. MAIN ROUTER
# ==========================================
if "landing_target" not in st.session_state: st.session_state.landing_target = None

if not st.session_state.get("logged_in", False):
    landing_page()
else:
    if st.session_state.role == "public": public_dashboard()
    elif st.session_state.role == "admin": admin_dashboard()
    elif st.session_state.role == "mnc": mnc_dashboard(st.session_state.client)
    elif st.session_state.role == "agency": agency_dashboard(st.session_state.client)

st.markdown("""
<div class="footer">
    © 2026 E4GRID. Global Industrial Immune System.
    <br>
    <a href="#">Privacy Policy</a> · <a href="#">Contact</a> · <a href="https://linkedin.com/company/e4grid" target="_blank">LinkedIn</a>
</div>
""", unsafe_allow_html=True)
