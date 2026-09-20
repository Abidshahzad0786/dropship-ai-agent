import streamlit as st
import requests
import json
import re
import urllib.parse

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & THEME
# -------------------------------------------------------------
st.set_page_config(
    page_title="My AI Phone Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

MACRODROID_URL = "https://trigger.macrodroid.com/3b017816-7e27-4e32-ad33-fe6b0e595c96/ai_command"

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
    .action-btn {
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white !important;
        padding: 12px 20px;
        border-radius: 12px;
        margin: 10px 0;
        display: inline-block;
        font-weight: 700;
        text-decoration: none;
        box-shadow: 0 4px 10px rgba(37,211,102,0.3);
    }
    .fb-btn {
        background: linear-gradient(135deg, #1877F2 0%, #0D5AC1 100%);
        box-shadow: 0 4px 10px rgba(24,119,242,0.3);
    }
    .yt-btn {
        background: linear-gradient(135deg, #FF0000 0%, #CC0000 100%);
        box-shadow: 0 4px 10px rgba(255,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. SMART INTENT DETECTOR & AI ENGINE
# -------------------------------------------------------------
def detect_action_locally(user_text):
    """User ke bolte hi foran action detect karta hai baghair kisi delay ke"""
    t = user_text.lower()
    
    # Facebook
    if "facebook" in t or "fb" in t:
        return {"action": "open_app", "app": "facebook", "url": "https://www.facebook.com", "label": "🔵 Open Facebook"}
    
    # YouTube
    if "youtube" in t or "yt" in t:
        return {"action": "open_app", "app": "youtube", "url": "https://www.youtube.com", "label": "🔴 Open YouTube"}
        
    # TikTok
    if "tiktok" in t:
        return {"action": "open_app", "app": "tiktok", "url": "https://www.tiktok.com", "label": "🎵 Open TikTok"}
        
    # WhatsApp Detection
    if "whatsapp" in t or "message" in t or "sms" in t:
        # Extract numbers if present
        nums = re.findall(r'\b\d{10,13}\b', t)
        phone = nums[0] if nums else ""
        # Clean text
        clean_msg = re.sub(r'(whatsapp|karo|bhejo|message|sms|ko|par|per)', '', t, flags=re.IGNORECASE).strip()
        wa_url = f"https://api.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(clean_msg)}" if phone else f"https://api.whatsapp.com/send?text={urllib.parse.quote(clean_msg)}"
        return {"action": "whatsapp", "phone": phone, "text": clean_msg, "url": wa_url, "label": f"🟢 Open WhatsApp ({phone if phone else 'Direct'})"}

    return None

def generate_ai_response(prompt_text):
    system_prompt = "Aap aik fast Roman Urdu Executive Mobile Assistant hain. Hamesha direct, mukhtasir aur friendly jawab dein."
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt_text)}?system={urllib.parse.quote(system_prompt)}&model=openai"
        res = requests.get(url, timeout=10)
        if res.status_code == 200 and res.text.strip():
            return res.text.strip()
    except Exception:
        pass
    return "Ji bilkul, main aapki command par foran amal kar raha hoon!"

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
        res = requests.get(MACRODROID_URL, params=params, timeout=4)
        return True if res.status_code == 200 else False
    except Exception:
        return False

# -------------------------------------------------------------
# 4. UI & CHAT INTERFACE
# -------------------------------------------------------------
st.markdown("<div class='main-header'><h2>🤖 My AI Phone Copilot</h2><p style='color:#6B7280;'>Live Phone & Apps Controller</p></div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalam-o-Alaikum! Main aapka AI Copilot hoon. WhatsApp, Facebook, YouTube ya koi bhi app khulwane ke liye bolein."}
    ]

for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    action_info = msg.get("action_info")
    
    if role == "user":
        st.markdown(f"<div class='chat-bubble-user'>👤 {content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-ai'>🤖 {content}</div>", unsafe_allow_html=True)
        if action_info:
            btn_class = "action-btn fb-btn" if "facebook" in action_info.get("app", "") else ("action-btn yt-btn" if "youtube" in action_info.get("app", "") else "action-btn")
            st.markdown(f"""
            <div style="clear:both; padding-top:6px; margin-bottom:10px;">
                <a href="{action_info['url']}" target="_blank" class="{btn_class}">
                    {action_info['label']}
                </a>
            </div>
            """, unsafe_allow_html=True)

user_input = st.chat_input("Bol kar ya likh kar command dein (e.g. Facebook kholo, WhatsApp par message karo)...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='chat-bubble-user'>👤 {user_input}</div>", unsafe_allow_html=True)

    # 1. Direct Instant Action Detection
    action = detect_action_locally(user_input)
    if action:
        trigger_phone_action(
            action_type=action.get("action", "open_app"),
            phone=action.get("phone", ""),
            text=action.get("text", ""),
            app_name=action.get("app", "")
        )

    # 2. Generate AI Response
    with st.spinner("AI action execute kar raha hai..."):
        ai_reply = generate_ai_response(user_input)
        
        st.markdown(f"<div class='chat-bubble-ai'>🤖 {ai_reply}</div>", unsafe_allow_html=True)
        
        if action:
            btn_class = "action-btn fb-btn" if "facebook" in action.get("app", "") else ("action-btn yt-btn" if "youtube" in action.get("app", "") else "action-btn")
            st.markdown(f"""
            <div style="clear:both; padding-top:6px; margin-bottom:10px;">
                <a href="{action['url']}" target="_blank" class="{btn_class}">
                    {action['label']}
                </a>
            </div>
            """, unsafe_allow_html=True)

        st.session_state.messages.append({"role": "assistant", "content": ai_reply, "action_info": action})
