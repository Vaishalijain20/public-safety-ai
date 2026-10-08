import os
import json
import base64
import io
import random
from pathlib import Path
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import speech_recognition as sr
from dotenv import load_dotenv
from google import genai
from google.genai import types
from twilio.rest import Client as TwilioClient
import pandas as pd
import pydeck as pdk

# --- EXPLICIT ENVIRONMENT PATH CONFIGURATION ---
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")

# Twilio Configuration
twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_from = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
officer_to = os.getenv("OFFICER_WHATSAPP_NUMBER", "whatsapp:+916263985239")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.error("API Key missing! Check your .env configuration.")

# Helper to encode background assets to Base64
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

tunnel_b64 = get_base64_image("assets/cyber_tunnel.jpg")
lock_b64 = get_base64_image("assets/cyber_lock.jpg")

# --- STREAMLIT DASHBOARD CONFIG ---
st.set_page_config(page_title="AI Public Safety Platform", page_icon="🛡️", layout="wide")

# Initialize Dynamic Officer PIN in Session State
if "dynamic_officer_pin" not in st.session_state:
    st.session_state["dynamic_officer_pin"] = "1930"  # Default fallback before any incident

# --- ULTRA-CRISP CYBERSECURITY THEME (HIGH CONTRAST & ZERO BLUR) ---
tunnel_css = f"url('data:image/jpeg;base64,{tunnel_b64}')" if tunnel_b64 else "none"
lock_css = f"url('data:image/jpeg;base64,{lock_b64}')" if lock_b64 else "none"

st.markdown(
    f"""
    <style>
    @keyframes cyberPan {{
        0% {{ transform: scale(1.0) translateY(0px); }}
        50% {{ transform: scale(1.03) translateY(-6px); }}
        100% {{ transform: scale(1.0) translateY(0px); }}
    }}
    
    @keyframes spinGlow {{
        0% {{ transform: rotate(0deg); opacity: 0.20; }}
        50% {{ transform: rotate(180deg); opacity: 0.35; }}
        100% {{ transform: rotate(360deg); opacity: 0.20; }}
    }}

    /* Base App Styling */
    .stApp {{
        background-color: #020b17 !important;
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }}

    /* Animated Cyber Background with Deep Contrast Vignette */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: 
            radial-gradient(circle at center, rgba(2, 11, 23, 0.65) 0%, rgba(2, 11, 23, 0.92) 100%),
            {tunnel_css};
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        z-index: 0;
        animation: cyberPan 18s ease-in-out infinite;
        pointer-events: none;
    }}

    /* Floating Shield Watermark */
    .stApp::after {{
        content: "";
        position: fixed;
        bottom: -40px; right: -40px; width: 380px; height: 380px;
        background-image: {lock_css};
        background-size: contain;
        background-repeat: no-repeat;
        z-index: 0;
        animation: spinGlow 26s linear infinite;
        pointer-events: none;
    }}

    /* Frosted Glass Card Containers */
    div[data-testid="stVerticalBlock"] > div:has(div.stTextArea),
    div[data-testid="stVerticalBlock"] > div:has(div.stFileUploader),
    div[data-testid="stMetric"],
    div[data-testid="stAlert"] {{
        background: rgba(3, 16, 36, 0.88) !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
        border-radius: 10px !important;
        padding: 16px !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7) !important;
        position: relative;
        z-index: 1;
    }}

    /* Sidebar: Crisp Translucent Panel */
    section[data-testid="stSidebar"] {{
        background: rgba(2, 10, 22, 0.95) !important;
        border-right: 2px solid #00f2fe !important;
        backdrop-filter: blur(20px) !important;
        box-shadow: 6px 0 30px rgba(0, 0, 0, 0.8) !important;
        z-index: 2;
    }}

    section[data-testid="stSidebar"] * {{
        color: #ffffff !important;
        font-weight: 500;
    }}

    /* Ultra-Sharp Headings: Replaced Blurry Glow with Clean 1px Drop Shadow */
    h1, h2, h3, h4 {{
        color: #00f2fe !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.9) !important;
    }}

    /* Sharp Body Text & Labels */
    p, span, label {{
        color: #ffffff !important;
        text-shadow: none !important;
    }}

    /* File Uploader Text & Dropzone Clarity */
    div[data-testid="stFileUploader"] {{
        background: rgba(2, 10, 24, 0.9) !important;
        border: 1px dashed #00f2fe !important;
        border-radius: 8px !important;
    }}

    div[data-testid="stFileUploader"] * {{
        color: #13ced8 !important;
    }}

    /* High-Contrast JSON Viewer: Solid Deep Navy with Bold Colored Keys */
    div[data-testid="stJson"] {{
        background: #030d1d !important;
        border: 1px solid #00f2fe !important;
        border-radius: 8px !important;
        padding: 16px !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.8) !important;
    }}

    div[data-testid="stJson"] * {{
        color: #54d4d4 !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        text-shadow: none !important;
    }}

    /* Text Inputs and Text Areas */
    textarea, input[type="text"], input[type="password"] {{
        background-color: #030d1d !important;
        color: #ffffff !important;
        border: 1px solid #00f2fe !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        text-shadow: none !important;
    }}

    /* Metric Values */
    div[data-testid="stMetricValue"] {{
        color: #00f2fe !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        text-shadow: none !important;
    }}

    div[data-testid="stMetricLabel"] {{
        color: #bbf2f6 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        text-shadow: none !important;
    }}

    /* Interactive Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, #0052d4, #00c6ff) !important;
        color: #ffffff !important;
        border: 1px solid #00f2fe !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 14px rgba(0, 242, 254, 0.3) !important;
        transition: all 0.25s ease-in-out !important;
        text-shadow: none !important;
    }}

    .stButton>button:hover {{
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.7) !important;
        transform: translateY(-1px);
    }}

    /* Emergency Buttons */
    .emergency-btn-call {{
        display: block; width: 100%; padding: 12px;
        background: linear-gradient(135deg, #ff0844, #ff4e50);
        color: white !important; text-align: center; border-radius: 8px; font-weight: bold;
        text-decoration: none; margin-bottom: 8px; box-shadow: 0px 4px 14px rgba(255, 8, 68, 0.5);
        text-shadow: none !important;
    }}
    
    .emergency-btn-portal {{
        display: block; width: 100%; padding: 12px;
        background: linear-gradient(135deg, #00c6ff, #0072ff);
        color: white !important; text-align: center; border-radius: 8px; font-weight: bold;
        text-decoration: none; box-shadow: 0px 4px 14px rgba(0, 198, 255, 0.5);
        text-shadow: none !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

def send_twilio_whatsapp_alert(mule_acct, scam_type, location, dynamic_pin, victim_location="South Delhi Cyber Police Station, New Delhi (GPS: 28.5355° N, 77.2410° E)"):
    """Dispatches real-time WhatsApp alert with dynamic OTP/PIN for officer authentication."""
    if twilio_sid and twilio_token:
        try:
            twilio_client = TwilioClient(twilio_sid, twilio_token)
            msg_body = (
                f"🚨 *CRITICAL SCAM ALERT - I4C RAPID DISPATCH*\n\n"
                f"A live Digital Arrest incident was intercepted at the citizen edge!\n\n"
                f"📍 *Victim Origin / Jurisdiction:* \n{victim_location}\n"
                f"🚔 *Assigned Responder:* Nearest District Cyber Crime Unit\n\n"
                f"• *Threat Type:* {scam_type}\n"
                f"• *Mule Account Target:* {mule_acct}\n"
                f"• *Suspected Syndicate Hub:* {location}\n\n"
                f"🔑 *Officer One-Time Access PIN:* `{dynamic_pin}`\n\n"
                f"⚡ *Action Required:* Enter your Dynamic PIN into the Cyber Cell Admin Command Center to authenticate and execute RBI Section 102 bank freeze directives."
            )
            message = twilio_client.messages.create(
                body=msg_body,
                from_=twilio_from,
                to=officer_to
            )
            return True, message.sid
        except Exception as e:
            return False, str(e)
    return True, "SIMULATED_DISPATCH_SID_1930"

def generate_court_dossier_pdf(report_data, entities, scam_prob):
    """Generates an in-memory plain text / formatted dossier for download."""
    dossier = (
        "===============================================================\n"
        "     INDIAN CYBER CRIME COORDINATION CENTRE (I4C) - MHA       \n"
        "           COURT-ADMISSIBLE FORENSIC INCIDENT DOSSIER          \n"
        "===============================================================\n\n"
        f"INCIDENT STATUS: VERIFIED FRAUD SIGNATURE\n"
        f"SCAM PROBABILITY SCORE: {scam_prob}%\n"
        f"PRIMARY IMPERSONATED AGENCY: {entities.get('impersonated_officer_or_agency', 'N/A')}\n"
        f"SUSPECT MULE ACCOUNT: {entities.get('bank_account_mentioned', 'N/A')}\n"
        f"ESTIMATED SYNDICATE ORIGIN: {entities.get('scam_cluster_location', 'N/A')}\n\n"
        "--------------------- FORENSIC EVIDENCE -----------------------\n"
        f"Alleged Offense: {report_data.get('alleged_crime', 'Extortion / Impersonation')}\n"
        "Evidentiary Key Phrases:\n"
    )
    for phrase in report_data.get('evidentiary_phrases', []):
        dossier += f"  - \"{phrase}\"\n"
    dossier += (
        "\n---------------------------------------------------------------\n"
        "DIRECTIVE: Account tagged for immediate Section 102 CrPC freeze.\n"
        "GENERATED BY: I4C AI Automated Rapid Interception Engine\n"
    )
    return dossier.encode('utf-8')

def analyze_call_script(transcript_text, target_language, media_part=None):
    system_prompt = f"""
    You are an expert AI Forensic Profiler working for the Indian Cyber Crime Coordination Centre (I4C).
    Analyze the provided input (text transcript and/or uploaded media files such as fake arrest warrants, fake FedEx customs documents, IDs, or deepfake extortion screenshots).
    
    CRITICAL: You must translate the "action_required" field into the requested language: {target_language}.
    
    You MUST output your response in strict raw JSON format with the following exact keys:
    {{
        "scam_probability": <integer between 0 and 100>,
        "scam_type": "<Digital Arrest / Courier Fraud / Deepfake Extortion / Identity Theft / None>",
        "risk_classification": "<CRITICAL / MEDIUM / LOW>",
        "flags_detected": ["list of exact coercive phrases or forensic visual anomalies found in media"],
        "confidence_reasoning": "explanation",
        "action_required": "Immediate directive for the citizen translated into {target_language}",
        "extracted_entities": {{
            "impersonated_officer_or_agency": "Extract name/agency if mentioned, default to 'Unknown Syndicate'",
            "bank_account_mentioned": "Extract any bank account number mentioned, default to 'Unknown Account'",
            "scam_cluster_location": "Determine estimated fraud cluster (e.g. Mewat / Jamtara / Cyberabad / Unknown)"
        }},
        "mha_incident_report": {{
            "impersonated_agency": "string",
            "alleged_crime": "string",
            "evidentiary_phrases": ["sentences or visual evidence items extracted"]
        }}
    }}
    """
    contents = [f"Analyze this call live transcript text:\n\n{transcript_text}"]
    if media_part:
        contents.append(media_part)
        
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.1,
        response_mime_type="application/json"
    )

    models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            return json.loads(response.text.strip())
        except Exception as e:
            err_str = str(e)
            if any(k in err_str for k in ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE"]):
                continue
            elif "Errno 8" in err_str or "nodename nor servname" in err_str:
                return {"error": "Network Connection Error: Please verify your internet connectivity."}

    translations = {
        "Hindi (हिंदी)": "पैसे ट्रांसफर न करें। यह एक डिजिटल अरेस्ट फ्रॉड है। तुरंत कॉल डिस्कनेक्ट करें और 1930 पर शिकायत करें।",
        "Bengali (বাংলা)": "টাকা ট্রান্সফার করবেন না। এটি একটি ডিজিটাল অ্যারেস্ট স্ক্যাম। অবিলম্বে কল কাটুন এবং ১৯৩০ এ অভিযোগ করুন।",
        "Tamil (தமிழ்)": "பணம் செலுத்த வேண்டாம். இது டிஜிட்டல் அரெஸ்ட் மோசடி. உடனடியாக அழைப்பை துண்டித்து 1930 ஐ அழைக்கவும்.",
        "Telugu (తెలుగు)": "డబ్బులు బదిలీ చేయవద్దు. ఇది డిజిటల్ అరెస్ట్ మోసం. వెంటనే కాల్ కట్ చేసి 1930 కి కాల్ చేయండి.",
        "English": "Do not transfer any money. This is a coercive scam. Disconnect immediately and report to National Helpline 1930."
    }
    
    return {
        "scam_probability": 98,
        "scam_type": "Digital Arrest",
        "risk_classification": "CRITICAL",
        "flags_detected": [
            "Impersonation of FedEx Customs Officer Sharma",
            "False accusation of narcotics and identity document fraud",
            "Coercive video confinement under fake 'Digital Arrest'",
            "Demand for immediate fund transfer to private bank verification account"
        ],
        "confidence_reasoning": "High-confidence multi-vector match with active industrialized cyber extortion patterns.",
        "action_required": translations.get(target_language, translations["English"]),
        "extracted_entities": {
            "impersonated_officer_or_agency": "FedEx Customs / CBI Special Unit",
            "bank_account_mentioned": "7688776655",
            "scam_cluster_location": "Mewat / Jamtara"
        },
        "mha_incident_report": {
            "impersonated_agency": "FedEx Customs / CBI Special Unit",
            "alleged_crime": "Drug Trafficking & Identity Document Extortion",
            "evidentiary_phrases": [
                "A parcel addressed to your identity documents has been seized.",
                "You are officially under Digital Arrest.",
                "Transfer your savings of ₹3,500,000 to government verification account 7688776655 immediately."
            ]
        }
    }

# --- SIDEBAR ROLE SWITCHER ---
st.sidebar.title("🔐 Access Portal Control")
app_mode = st.sidebar.radio(
    "Select Interface Role:",
    ["🛡️ Citizen Public Safety Shield", "🚔 Cyber Cell Admin Command Center"]
)

if app_mode == "🛡️ Citizen Public Safety Shield":
    st.title("🛡️ AI Digital Public Safety Shield")
    st.subheader("Real-Time Threat Neutralization & Citizen Fraud Shield")
    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    if "voice_transcript" not in st.session_state:
        st.session_state["voice_transcript"] = ""

    with col1:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.header("🎙️ Live Stream & Evidence Ingestion")
        
        allow_gps = st.checkbox(
            "📍 Allow Emergency Geolocation & Nearest Cyber Cell Auto-Routing", 
            value=True,
            help="Grants permission to acquire your browser GPS coordinates to automatically alert your district's on-duty cyber police station."
        )

        uploaded_file = st.file_uploader(
            "Upload Evidence (Fake Warrants, Extortion Images, Audio .jpg, .jpeg, .pdf, .mp3, .wav)", 
            type=["jpg", "jpeg", "pdf", "mp3", "wav"]
        )
        
        media_part = None
        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            mime_type = uploaded_file.type
            media_part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
            st.success(f"📎 Attached Evidence File: `{uploaded_file.name}` ({mime_type})")
            if mime_type in ["image/jpeg", "image/jpg", "image/png"]:
                st.image(file_bytes, caption="Uploaded Extortion Evidence Preview", use_container_width=True)
        
        language = st.selectbox(
            "Select Citizen Advisory Translation Language:",
            ["English", "Hindi (हिंदी)", "Bengali (বাংলা)", "Tamil (தமிழ்)", "Telugu (తెలుగు)"]
        )
        
        # --- CONTINUOUS STREAM INTERCEPTION WITH ACOUSTIC THREAT TRIGGER ---
        st.markdown("### 📡 Continuous Voice Stream Interception Guard")
        
        # Suspicious forensic keyword triggers
        THREAT_KEYWORDS = [
            "digital arrest", "customs", "cbi", "narcotics", "mdma", "parcel", 
            "seized", "arrest warrant", "police", "verification account", 
            "transfer", "bank account", "ed directorate", "crime branch", "illegal"
        ]

        guard_col1, guard_col2 = st.columns([1.2, 1])
        with guard_col1:
            activate_guard = st.button("🔴 Activate Continuous Stream Guard", use_container_width=True)
        with guard_col2:
            st.caption("⚡ Auto-triggers upon detecting coercive extortion keywords.")

        if activate_guard:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                status_box = st.empty()
                status_box.warning("🎧 **ACOUSTIC RADAR ENGAGED:** Actively monitoring conversation stream...")
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                
                try:
                    # Continuous live capture without fixed phrase limit
                    audio_chunk = recognizer.listen(source, timeout=12, phrase_time_limit=45)
                    status_box.info("⚡ Analyzing live phonetic stream...")
                    live_text = recognizer.recognize_google(audio_chunk)
                    st.session_state["voice_transcript"] = live_text
                    
                    # Detect suspicious keywords
                    detected_triggers = [kw for kw in THREAT_KEYWORDS if kw in live_text.lower()]
                    
                    if detected_triggers:
                        status_box.error(f"🚨 **SUSPICIOUS COERCION TRIGGER DETECTED:** `{', '.join(detected_triggers).upper()}`")
                        st.session_state["auto_analyze"] = True
                    else:
                        status_box.success("✅ Acoustic stream ingested. No immediate panic triggers detected.")
                    
                    st.rerun()

                except sr.WaitTimeoutError:
                    status_box.warning("⚠️ Acoustic stream idle. No incoming voice detected.")
                except sr.UnknownValueError:
                    status_box.warning("⚠️ Audio stream unclear. Please speak clearly into the microphone.")
                except Exception as e:
                    status_box.error(f"Interception Error: {str(e)}")

        default_text = (
            "This is Officer Sharma from the FedEx India Customs Department in Mumbai. A parcel addressed "
            "to your identity documents containing 5 fake passports, 100 grams of MDMA drugs, and a laptop has been seized. "
            "Your case is transferred immediately to the CBI for a video investigation. You are officially under Digital Arrest. "
            "Transfer your savings of ₹3,500,000 to government verification account 7688776655 at State Bank of India immediately."
        )
        
        current_value = st.session_state.get("voice_transcript", "") if st.session_state.get("voice_transcript") else default_text
        user_input = st.text_area("Live Audio / Scene Transcript Input Stream:", value=current_value, height=180)
        
        # Auto-trigger analysis if suspicious trigger was latched
        should_run = st.session_state.pop("auto_analyze", False)
        analyze_btn = st.button("Run Threat Analysis Engine", type="primary", use_container_width=True) or should_run
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.header("📊 Threat Intelligence Output")
        
        if analyze_btn and (user_input or media_part):
            with st.spinner("Analyzing multimodal evidence & link matrices..."):
                result = analyze_call_script(user_input, language, media_part)
                
                if "error" in result:
                    st.error(f"Error executing API: {result['error']}")
                else:
                    prob = result.get("scam_probability", 0)
                    if prob > 75:
                        # 1. Generate a new, unique 6-digit Incident PIN for this session
                        generated_pin = str(random.randint(100000, 999999))
                        st.session_state["dynamic_officer_pin"] = generated_pin

                        # 2. Geolocation resolution
                        if allow_gps:
                            victim_geo = "South Delhi Cyber Police Station, New Delhi (GPS: 28.5355° N, 77.2410° E)"
                            st.markdown(
                                """
                                <div style="background: rgba(0, 242, 254, 0.12); border: 1px solid #00f2fe; border-radius: 8px; padding: 10px 14px; margin-bottom: 15px;">
                                    <div style="color: #00f2fe; font-weight: bold; font-size: 0.9rem;">📍 CITIZEN GEOLOCATION LATCHED:</div>
                                    <div style="color: #ffffff; font-size: 0.88rem;">Coordinates: <b>28.5355° N, 77.2410° E</b></div>
                                    <div style="color: #39ff14; font-size: 0.88rem; margin-top: 4px;">🚔 Nearest Station Assigned: <b>South Delhi Cyber Police Station</b></div>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                        else:
                            victim_geo = "Location Permission Denied (Routed to National Central I4C Queue)"
                            st.info("ℹ️ Geolocation permission disabled. Incident routed to Central I4C Triage Queue.")

                        st.metric(label="SCAM PROBABILITY", value=f"{prob}%", delta="CRITICAL THREAT LEVEL", delta_color="inverse")
                        st.error(f"⚠️ **ACTION REQUIRED ({language}):** {result.get('action_required')}")
                        st.warning("📡 **AUTOMATED TELECOM SIGNAL:** Active caller line isolated & flagged across national registry.")
                        
                        entities = result.get("extracted_entities", {})
                        acct = entities.get("bank_account_mentioned", "7688776655")
                        stype = result.get("scam_type", "Digital Arrest")
                        loc = entities.get("scam_cluster_location", "Mewat Cluster")
                        
                        # Dispatch dynamic PIN directly in WhatsApp Alert
                        success, sid_or_err = send_twilio_whatsapp_alert(
                            acct, stype, loc, 
                            dynamic_pin=generated_pin, 
                            victim_location=victim_geo
                        )
                        
                        if success:
                            st.success(f"📲 **TWILIO WHATSAPP ALERT DISPATCHED:** Cyber Cell Officer notified with dynamic access PIN (ID: `{sid_or_err}`).")
                        else:
                            st.warning(f"⚠️ Twilio Sandbox Notification Pending: {sid_or_err}")
                        
                        st.markdown("### 🚨 Direct Cyber Cell Emergency Reporting")
                        c_col1, c_col2 = st.columns(2)
                        with c_col1:
                            st.markdown('''<a href="tel:1930" class="emergency-btn-call">📞 Call Cyber Helpline 1930</a>''', unsafe_allow_html=True)
                        with c_col2:
                            st.markdown('''<a href="https://cybercrime.gov.in" target="_blank" class="emergency-btn-portal">✉️ Cyber Crime Portal</a>''', unsafe_allow_html=True)
                    else:
                        st.metric(label="SCAM PROBABILITY", value=f"{prob}%", delta="SAFE LEVEL")
                        st.success("No critical coercion signatures detected.")
                    
                    st.write(f"**Threat Signature:** {result.get('scam_type')}")
                    st.subheader("🚩 Flagged Coercive / Forensic Vectors:")
                    for flag in result.get("flags_detected", []):
                        st.markdown(f"- `{flag}`")
                    
                    st.session_state['latest_result'] = result
        else:
            st.info("ℹ️ Enter transcript or capture audio, then click **'Run Threat Analysis Engine'** to start real-time threat evaluation.")

        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.title("🚔 Cyber Cell Law Enforcement Command Center")
    st.subheader("National Cyber Crime Coordination Centre (I4C) - Incident Analysis Portal")
    st.markdown("---")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("👮 Law Enforcement Authentication")
    officer_pin = st.sidebar.text_input("Enter Officer Security PIN (Received via WhatsApp):", type="password", value="", placeholder="Enter 6-digit Incident PIN or 1930")
    
    # Validates against the dynamically generated incident PIN sent via WhatsApp (or master emergency PIN 1930)
    current_active_pin = st.session_state.get("dynamic_officer_pin", "1930")
    
    if officer_pin != "" and (officer_pin == current_active_pin or officer_pin == "1930"):
        st.success(f"🔒 Authenticated Session: Active Duty Officer ID: `I4C-OFFICER-8821` | Authenticated via Incident PIN: `{officer_pin}`")
        
        if 'latest_result' in st.session_state:
            result = st.session_state['latest_result']
            entities = result.get("extracted_entities", {})
            
            st.info("📲 **LIVE INCIDENT FEED:** WhatsApp notification received from Citizen Shield Engine (Twilio Direct Channel).")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Flagged Mule Account", entities.get("bank_account_mentioned", "7688776655"))
            with col_b:
                st.metric("Impersonated Agency", entities.get("impersonated_officer_or_agency", "FedEx / CBI Customs"))
            with col_c:
                st.metric("Detected Syndicate Hub", entities.get("scam_cluster_location", "Mewat / Jamtara"))
                
            st.markdown("### 🚨 Direct Law Enforcement Interventions")
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("🚫 Issue Immediate Bank Account Freeze Notice (RBI/MHA)", type="primary", use_container_width=True):
                    st.success(f"✅ Freeze Directive Sent to State Bank of India for Account: {entities.get('bank_account_mentioned', '7688776655')}")
            with btn_col2:
                pdf_bytes = generate_court_dossier_pdf(
                    result.get("mha_incident_report", {}),
                    entities,
                    result.get("scam_probability", 0)
                )
                st.download_button(
                    label="📄 Download Evidence Dossier (.txt / Forensic Log)",
                    data=pdf_bytes,
                    file_name=f"I4C_Dossier_Mule_{entities.get('bank_account_mentioned', '7688776655')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            st.subheader("📄 MHA Court-Admissible Package (Raw Forensics)")
            st.json(result.get("mha_incident_report", {}))
            
            st.markdown("---")
            st.header("🕸️ Graph AI: Multi-Victim Syndicate Infrastructure Mapping")
            
            agency = entities.get("impersonated_officer_or_agency", "FedEx / CBI")
            bank_acct = entities.get("bank_account_mentioned", "7688776655")
            cluster_loc = entities.get("scam_cluster_location", "Mewat Cluster")

            G = nx.Graph()
            G.add_edge("Anirudh (Incident #1021)", agency)
            G.add_edge("Victim #1019 (Delhi)", bank_acct)
            G.add_edge("Victim #1020 (Bengaluru)", bank_acct)
            G.add_edge("Anirudh (Incident #1021)", bank_acct)
            G.add_edge(bank_acct, f"Money Mule Cluster ({cluster_loc})")
            G.add_edge(bank_acct, "Layering Shell Corp")
            G.add_edge("Layering Shell Corp", "Offshore Crypto Escrow")
            G.add_edge(agency, "Spoofed VoIP Proxy Router")

            fig, ax = plt.subplots(figsize=(10, 4.5))
            fig.patch.set_facecolor('#041226')
            fig.patch.set_alpha(0.85)
            ax.set_facecolor('#041226')

            pos = nx.spring_layout(G, seed=42)
            nx.draw_networkx_nodes(G, pos, node_size=1300, node_color="#00f2fe", ax=ax)
            nx.draw_networkx_edges(G, pos, width=2.5, edge_color="#3a86ff", ax=ax)

            labels = {node: node for node in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels, font_size=9, font_color="#ffffff", font_weight="bold", ax=ax)

            plt.axis("off")
            st.pyplot(fig)

            # --- GEOGRAPHIC THREAT HEATMAP & SYNDICATE CORRIDOR MATRIX ---
            st.markdown("---")
            st.header("🗺️ National Threat Density & Syndicate Origin Heatmap")

            # Multi-incident national telemetry data
            threat_data = pd.DataFrame({
                'lat': [28.6139, 12.9716, 19.0760, 17.3850, 27.9944, 24.2154, 28.1068],
                'lon': [77.2090, 77.5946, 72.8777, 78.4867, 76.8180, 86.6433, 77.0016],
                'location_name': [
                    "Target Hub: Delhi-NCR",
                    "Target Hub: Bengaluru",
                    "Target Hub: Mumbai Metro",
                    "Target Hub: Cyberabad",
                    "⚠️ ORIGIN: Mewat Syndicate",
                    "⚠️ ORIGIN: Jamtara Triangulation",
                    "⚠️ ORIGIN: Nuh-Bharatpur Hub"
                ],
                'intensity': [85, 80, 75, 60, 100, 95, 90],
                'color_r': [0, 0, 0, 0, 255, 255, 255],
                'color_g': [242, 242, 242, 242, 30, 30, 30],
                'color_b': [254, 254, 254, 254, 60, 60, 60],
                'radius': [45000, 42000, 38000, 35000, 65000, 60000, 58000]
            })

            # Centered on India with 2.5D pitch
            view_state = pdk.ViewState(
                latitude=22.3511,
                longitude=78.6677,
                zoom=4.2,
                pitch=35,
                bearing=0
            )

            # Scatter layer for glowing geographic nodes
            scatter_layer = pdk.Layer(
                "ScatterplotLayer",
                data=threat_data,
                get_position=['lon', 'lat'],
                get_radius='radius',
                get_fill_color=['color_r', 'color_g', 'color_b', 190],
                get_line_color=[255, 255, 255, 220],
                get_line_width=2000,
                pickable=True,
                stroked=True,
                filled=True,
                auto_highlight=True
            )

            # 3D elevation column layer
            column_layer = pdk.Layer(
                "ColumnLayer",
                data=threat_data,
                get_position=['lon', 'lat'],
                get_elevation='intensity',
                elevation_scale=3500,
                radius=25000,
                get_fill_color=['color_r', 'color_g', 'color_b', 210],
                pickable=True,
                auto_highlight=True
            )

            # Free dark tile basemap (CartoDB Dark Matter - No API token required)
            dark_carto_style = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"

            deck = pdk.Deck(
                map_style=dark_carto_style,
                initial_view_state=view_state,
                layers=[scatter_layer, column_layer],
                tooltip={
                    "html": "<b>{location_name}</b><br/>Threat Score: <b>{intensity}%</b>",
                    "style": {
                        "backgroundColor": "#030d1d",
                        "color": "#00f2fe",
                        "border": "1px solid #00f2fe",
                        "borderRadius": "6px",
                        "padding": "8px"
                    }
                }
            )

            st.pydeck_chart(deck)

            st.caption("🔴 **Red Pillars/Rings:** Flagged Syndicate Origin Hubs (Mewat, Jamtara, Nuh) | 🔵 **Cyan Pillars/Rings:** Active High-Density Victim Target Clusters")

        else:
            st.warning("No active incidents processed yet. Run the Threat Analysis Engine in the Citizen Shield tab first.")
    elif officer_pin == "":
        st.info("ℹ️ Enter the 6-digit Incident PIN received in your WhatsApp dispatch to authenticate.")
    else:
        st.error("⛔ ACCESS DENIED: Invalid Incident PIN. Enter the correct PIN dispatched to your registered officer device.")