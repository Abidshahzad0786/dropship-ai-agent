import streamlit as st
import streamlit.components.v1 as components
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
# 2. AUTO-ACTION INTENT DETECTOR
# -------------------------------------------------------------
def detect_action_and_reply(user_text):
    t = user_text.lower()
    
    # 1. Facebook
    if "facebook" in t or "fb" in t:
        return {
            "action": "open_app",
            "url": "https://www.facebook.com",
            "label": "🔵 Facebook Khol Diya Gaya Hai",
            "reply": "Ji zaroor, main aapke mobile par Facebook open kar raha hoon!",
            "btn_class": "action-btn fb-btn"
        }
    
    # 2. YouTube
    if "youtube" in t or "yt" in t:
        return {
            "action": "open_app",
            "url": "https://www.youtube.com",
            "label": "🔴 YouTube Khol Diya Gaya Hai",
            "reply": "YouTube open ho raha hai, aap jo dekhna chahein enjoy karein!",
            "btn_class": "action-btn yt-btn"
        }
        
    # 3. TikTok
    if "tiktok" in t:
        return {
            "action": "open_app",
            "url": "https://www.tiktok.com",
            "label": "🎵 TikTok Khol Diya Gaya Hai",
            "reply": "TikTok launch kiya ja raha hai!",
            "btn_class": "action-btn"
        }
        
    # 4. WhatsApp Automation
    if "whatsapp" in t or "sms" in t or "message" in t:
        nums = re.findall(r'\b\d{10,13}\b', t)
        phone = nums[0] if nums else ""
        
        # Name detection
        clean_msg = t
        for word in ["whatsapp", "kholo", "karo", "bhejo", "message", "sms", "ko", "par", "per", "open", "send"]:
            clean_msg = re.sub(r'\b' + word + r'\b', '', clean_msg, flags=re.IGNORECASE)
        clean_msg = clean_msg.strip()
        
        wa_url = f"https://api.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(clean_msg)}" if phone else f"https://api.whatsapp.com/send?text={urllib.parse.quote(clean_msg)}"
        
        return {
            "action": "whatsapp",
            "url": wa_url,
            "label": f"🟢 WhatsApp Khol Diya Gaya Hai",
            "reply": f"Theek hai, main WhatsApp khol kar message ready kar raha hoon!",
            "btn_class": "action-btn"
        }

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
    return "Main aapke mobile ka Copilot hoon. Batayein WhatsApp, Facebook ya koi aur app kholni hai?"

# -------------------------------------------------------------
# 3. MACRODROID DISPATCHER
# -------------------------------------------------------------
def trigger_phone_action(action_url):
    try:
        params = {"url": str(action_url)}
        requests.get(MACRODROID_URL, params=params, timeout=3)
    except Exception:
        pass

# -------------------------------------------------------------
# 4. UI & CHAT INTERFACE
# -------------------------------------------------------------
st.markdown("<div class='main-header'><h2>🤖 My AI Phone Copilot</h2><p style='color:#6B7280;'>Live Auto-Open Phone Controller</p></div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalam-o-Alaikum! Main aapka AI Phone Copilot hoon. WhatsApp, Facebook, YouTube ya koi bhi app khulwane ke liye bolein."}
    ]

# Display Messages
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    action_info = msg.get("action_info")
    
    if role == "user":
        st.markdown(f"<div class='chat-bubble-user'>👤 {content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-ai'>🤖 {content}</div>", unsafe_allow_html=True)
        if action_info:
            st.markdown(f"""
            <div style="clear:both; padding-top:6px; margin-bottom:10px;">
                <a href="{action_info['url']}" target="_blank" class="{action_info['btn_class']}">
                    {action_info['label']}
                </a>
            </div>
            """, unsafe_allow_html=True)

user_input = st.chat_input("Bol kar ya likh kar command dein (e.g. Facebook kholo, Ghulam Rasool ko WhatsApp karo)...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='chat-bubble-user'>👤 {user_input}</div>", unsafe_allow_html=True)

    # 1. Action & Instant Auto-Open Detection
    action = detect_action_and_reply(user_input)
    
    if action:
        ai_reply = action["reply"]
        trigger_phone_action(action["url"])
    else:
        with st.spinner("AI reply tayyar kar raha hai..."):
            ai_reply = generate_ai_response(user_input)

    # Display AI Response
    st.markdown(f"<div class='chat-bubble-ai'>🤖 {ai_reply}</div>", unsafe_allow_html=True)

    # 2. AUTO-OPEN JAVASCRIPT ENGINE (Baghair Click Kiye Khud Khulega)
    if action:
        st.markdown(f"""
        <div style="clear:both; padding-top:6px; margin-bottom:10px;">
            <a href="{action['url']}" id="auto-link" target="_blank" class="{action['btn_class']}">
                {action['label']}
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # Automatic redirect / popup trigger
        components.html(f"""
        <script>
            setTimeout(function() {{
                window.open("{action['url']}", "_blank");
            }}, 400);
        </script>
        """, height=0, width=0)

    st.session_state.messages.append({"role": "assistant", "content": ai_reply, "action_info": action})
