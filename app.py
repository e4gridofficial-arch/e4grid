import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import random

# ==========================================
# CONFIG & CSS (Billionaire Gold Theme)
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
        
        /* Timeline CSS */
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
        
        /* AI Suggestion Badge */
        .ai-badge { background: #3b82f6; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
        .boss-badge { background: #fbbf24; color: black; padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
        .ai-suggestion-box { background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 10px; border-radius: 8px; margin: 5px 0; }
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
        {"id": 1, "name": "Saga Sports", "status": "Green", "risk": "Low", "client": "Nike", "ai_suggestion": "Green", "human_override": False, "history": []},
        {"id": 2, "name": "Forward Sports", "status": "Green", "risk": "Low", "client": "Nike", "ai_suggestion": "Green", "human_override": False, "history": []},
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
# AI SUGGESTION ENGINE (Mock - Phase 3)
# ==========================================
def ai_suggest_status(factory_name):
    """AI mock function: Randomly suggests a status based on 'intelligence'"""
    suggestions = ["Green", "Yellow", "Red"]
    weights = [0.6, 0.3, 0.1]  # 60% Green, 30% Yellow, 10% Red
    return random.choices(suggestions, weights=weights, k=1)[0]

# ==========================================
# HELPER: TIMELINE GENERATOR
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
        html += f"""
        <div class="timeline-step">
            <div class="timeline-dot" style="background:{dot_color};"></div>
            <span class="timeline-label {label_class}">{step}</span>
        </div>
        """
        if i < len(steps)-1:
            line_class = "done" if i < active_index else ""
            html += f'<div class="timeline-line {line_class}"></div>'
    html += '</div>'
    return html

# ==========================================
# LANDING PAGE
# ==========================================
def landing_page():
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=120)
        else:
            st.markdown("<h1 style='color:#fbbf24;'>⚡</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown(
            f"""
            <div style="padding-top: 15px;">
                <div style="font-size: 2.8rem; font-weight: 800; color: #fbbf24;">E4GRID</div>
                <div class="tagline-gold" style="font-size: 1.1rem; letter-spacing: 2px;">See Risk · Build Trust · Stay Complaint</div>
                <div style="color: #64748b; font-size: 0.8rem; letter-spacing: 3px;">BUILDING A SAFER DIGITAL WORLD</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.divider()
    st.markdown("### 🌐 A Unified Grid for Global Security")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background:#1e293b; padding:20px; border-radius:12px; border-top:4px solid #fbbf24;">
            <h4 style="color:#fbbf24;">🛡️ Public</h4>
            <p style="color:#94a3b8; font-size:0.9rem;">Report cybercrime, upload evidence, and track status with a unique ID.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#1e293b; padding:20px; border-radius:12px; border-top:4px solid #3b82f6;">
            <h4 style="color:#3b82f6;">🏢 Enterprise</h4>
            <p style="color:#94a3b8; font-size:0.9rem;">Monitor factory compliance, risk scores, and supply chain health.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:#1e293b; padding:20px; border-radius:12px; border-top:4px solid #22c55e;">
            <h4 style="color:#22c55e;">🛡️ Agency</h4>
            <p style="color:#94a3b8; font-size:0.9rem;">Investigate assigned cases with full evidence & actionable intelligence.</p>
        </div>
        """, unsafe_allow_html=True)
    
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
                    "tracking_id": tracking_id,
                    "name": name if name else "Anonymous",
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
    st.subheader("🔍 Track Complaint")
    track = st.text_input("Enter Tracking ID")
    if st.button("Check Status"):
        found = [a for a in st.session_state.cyber_alerts if a.get("tracking_id") == track]
        if found:
            st.success(f"Status: {found[0]['status']} | Assigned to: {found[0].get('assigned_to', 'Pending')}")
            st.markdown(generate_timeline(found[0]['status']), unsafe_allow_html=True)

# ==========================================
# ADMIN DASHBOARD (Phase 3: AI Suggestions + Override)
# ==========================================
def admin_dashboard():
    st.header("👑 Command Center")
    
    total = len(st.session_state.cyber_alerts)
    pending = len([a for a in st.session_state.cyber_alerts if a['status'] not in ['Resolved', 'Closed', 'Archived']])
    resolved = len([a for a in st.session_state.cyber_alerts if a['status'] == 'Resolved'])
    views = st.session_state.views_data
    
    col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
    col1.metric("📊 Reports", total)
    col2.metric("⏳ Pending", pending)
    col3.metric("✅ Resolved", resolved)
    col4.metric("👁️ Views", views["total"])
    col5.metric("📆 Today", views["today"])
    with col6:
        st.markdown(f"""
        <div style="text-align: center; padding-top: 10px;">
            <span class="notif-bell" style="font-size: 2rem;">🔔</span>
            <span class="notif-badge" style="position: relative; top: -15px; left: -10px; background: #ef4444; color: white; border-radius: 50%; padding: 2px 8px; font-size: 14px;">{pending}</span>
        </div>
        """, unsafe_allow_html=True)
    
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

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Reports", "🏭 Factories", "🏢 MNCs", "🌍 Agencies", "📜 Audit Logs", "🤖 AI Control"])
    
    with tab1:
        search = st.text_input("🔍 Search")
        filtered = st.session_state.cyber_alerts
        if search:
            filtered = [a for a in filtered if search.lower() in str(a.get('tracking_id', '')).lower() or search.lower() in a.get('name', '').lower()]
        active_reports = [a for a in filtered if a.get('status') != 'Archived']
        if active_reports:
            df = pd.DataFrame(active_reports)
            st.dataframe(df[['tracking_id', 'name', 'country', 'category', 'status', 'priority', 'assigned_to', 'time']], use_container_width=True)
            for alert in active_reports:
                with st.expander(f"📌 {alert.get('tracking_id')} - {alert.get('name')}"):
                    st.markdown(generate_timeline(alert.get('status')), unsafe_allow_html=True)
                    
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
                        agency_list = list(st.session_state.agencies.keys())
                        assigned_to = st.selectbox("Assign to Agency", agency_list, index=agency_list.index(alert.get('assigned_to')) if alert.get('assigned_to') in agency_list else 0, key=f"assign_{alert['id']}")
                        if assigned_to != alert.get('assigned_to'):
                            alert['assigned_to'] = assigned_to
                            if "Assigned" not in alert.get('timeline', []):
                                alert['timeline'] = alert.get('timeline', ["New"]) + [f"Assigned to {assigned_to}"]
                            save_all()
                            log_audit(f"Assigned {alert.get('tracking_id')} to {assigned_to}")
                        new_status = st.selectbox("Status", ["New", "Under Review", "Resolved", "Closed", "Archived"], index=["New","Under Review","Resolved","Closed","Archived"].index(alert.get('status')), key=f"st_{alert['id']}")
                        if new_status != alert.get('status'):
                            alert['status'] = new_status
                            if new_status not in alert.get('timeline', []):
                                alert['timeline'] = alert.get('timeline', ["New"]) + [new_status]
                            save_all()
                            log_audit(f"Status changed to {new_status} for {alert.get('tracking_id')}")
                        priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=["Low","Medium","High"].index(alert.get('priority', 'Medium')), key=f"pr_{alert['id']}")
                        if priority != alert.get('priority'):
                            alert['priority'] = priority
                            save_all()
        else:
            st.success("✅ No active reports.")
    
    # --- TAB 2: FACTORIES (Phase 3: AI Suggestion + Human Override) ---
    with tab2:
        st.subheader("🏭 Factory Compliance (AI Suggested + Boss Verified)")
        st.caption("🤖 AI scans public data. 👑 You verify and override.")
        
        # Stats for Factories
        total_factories = len(st.session_state.factories)
        green = len([f for f in st.session_state.factories if f['status'] == 'Green'])
        yellow = len([f for f in st.session_state.factories if f['status'] == 'Yellow'])
        red = len([f for f in st.session_state.factories if f['status'] == 'Red'])
        st.metric("📊 Factories Health", f"{green} Green, {yellow} Yellow, {red} Red out of {total_factories}")
        
        # Factory Table with AI Suggestions
        for factory in st.session_state.factories:
            with st.expander(f"🏭 {factory['name']} (Current: {factory['status']}) - Client: {factory['client']}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**Factory:** {factory['name']}")
                    st.write(f"**Client:** {factory['client']}")
                    st.write(f"**Current Status:** {factory['status']}")
                    
                    # AI Suggestion Box (Phase 3)
                    ai_suggestion = factory.get('ai_suggestion', 'Green')
                    st.markdown(f"""
                    <div class="ai-suggestion-box">
                        <span class="ai-badge">🤖 AI SUGGESTION</span>
                        <span style="color: #3b82f6; font-weight: 600; margin-left: 10px;">{ai_suggestion}</span>
                        <span style="color: #94a3b8; font-size: 0.8rem; margin-left: 10px;">(Based on satellite & public data scan)</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Human Override Indicator
                    if factory.get('human_override', False):
                        st.markdown(f"""
                        <div style="background: rgba(251, 191, 36, 0.1); border-left: 4px solid #fbbf24; padding: 10px; border-radius: 8px; margin: 5px 0;">
                            <span class="boss-badge">👑 BOSS VERIFIED</span>
                            <span style="color: #fbbf24; margin-left: 10px;">You manually approved this status.</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                with col2:
                    st.subheader("Update Status")
                    new_status = st.selectbox(
                        f"Set Status for {factory['name']}",
                        ["Green", "Yellow", "Red"],
                        index=["Green", "Yellow", "Red"].index(factory['status']),
                        key=f"fact_status_{factory['id']}"
                    )
                    if new_status != factory['status']:
                        factory['status'] = new_status
                        factory['human_override'] = True  # Mark as human verified
                        if 'history' not in factory:
                            factory['history'] = []
                        factory['history'].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Status changed to {new_status}")
                        save_all()
                        log_audit(f"Factory {factory['name']} status changed to {new_status} (Human Override)")
                        st.rerun()
                
                with col3:
                    st.subheader("AI Scan")
                    if st.button(f"🔄 Run AI Scan for {factory['name']}", key=f"ai_scan_{factory['id']}"):
                        new_ai_suggestion = ai_suggest_status(factory['name'])
                        factory['ai_suggestion'] = new_ai_suggestion
                        # Only auto-apply if no human override
                        if not factory.get('human_override', False):
                            factory['status'] = new_ai_suggestion
                        save_all()
                        log_audit(f"AI Scan ran for {factory['name']}. Suggested: {new_ai_suggestion}")
                        st.rerun()
                    
                    st.caption("⚡ AI will scan satellite & public data.")
                
                # History
                if factory.get('history'):
                    st.caption("📜 History:")
                    for h in factory['history'][-3:]:
                        st.caption(f"- {h}")
        
        # Add New Factory (with AI pre-scan)
        st.divider()
        st.subheader("➕ Add New Factory (AI will scan automatically)")
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Factory Name")
            new_client = st.selectbox("Assign to MNC", list(st.session_state.mnc_clients.keys()))
        with col2:
            new_status = st.selectbox("Initial Status", ["Green", "Yellow", "Red"])
            if st.button("Add Factory with AI Suggestion"):
                if new_name:
                    ai_suggestion = ai_suggest_status(new_name)
                    new_factory = {
                        "id": len(st.session_state.factories) + 1,
                        "name": new_name,
                        "status": new_status,
                        "risk": "Low" if new_status == "Green" else "Medium" if new_status == "Yellow" else "High",
                        "client": new_client,
                        "ai_suggestion": ai_suggestion,
                        "human_override": False,
                        "history": [f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Factory added (AI suggested {ai_suggestion})"]
                    }
                    st.session_state.factories.append(new_factory)
                    save_all()
                    log_audit(f"Factory Added: {new_name} (AI Suggested: {ai_suggestion})")
                    st.success(f"✅ Factory added! AI Suggestion: {ai_suggestion}")
                    st.rerun()
    
    with tab3:
        st.subheader("Manage MNC Clients")
        for name, data in st.session_state.mnc_clients.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1: st.write(f"**{name}**")
            with col2:
                np = st.text_input(f"Password", value=data["password"], key=f"mp_{name}")
                if np != data["password"]: st.session_state.mnc_clients[name]["password"] = np; save_all(); log_audit(f"MNC Pass changed: {name}")
            with col3:
                active = st.checkbox("Active", value=data["active"], key=f"ma_{name}")
                if active != data["active"]: st.session_state.mnc_clients[name]["active"] = active; save_all(); st.rerun()
        st.divider()
        new_mnc = st.text_input("New MNC Name")
        new_mnc_pass = st.text_input("Set Password")
        if st.button("Add MNC"):
            if new_mnc and new_mnc_pass:
                st.session_state.mnc_clients[new_mnc] = {"password": new_mnc_pass, "active": True}
                save_all(); log_audit(f"MNC Added: {new_mnc}"); st.rerun()

    with tab4:
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
            if n_ag and n_pass:
                st.session_state.agencies[n_ag] = {"password": n_pass, "helpline": n_hl, "active": True}
                save_all(); log_audit(f"Agency Added: {n_ag}"); st.rerun()

    with tab5:
        st.subheader("📜 Complete Activity Trail")
        if st.session_state.audit_logs:
            df_audit = pd.DataFrame(st.session_state.audit_logs[::-1])
            st.dataframe(df_audit, use_container_width=True)
            if st.button("🗑️ Clear All Logs", use_container_width=True):
                st.session_state.audit_logs.clear()
                save_json("audit.json", [])
                st.rerun()
        else:
            st.info("No activities recorded yet.")

    with tab6:
        st.subheader("🤖 AI Control Center")
        st.caption("Manage AI settings and scan all factories at once.")
        
        if st.button("🔄 Run AI Scan on ALL Factories", use_container_width=True):
            for factory in st.session_state.factories:
                ai_suggestion = ai_suggest_status(factory['name'])
                factory['ai_suggestion'] = ai_suggestion
                if not factory.get('human_override', False):
                    factory['status'] = ai_suggestion
                if 'history' not in factory:
                    factory['history'] = []
                factory['history'].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - AI Scan: Suggested {ai_suggestion}")
            save_all()
            log_audit("Bulk AI Scan executed on all factories")
            st.success("✅ AI Scan completed! Check each factory for suggestions.")
            st.rerun()
        
        st.info("💡 AI currently uses mock intelligence. When you're ready, I can integrate real satellite API (Google Earth Engine).")

# ==========================================
# MNC DASHBOARD (Health Score)
# ==========================================
def mnc_dashboard(client):
    st.header(f"🏢 {client} - Compliance Dashboard")
    st.caption("See Risk · Build Trust · Stay Complaint")
    
    df = pd.DataFrame([f for f in st.session_state.factories if f["client"] == client])
    if not df.empty:
        total = len(df)
        green = len(df[df['status'] == 'Green'])
        yellow = len(df[df['status'] == 'Yellow'])
        red = len(df[df['status'] == 'Red'])
        score = (green / total) * 100 if total > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏭 Total Factories", total)
        col2.metric("🟢 Green", green)
        col3.metric("🟡 Yellow", yellow)
        col4.metric("🔴 Red", red)
        
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: #1e293b; border-radius: 12px; margin: 10px 0;">
            <p style="color: #94a3b8; margin: 0;">Overall Compliance Health Score</p>
            <div class="health-score">{round(score)}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(df)
    else:
        st.info("No factories assigned yet.")

# ==========================================
# AGENCY DASHBOARD
# ==========================================
def agency_dashboard(agency):
    st.header(f"🛡️ {agency} - Case Investigation Panel")
    
    my_reports = [a for a in st.session_state.cyber_alerts if a.get("assigned_to") == agency and a.get('status') != 'Archived']
    
    if not my_reports:
        st.success("✅ No cases assigned to you yet.")
        return

    st.subheader("📋 Assigned Cases")
    df = pd.DataFrame(my_reports)
    st.dataframe(df[['tracking_id', 'category', 'status', 'priority', 'time']], use_container_width=True)
    
    if not df.empty and 'category' in df.columns:
        st.subheader("📊 Case Analytics")
        col_ch1, col_ch2 = st.columns(2)
        with col_ch1:
            st.bar_chart(df['category'].value_counts())
        with col_ch2:
            st.bar_chart(df['status'].value_counts())

    st.divider()
    st.subheader("📂 Case Files (Complete Details)")
    
    for alert in my_reports:
        with st.expander(f"🔍 Case: {alert.get('tracking_id')} - {alert.get('name')} ({alert.get('status')})"):
            st.markdown(generate_timeline(alert.get('status')), unsafe_allow_html=True)
            
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown(f"**👤 Name:** {alert.get('name')}")
                st.markdown(f"**📧 Email:** {alert.get('email', 'N/A')}")
                st.markdown(f"**🌍 Country:** {alert.get('country')} | **🏙️ City:** {alert.get('city', 'N/A')}")
                st.markdown(f"**📂 Category:** {alert.get('category')}")
                st.markdown(f"**🔗 Website/URL:** {alert.get('website', 'N/A')}")
                st.markdown(f"**📝 Description:**")
                st.info(alert.get('text'))
                
                if alert.get('evidence_file'):
                    file_path = os.path.join(UPLOAD_DIR, alert['evidence_file'])
                    if os.path.exists(file_path):
                        st.markdown("**📎 Evidence Uploaded:**")
                        if alert['evidence_file'].lower().endswith(('png', 'jpg', 'jpeg')):
                            st.image(file_path, caption="Evidence Image", width=300)
                        else:
                            with open(file_path, "rb") as f:
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
# SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    else:
        st.markdown("<h2 style='color:#fbbf24;'>⚡ E4GRID</h2>", unsafe_allow_html=True)
    st.caption("See Risk · Build Trust · Stay Complaint")
    st.divider()
    if st.session_state.get("logged_in", False):
        st.write(f"**User:** `{st.session_state.role}`")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False; st.session_state.role = None; st.session_state.client = None; st.session_state.landing_target = None; st.rerun()

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
    <a href="#">Privacy Policy</a> · <a href="#">Contact</a> · <a href="https://linkedin.com/company/e4grid" target="_blank">LinkedIn</a>
</div>
""", unsafe_allow_html=True)
