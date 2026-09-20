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
    .status-badge {
        background-color: #25D366;
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. SMART PARSER (Name & Message Extraction)
# -------------------------------------------------------------
def parse_command(user_text):
    t = user_text.lower()
    
    # Check WhatsApp Business / WhatsApp
    if any(k in t for k in ["whatsapp", "business", "wa", "sms", "message", "chat"]):
        # Extract Name
        name = ""
        # Match patterns like "love name ka", "love ko", "ghulam rasool ko"
        name_match = re.search(r'([a-zA-Z0-9_\s]+?)\s+(?:name|ko|ka|ki)\b', t)
        if name_match:
            candidate = name_match.group(1).strip()
            # remove trigger words
            for skip in ["whatsapp", "business", "main", "par", "per", "ok", "hi", "hello"]:
                candidate = re.sub(r'\b' + skip + r'\b', '', candidate, flags=re.IGNORECASE).strip()
            name = candidate
            
        # Extract Message
        msg_match = re.search(r'(?:kaho|bolo|likho|send|sms|message)\s+(.*)', t)
        msg_text = msg_match.group(1).strip() if msg_match else ""
        
        # If no explicit "kaho/bolo", take cleaned text
        if not msg_text:
            msg_text = t
            for skip in ["whatsapp", "business", "main", "kholo", "on", "karo", "person", "hai", "dakho", "chat", name]:
                msg_text = re.sub(r'\b' + skip + r'\b', '', msg_text, flags=re.IGNORECASE).strip()
                
        return {
            "type": "whatsapp_name",
            "name": name if name else "contact",
            "text": msg_text,
            "reply": f"Theek hai, main WhatsApp Business mein **'{name.capitalize()}'** ko search karke message send kar raha hoon!"
        }
        
    # Facebook
    if "facebook" in t or "fb" in t:
        return {"type": "open_app", "app": "facebook", "reply": "Facebook open kiya ja raha hai!"}
        
    # YouTube
    if "youtube" in t or "yt" in t:
        return {"type": "open_app", "app": "youtube", "reply": "YouTube open kiya ja raha hai!"}

    return None

# -------------------------------------------------------------
# 3. MACRODROID SENDER
# -------------------------------------------------------------
def send_to_macrodroid(params_dict):
    try:
        requests.get(MACRODROID_URL, params=params_dict, timeout=4)
        return True
    except Exception:
        return False

# -------------------------------------------------------------
# 4. UI & CHAT ENGINE
# -------------------------------------------------------------
st.markdown("<div class='main-header'><h2>🤖 My AI Phone Copilot</h2><p style='color:#6B7280;'>Live WhatsApp Business Contact Search</p></div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalam-o-Alaikum! Main aapka AI Phone Copilot hoon. Aap kisi bhi saved contact ka naam lein, main direct WhatsApp Business mein search karke message bhej dunga."}
    ]

for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    if role == "user":
        st.markdown(f"<div class='chat-bubble-user'>👤 {content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-ai'>🤖 {content}</div>", unsafe_allow_html=True)

user_input = st.chat_input("Bol kar ya likh kar command dein (e.g. Love ko WhatsApp par bolo ok good night)...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='chat-bubble-user'>👤 {user_input}</div>", unsafe_allow_html=True)

    parsed = parse_command(user_input)
    
    if parsed:
        ai_reply = parsed["reply"]
        if parsed["type"] == "whatsapp_name":
            send_to_macrodroid({
                "action": "search_whatsapp",
                "name": parsed["name"],
                "text": parsed["text"],
                "app": "whatsapp_business"
            })
        elif parsed["type"] == "open_app":
            send_to_macrodroid({
                "action": "open_app",
                "app": parsed["app"]
            })
    else:
        ai_reply = "Main aapke phone ka AI Copilot hoon. Batayein WhatsApp Business mein kis contact ko message bhejna hai?"

    st.markdown(f"<div class='chat-bubble-ai'>🤖 {ai_reply}</div>", unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
