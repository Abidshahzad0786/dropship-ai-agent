import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image
import requests

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="My Personal Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- CLEAN MOBILE APP CSS -----------------
st.markdown("""
<style>
    /* Full White Clean Mobile Look */
    .stApp {
        background-color: #ffffff;
        color: #111b21;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 6.5rem !important;
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* Clean Message Bubbles */
    [data-testid="stChatMessage"] {
        background-color: #f0f2f5;
        border-radius: 16px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border: none;
    }
    
    p, span, div {
        color: #111b21 !important;
        font-size: 15px;
    }
    
    /* Fixed Bottom Input */
    div[data-testid="stChatInput"] {
        position: fixed;
        bottom: 12px;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SYSTEM PROMPT -----------------
SYSTEM_INSTRUCTION = """
You are a private, direct, and highly intelligent Personal Copilot & Business Partner.
1. Answer directly and concisely without moral lectures, generic filler, or repetitive warnings.
2. Provide exact solutions, business calculations, unit economics, and dropshipping profit margins.
3. Analyze images, products, receipts, and documents with high precision.
"""

# ----------------- SIDEBAR (ONLY API KEY & RESET) -----------------
with st.sidebar:
    st.markdown("### ⚙️ **Settings**")
    api_key = st.text_input("Google AI Studio API Key", type="password", help="Paste your Gemini key")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ----------------- SESSION STATE -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- HEADER -----------------
st.markdown("""
<div style="text-align: center; margin-bottom: 1.2rem;">
    <h3 style="color: #0b57d0; margin: 0; font-weight: 700;">⚡ My Personal Copilot</h3>
    <p style="color: #5f6368; font-size: 13px; margin-top: 3px;">24/7 Smart Autonomous Assistant</p>
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

# Image helper
def generate_image(prompt):
    return f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"

# Display Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image" in msg:
            st.image(msg["image"], use_container_width=True)

# ----------------- ATTACHMENT BOX -----------------
with st.expander("📎 Photo / Document Attach Karein (Camera / Gallery)", expanded=False):
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")

# ----------------- BOTTOM CHAT INPUT -----------------
user_prompt = st.chat_input("Apna task, sawal ya photo prompt likhein...")

# ----------------- AUTO-FALLBACK ENGINE -----------------
if user_prompt or uploaded_file:
    # 1. Image Generation Check
    if user_prompt and (user_prompt.lower().startswith("photo:") or user_prompt.lower().startswith("image:") or user_prompt.lower().startswith("generate:")):
        clean_prompt = user_prompt.split(":", 1)[1].strip() if ":" in user_prompt else user_prompt
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Photo ban rahi hai..."):
                img_url = generate_image(clean_prompt)
                st.image(img_url, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": "Photo tayar hai:", "image": img_url})

    # 2. General Chat / Analysis / Dropshipping
    elif user_prompt:
        input_data = []
        pil_image = None
        
        if uploaded_file:
            pil_image = Image.open(uploaded_file)
            input_data.append(pil_image)
            
        input_data.append(user_prompt)
        
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
            if pil_image:
                st.image(pil_image, width=280)
                
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Dynamically tries models until a working one responds
                response_text = None
                models_to_try = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-8b", "gemini-pro"]
                
                # Also check all available live models from user's key
                try:
                    live_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    models_to_try = live_models + models_to_try
                except Exception:
                    pass

                for model_name in models_to_try:
                    try:
                        m = genai.GenerativeModel(
                            model_name=model_name,
                            system_instruction=SYSTEM_INSTRUCTION,
                            safety_settings=SAFETY_SETTINGS
                        )
                        res = m.generate_content(input_data)
                        if res and res.text:
                            response_text = res.text
                            break
                    except Exception:
                        continue
                
                if response_text:
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                else:
                    st.error("Error: Key connect nahi ho saki. Please Google AI Studio se 'Gemini API Key 2' check karein.")
