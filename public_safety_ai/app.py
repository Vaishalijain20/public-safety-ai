import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from colorama import Fore, Style, init

# Initialize colorama for clean, scannable hackathon terminal visuals
init(autoreset=True)

# Load environment variables from the hidden .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print(f"{Fore.RED}[ERROR] GEMINI_API_KEY not found! Please check your .env file.")
    exit(1)

# Initialize the Gemini Client
client = genai.Client(api_key=api_key)

def analyze_call_script(transcript_text):
    """
    Sends the suspicious transcript to Gemini to calculate a risk assessment
    and return structured JSON matching high-precision public safety signatures.
    """
    
    system_prompt = """
    You are an expert AI Forensic Profiler working for the Indian Cyber Crime Coordination Centre (I4C) and Ministry of Home Affairs (MHA).
    Your task is to analyze the text transcript of an ongoing live phone/video call and instantly detect if it is a 'Digital Arrest' or cyber-fraud scam.
    
    Look specifically for these high-risk behavioral indicators:
    1. Impersonation of authority (Customs, CBI, Police, ED, Narcotics Bureau, FedEx, DHL).
    2. Claims about illegal contraband, passports, or drugs linked to the victim's Aadhaar card.
    3. Coercion to move to a private video call (Skype/WhatsApp) for "online investigation".
    4. Threat of 'Digital Arrest' and forbidding the victim to contact family members or lawyers.
    5. Demand to transfer money to a 'Government verification escrow account' or 'RBI vault' to clear their name.
    
    You MUST output your response in strict raw JSON format with the following exact keys:
    {
        "scam_probability": <integer between 0 and 100>,
        "scam_type": "<Digital Arrest / Courier Fraud / Identity Theft / None>",
        "risk_classification": "<CRITICAL / MEDIUM / LOW>",
        "flags_detected": ["list of exact coercive phrases found"],
        "confidence_reasoning": "brief explanation of precision matching",
        "action_required": "Immediate instruction for the citizen",
        "mha_incident_report": {
            "impersonated_agency": "string",
            "alleged_crime": "string",
            "evidentiary_phrases": ["sentences from text showing fraud intent"]
        }
    }
    """
    
    try:
        # Using gemini-2.5-flash for incredibly fast hackathon prototype responses
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Analyze this call live transcript text:\n\n{transcript_text}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
                # Forces Gemini to reply strictly in valid JSON structure
                response_mime_type="application/json" 
            )
        )
        
        return json.loads(response.text.strip())
    
    except Exception as e:
        return {"error": f"Failed to parse or reach Gemini API: {str(e)}"}

# --- SIMULATION AND TESTING ENGINE ---
if __name__ == "__main__":
    print(Style.BRIGHT + Fore.CYAN + "==================================================")
    print(Style.BRIGHT + Fore.CYAN + "   AI DIGITAL PUBLIC SAFETY: CITIZEN FRAUD SHIELD ")
    print(Style.BRIGHT + Fore.CYAN + "==================================================\n")
    
    mock_scam_transcript = """
    Officer: Speak clearly! This is Inspector Kumar from the Mumbai Narcotics Cell. Your Aadhaar number 
    was mapped to a package seized at customs containing 5 fake passports and 100 grams of MDMA drugs. 
    Victim: Sir, I swear I didn't send any package!
    Officer: Silence! A Supreme Court warrant has been logged. You are officially under Digital Arrest. 
    Move to Skype immediately for a live video verification. Do not call your family or tell anyone, this case 
    is highly confidential. To clear your name, you must transfer your account balance of 3,50,000 rupees 
    to the RBI verification vault right now. It will be returned after clearance.
    """
    
    print(Fore.YELLOW + "[STEP 1] Ingesting Live Call Audio Stream (Simulated Transcript Data)...")
    print(Fore.WHITE + "--------------------------------------------------")
    print(mock_scam_transcript.strip())
    print(Fore.WHITE + "--------------------------------------------------\n")
    
    print(Fore.YELLOW + "[STEP 2] Running Multi-Agent Extraction & Risk Evaluation (Gemini API)...")
    analysis = analyze_call_script(mock_scam_transcript)
    
    if "error" in analysis:
        print(Fore.RED + f"Execution Error: {analysis['error']}")
    else:
        print(Fore.GREEN + "[STEP 3] Parsing Live Threat Intelligence Report:\n")
        
        prob = analysis.get("scam_probability", 0)
        color = Fore.RED if prob > 75 else (Fore.YELLOW if prob > 40 else Fore.GREEN)
        
        print(f"-> SCAM PROBABILITY: {color}{prob}%")
        print(f"-> THREAT TYPE:       {Fore.MAGENTA}{analysis.get('scam_type')}")
        print(f"-> ALERT LEVEL:       {color}{analysis.get('risk_classification')}")
        print(f"-> USER ACTION:       {Fore.LIGHTWHITE_EX}{Style.BRIGHT}{analysis.get('action_required')}\n")
        
        print(Fore.BLUE + "Detected Fraud Indicators / Red Flags:")
        for flag in analysis.get("flags_detected", []):
            print(f" [!] {flag}")
            
        print("\n" + Fore.CYAN + "==================================================")
        print(Fore.CYAN + "  AUTO-GENERATED COURT-ADMISSIBLE RECOVERY PACKAGE")
        print(Fore.CYAN + "==================================================")
        print(json.dumps(analysis.get("mha_incident_report", {}), indent=4))
        print(Fore.CYAN + "==================================================")