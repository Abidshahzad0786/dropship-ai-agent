import streamlit as st
import google.generativeai as genai
import requests
import json
import urllib.parse

# -------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# -------------------------------------------------------------
st.set_page_config(
    page_title="AI Super Copilot & Phone Controller",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# MacroDroid Webhook URL
MACRODROID_URL = "https://trigger.macrodroid.com/3b017816-7e27-4e32-ad33-fe6b0e595c96/ai_command"

# Custom Styling (Google AI Studio + WhatsApp Clean Theme)
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; color: #1F1F1F; }
    .chat-card {
        background-color: white;
        padding: 15px 20px;
        border-radius: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #E5E7EB;
    }
    .action-badge {
        background-color: #25D366;
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# API SETUP
# -------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY secret mein add nahi hai!")
    st.stop()

genai.configure(api_key=api_key)

# -------------------------------------------------------------
# PHONE ACTION CONTROLLER (Webhook Dispatcher)
# -------------------------------------------------------------
def trigger_phone_action(action_type, phone="", text="", app_name=""):
    """Phone par MacroDroid webhook trigger karta hai"""
    try:
        params = {
            "action": action_type,
            "phone": phone,
            "text": text,
            "app": app_name
        }
        res = requests.get(MACRODROID_URL, params=params, timeout=5)
        return True
    except Exception as e:
        return False

# -------------------------------------------------------------
# GEMINI MODEL WITH PHONE CONTROLLER SYSTEM INSTRUCTIONS
# -------------------------------------------------------------
SYSTEM_PROMPT = """
Aap aik All-in-One Executive AI Assistant aur Mobile Phone Copilot hain.
Aapka user Roman Urdu mein baat karta hai.

Phone Control Rules:
1. Jab user kahe WhatsApp par message bhejo, phone call lagao ya koi app kholo, aap direct tool/action format mein output denge.
2. Agar WhatsApp message bhejna ho to jawab ke aakhir mein aik secret JSON block shamil karein:
<<<ACTION:{"action":"whatsapp", "phone":"NUM_OR_NAME", "text":"MSG_CONTENT"}>>>
3. Hamesha direct, friendly aur insano jaisa Roman Urdu mein jawab dein. Faltoo lambi explanation na dein.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=SYSTEM_PROMPT
)

# -------------------------------------------------------------
# UI & CHAT ENGINE
# -------------------------------------------------------------
st.title("🤖 AI Personal Copilot & Phone Controller")
st.write("24/7 Voice & Action Assistant — Ab aapke mobile par direct control ke sath!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Past Messages
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    with st.chat_message(role):
        st.markdown(content)

# User Input
user_input = st.chat_input("Bol kar ya likh kar command dein (e.g., Ali ko WhatsApp par message bhej do)...")

if user_input:
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate Response from AI
    with st.chat_message("assistant"):
        with st.spinner("AI phone se connect ho raha hai..."):
            response = model.generate_content(user_input)
            raw_text = response.text

            # Check if Action exists in response
            action_triggered = False
            clean_text = raw_text

            if "<<<ACTION:" in raw_text:
                start = raw_text.find("<<<ACTION:") + len("<<<ACTION:")
                end = raw_text.find(">>>", start)
                action_json_str = raw_text[start:end]
                clean_text = raw_text[:raw_text.find("<<<ACTION:")].strip()

                try:
                    action_data = json.loads(action_json_str)
                    # Trigger Phone Webhook
                    success = trigger_phone_action(
                        action_type=action_data.get("action", "whatsapp"),
                        phone=action_data.get("phone", ""),
                        text=action_data.get("text", "")
                    )
                    if success:
                        action_triggered = True
                except Exception:
                    pass

            st.markdown(clean_text)

            if action_triggered:
                st.success("⚡ Command aapke mobile phone par bhej di gayi hai!")

            # Store Clean Message
            st.session_state.messages.append({"role": "assistant", "content": clean_text})
