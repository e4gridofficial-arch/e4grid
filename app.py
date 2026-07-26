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
        .ai-suggestion-box { background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 10px; border-radius: 8px; margin: 5px 0; }
        .ai-reason-text { color: #94a3b8; font-size: 0.8rem; margin-top: 4px; }
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
        {"id": 1, "name": "Saga Sports", "status": "Green", "risk": "Low", "client": "Nike", "ai_suggestion": "Green", "ai_reason": "✅ No violations found.", "human_override": False, "history": []}
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
# DETERMINISTIC AI ENGINE (No Randomness)
# ==========================================
def ai_analyze_factory(factory_name):
    name_lower = factory_name.lower()
    
    # Hardcoded rules
    if "tannery" in name_lower or "leather" in name_lower:
        return "Red", "⚠️ High Chromium & heavy metal pollutants detected in surrounding soil/water (EPA Reports)."
    if "waste" in name_lower or "dump" in name_lower:
        return "Red", "⚠️ Illegal waste dumping detected near facility (Satellite Imagery)."
    if "dye" in name_lower or "chemical" in name_lower:
        return "Yellow", "🟡 High chemical usage detected. Requires periodic environmental checks."
    if "child" in name_lower or "labor" in name_lower:
        return "Red", "⚠️ Historical child labor complaints found in public records."
    if "sport" in name_lower or "textile" in name_lower:
        return "Green", "✅ Satellite imagery clear. No recent EPA violations found."
    
    # Deterministic hash-based fallback (same name → same result always)
    hash_val = sum(ord(c) for c in factory_name) % 10
    if hash_val <= 6:
        return "Green", "✅ No violations detected in public records or satellite scan."
    elif hash_val <= 8:
        return "Yellow", "🟡 Minor anomaly detected. Suggest a physical audit."
    else:
        return "Red", "🔴 Critical violation flagged by AI based on environmental data."

# ==========================================
# TIMELINE GENERATOR
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
            <p style="color:#94a3b8; font-size:0.9rem;">Report cybercrime, upload evidence, and track status.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#1e293b; padding:20px; border-radius:12px; border-top:4px solid #3b82f6;">
            <h4 style="color:#3b82f6;">🏢 Enterprise</h4>
            <p style="color:#94a3b8; font-size:0.9rem;">Monitor compliance, risk scores, and supply chain health.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:#1e293b; padding:20px; border-radius:12px; border-top:4px solid #22c55e;">
            <h4 style="color:#22c55e;">🛡️ Agency</h4>
            <p style="color:#94a3b8; font-size:0.9rem;">Investigate assigned cases with full evidence.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🌍 Public", use_container_width=True):
            st.session_state.role = "public"; st.session_state.logged_in = True; st.rerun()
    with col2:
        if st.button("🏢 Enterprise", use_container_width=True):
            st.session_state.landing_target = "mnc"; st.rerun()
    with col3:
        if st.button("🛡️ Agency", use_container_width=True):
            st.session_state.landing_target = "agency"; st.rerun()
    with col4:
        if st.button("👑 Owner", use_container_width=True):
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
# ADMIN DASHBOARD
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
            with col_ch1: st.subheader("Category"); st.bar_chart(df['category'].value_counts())
            with col_ch2: st.subheader("Status"); st.bar_chart(df['status'].value_counts())

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Reports", "🏭 Factories", "🏢 MNCs", "🌍 Agencies", "📜 Audit Logs", "🤖 AI Control"])
    
    # --- REPORTS ---
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
                                if alert['evidence_file'].lower().endswith(('png', 'jpg', 'jpeg')):
                                    st.image(fp, width=300)
                                else:
                                    with open(fp, "rb") as f:
                                        st.download_button("📥 Download", f, file_name=alert['evidence_file'])
                        notes = st.text_area("Notes", value=alert.get('notes', ''), key=f"notes_{alert['id']}")
                        if notes != alert.get('notes'):
                            alert['notes'] = notes
                            save_all()
                            log_audit(f"Notes updated {alert.get('tracking_id')}")
                    with col_b:
                        agency_list = list(st.session_state.agencies.keys())
                        assigned = st.selectbox("Assign", agency_list, index=agency_list.index(alert.get('assigned_to')) if alert.get('assigned_to') in agency_list else 0, key=f"assign_{alert['id']}")
                        if assigned != alert.get('assigned_to'):
                            alert['assigned_to'] = assigned
                            if "Assigned" not in alert.get('timeline', []):
                                alert['timeline'] = alert.get('timeline', ["New"]) + [f"Assigned to {assigned}"]
                            save_all()
                        new_status = st.selectbox("Status", ["New", "Under Review", "Resolved", "Closed", "Archived"], index=["New","Under Review","Resolved","Closed","Archived"].index(alert.get('status')), key=f"st_{alert['id']}")
                        if new_status != alert.get('status'):
                            alert['status'] = new_status
                            if new_status not in alert.get('timeline', []):
                                alert['timeline'] = alert.get('timeline', ["New"]) + [new_status]
                            save_all()
                        priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=["Low","Medium","High"].index(alert.get('priority', 'Medium')), key=f"pr_{alert['id']}")
                        if priority != alert.get('priority'):
                            alert['priority'] = priority
                            save_all()
        else:
            st.success("✅ No active reports.")
    
    # --- FACTORIES ---
    with tab2:
        st.subheader("🏭 Factory Compliance (AI Suggested + Boss Verified)")
        st.caption("🤖 AI scans public data. 👑 You verify and override.")
        
        total_f = len(st.session_state.factories)
        green = len([f for f in st.session_state.factories if f['status'] == 'Green'])
        yellow = len([f for f in st.session_state.factories if f['status'] == 'Yellow'])
        red = len([f for f in st.session_state.factories if f['status'] == 'Red'])
        st.metric("📊 Health", f"{green} 🟢, {yellow} 🟡, {red} 🔴 out of {total_f}")
        
        col_del1, col_del2 = st.columns([1, 3])
        with col_del1:
            del_id = st.number_input("Enter Factory ID to Delete", min_value=1, step=1, key="del_fact_id")
            if st.button("🗑️ Delete Factory"):
                found = any(f["id"] == del_id for f in st.session_state.factories)
                if found:
                    st.session_state.factories = [f for f in st.session_state.factories if f["id"] != del_id]
                    save_all()
                    log_audit(f"Factory Deleted: ID {del_id}")
                    st.success(f"✅ Factory ID {del_id} deleted!")
                    st.rerun()
                else:
                    st.error(f"❌ Factory ID {del_id} not found.")
        with col_del2:
            st.caption("Tip: Check the ID from the list below before deleting.")
        
        st.divider()
        
        for factory in st.session_state.factories:
            with st.expander(f"🏭 {factory['name']} (Status: {factory['status']}) - {factory['client']}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**Client:** {factory['client']}")
                    st.write(f"**Current Status:** {factory['status']}")
                    
                    ai_suggestion = factory.get('ai_suggestion', 'Green')
                    ai_reason = factory.get('ai_reason', 'No specific reason provided.')
                    st.markdown(f"""
                    <div class="ai-suggestion-box">
                        <span class="ai-badge">🤖 AI SUGGESTION</span>
                        <span style="color: #3b82f6; font-weight: 600; margin-left: 10px;">{ai_suggestion}</span>
                        <div class="ai-reason-text">📌 {ai_reason}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if factory.get('human_override', False):
                        st.markdown(f"""
                        <div style="background: rgba(251, 191, 36, 0.1); border-left: 4px solid #fbbf24; padding: 10px; border-radius: 8px; margin: 5px 0;">
                            <span class="boss-badge">👑 BOSS VERIFIED</span>
                            <span style="color: #fbbf24; margin-left: 10px;">You manually approved this status.</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                with col2:
                    st.subheader("Override")
                    new_status = st.selectbox(
                        f"Set Status",
                        ["Green", "Yellow", "Red"],
                        index=["Green", "Yellow", "Red"].index(factory['status']),
                        key=f"fact_status_{factory['id']}"
                    )
                    if new_status != factory['status']:
                        factory['status'] = new_status
                        factory['human_override'] = True
                        if 'history' not in factory: factory['history'] = []
                        factory['history'].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Boss changed to {new_status}")
                        save_all()
                        log_audit(f"Boss changed {factory['name']} to {new_status}")
                        st.rerun()
                
                with col3:
                    st.subheader("Scan")
                    if st.button(f"🔄 AI Scan", key=f"ai_scan_{factory['id']}"):
                        suggestion, reason = ai_analyze_factory(factory['name'])
                        factory['ai_suggestion'] = suggestion
                        factory['ai_reason'] = reason
                        if not factory.get('human_override', False):
                            factory['status'] = suggestion
                        if 'history' not in factory: factory['history'] = []
                        factory['history'].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - AI Scan: {suggestion}")
                        save_all()
                        log_audit(f"AI Scanned {factory['name']}: {suggestion}")
                        st.rerun()
                
                if factory.get('history'):
                    with st.expander("📜 History"):
                        for h in factory['history'][-5:]:
                            st.caption(f"- {h}")
        
        st.divider()
        st.subheader("➕ Add New Factory (AI will analyze)")
        col_a, col_b = st.columns(2)
        with col_a:
            new_name = st.text_input("Factory Name")
            new_client = st.selectbox("Assign to MNC", list(st.session_state.mnc_clients.keys()))
        with col_b:
            new_status = st.selectbox("Initial Status", ["Green", "Yellow", "Red"])
            if st.button("Add Factory with AI Suggestion"):
                if new_name:
                    suggestion, reason = ai_analyze_factory(new_name)
                    new_factory = {
                        "id": len(st.session_state.factories)+1,
                        "name": new_name,
                        "status": new_status,
                        "risk": "Low" if new_status=="Green" else "Medium",
                        "client": new_client,
                        "ai_suggestion": suggestion,
                        "ai_reason": reason,
                        "human_override": False,
                        "history": [f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Added (AI suggests {suggestion})"]
                    }
                    st.session_state.factories.append(new_factory)
                    save_all()
                    log_audit(f"Factory Added: {new_name}")
                    st.success(f"✅ Added! AI Suggests: {suggestion} - {reason}")
                    st.rerun()
    
    # --- MNCs ---
    with tab3:
        for name, data in st.session_state.mnc_clients.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1: st.write(f"**{name}**")
            with col2:
                np = st.text_input(f"Pass", value=data["password"], key=f"mp_{name}")
                if np != data["password"]: st.session_state.mnc_clients[name]["password"] = np; save_all(); log_audit(f"MNC Pass changed: {name}")
            with col3:
                active = st.checkbox("Active", value=data["active"], key=f"ma_{name}")
                if active != data["active"]: st.session_state.mnc_clients[name]["active"] = active; save_all(); st.rerun()
        new_mnc = st.text_input("New MNC Name"); new_pass = st.text_input("Set Password")
        if st.button("Add MNC"):
            if new_mnc and new_pass:
                st.session_state.mnc_clients[new_mnc] = {"password": new_pass, "active": True}
                save_all(); log_audit(f"MNC Added: {new_mnc}"); st.rerun()
    
    # --- AGENCIES ---
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
    
    # --- AUDIT LOGS ---
    with tab5:
        if st.session_state.audit_logs:
            df_audit = pd.DataFrame(st.session_state.audit_logs[::-1])
            st.dataframe(df_audit, use_container_width=True)
            if st.button("🗑️ Clear All Logs"):
                st.session_state.audit_logs.clear()
                save_json("audit.json", [])
                st.rerun()
        else:
            st.info("No logs.")
    
    # --- AI CONTROL ---
    with tab6:
        st.subheader("🤖 AI Control Center")
        if st.button("🔄 Run AI Scan on ALL Factories", use_container_width=True):
            for factory in st.session_state.factories:
                suggestion, reason = ai_analyze_factory(factory['name'])
                factory['ai_suggestion'] = suggestion
                factory['ai_reason'] = reason
                if not factory.get('human_override', False):
                    factory['status'] = suggestion
                if 'history' not in factory: factory['history'] = []
                factory['history'].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Bulk AI: {suggestion}")
            save_all()
            log_audit("Bulk AI Scan Executed")
            st.success("✅ All factories scanned! Check their AI suggestions.")
            st.rerun()
        st.info("💡 AI uses deterministic logic. Same factory name = same result.")

# ==========================================
# MNC DASHBOARD
# ==========================================
def mnc_dashboard(client):
    st.header(f"🏢 {client} - Compliance")
    df = pd.DataFrame([f for f in st.session_state.factories if f["client"] == client])
    if not df.empty:
        total = len(df)
        green = len(df[df['status'] == 'Green'])
        yellow = len(df[df['status'] == 'Yellow'])
        red = len(df[df['status'] == 'Red'])
        score = (green / total) * 100
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏭 Total", total); col2.metric("🟢 Green", green)
        col3.metric("🟡 Yellow", yellow); col4.metric("🔴 Red", red)
        st.markdown(f"""
        <div style="text-align:center; padding:20px; background:#1e293b; border-radius:12px;">
            <p style="color:#94a3b8;">Health Score</p>
            <div class="health-score">{round(score)}%</div>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(df)
    else:
        st.info("No factories assigned.")

# ==========================================
# AGENCY DASHBOARD
# ==========================================
def agency_dashboard(agency):
    st.header(f"🛡️ {agency} - Cases")
    my_reports = [a for a in st.session_state.cyber_alerts if a.get("assigned_to") == agency and a.get('status') != 'Archived']
    if not my_reports:
        st.success("✅ No cases.")
        return
    df = pd.DataFrame(my_reports)
    st.dataframe(df[['tracking_id', 'category', 'status', 'priority', 'time']])
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1: st.bar_chart(df['category'].value_counts())
        with col2: st.bar_chart(df['status'].value_counts())
    
    for alert in my_reports:
        with st.expander(f"🔍 {alert.get('tracking_id')}"):
            st.markdown(generate_timeline(alert.get('status')), unsafe_allow_html=True)
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.write(f"**Name:** {alert.get('name')}")
                st.write(f"**Details:** {alert.get('text')}")
                if alert.get('evidence_file'):
                    fp = os.path.join(UPLOAD_DIR, alert['evidence_file'])
                    if os.path.exists(fp):
                        if alert['evidence_file'].lower().endswith(('png', 'jpg', 'jpeg')):
                            st.image(fp, width=300)
                        else:
                            with open(fp, "rb") as f:
                                st.download_button("📥 Download", f, file_name=alert['evidence_file'])
                notes = st.text_area("Notes", value=alert.get('notes', ''), key=f"ag_notes_{alert['id']}")
                if notes != alert.get('notes'): alert['notes'] = notes; save_all()
            with col_b:
                new_status = st.selectbox("Status", ["New", "Under Review", "Resolved", "Closed"], index=["New","Under Review","Resolved","Closed"].index(alert.get('status')) if alert.get('status') in ["New","Under Review","Resolved","Closed"] else 0, key=f"ag_st_{alert['id']}")
                if new_status != alert.get('status'):
                    alert['status'] = new_status
                    if new_status not in alert.get('timeline', []):
                        alert['timeline'] = alert.get('timeline', ["New"]) + [new_status]
                    save_all()
                    st.rerun()

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=150)
    else: st.markdown("<h2 style='color:#fbbf24;'>⚡ E4GRID</h2>", unsafe_allow_html=True)
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
