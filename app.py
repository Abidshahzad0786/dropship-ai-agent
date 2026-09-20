import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image
import requests

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="AI Studio Copilot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- GOOGLE AI STUDIO CLEAN LIGHT THEME -----------------
st.markdown("""
<style>
    /* Main Clean Light Background */
    .stApp {
        background-color: #f8f9fa;
        color: #1f1f1f;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Clean Chat Containers */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 6rem;
        max-width: 900px;
    }
    
    /* Google AI Studio Style Message Bubbles */
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border: 1px solid #e3e7ed;
        border-radius: 16px;
        padding: 12px 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        color: #1f1f1f;
    }
    
    /* Make text super sharp and visible */
    p, span, label, div {
        color: #1f1f1f !important;
        font-size: 15px;
    }

    /* Fixed Bottom Input Bar */
    div[data-testid="stChatInput"] {
        position: fixed;
        bottom: 12px;
        z-index: 999;
    }
    
    div[data-testid="stChatInput"] > div {
        background-color: #ffffff !important;
        border: 1px solid #c4c7c5 !important;
        border-radius: 28px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;
    }
</style>
""", unsafe_allow_html=True)

SYSTEM_INSTRUCTION = """
You are a direct, highly capable Personal Copilot & Business Partner.
1. Answer directly, practically, and concisely without moral lectures, generic filler, or repetitive warnings.
2. Provide exact step-by-step solutions, code, calculations, and strategies.
3. For dropshipping / products: Calculate exact cost, shipping, TikTok/Shopify ad spend, and net margins.
"""

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### ⚙️ **Studio Settings**")
    api_key = st.text_input("Google AI Studio API Key", type="password", help="Paste your API key here")
    
    mode = st.radio(
        "Mode",
        ["💬 Direct Chat & Business", "🎨 Photo Generator (AI)", "📊 Profit & Sourcing Math"]
    )
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ----------------- SESSION STATE -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- HEADER -----------------
st.markdown("""
<div style="text-align: center; margin-bottom: 1.5rem;">
    <h2 style="color: #1a73e8; margin: 0; font-weight: 600;">✨ AI Studio Copilot</h2>
    <p style="color: #5f6368; font-size: 14px; margin-top: 4px;">Multimodal Autonomous Workspace</p>
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.info("👈 Pehle sidebar (>> icon) khol kar apni Google AI Studio API Key paste karein.")
    st.stop()

# Configure API
genai.configure(api_key=api_key)

# Dynamic Model Finder (Avoids 404 permanently)
@st.cache_resource(show_spinner=False)
def get_best_model(_api_key):
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for pref in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"]:
            for m in available:
                if pref in m:
                    return m
        if available:
            return available[0]
    except Exception:
        pass
    return "models/gemini-1.5-flash"

ACTIVE_MODEL_NAME = get_best_model(api_key)

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

def generate_image(prompt):
    return f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"

# Display Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image" in msg:
            st.image(msg["image"], use_container_width=True)

# ----------------- SMS STYLE ATTACHMENT BOX -----------------
with st.expander("📎 Attach Photo / File (Tap to open)", expanded=False):
    uploaded_file = st.file_uploader("Upload Media", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")

# ----------------- BOTTOM INPUT BAR -----------------
user_prompt = st.chat_input("Message your Copilot...")

# ----------------- EXECUTION -----------------
if user_prompt or uploaded_file:
    if mode == "🎨 Photo Generator (AI)" and user_prompt:
        st.session_state.messages.append({"role": "user", "content": f"🎨 {user_prompt}"})
        with st.chat_message("user"):
            st.markdown(f"🎨 {user_prompt}")
            
        with st.chat_message("assistant"):
            with st.spinner("Generating photo..."):
                img_url = generate_image(user_prompt)
                st.image(img_url, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": "Photo tayar hai:", "image": img_url})

    elif user_prompt:
        input_data = []
        pil_image = None
        
        if uploaded_file:
            pil_image = Image.open(uploaded_file)
            input_data.append(pil_image)
            
        final_prompt = user_prompt
        if mode == "📊 Profit & Sourcing Math":
            final_prompt = f"[TASK: Calculate Exact Unit Economics, Ad Spend & Profit]\n{user_prompt}"
            
        input_data.append(final_prompt)
        
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
            if pil_image:
                st.image(pil_image, width=280)
                
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                try:
                    model = genai.GenerativeModel(
                        model_name=ACTIVE_MODEL_NAME,
                        system_instruction=SYSTEM_INSTRUCTION,
                        safety_settings=SAFETY_SETTINGS
                    )
                    response = model.generate_content(input_data)
                    output_text = response.text
                    st.markdown(output_text)
                    st.session_state.messages.append({"role": "assistant", "content": output_text})
                except Exception as e:
                    st.error(f"Error: {str(e)}")
