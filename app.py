import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image
import requests
import re

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="My Personal Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- CLEAN UI CSS -----------------
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
        color: #111b21;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 7rem !important;
        max-width: 800px;
        margin: 0 auto;
    }
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border: 1px solid #e3e7ed;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    p, span, div {
        color: #111b21 !important;
        font-size: 15px;
    }
    div[data-testid="stChatInput"] {
        position: fixed;
        bottom: 8px;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- REASONING STRIPPER (CLEANS BULLETS) -----------------
def extract_clean_text(raw_text):
    if not raw_text:
        return ""
    lines = raw_text.strip().split("\n")
    cleaned = []
    for line in lines:
        l = line.strip().lower()
        if l.startswith(("•", "*", "-", "◦")) and any(k in l for k in ["user said", "goal:", "constraint", "roman urdu", "hindi", "friendly", "direct"]):
            continue
        cleaned.append(line)
    result = "\n".join(cleaned).strip()
    # Remove outer quotes if wrapped
    if result.startswith('"') and result.endswith('"') and len(result) > 2:
        result = result[1:-1].strip()
    return result if result else raw_text.strip()

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### ⚙️ **Settings**")
    api_key = st.text_input("Google AI Studio API Key", type="password", help="Paste your Gemini key")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- 1. HEADER (TOP) -----------------
st.markdown("""
<div style="text-align: center; margin-bottom: 1rem;">
    <h3 style="color: #0b57d0; margin: 0; font-weight: 700;">⚡ My Personal Copilot</h3>
    <p style="color: #5f6368; font-size: 13px; margin-top: 2px;">24/7 Voice | Vision | Autonomous Assistant</p>
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.info("👈 Pehle sidebar (>> icon) khol kar apni Google AI Studio Key paste karein.")
    st.stop()

# Configure API
genai.configure(api_key=api_key)

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

SYSTEM_INSTRUCTION = """
You are a friendly, hyper-practical Personal Copilot & eCommerce Partner.
Rules:
1. ALWAYS speak directly in easy, natural Roman Urdu.
2. NEVER output your inner reasoning, constraints, or thought process.
3. Keep answers concise, helpful, and direct.
"""

def generate_image(prompt):
    return f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"

# ----------------- 2. CHAT HISTORY (MIDDLE SCREEN) -----------------
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "image" in msg:
                st.image(msg["image"], use_container_width=True)

# ----------------- 3. CONTROLS DOCK (BILKUL NEECHE) -----------------
st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
bottom_col1, bottom_col2 = st.columns([1, 1])

with bottom_col1:
    with st.expander("📎 Photo / Document", expanded=False):
        uploaded_file = st.file_uploader("Media", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")

with bottom_col2:
    with st.expander("🎙️ Voice Mic", expanded=False):
        audio_file = st.audio_input("Audio", label_visibility="collapsed")

# ----------------- 4. BOTTOM INPUT BAR -----------------
user_prompt = st.chat_input("Message likhein ya photo prompt dein...")

# ----------------- 5. EXECUTION LOGIC -----------------
if user_prompt or uploaded_file or audio_file:
    # Photo Generation Check
    if user_prompt and (user_prompt.lower().startswith("photo:") or user_prompt.lower().startswith("image:")):
        clean_prompt = user_prompt.split(":", 1)[1].strip()
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_prompt)
            with st.chat_message("assistant"):
                with st.spinner("Photo bana raha hoon..."):
                    img_url = generate_image(clean_prompt)
                    st.image(img_url, use_container_width=True)
                    st.session_state.messages.append({"role": "assistant", "content": "Photo tayar hai:", "image": img_url})
        st.rerun()

    # Voice, Vision & Text Processing
    else:
        input_data = []
        pil_image = None
        
        if uploaded_file:
            pil_image = Image.open(uploaded_file)
            input_data.append(pil_image)
            
        if audio_file:
            audio_bytes = audio_file.read()
            input_data.append({"mime_type": "audio/wav", "data": audio_bytes})
            input_data.append("Is audio command ko sun kar sirf Roman Urdu mein direct aasan jawab do.")

        if user_prompt:
            input_data.append(user_prompt)
            display_text = user_prompt
        elif audio_file:
            display_text = "🎙️ [Voice Command Sent]"
        else:
            display_text = "📎 [Photo Attached]"

        st.session_state.messages.append({"role": "user", "content": display_text})
        
        # Call API
        models_to_try = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-3.6-flash", "gemini-pro"]
        try:
            live_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            models_to_try = live_models + models_to_try
        except Exception:
            pass

        response_text = None
        for model_name in models_to_try:
            try:
                m = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=SYSTEM_INSTRUCTION,
                    safety_settings=SAFETY_SETTINGS
                )
                res = m.generate_content(input_data)
                if res and res.text:
                    response_text = extract_clean_text(res.text)
                    break
            except Exception:
                continue

        if response_text:
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "⚠️ Connection issue, dobara try karein."})
            
        st.rerun()
