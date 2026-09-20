import streamlit as st
import requests
import json
import re
import urllib.parse

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & THEME
# -------------------------------------------------------------
st.set_page_config(
    page_title="AI Phone Copilot & WhatsApp Controller",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

MACRODROID_URL = "https://trigger.macrodroid.com/3b017816-7e27-4e32-ad33-fe6b0e595c96/ai_command"
FALLBACK_KEY = "AQ.Ab8RN6LzczOTyOyhS8yoBvQzLs8ogfa06jJIRdvlv_DoEOfZyA"
API_KEY = st.secrets.get("GEMINI_API_KEY", FALLBACK_KEY).strip()

st.markdown("""
<style>
    .stApp { 
        background-color: #F8F9FA; 
        color: #1F1F1F; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .main-header {
        text-align: center;
        padding: 5px 0 15px 0;
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
        padding: 10px 18px;
        border-radius: 12px;
        margin: 10px 0;
        display: inline-block;
        font-weight: 600;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. MULTI-GATEWAY AI ENGINE (Supports AQ. & Classic Keys)
# -------------------------------------------------------------
SYSTEM_INSTRUCTIONS = """
Aap aik All-in-One Executive AI Phone Copilot hain jo user ke sath Roman Urdu mein direct baat karta hai.

Phone Action Rules:
1. Jab user kahe WhatsApp par message bhejo ya kisi ko call karo:
   - Direct, pyara aur mukhtasir jawab dein (jaise: "Theek hai, main message send kar raha hoon.")
   - Apne jawab ke bilkul aakhir mein secret tag shamil karein:
   <<<ACTION:{"action":"whatsapp", "phone":"NUMBER_OR_NAME", "text":"MSG_CONTENT"}>>>
2. Koi lambi explanation ya faaltu formatting na karein.
"""

def generate_ai_response(prompt_text):
    # Method 1: OpenAI-Compatible Gateway for AQ Keys (Bearer Auth)
    try:
        openai_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        headers_bearer = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        body_openai = {
            "model": "gemini-2.0-flash",
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": prompt_text}
            ]
        }
        res = requests.post(openai_url, headers=headers_bearer, json=body_openai, timeout=15)
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]
    except Exception:
        pass

    # Method 2: Vertex Express Gateway
    try:
        vertex_url = "https://aiplatform.googleapis.com/v1beta1/publishers/google/models/gemini-2.0-flash:generateContent"
        headers_vertex = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTIONS}]},
            "contents": [{"role": "user", "parts": [{"text": prompt_text}]}]
        }
        res = requests.post(vertex_url, headers=headers_vertex, json=payload, timeout=15)
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        pass

    # Method 3: Standard Native Key Gateway
    try:
        native_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
        headers_native = {"Content-Type": "application/json"}
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTIONS}]},
            "contents": [{"role": "user", "parts": [{"text": prompt_text}]}]
        }
        res = requests.post(native_url, headers=headers_native, json=payload, timeout=15)
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Status {res.status_code}: {res.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------------------------------------------
# 3. MACRODROID PHONE CONTROLLER
# -------------------------------------------------------------
def trigger_phone_action(action_type, phone="", text="", app_name=""):
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
# 4. UI & CHAT INTERFACE
# -------------------------------------------------------------
st.markdown("<div class='main-header'><h2>🤖 AI Phone Copilot</h2><p style='color:#6B7280;'>Live WhatsApp & Mobile Automation Connected</p></div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalam-o-Alaikum! Main aapka AI Phone Copilot hoon. Aap mujhse WhatsApp messages bhejwa sakte hain ya koi bhi sawal pooch sakte hain."}
    ]

# Display Messages
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    if role == "user":
        st.markdown(f"<div class='chat-bubble-user'>👤 {content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-ai'>🤖 {content}</div>", unsafe_allow_html=True)

# User Chat Input
user_input = st.chat_input("Bol kar ya likh kar command dein (e.g. 03001234567 par WhatsApp karo)...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='chat-bubble-user'>👤 {user_input}</div>", unsafe_allow_html=True)

    with st.spinner("AI phone par command bhej raha hai..."):
        raw_text = generate_ai_response(user_input)
        clean_text = raw_text
        action_data = None

        if "<<<ACTION:" in raw_text:
            start = raw_text.find("<<<ACTION:") + len("<<<ACTION:")
            end = raw_text.find(">>>", start)
            action_json_str = raw_text[start:end]
            clean_text = raw_text[:raw_text.find("<<<ACTION:")].strip()

            try:
                action_data = json.loads(action_json_str)
                # Webhook to Phone
                trigger_phone_action(
                    action_type=action_data.get("action", "whatsapp"),
                    phone=action_data.get("phone", ""),
                    text=action_data.get("text", "")
                )
            except Exception:
                pass

        st.markdown(f"<div class='chat-bubble-ai'>🤖 {clean_text}</div>", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": clean_text})

        # Interactive WhatsApp Button
        if action_data and action_data.get("action") == "whatsapp":
            phone_num = re.sub(r'[^0-9]', '', str(action_data.get("phone", "")))
            msg_body = urllib.parse.quote(str(action_data.get("text", "")))
            wa_url = f"https://api.whatsapp.com/send?phone={phone_num}&text={msg_body}" if phone_num else f"https://api.whatsapp.com/send?text={msg_body}"
            
            st.markdown(f"""
            <div style="clear:both; padding-top:10px;">
                <a href="{wa_url}" target="_blank" class="action-card">
                    🚀 Direct WhatsApp Kholein ({action_data.get('phone', 'Chat')})
                </a>
            </div>
            """, unsafe_allow_html=True)
