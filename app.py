import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import random
import requests
import time
import re
import urllib.parse
from fpdf import FPDF
import io
import base64

# ==========================================
# 🔒 SECURE
# ==========================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

SENTINEL_CLIENT_ID = st.secrets.get("SENTINEL_CLIENT_ID", "")
SENTINEL_CLIENT_SECRET = st.secrets.get("SENTINEL_CLIENT_SECRET", "")
APIFY_TOKEN = st.secrets.get("APIFY_TOKEN", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ==========================================
# 🏛️ COMPLIANCE RULES (ILO + Local Laws 2024-2025)
# ==========================================
COMPLIANCE_RULES = {
    "Pakistan": {"min_wage": 32000, "max_hours": 48, "currency": "PKR"},
    "Bangladesh": {"min_wage": 12500, "max_hours": 48, "currency": "BDT"},
    "Vietnam": {"min_wage": 4960000, "max_hours": 48, "currency": "VND"},
    "India": {"min_wage": 18000, "max_hours": 48, "currency": "INR"},
    "USA": {"min_wage": 2080, "max_hours": 40, "currency": "USD"},
    "Turkey": {"min_wage": 17002, "max_hours": 45, "currency": "TRY"},
    "Brazil": {"min_wage": 1412, "max_hours": 44, "currency": "BRL"},
    # Default fallback for other countries
    "Default": {"min_wage": 0, "max_hours": 48, "currency": "USD"}
}

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

def db_delete_all(table):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    response = requests.delete(url, headers=HEADERS)
    return response.status_code == 204

def save_data(table, data):
    db_delete_all(table)
    for item in data:
        db_post(table, item)

# ==========================================
# DATA LOAD FUNCTIONS
# ==========================================
def load_factories():
    data = db_get("factories")
    if data:
        for item in data:
            if "country" not in item or not item["country"]:
                item["country"] = "Pakistan"
            if "ai_suggestion" not in item:
                item["ai_suggestion"] = "Green"
            if "ai_reason" not in item:
                item["ai_reason"] = "✅ No violations detected."
            if "human_override" not in item:
                item["human_override"] = False
            if "history" not in item:
                item["history"] = []
        return data
    return [{"id": 1, "name": "Saga Sports", "status": "Green", "risk": "Low", "client": "Nike", "country": "Pakistan", "ai_suggestion": "Green", "ai_reason": "✅ No violations detected.", "human_override": False, "history": []}]

def save_factories(data):
    db_delete_all("factories")
    if not data:
        data = [{"id": 1, "name": "Saga Sports", "status": "Green", "risk": "Low", "client": "Nike", "country": "Pakistan", "ai_suggestion": "Green", "ai_reason": "✅ No violations detected.", "human_override": False, "history": []}]
    for item in data:
        if "id" not in item:
            item["id"] = len(data) + 1
        db_post("factories", item)

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
            if "country" not in item or not item["country"]:
                item["country"] = "Pakistan"
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
# 🧠 ULTIMATE DATA-DRIVEN AI ENGINE
# ==========================================
def ai_analyze_factory(factory_name, country="Pakistan", enable_news=False):
    risk_score = 0
    reasons = []
    name_lower = factory_name.lower()
    country_lower = country.lower()
    factory_location = None
    overpass_url = "https://overpass-api.de/api/interpreter"

    # --- 1. OPENSTREETMAP (Location + Water Proximity) ---
    try:
        query = f'[out:json];node["name"~"{factory_name}"]["industrial"](around:1000);out;'
        response = requests.get(overpass_url, params={'data': query}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('elements'):
                elem = data['elements'][0]
                if 'lat' in elem and 'lon' in elem:
                    factory_location = (elem['lat'], elem['lon'])
                    reasons.append(f"🌍 Location found (OSM).")
                    water_query = f'[out:json];node["water"](around:500,{elem["lat"]},{elem["lon"]});out;'
                    water_response = requests.get(overpass_url, params={'data': water_query}, timeout=10)
                    if water_response.status_code == 200 and water_response.json().get('elements'):
                        risk_score += 0.5
                        reasons.append("⚠️ Industrial location near water body (OSM).")
    except:
        pass

    # --- 2. REAL EPA ECHO API (USA - Fuzzy Matching) ---
    if country_lower in ["usa", "united states"]:
        try:
            encoded_name = urllib.parse.quote(factory_name)
            epa_url = f"https://echo.epa.gov/rest/ef/search?q={encoded_name}&fields=facility_name,state,city,regulated_by,active_inspections_count,penalties,enforcement_actions"
            response = requests.get(epa_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and data.get('data') and data['data']:
                    best_match = None
                    best_score = 0
                    for facility in data['data']:
                        fac_name = facility.get('facility_name', '').lower()
                        if factory_name.lower() in fac_name or fac_name in factory_name.lower():
                            best_match = facility
                            break
                        name_parts = factory_name.lower().split()
                        match_count = sum(1 for part in name_parts if part in fac_name)
                        if match_count > best_score:
                            best_score = match_count
                            best_match = facility
                    if best_match:
                        if best_match.get('active_inspections_count', 0) > 0:
                            risk_score += 3
                            reasons.append(f"⚠️ Active EPA inspections found (USA ECHO).")
                        if best_match.get('penalties', 0) > 0:
                            risk_score += 2
                            reasons.append(f"⚠️ EPA penalties recorded (USA ECHO).")
                        if best_match.get('enforcement_actions', 0) > 0:
                            risk_score += 2
                            reasons.append(f"⚠️ EPA enforcement actions recorded (USA ECHO).")
                        if best_match.get('city'):
                            reasons.append(f"📍 Location: {best_match.get('city')}, {best_match.get('state')} (EPA).")
        except:
            pass

    # --- 3. ILO / WORLD BANK COUNTRY RISK ---
    high_risk_countries = ["bangladesh", "vietnam", "pakistan", "turkey", "brazil", "indonesia", "ethiopia", "cambodia", "myanmar"]
    medium_risk_countries = ["thailand", "malaysia", "philippines", "sri lanka", "egypt", "morocco", "colombia", "peru"]
    
    if country_lower in high_risk_countries:
        risk_score += 1
        reasons.append(f"⚠️ High industrial risk country ({country}) - ILO/World Bank.")
    elif country_lower in medium_risk_countries:
        risk_score += 0.5
        reasons.append(f"🟡 Medium industrial risk country ({country}) - ILO/World Bank.")

    # --- 4. LOCAL RULES (EXTREME CASES) ---
    if "tannery" in name_lower or "leather" in name_lower:
        risk_score += 2
        reasons.append("🔴 Local Rule: Tannery detected.")
    if "waste" in name_lower or "dump" in name_lower:
        risk_score += 2
        reasons.append("🔴 Local Rule: Waste dumping detected.")
    if "dye" in name_lower or "chemical" in name_lower:
        risk_score += 1
        reasons.append("🟡 Local Rule: Chemical usage detected.")

    # --- 5. SMART NEWS SCANNER (Optional) ---
    if enable_news:
        try:
            query = f"{factory_name} {country} violation pollution child labor fine"
            url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                content = response.text.lower()
                if factory_name.lower() in content:
                    negative_keywords = ['violation', 'pollution', 'fine', 'child labor', 'illegal']
                    for word in negative_keywords:
                        if word in content:
                            risk_score += 1
                            reasons.append(f"🟡 News mentions '{word}' for this factory.")
                            break
        except:
            pass

    # --- 6. APIFY ILAB (Labor - Real Data) ---
    if APIFY_TOKEN:
        try:
            apify_url = "https://api.apify.com/v2/acts/ilab~ilab-supply-chain/runs"
            headers = {"Authorization": f"Bearer {APIFY_TOKEN}", "Content-Type": "application/json"}
            payload = {"country": country, "goods": "textile", "waitForFinish": 15}
            response = requests.post(apify_url, json=payload, headers=headers, timeout=20)
            if response.status_code == 200:
                data = response.json()
                if data and data.get('data'):
                    labor_data = data['data']
                    if labor_data.get('childLabor', False) or labor_data.get('forcedLabor', False):
                        risk_score += 3
                        reasons.append(f"⚠️ Child/Forced labor flagged (ILAB).")
        except:
            pass

    # --- 7. SENTINEL HUB (Satellite - Real) ---
    if SENTINEL_CLIENT_ID and SENTINEL_CLIENT_SECRET and factory_location:
        try:
            lat, lon = factory_location
            auth_url = "https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token"
            auth_data = {
                "client_id": SENTINEL_CLIENT_ID,
                "client_secret": SENTINEL_CLIENT_SECRET,
                "grant_type": "client_credentials"
            }
            auth_response = requests.post(auth_url, data=auth_data, timeout=10)
            if auth_response.status_code == 200:
                token = auth_response.json().get('access_token')
                if token:
                    bbox = f"{lon-0.01},{lat-0.01},{lon+0.01},{lat+0.01}"
                    wms_url = (
                        f"https://services.sentinel-hub.com/ogc/wms/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                        f"?SERVICE=WMS&REQUEST=GetMap&FORMAT=image/png&TRANSPARENT=TRUE"
                        f"&VERSION=1.3.0&LAYERS=TRUE-COLOR&WIDTH=512&HEIGHT=512&CRS=EPSG:4326"
                        f"&BBOX={bbox}"
                    )
                    img_response = requests.head(wms_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
                    if img_response.status_code == 200:
                        risk_score += 1
                        reasons.append("🛰️ Satellite image retrieved.")
        except:
            pass

    # --- 8. COMPLIANCE RULES (Wage & Hours Check) ---
    # This will be applied when CSV is uploaded, not here

    # --- 9. FINAL DECISION ---
    if risk_score >= 3:
        final_status = "Red"
    elif risk_score >= 0.5:
        final_status = "Yellow"
    else:
        final_status = "Green"

    if not reasons:
        final_status = "Green"
        reasons = ["✅ No violations detected in public records. All clear."]

    final_reason = f"[Score: {round(risk_score, 1)}] " + " | ".join(reasons)
    return final_status, final_reason

# ==========================================
# 📄 PDF REPORT GENERATOR
# ==========================================
def generate_pdf_report(factory_name, country, status, reason, score, rules_check=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="E4GRID - Compliance Report", ln=1, align='C')
    pdf.ln(10)
    
    # Factory Details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, txt="Factory Name:", ln=0)
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, txt=factory_name, ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, txt="Country:", ln=0)
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, txt=country, ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, txt="Risk Status:", ln=0)
    pdf.set_font("Arial", size=12)
    color = "Red" if status == "Red" else "Yellow" if status == "Yellow" else "Green"
    pdf.cell(100, 10, txt=f"{status} ({color})", ln=1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, txt="Risk Score:", ln=0)
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, txt=str(score), ln=1)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Reason(s):", ln=1)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt=reason)
    
    # Compliance Rules Check
    if rules_check:
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt="Compliance Rules Check:", ln=1)
        pdf.set_font("Arial", size=10)
        for check in rules_check:
            pdf.multi_cell(0, 6, txt=f"• {check}")
    
    pdf.ln(10)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 5, txt=f"Generated by E4GRID on {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1)
    pdf.cell(0, 5, txt="This is an AI-generated report. Human verification recommended.", ln=1)
    
    return pdf.output(dest='S').encode('latin1')

def download_pdf(factory_name, country, status, reason, score, rules_check=None):
    pdf_data = generate_pdf_report(factory_name, country, status, reason, score, rules_check)
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{factory_name.replace(" ", "_")}_compliance_report.pdf">📥 Download PDF Report</a>'
    return href

# ==========================================
# ⚖️ COMPLIANCE RULES CHECK (Payroll vs Attendance)
# ==========================================
def check_compliance_rules(country, payroll_df, attendance_df):
    """
    Check payroll vs attendance against country's rules
    Returns list of alerts
    """
    alerts = []
    rules = COMPLIANCE_RULES.get(country, COMPLIANCE_RULES["Default"])
    min_wage = rules.get("min_wage", 0)
    max_hours = rules.get("max_hours", 48)
    
    if not payroll_df.empty:
        # Check wages
        if "wage" in payroll_df.columns:
            below_min = payroll_df[payroll_df["wage"] < min_wage]
            if not below_min.empty:
                alerts.append(f"⚠️ {len(below_min)} workers paid below minimum wage ({rules['currency']} {min_wage}).")
    
    if not attendance_df.empty:
        # Check hours
        if "hours" in attendance_df.columns:
            over_hours = attendance_df[attendance_df["hours"] > max_hours]
            if not over_hours.empty:
                alerts.append(f"⚠️ {len(over_hours)} workers exceeded max working hours ({max_hours} hours/week).")
    
    return alerts

# ==========================================
# TIMELINE & TRACKING ID
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
# FILE UPLOAD
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
        .score-badge { font-weight: 600; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; }
    </style>
""", unsafe_allow_html=True)

DEMO_FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSf6dliM5l1-dg34Uj_4MWwbJOLDiI7DuUnDxG9M-gBdvYxNyA/viewform?usp=header"

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
                    "email": email, "country": country,
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
# ADMIN DASHBOARD
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

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📋 Reports", "🏭 Factories", "🏢 MNCs", "🌍 Agencies", "📜 Audit Logs", "🤖 AI Control", "⚖️ Compliance Rules"])
    
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
        st.subheader("🏭 Factory Compliance (Data-Driven AI)")
        total_f = len(st.session_state.factories)
        green = len([f for f in st.session_state.factories if f['status'] == 'Green'])
        yellow = len([f for f in st.session_state.factories if f['status'] == 'Yellow'])
        red = len([f for f in st.session_state.factories if f['status'] == 'Red'])
        st.metric("📊 Health", f"{green} 🟢, {yellow} 🟡, {red} 🔴 out of {total_f}")
        
        # AI Settings
        st.divider()
        st.subheader("🤖 AI Settings")
        if "enable_news" not in st.session_state:
            st.session_state.enable_news = False
        
        st.toggle("Enable Smart News Scanner (Exact Match Only)", value=st.session_state.enable_news, key="news_toggle")
        st.session_state.enable_news = st.session_state.news_toggle
        st.caption("✅ Current Mode: " + ("🟢 News ON" if st.session_state.enable_news else "🔴 News OFF (Data-Driven)"))
        
        with st.expander("📤 Bulk Upload CSV - Payroll & Attendance"):
            st.caption("Upload a CSV with columns: `worker_id, wage, hours, name`")
            uploaded_file = st.file_uploader("Upload CSV", type=['csv'], key="bulk_csv")
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.dataframe(df.head(10))
                    
                    # Compliance check button
                    if st.button("🔍 Check Compliance Rules", key="compliance_check_btn"):
                        country = st.selectbox("Select Country for Rules", list(COMPLIANCE_RULES.keys()), key="compliance_country")
                        alerts = check_compliance_rules(country, df, df)
                        if alerts:
                            st.error("🚨 Compliance Violations Found:")
                            for alert in alerts:
                                st.write(f"- {alert}")
                        else:
                            st.success("✅ All workers are compliant with minimum wage and working hours.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        st.divider()
        
        col_del1, col_del2 = st.columns([1,3])
        with col_del1:
            del_id = st.number_input("Delete ID", min_value=1, step=1, key="del_fact_id_global")
            if st.button("🗑️ Delete", key="del_fact_btn_global"):
                found = any(f["id"] == del_id for f in st.session_state.factories)
                if found:
                    st.session_state.factories = [f for f in st.session_state.factories if f["id"] != del_id]
                    save_all()
                    log_audit(f"Factory Deleted: ID {del_id}")
                    st.success(f"✅ Deleted ID {del_id}!")
                    st.rerun()
                else:
                    st.error(f"❌ ID {del_id} not found.")
        with col_del2: st.caption("Tip: Check the ID from the list below.")
        st.divider()
        
        for idx, factory in enumerate(st.session_state.factories):
            country = factory.get("country", "Pakistan")
            with st.expander(f"🏭 {factory['name']} ({country}) - Status: {factory['status']}"):
                col1, col2, col3 = st.columns([2,1,1])
                with col1:
                    st.write(f"**Client:** {factory['client']}")
                    st.write(f"**Country:** {country}")
                    st.write(f"**Current Status:** {factory['status']}")
                    ai_suggestion = factory.get('ai_suggestion','Green')
                    ai_reason = factory.get('ai_reason','No reason.')
                    score_display = ai_reason.split(']')[0].replace('[Score: ', '') if '[Score:' in ai_reason else '0'
                    st.markdown(f"""<div class="ai-suggestion-box">
                        <span class="ai-badge">🤖 AI SUGGESTION</span>
                        <span style="color:#3b82f6;font-weight:600;margin-left:10px;">{ai_suggestion}</span>
                        <span class="score-badge" style="background:#1e293b;color:#94a3b8;margin-left:10px;">Score: {score_display}</span>
                        <div class="ai-reason-text">📌 {ai_reason.replace('[Score: '+score_display+'] ', '') if '[Score:' in ai_reason else ai_reason}</div>
                    </div>""", unsafe_allow_html=True)
                    if factory.get('human_override', False):
                        st.markdown(f"""<div style="background:rgba(251,191,36,0.1);border-left:4px solid #fbbf24;padding:10px;border-radius:8px;margin:5px 0;">
                            <span class="boss-badge">👑 BOSS VERIFIED</span>
                            <span style="color:#fbbf24;margin-left:10px;">You manually approved this.</span>
                        </div>""", unsafe_allow_html=True)
                    
                    # PDF Download Button
                    rules_check = check_compliance_rules(country, pd.DataFrame(), pd.DataFrame())
                    pdf_link = download_pdf(
                        factory['name'], 
                        country, 
                        factory['status'], 
                        ai_reason, 
                        score_display,
                        rules_check if rules_check else None
                    )
                    st.markdown(pdf_link, unsafe_allow_html=True)
                    
                with col2:
                    current_status_index = ["Green","Yellow","Red"].index(factory['status'])
                    new_status = st.selectbox("Override", ["Green","Yellow","Red"], index=current_status_index, key=f"fact_status_override_{factory['id']}_{idx}")
                    if new_status != factory['status']:
                        factory['status'] = new_status
                        factory['human_override'] = True
                        if 'history' not in factory: factory['history'] = []
                        factory['history'].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Boss Override")
                        save_all()
                        log_audit(f"Boss changed {factory['name']} to {new_status}")
                        st.rerun()
                with col3:
                    if st.button(f"🔄 AI Scan", key=f"ai_scan_btn_{factory['id']}_{idx}"):
                        suggestion, reason = ai_analyze_factory(factory['name'], country, st.session_state.enable_news)
                        factory['ai_suggestion'] = suggestion
                        factory['ai_reason'] = reason
                        if not factory.get('human_override', False):
                            factory['status'] = suggestion
                        if 'history' not in factory: factory['history'] = []
                        factory['history'].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - AI Scan")
                        save_all()
                        log_audit(f"AI Scanned {factory['name']}")
                        st.rerun()
                if factory.get('history'):
                    with st.expander("📜 History"):
                        for h in factory['history'][-5:]: st.caption(f"- {h}")
        
        st.divider()
        st.subheader("➕ Add New Factory (Data-Driven AI)")
        col_a, col_b = st.columns(2)
        with col_a:
            new_name = st.text_input("Factory Name", key="new_fact_name_global")
            new_client = st.selectbox("Assign to MNC", list(st.session_state.mnc_clients.keys()), key="new_fact_client_global")
            new_country = st.text_input("Country (e.g., Bangladesh, Vietnam, USA)", "Pakistan", key="new_fact_country_global")
        with col_b:
            new_status = st.selectbox("Initial Status", ["Green","Yellow","Red"], key="new_fact_status_global")
            if st.button("Add with AI", key="add_fact_global_btn"):
                if new_name:
                    suggestion, reason = ai_analyze_factory(new_name, new_country, st.session_state.enable_news)
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
                        "history": [f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Added"]
                    }
                    st.session_state.factories.append(new_factory)
                    save_all()
                    log_audit(f"Factory Added: {new_name}")
                    st.success(f"✅ Added! AI Suggests: {suggestion}")
                    st.rerun()

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
        if st.button("🔄 Run Global AI Scan on ALL Factories", use_container_width=True):
            for factory in st.session_state.factories:
                country = factory.get("country", "Pakistan")
                suggestion, reason = ai_analyze_factory(factory['name'], country, st.session_state.enable_news)
                factory['ai_suggestion'] = suggestion; factory['ai_reason'] = reason
                if not factory.get('human_override', False): factory['status'] = suggestion
                if 'history' not in factory: factory['history'] = []
                factory['history'].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - Bulk AI Scan")
            save_all(); log_audit("Bulk AI Scan Executed"); st.success("✅ All factories scanned!"); st.rerun()
        st.info("💡 AI uses Data-Driven Intelligence: EPA + ILO + OSM + Sentinel + Smart News.")

    # --- TAB 7: COMPLIANCE RULES ---
    with tab7:
        st.subheader("⚖️ Global Compliance Rules (ILO + Local Laws 2024-2025)")
        st.caption("These rules are automatically applied when checking payroll/attendance data.")
        
        rules_df = pd.DataFrame([
            {"Country": k, "Min Wage": v["min_wage"], "Max Hours": v["max_hours"], "Currency": v["currency"]}
            for k, v in COMPLIANCE_RULES.items()
        ])
        st.dataframe(rules_df, use_container_width=True)
        
        st.divider()
        st.subheader("📋 Manual Compliance Check (Single Factory)")
        col1, col2 = st.columns(2)
        with col1:
            check_country = st.selectbox("Country", list(COMPLIANCE_RULES.keys()), key="check_country")
            wage = st.number_input("Monthly Wage", min_value=0, value=30000, key="check_wage")
        with col2:
            hours = st.number_input("Weekly Hours", min_value=0, value=40, key="check_hours")
            if st.button("Check Compliance", key="check_compliance_btn"):
                rules = COMPLIANCE_RULES.get(check_country, COMPLIANCE_RULES["Default"])
                alerts = []
                if wage < rules["min_wage"]:
                    alerts.append(f"⚠️ Wage ({rules['currency']} {wage}) is below minimum ({rules['currency']} {rules['min_wage']})")
                if hours > rules["max_hours"]:
                    alerts.append(f"⚠️ Hours ({hours}) exceed maximum ({rules['max_hours']} hours/week)")
                if alerts:
                    st.error("🚨 Violations Found:")
                    for alert in alerts:
                        st.write(f"- {alert}")
                else:
                    st.success("✅ All rules satisfied.")

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
