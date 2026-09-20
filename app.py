import streamlit as st
import google.generativeai as genai
import requests
import json
import re
import urllib.parse

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & CLEAN STYLING
# -------------------------------------------------------------
st.set_page_config(
    page_title="AI Super Copilot & Phone Controller",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# MacroDroid Webhook Device Link
MACRODROID_URL = "https://trigger.macrodroid.com/3b017816-7e27-4e32-ad33-fe6b0e595c96/ai_command"

# Google AI Studio + WhatsApp Style Theme
st.markdown("""
<style>
    .stApp { 
        background-color: #F8F9FA; 
        color: #1F1F1F; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .main-header {
        text-align: center;
        padding: 10px 0 20px 0;
    }
    .chat-bubble-user {
        background-color: #E7F8EC;
        border: 1px solid #C2E7CB;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        margin: 8px 0;
        max-width: 85%;
        float: right;
        clear: both;
        color: #0F5132;
    }
    .chat-bubble-ai {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 18px;
        margin: 8px 0;
        max-width: 85%;
        float: left;
        clear: both;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        color: #1F2937;
    }
    .action-card {
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white !important;
        padding: 10px 16px;
        border-radius: 12px;
        margin: 10px 0;
        display: inline-block;
        font-weight: 600;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. SECURE API CONFIGURATION (Auto-Fallback)
# -------------------------------------------------------------
FALLBACK_KEY = "AQ.Ab8RN6I71bl-ynam3zuyB1wiVqU_kMICDMA_q9CtqBpuTpTJ7w"
api_key = st.secrets.get("GEMINI_API_KEY", FALLBACK_KEY)

try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"API Configure Error: {e}")

# -------------------------------------------------------------
# 3. PHONE CONTROLLER ENGINE (MacroDroid Dispatcher)
# -------------------------------------------------------------
def trigger_phone_action(action_type, phone="", text="", app_name=""):
    """Phone par MacroDroid webhook trigger karta hai"""
    try:
        params = {
            "action": str(action_type),
            "phone": str(phone),
            "text": str(text),
            "app": str(app_name)
        }
        res = requests.get(MACRODROID_URL, params=params, timeout=5)
        return True if res.status_code == 200 else False
    except Exception:
        return False

# -------------------------------------------------------------
# 4. SYSTEM PROMPT & MODEL SETUP
# -------------------------------------------------------------
SYSTEM_INSTRUCTIONS = """
Aap aik All-in-One Executive AI Phone Copilot hain jo user ke sath friendly Roman Urdu mein baat karta hai.

Phone Control Rules:
1. Jab bhi user kahe WhatsApp par message bhejo, call milao ya koi action karne ko kahe:
   - Saaf aur direct Roman Urdu mein jawab dein (jaise: "Theek hai, main message bhej raha hoon.")
   - Apne jawab ke bilkul aakhir mein secret JSON tag shamil karein:
   <<<ACTION:{"action":"whatsapp", "phone":"NUMBER_OR_NAME", "text":"MSG_CONTENT"}>>>
2. Agar koi general sawal ho to seedha practical jawab dein. Bekaar lamba bhashan ya formatting bullets na dein.
"""

def get_ai_model():
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    for m in models_to_try:
        try:
            return genai.GenerativeModel(
                model_name=m,
                system_instruction=SYSTEM_INSTRUCTIONS
            )
        except Exception:
            continue
    return genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_INSTRUCTIONS)

model = get_ai_model()

# -------------------------------------------------------------
# 5. UI HEADER & SESSION STATE
# -------------------------------------------------------------
st.markdown("<div class='main-header'><h2>🤖 AI Phone Copilot</h2><p style='color:#6B7280;'>Live WhatsApp & Mobile Automation Connected</p></div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalam-o-Alaikum! Main aapka AI Phone Copilot hoon. Aap mujhse WhatsApp messages bhejwa sakte hain ya koi bhi kaam keh sakte hain."}
    ]

# Display Past Messages
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    if role == "user":
        st.markdown(f"<div class='chat-bubble-user'>👤 {content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-ai'>🤖 {content}</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 6. USER INPUT & ACTION EXECUTION
# -------------------------------------------------------------
user_input = st.chat_input("Bol kar ya likh kar command dein (e.g. 03001234567 par WhatsApp karo ke main aa raha hoon)...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='chat-bubble-user'>👤 {user_input}</div>", unsafe_allow_html=True)

    with st.spinner("AI phone par command execute kar raha hai..."):
        try:
            response = model.generate_content(user_input)
            raw_text = response.text

            # Clean Thinking & Regex
            clean_text = raw_text
            action_data = None

            if "<<<ACTION:" in raw_text:
                start = raw_text.find("<<<ACTION:") + len("<<<ACTION:")
                end = raw_text.find(">>>", start)
                action_json_str = raw_text[start:end]
                clean_text = raw_text[:raw_text.find("<<<ACTION:")].strip()

                try:
                    action_data = json.loads(action_json_str)
                    # Trigger Phone Webhook
                    trigger_phone_action(
                        action_type=action_data.get("action", "whatsapp"),
                        phone=action_data.get("phone", ""),
                        text=action_data.get("text", "")
                    )
                except Exception:
                    pass

            st.markdown(f"<div class='chat-bubble-ai'>🤖 {clean_text}</div>", unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": clean_text})

            # Show direct interactive WhatsApp Button as instant fallback
            if action_data and action_data.get("action") == "whatsapp":
                phone_num = re.sub(r'[^0-9]', '', str(action_data.get("phone", "")))
                msg_body = urllib.parse.quote(str(action_data.get("text", "")))
                wa_url = f"https://api.whatsapp.com/send?phone={phone_num}&text={msg_body}" if phone_num else f"https://api.whatsapp.com/send?text={msg_body}"
                
                st.markdown(f"""
                <div style="clear:both; padding-top:10px;">
                    <a href="{wa_url}" target="_blank" class="action-card">
                        🚀 Direct WhatsApp Khalein ({action_data.get('phone', 'Chat')})
                    </a>
                </div>
                """, unsafe_allow_html=True)

        except Exception as err:
            err_msg = f"Kuch masla aaya: {str(err)}"
            st.markdown(f"<div class='chat-bubble-ai'>⚠️ {err_msg}</div>", unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": err_msg})
