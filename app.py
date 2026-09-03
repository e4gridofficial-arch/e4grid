import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import random
import requests

# ==========================================
# 🔥 BOSS: APNI SUPABASE KEYS YAHAN DAALEIN
# ==========================================
SUPABASE_URL = "https://YOUR_PROJECT_REFERENCE.supabase.co"   # <-- Yahan Project URL daalo
SUPABASE_KEY = "YOUR_PUBLISHABLE_KEY_HERE"                   # <-- Yahan Publishable key daalo

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ==========================================
# 📌 DEMO REQUEST LINK
# ==========================================
DEMO_FORM_LINK = "https://forms.gle/YOUR_FORM_ID_HERE"

# ==========================================
# DATABASE HELPERS
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
# DATA LOAD FUNCTIONS
# ==========================================
def load_factories():
    data = db_get("factories")
    if data:
        for item in data:
            if "country" not in item or not item["country"]:
                item["country"] = "Pakistan"
        return data
    return [{"id": 1, "name": "Saga Sports", "status": "Green", "risk": "Low", "client": "Nike", "country": "Pakistan", "ai_suggestion": "Green", "ai_reason": "✅ No violations.", "human_override": False, "history": []}]

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
    if data:
        # Ensure every alert has a country (for old data)
        for item in data:
            if "country" not in item or not item["country"]:
                item["country"] = "Pakistan"
        return data
    return []

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

ADMIN_PASSWORD = "esha4t4boss"

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
# 🤖 GLOBAL AI ENGINE
# ==========================================
def ai_analyze_factory(factory_name, country="Pakistan"):
    try:
        query = f"{factory_name} {country} violation OR pollution OR child labor OR fine OR accident"
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            content = response.text.lower()
            negative_keywords = ['violation', 'pollution', 'fine', 'child labor', 'illegal', 'waste', 'toxic', 'accident', 'hazard', 'cancer']
            for word in negative_keywords:
                if word in content:
                    return "Red", f"⚠️ Recent news mentions '{word}' for this factory in {country}."
            if "item" in content or "title" in content:
                return "Yellow", f"🟡 Recent news found for {factory_name} in {country}."
    except:
        pass

    name_lower = factory_name.lower()
    if "tannery" in name_lower or "leather" in name_lower:
        return "Red", "⚠️ High Chromium & heavy metal pollutants detected (Local Rule)."
    if "waste" in name_lower or "dump" in name_lower:
        return "Red", "⚠️ Illegal waste dumping detected (Local Rule)."
    if "dye" in name_lower or "chemical" in name_lower:
        return "Yellow", "🟡 High chemical usage detected."
    if "sport" in name_lower or "textile" in name_lower:
        return "Green", "✅ Satellite imagery clear."
    
    hash_val = sum(ord(c) for c in factory_name) % 10
    if hash_val <= 6: return "Green", "✅ No violations detected."
    elif hash_val <= 8: return "Yellow", "🟡 Minor anomaly detected."
    else: return "Red", "🔴 Critical violation flagged."

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

# ==========================================
# FILE UPLOAD HELPER
# ==========================================
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
        .ai-badge { background: #3b82f6; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
        .boss-badge { background: #fbbf24; color: black; padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
        .ai-suggestion-box { background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 10px; border-radius: 8px; margin: 5px 0; }
        .ai-reason-text { color: #94a3b8; font-size: 0.8rem; margin-top: 4px; }
        .demo-banner { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #0a0f1e; padding: 10px 20px; border-radius: 30px; font-weight: 700; text-align: center; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=150)
    else: st.markdown("<h2 style='color:#fbbf24;'>⚡ E4GRID</h2>", unsafe_allow_html=True)
    st.caption("See Risk · Build Trust · Stay Compliant")
    
    st.divider()
    st.markdown("### 🚀 Interested in E4GRID?")
    st.link_button("📌 Book a 15-min Live Demo", DEMO_FORM_LINK, use_container_width=True)
    st.caption("For Agencies, MNCs, and Enterprises.")
    st.divider()
    
    if st.session_state.get("logged_in", False):
        st.write(f"**User:** `{st.session_state.role}`")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False; st.session_state.role = None; st.session_state.client = None; st.session_state.landing_target = None; st.rerun()

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
                    "tracking_id": tracking_id, "name": name or "Anonymous",
                    "email": email, 
                    "country": country,  # <-- COUNTRY ZAROORI HAI
                    "city": city,
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
# ADMIN DASHBOARD (ALL REPORTS)
# ==========================================
def admin_dashboard():
    st.header("👑 Command Center")
    total = len(st.session_state.cyber_alerts)
    pending = len([a for a in st.session_state.cyber_alerts if a['status'] not in ['Resolved', 'Closed', 'Archived']])
    resolved = len([a for a in st.session_state.cyber_alerts if a['status'] == 'Resolved'])
    views = st.session_state.views_data
    col1, col2, col3, col4, col5, col6 = st.columns([2,1,1,1,1,1])
    col1.metric("📊 Reports", total)
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
            with col_ch1: st.subheader("Category"); st.bar_chart(df['category'].value_counts())
            with col_ch2: st.subheader("Status"); st.bar_chart(df['status'].value_counts())

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Reports", "🏭 Factories", "🏢 MNCs", "🌍 Agencies", "📜 Audit Logs", "🤖 AI Control"])
    
    # --- REPORTS (Admin sees EVERYTHING) ---
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
    
    # --- FACTORIES ---
    with tab2:
        st.subheader("🏭 Factory Compliance (Global)")
        total_f = len(st.session_state.factories)
        green = len([f for f in st.session_state.factories if f['status'] == 'Green'])
        yellow = len([f for f in st.session_state.factories if f['status'] == 'Yellow'])
        red = len([f for f in st.session_state.factories if f['status'] == 'Red'])
        st.metric("📊 Health", f"{green} 🟢, {yellow} 🟡, {red} 🔴 out of {total_f}")
        
        col_del1, col_del2 = st.columns([1,3])
        with col_del1:
            del_id = st.number_input("Delete ID", min_value=1, step=1, key="del_fact_id")
            if st.button("🗑️ Delete"):
                found = any(f["id"] == del_id for f in st.session_state.factories)
                if found:
                    st.session_state.factories = [f for f in st.session_state.factories if f["id"] != del_id]
                    save_all(); log_audit(f"Factory Deleted: ID {del_id}"); st.success(f"✅ Deleted ID {del_id}!"); st.rerun()
                else: st.error(f"❌ ID {del_id} not found.")
        with col_del2: st.caption("Tip: Check the ID from the list below.")
        st.divider()
        
        for factory in st.session_state.factories:
            country = factory.get("country", "Pakistan")
            with st.expander(f"🏭 {factory['name']} ({country}) - Status: {factory['status']}"):
                col1, col2, col3 = st.columns([2,1,1])
                with col1:
                    st.write(f"**Client:** {factory['client']}")
                    st.write(f"**Country:** {country}")
                    st.write(f"**Current Status:** {factory['status']}")
                    ai_suggestion = factory.get('ai_suggestion','Green')
                    ai_reason = factory.get('ai_reason','No reason.')
                    st.markdown(f"""<div class="ai-suggestion-box"><span class="ai-badge">🤖 AI SUGGESTION</span> <span style="color:#3b82f6;font-weight:600;margin-left:10px;">{ai_suggestion}</span><div class="ai-reason-text">📌 {ai_reason}</div></div>""", unsafe_allow_html=True)
                    if factory.get('human_override', False):
                        st.markdown(f"""<div style="background:rgba(251,191,36,0.1);border-left:4px solid #fbbf24;padding:10px;border-radius:8px;margin:5px 0;"><span class="boss-badge">👑 BOSS VERIFIED</span> <span style="color:#fbbf24;margin-left:10px;">You manually approved this.</span></div>""", unsafe_allow_html=True)
                with col2:
                    new_status = st.selectbox("Override", ["Green","Yellow","Red"], index=["Green","Yellow","Red"].index(factory['status']), key=f"fact_status_{factory['id']}")
                    if new_status != factory['status']:
                        factory['status'] = new_status; factory['human_override'] = True
                        if 'history' not in factory: factory['history'] = []
                        factory['history'].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Boss changed to {new_status}")
                        save_all(); log_audit(f"Boss changed {factory['name']} to {new_status}"); st.rerun()
                with col3:
                    if st.button(f"🔄 AI Scan (Global)", key=f"ai_scan_{factory['id']}"):
                        suggestion, reason = ai_analyze_factory(factory['name'], country)
                        factory['ai_suggestion'] = suggestion; factory['ai_reason'] = reason
                        if not factory.get('human_override', False): factory['status'] = suggestion
                        if 'history' not in factory: factory['history'] = []
                        factory['history'].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - AI Scan (Global): {suggestion}")
                        save_all(); log_audit(f"AI Scanned {factory['name']} ({country}): {suggestion}"); st.rerun()
                if factory.get('history'):
                    with st.expander("📜 History"):
                        for h in factory['history'][-5:]: st.caption(f"- {h}")
        
        st.divider()
        st.subheader("➕ Add New Factory (Global)")
        col_a, col_b = st.columns(2)
        with col_a:
            new_name = st.text_input("Factory Name")
            new_client = st.selectbox("Assign to MNC", list(st.session_state.mnc_clients.keys()))
            new_country = st.text_input("Country (e.g., Bangladesh, Vietnam, USA)", "Pakistan")
        with col_b:
            new_status = st.selectbox("Initial Status", ["Green","Yellow","Red"])
            if st.button("Add with Global AI"):
                if new_name:
                    suggestion, reason = ai_analyze_factory(new_name, new_country)
                    new_factory = {
                        "id": len(st.session_state.factories)+1,
                        "name": new_name,
                        "status": new_status,
                        "risk": "Low" if new_status=="Green" else "Medium",
                        "client": new_client,
                        "country": new_country,
                        "ai_suggestion": suggestion,
                        "ai_reason": reason,
                        "human_override": False,
                        "history": [f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Added (AI suggests {suggestion} for {new_country})"]
                    }
                    st.session_state.factories.append(new_factory)
                    save_all(); log_audit(f"Factory Added: {new_name} ({new_country})"); st.success(f"✅ Added! AI Suggests: {suggestion} - {reason}"); st.rerun()

    # --- MNCs ---
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

    # --- AGENCIES ---
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

    # --- AUDIT LOGS ---
    with tab5:
        if st.session_state.audit_logs:
            df_audit = pd.DataFrame(st.session_state.audit_logs[::-1])
            st.dataframe(df_audit, use_container_width=True)
            if st.button("🗑️ Clear All Logs"):
                st.session_state.audit_logs.clear(); save_audit([]); st.rerun()
        else: st.info("No logs.")

    # --- AI CONTROL ---
    with tab6:
        if st.button("🔄 Run Global AI Scan on ALL Factories", use_container_width=True):
            for factory in st.session_state.factories:
                country = factory.get("country", "Pakistan")
                suggestion, reason = ai_analyze_factory(factory['name'], country)
                factory['ai_suggestion'] = suggestion; factory['ai_reason'] = reason
                if not factory.get('human_override', False): factory['status'] = suggestion
                if 'history' not in factory: factory['history'] = []
                factory['history'].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Bulk AI (Global): {suggestion}")
            save_all(); log_audit("Bulk Global AI Scan Executed"); st.success("✅ All factories scanned globally!"); st.rerun()
        st.info("💡 AI now scans Google News for real-time global alerts + fallback logic.")

# ==========================================
# ✅ AGENCY DASHBOARD (FIXED: Strict Country Filter + Auto-Remove Resolved)
# ==========================================
def agency_dashboard(agency):
    st.header(f"🛡️ {agency} - Cyber Crime Dashboard")
    
    # --- STRICT FILTER: Sirf us country ki reports jo Pending/Under Review hain ---
    my_reports = [
        a for a in st.session_state.cyber_alerts 
        if a.get("country", "").strip() == agency.strip()  # <-- STRICT MATCH
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
# MNC DASHBOARD
# ==========================================
def mnc_dashboard(client):
    st.header(f"🏢 {client} - Compliance")
    df = pd.DataFrame([f for f in st.session_state.factories if f["client"] == client])
    if not df.empty:
        total = len(df); green = len(df[df['status']=='Green']); yellow = len(df[df['status']=='Yellow']); red = len(df[df['status']=='Red'])
        score = (green/total)*100
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏭 Total", total); col2.metric("🟢 Green", green); col3.metric("🟡 Yellow", yellow); col4.metric("🔴 Red", red)
        st.markdown(f"""<div style="text-align:center;padding:20px;background:#1e293b;border-radius:12px;"><p style="color:#94a3b8;">Health Score</p><div class="health-score">{round(score)}%</div></div>""", unsafe_allow_html=True)
        st.dataframe(df[['id', 'name', 'country', 'status', 'risk']])
    else: st.info("No factories assigned.")

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
