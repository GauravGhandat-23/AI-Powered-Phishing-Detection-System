<<<<<<< HEAD
import pandas as pd
import numpy as np
import re
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib
from nltk.corpus import stopwords
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import time

# Download NLTK data
import nltk
nltk.download('stopwords')

# Load stopwords
STOPWORDS = set(stopwords.words("english"))

# Function to clean and process the email body
def clean_email_body(email_body):
    # Removing non-alphabetic characters
    email_body = re.sub(r'[^a-zA-Z\s]', '', email_body)
    # Lowercasing and removing stopwords
    email_body = ' '.join([word.lower() for word in email_body.split() if word.lower() not in STOPWORDS])
    return email_body

def extract_url_features(email_body):
    urls = re.findall(r'(https?://[^\s]+)', email_body)
    features = []

    for url in urls:
        parsed_url = urlparse(url)

        # Ensure numeric values are appended to the features list
        domain_length = len(parsed_url.netloc)  # Length of the domain
        path_length = len(parsed_url.path)  # Length of the path
        protocol = parsed_url.scheme  # Protocol (http/https)

        features.append(domain_length)
        features.append(path_length)

        # Check if the protocol is valid and append to features
        if protocol in ['http', 'https']:
            features.append(1)
        else:
            features.append(0)

        # Try to fetch the URL to check its status code
        try:
            response = requests.get(url, timeout=3)
            status_code = response.status_code
            features.append(status_code)
        except:
            features.append(0)  # If URL is not reachable, append 0

    # Return the mean of numeric values in the features list or 0 if empty
    return np.mean([f for f in features if isinstance(f, (int, float))]) if features else 0

# ----------------------------------------------------------------------------------
# Fraud risk heuristics (keyword/pattern based — no external calls, runs locally)
# ----------------------------------------------------------------------------------
FRAUD_SIGNAL_CATEGORIES = {
    "Advance-Fee / Inheritance Scam": [
        "inheritance", "next of kin", "unclaimed fund", "beneficiary", "estate of",
        "million dollars", "lottery winner", "claim your prize", "processing fee",
        "clearance fee", "diplomatic courier"
    ],
    "Financial / Payment Urgency": [
        "wire transfer", "bank account", "routing number", "gift card", "bitcoin",
        "crypto wallet", "western union", "moneygram", "urgent payment", "overdue invoice",
        "account suspended", "account will be closed", "verify your account"
    ],
    "Credential / Identity Harvesting": [
        "social security number", "ssn", "date of birth", "login credentials",
        "confirm your password", "update your billing", "verify your identity",
        "one time password", "otp code"
    ],
    "Pressure / Intimidation Tactics": [
        "act now", "immediate action required", "final notice", "legal action",
        "your account has been compromised", "within 24 hours", "failure to comply",
        "as soon as possible"
    ],
}

def extract_fraud_signals(email_body):
    """
    Lightweight, local, rule-based scan for common social-engineering / fraud
    language patterns. Returns an overall risk score (0-100) plus the specific
    categories and keyword hits that were matched, for analyst transparency.
    """
    text = email_body.lower()
    matched_categories = {}
    total_hits = 0

    for category, keywords in FRAUD_SIGNAL_CATEGORIES.items():
        hits = [kw for kw in keywords if kw in text]
        if hits:
            matched_categories[category] = hits
            total_hits += len(hits)

    # Extra signal: unusually high count of currency/urgency punctuation
    exclamation_density = text.count('!') / max(len(text.split()), 1)
    currency_mentions = len(re.findall(r'(\$|usd|inr|₹|€|eur)\s?\d', text))

    score = min(100, (total_hits * 12) + (currency_mentions * 8) + (exclamation_density * 100))

    if score >= 60:
        risk_level = "High"
    elif score >= 25:
        risk_level = "Medium"
    elif score > 0:
        risk_level = "Low"
    else:
        risk_level = "None"

    return {
        "score": round(score, 1),
        "risk_level": risk_level,
        "categories": matched_categories,
        "currency_mentions": currency_mentions,
    }


# Function to load and train the model
def train_model(data):
    # Clean and process email bodies
    data['cleaned_body'] = data['email_body'].apply(clean_email_body)
    data['url_features'] = data['email_body'].apply(extract_url_features)

    X = pd.concat([data['cleaned_body'], data['url_features']], axis=1)
    X.columns = ['email_body', 'url_features']
    y = data['label']

    # Use CountVectorizer for email body and concatenate URL features
    body_vectorizer = CountVectorizer()
    model = make_pipeline(body_vectorizer, MultinomialNB())

    # Train the model
    model.fit(X['email_body'], y)

    # Save the trained model
    joblib.dump(model, 'phishing_model.pkl')

# Function to predict phishing
def predict_phishing(model, email_body):
    # Clean and process the email body and extract URL features
    cleaned_body = clean_email_body(email_body)
    url_features = extract_url_features(email_body)
    X = pd.DataFrame([[cleaned_body, url_features]], columns=['email_body', 'url_features'])

    # Predict using the trained model
    prediction = model.predict(X['email_body'])
    return 'Phishing' if prediction[0] == 1 else 'Safe'


# ----------------------------------------------------------------------------------
# STREAMLIT INTERFACE (UI ONLY — no logic above this line was changed)
# ----------------------------------------------------------------------------------

def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&family=Share+Tech+Mono&display=swap');

        html, body, [class*="css"] {
            font-family: 'JetBrains Mono', monospace;
        }

        :root {
            --bg-deep: #05080a;
            --bg-panel: #0b1116;
            --bg-panel-2: #0e161c;
            --neon-green: #00ff9d;
            --neon-cyan: #00e5ff;
            --neon-red: #ff2e63;
            --neon-amber: #ffb800;
            --grid-line: rgba(0, 255, 157, 0.07);
            --text-dim: #6b8a80;
        }

        .stApp {
            background:
                linear-gradient(var(--grid-line) 1px, transparent 1px),
                linear-gradient(90deg, var(--grid-line) 1px, transparent 1px),
                radial-gradient(circle at 15% 0%, #0d2620 0%, var(--bg-deep) 45%),
                var(--bg-deep);
            background-size: 34px 34px, 34px 34px, 100% 100%, 100%;
        }

        #MainMenu, footer, header {visibility: hidden;}

        .block-container {
            padding-top: 1.5rem;
            max-width: 1100px;
        }

        /* ---- Terminal header banner ---- */
        .term-banner {
            border: 1px solid rgba(0,255,157,0.35);
            background: linear-gradient(180deg, rgba(0,255,157,0.06), rgba(0,0,0,0));
            border-radius: 6px;
            padding: 18px 22px;
            margin-bottom: 22px;
            position: relative;
            box-shadow: 0 0 25px rgba(0,255,157,0.08), inset 0 0 40px rgba(0,255,157,0.03);
        }
        .term-banner::before {
            content: "● ● ●";
            position: absolute;
            top: 10px;
            left: 16px;
            color: #ff5f56;
            letter-spacing: 6px;
            font-size: 10px;
            opacity: 0.7;
        }
        .term-title {
            margin-top: 14px;
            font-size: 26px;
            font-weight: 800;
            letter-spacing: 1px;
            color: var(--neon-green);
            text-shadow: 0 0 12px rgba(0,255,157,0.5);
        }
        .term-sub {
            font-family: 'Share Tech Mono', monospace;
            color: var(--text-dim);
            font-size: 13px;
            margin-top: 4px;
            letter-spacing: 0.5px;
        }
        .blink-cursor::after {
            content: "█";
            color: var(--neon-green);
            animation: blink 1s steps(1) infinite;
            margin-left: 4px;
        }
        @keyframes blink { 50% { opacity: 0; } }

        /* ---- Status pill ---- */
        .status-row { display: flex; gap: 10px; margin-top: 12px; flex-wrap: wrap; }
        .pill {
            font-size: 11px;
            padding: 4px 10px;
            border-radius: 3px;
            border: 1px solid rgba(0,255,157,0.3);
            color: var(--neon-green);
            background: rgba(0,255,157,0.05);
            letter-spacing: 0.5px;
        }
        .pill.warn { color: var(--neon-amber); border-color: rgba(255,184,0,0.35); background: rgba(255,184,0,0.05); }
        .pill.err { color: var(--neon-red); border-color: rgba(255,46,99,0.35); background: rgba(255,46,99,0.05); }

        /* ---- Section labels ---- */
        .sec-label {
            font-size: 12px;
            letter-spacing: 2px;
            color: var(--neon-cyan);
            text-transform: uppercase;
            border-bottom: 1px solid rgba(0,229,255,0.2);
            padding-bottom: 6px;
            margin: 28px 0 14px 0;
            font-weight: 700;
        }
        .sec-label::before { content: "// "; color: var(--text-dim); }

        /* ---- Panels ---- */
        .panel {
            background: var(--bg-panel);
            border: 1px solid rgba(0,255,157,0.15);
            border-radius: 6px;
            padding: 18px 20px;
            margin-bottom: 16px;
        }

        /* ---- Streamlit widget overrides ---- */
        textarea, .stTextArea textarea {
            background-color: var(--bg-panel-2) !important;
            color: #d6ffe9 !important;
            border: 1px solid rgba(0,255,157,0.25) !important;
            font-family: 'JetBrains Mono', monospace !important;
            border-radius: 4px !important;
        }
        textarea:focus {
            border: 1px solid var(--neon-green) !important;
            box-shadow: 0 0 12px rgba(0,255,157,0.25) !important;
        }

        .stButton > button {
            background: linear-gradient(180deg, #0e2a22, #081a15);
            color: var(--neon-green);
            border: 1px solid var(--neon-green);
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            letter-spacing: 1px;
            padding: 10px 22px;
            text-transform: uppercase;
            font-size: 12px;
            transition: all 0.15s ease;
        }
        .stButton > button:hover {
            background: var(--neon-green);
            color: #001410;
            box-shadow: 0 0 20px rgba(0,255,157,0.55);
        }

        [data-testid="stFileUploader"] {
            background: var(--bg-panel-2);
            border: 1px dashed rgba(0,229,255,0.35);
            border-radius: 6px;
            padding: 10px;
        }

        [data-testid="stFileUploader"] label {
            color: var(--neon-cyan) !important;
        }

        /* ---- Result readouts ---- */
        .result-box {
            border-radius: 6px;
            padding: 18px 20px;
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 0.5px;
            margin-top: 14px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .result-safe {
            background: rgba(0,255,157,0.07);
            border: 1px solid var(--neon-green);
            color: var(--neon-green);
            box-shadow: 0 0 20px rgba(0,255,157,0.15);
        }
        .result-phish {
            background: rgba(255,46,99,0.08);
            border: 1px solid var(--neon-red);
            color: var(--neon-red);
            box-shadow: 0 0 20px rgba(255,46,99,0.2);
            animation: pulse-red 1.4s infinite;
        }
        @keyframes pulse-red {
            0%, 100% { box-shadow: 0 0 12px rgba(255,46,99,0.2); }
            50% { box-shadow: 0 0 28px rgba(255,46,99,0.45); }
        }

        .log-line {
            font-family: 'Share Tech Mono', monospace;
            font-size: 12px;
            color: var(--text-dim);
            margin-top: 8px;
        }
        .log-line span { color: var(--neon-green); }

        hr { border-color: rgba(0,255,157,0.12) !important; }

        /* ---- Tabs ---- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            border-bottom: 1px solid rgba(0,255,157,0.15);
        }
        .stTabs [data-baseweb="tab"] {
            background: var(--bg-panel-2);
            border: 1px solid rgba(0,255,157,0.12);
            border-bottom: none;
            border-radius: 4px 4px 0 0;
            color: var(--text-dim);
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            letter-spacing: 0.5px;
            padding: 8px 16px;
        }
        .stTabs [aria-selected="true"] {
            color: var(--neon-green) !important;
            border-color: rgba(0,255,157,0.4) !important;
            box-shadow: inset 0 -2px 0 var(--neon-green);
        }

        /* ---- Fraud risk gauge ---- */
        .gauge-wrap { margin-top: 10px; }
        .gauge-track {
            width: 100%;
            height: 10px;
            background: rgba(255,255,255,0.06);
            border-radius: 5px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.08);
        }
        .gauge-fill {
            height: 100%;
            border-radius: 5px;
            transition: width 0.5s ease;
        }
        .gauge-fill.low { background: linear-gradient(90deg, var(--neon-green), #6fffcf); }
        .gauge-fill.medium { background: linear-gradient(90deg, var(--neon-amber), #ffd76a); }
        .gauge-fill.high { background: linear-gradient(90deg, var(--neon-red), #ff7a9c); }
        .gauge-fill.none { background: rgba(255,255,255,0.15); }
        .gauge-label {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: var(--text-dim);
            margin-top: 6px;
            font-family: 'Share Tech Mono', monospace;
        }

        /* ---- Fraud category chip ---- */
        .chip {
            display: inline-block;
            font-size: 11px;
            padding: 3px 9px;
            margin: 3px 4px 0 0;
            border-radius: 3px;
            border: 1px solid rgba(255,184,0,0.35);
            color: var(--neon-amber);
            background: rgba(255,184,0,0.06);
        }

        /* ---- Metric mini cards ---- */
        .metric-row { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 10px; }
        .metric-card {
            flex: 1;
            min-width: 140px;
            background: var(--bg-panel-2);
            border: 1px solid rgba(0,229,255,0.15);
            border-radius: 6px;
            padding: 12px 14px;
        }
        .metric-card .m-label {
            font-size: 10px;
            letter-spacing: 1px;
            color: var(--text-dim);
            text-transform: uppercase;
        }
        .metric-card .m-value {
            font-size: 20px;
            font-weight: 800;
            color: var(--neon-cyan);
            margin-top: 4px;
        }

        /* ---- Dataframe container ---- */
        [data-testid="stDataFrame"] {
            border: 1px solid rgba(0,255,157,0.15);
            border-radius: 6px;
        }
    </style>
    """, unsafe_allow_html=True)


def render_fraud_gauge(fraud_result):
    level_class = fraud_result["risk_level"].lower()
    st.markdown(f"""
    <div class="gauge-wrap">
        <div class="gauge-track">
            <div class="gauge-fill {level_class}" style="width:{fraud_result['score']}%;"></div>
        </div>
        <div class="gauge-label">
            <span>FRAUD RISK SCORE</span>
            <span>{fraud_result['score']}/100 — {fraud_result['risk_level'].upper()}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if fraud_result["categories"]:
        chips = "".join([f'<span class="chip">{cat} ({len(kws)})</span>' for cat, kws in fraud_result["categories"].items()])
        st.markdown(f'<div style="margin-top:10px;">{chips}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="log-line"><span>[OK]</span> No fraud/social-engineering keyword patterns matched.</div>', unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="Phishing Detection // SOC Console", page_icon="🛡️", layout="wide")
    inject_css()

    # ---- Terminal-style header banner ----
    st.markdown("""
    <div class="term-banner">
        <div class="term-title">🛡️ AI-POWERED PHISHING & FRAUD DETECTION SYSTEM<span class="blink-cursor"></span></div>
        <div class="term-sub">root@soc-console:~$ email_threat_analysis --module=nlp+url-heuristics</div>
        <div class="status-row">
            <span class="pill">● ENGINE: NAIVE-BAYES</span>
            <span class="pill">● FEATURES: NLP + URL</span>
            <span class="pill warn">● MODE: LIVE ANALYSIS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Display the logo (kept, styled inside a panel)
    try:
        st.image("logo.JPEG", width=700)
    except Exception:
        pass

    # ---- Model status ----
    st.markdown('<div class="sec-label">Model Status</div>', unsafe_allow_html=True)
    try:
        model = joblib.load('phishing_model.pkl')
        st.markdown("""
        <div class="panel">
            <span class="pill">✔ MODEL LOADED</span>
            <div class="log-line"><span>[OK]</span> phishing_model.pkl deserialized and ready for inference.</div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        model = None
        st.markdown("""
        <div class="panel">
            <span class="pill err">✖ NO MODEL FOUND</span>
            <div class="log-line"><span>[WARN]</span> No trained model detected. Upload a labeled dataset below to train one.</div>
        </div>
        """, unsafe_allow_html=True)

    # ---- Session state for scan history ----
    if "scan_history" not in st.session_state:
        st.session_state.scan_history = []

    tab_scan, tab_bulk, tab_history, tab_train = st.tabs(
        ["🔍 THREAT SCAN", "📦 BULK CSV SCAN", "🗂 SCAN HISTORY", "🧠 MODEL TRAINING"]
    )

    # ============================ TAB 1: Single email scan (phishing + fraud) ============================
    with tab_scan:
        st.markdown('<div class="sec-label">Email Analysis Console</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        email_input = st.text_area("PASTE RAW EMAIL BODY BELOW:", height=200, placeholder="> paste suspicious email content here...", key="single_email")
        scan_clicked = st.button("▶ RUN THREAT SCAN")
        st.markdown('</div>', unsafe_allow_html=True)

        if scan_clicked:
            if email_input:
                fraud_result = extract_fraud_signals(email_input)

                if model is not None:
                    with st.spinner("Analyzing payload... running NLP + URL heuristics..."):
                        time.sleep(0.4)
                        phishing_result = predict_phishing(model, email_input)
                else:
                    phishing_result = "Unknown"

                # --- Phishing verdict ---
                if phishing_result == 'Phishing':
                    st.markdown("""
                    <div class="result-box result-phish">⚠ THREAT DETECTED — CLASSIFICATION: PHISHING</div>
                    <div class="log-line"><span>[ALERT]</span> Recommend quarantine and further header/URL inspection.</div>
                    """, unsafe_allow_html=True)
                elif phishing_result == 'Safe':
                    st.markdown("""
                    <div class="result-box result-safe">✔ NO PHISHING INDICATORS — CLASSIFICATION: SAFE</div>
                    <div class="log-line"><span>[OK]</span> No indicators of phishing found in this sample.</div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="result-box result-phish">✖ NO MODEL LOADED — PHISHING CHECK SKIPPED</div>
                    """, unsafe_allow_html=True)

                # --- Fraud risk gauge ---
                st.markdown('<div class="sec-label">Fraud Risk Assessment</div>', unsafe_allow_html=True)
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                render_fraud_gauge(fraud_result)
                st.markdown('</div>', unsafe_allow_html=True)

                # --- Combined metrics row ---
                url_feat = extract_url_features(email_input)
                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-card"><div class="m-label">Phishing Verdict</div><div class="m-value">{phishing_result}</div></div>
                    <div class="metric-card"><div class="m-label">Fraud Risk</div><div class="m-value">{fraud_result['risk_level']}</div></div>
                    <div class="metric-card"><div class="m-label">URL Signal Score</div><div class="m-value">{round(url_feat, 1)}</div></div>
                </div>
                """, unsafe_allow_html=True)

                # --- Log to history ---
                st.session_state.scan_history.append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "email_snippet": (email_input[:80] + "...") if len(email_input) > 80 else email_input,
                    "phishing_verdict": phishing_result,
                    "fraud_risk_score": fraud_result["score"],
                    "fraud_risk_level": fraud_result["risk_level"],
                    "url_signal_score": round(url_feat, 1),
                })
            else:
                st.markdown("""
                <div class="log-line"><span>[WARN]</span> No input detected. Paste an email body before running the scan.</div>
                """, unsafe_allow_html=True)

    # ============================ TAB 2: Bulk CSV scan ============================
    with tab_bulk:
        st.markdown('<div class="sec-label">Bulk Email Batch Scan</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.write("Upload a CSV with an `email_body` column to run phishing + fraud risk scoring across many emails at once.")
        bulk_file = st.file_uploader("SELECT BATCH FILE (.csv)", type="csv", key="bulk_csv")
        run_bulk = st.button("▶ RUN BATCH SCAN")
        st.markdown('</div>', unsafe_allow_html=True)

        if run_bulk:
            if bulk_file is not None:
                bulk_data = pd.read_csv(bulk_file)
                if 'email_body' in bulk_data.columns:
                    with st.spinner(f"Scanning {len(bulk_data)} emails..."):
                        results = []
                        for body in bulk_data['email_body'].astype(str):
                            fr = extract_fraud_signals(body)
                            verdict = predict_phishing(model, body) if model is not None else "Unknown"
                            results.append({
                                "email_snippet": (body[:80] + "...") if len(body) > 80 else body,
                                "phishing_verdict": verdict,
                                "fraud_risk_score": fr["score"],
                                "fraud_risk_level": fr["risk_level"],
                            })
                        results_df = pd.DataFrame(results)
                    st.markdown('<div class="log-line"><span>[OK]</span> Batch scan complete.</div>', unsafe_allow_html=True)
                    st.dataframe(results_df, use_container_width=True)
                    csv_out = results_df.to_csv(index=False).encode('utf-8')
                    st.download_button("⬇ DOWNLOAD RESULTS (.csv)", csv_out, "batch_scan_results.csv", "text/csv")
                else:
                    st.markdown('<div class="log-line"><span>[ERROR]</span> CSV must contain an "email_body" column.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="log-line"><span>[WARN]</span> Please upload a CSV file first.</div>', unsafe_allow_html=True)

    # ============================ TAB 3: Scan history ============================
    with tab_history:
        st.markdown('<div class="sec-label">Session Scan History</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        if st.session_state.scan_history:
            hist_df = pd.DataFrame(st.session_state.scan_history)
            st.dataframe(hist_df, use_container_width=True)

            total = len(hist_df)
            phishing_count = (hist_df["phishing_verdict"] == "Phishing").sum()
            high_fraud_count = (hist_df["fraud_risk_level"] == "High").sum()
            st.markdown(f"""
            <div class="metric-row">
                <div class="metric-card"><div class="m-label">Total Scans</div><div class="m-value">{total}</div></div>
                <div class="metric-card"><div class="m-label">Phishing Flags</div><div class="m-value">{phishing_count}</div></div>
                <div class="metric-card"><div class="m-label">High Fraud Risk</div><div class="m-value">{high_fraud_count}</div></div>
            </div>
            """, unsafe_allow_html=True)

            csv_hist = hist_df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇ EXPORT HISTORY (.csv)", csv_hist, "scan_history.csv", "text/csv")
            if st.button("🗑 CLEAR HISTORY"):
                st.session_state.scan_history = []
                st.rerun()
        else:
            st.markdown('<div class="log-line"><span>[INFO]</span> No scans recorded yet this session.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ============================ TAB 4: Model training ============================
    with tab_train:
        st.markdown('<div class="sec-label">Model Training // Optional</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.write("Upload a labeled CSV (`email_body`, `label`) to retrain the detection engine.")
        uploaded_file = st.file_uploader("SELECT DATASET (.csv)", type="csv", key="train_csv")

        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)
            if 'email_body' in data.columns and 'label' in data.columns:
                st.markdown('<div class="log-line"><span>[INFO]</span> Dataset validated. Initiating training sequence...</div>', unsafe_allow_html=True)
                with st.spinner("Training model on uploaded dataset..."):
                    train_model(data)
                st.markdown("""
                <div class="result-box result-safe">✔ MODEL TRAINED & SAVED SUCCESSFULLY</div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="log-line"><span>[ERROR]</span> CSV must contain "email_body" and "label" columns.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == '__main__':
    main()
=======
import pandas as pd
import numpy as np
import re
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib
from nltk.corpus import stopwords
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# Download NLTK data
import nltk
nltk.download('stopwords')

# Load stopwords
STOPWORDS = set(stopwords.words("english"))

# Function to clean and process the email body
def clean_email_body(email_body):
    # Removing non-alphabetic characters
    email_body = re.sub(r'[^a-zA-Z\s]', '', email_body)
    # Lowercasing and removing stopwords
    email_body = ' '.join([word.lower() for word in email_body.split() if word.lower() not in STOPWORDS])
    return email_body

def extract_url_features(email_body):
    urls = re.findall(r'(https?://[^\s]+)', email_body)
    features = []
    
    for url in urls:
        parsed_url = urlparse(url)
        
        # Ensure numeric values are appended to the features list
        domain_length = len(parsed_url.netloc)  # Length of the domain
        path_length = len(parsed_url.path)  # Length of the path
        protocol = parsed_url.scheme  # Protocol (http/https)
        
        features.append(domain_length)
        features.append(path_length)
        
        # Check if the protocol is valid and append to features
        if protocol in ['http', 'https']:
            features.append(1)
        else:
            features.append(0)
        
        # Try to fetch the URL to check its status code
        try:
            response = requests.get(url, timeout=3)
            status_code = response.status_code
            features.append(status_code)
        except:
            features.append(0)  # If URL is not reachable, append 0
    
    # Return the mean of numeric values in the features list or 0 if empty
    return np.mean([f for f in features if isinstance(f, (int, float))]) if features else 0

# Function to load and train the model
def train_model(data):
    # Clean and process email bodies
    data['cleaned_body'] = data['email_body'].apply(clean_email_body)
    data['url_features'] = data['email_body'].apply(extract_url_features)

    X = pd.concat([data['cleaned_body'], data['url_features']], axis=1)
    X.columns = ['email_body', 'url_features']
    y = data['label']

    # Use CountVectorizer for email body and concatenate URL features
    body_vectorizer = CountVectorizer()
    model = make_pipeline(body_vectorizer, MultinomialNB())

    # Train the model
    model.fit(X['email_body'], y)
    
    # Save the trained model
    joblib.dump(model, 'phishing_model.pkl')

# Function to predict phishing
def predict_phishing(model, email_body):
    # Clean and process the email body and extract URL features
    cleaned_body = clean_email_body(email_body)
    url_features = extract_url_features(email_body)
    X = pd.DataFrame([[cleaned_body, url_features]], columns=['email_body', 'url_features'])
    
    # Predict using the trained model
    prediction = model.predict(X['email_body'])
    return 'Phishing' if prediction[0] == 1 else 'Safe'

# Streamlit interface
def main():
    # Display the logo
    st.image("logo.JPEG", width=700)  # Adjust the width as needed
    st.title("AI-Powered Phishing Detection System")
    
    # Load trained model if available
    try:
        model = joblib.load('phishing_model.pkl')
        st.write("Model loaded successfully!")
    except:
        st.write("No trained model found. Please train the model first.")
    
    # Email Input
    email_input = st.text_area("Enter the Email Body to Check:", height=200)
    
    if st.button("Check Phishing"):
        if email_input:
            result = predict_phishing(model, email_input)
            st.write(f"Prediction: {result}")
        else:
            st.write("Please enter an email body for analysis.")
            
    # Upload email dataset for training the model
    st.subheader("Train the Model (Optional)")
    uploaded_file = st.file_uploader("Choose a CSV file with email data", type="csv")
    
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        if 'email_body' in data.columns and 'label' in data.columns:
            st.write("Training the model with the uploaded data...")
            train_model(data)
            st.write("Model trained and saved successfully!")

if __name__ == '__main__':
    main()
>>>>>>> 72fd10d36626e80342aa047757a65096980cb9a1
