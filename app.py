import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image
import requests

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="AI Studio Hub",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- MOBILE RESPONSIVE & KEYBOARD SCROLL CSS -----------------
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
        color: #1f1f1f;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Auto Scroll & Chat Container */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 7.5rem;
        max-width: 850px;
        overflow-anchor: auto;
        scroll-behavior: smooth;
    }
    
    /* Clean Message Cards */
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e3e7ed;
    }
    
    p, span, div {
        color: #1f1f1f !important;
    }
    
    /* Pinned Bottom Container */
    div[data-testid="stChatInput"] {
        position: fixed;
        bottom: 8px;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

SYSTEM_INSTRUCTION = """
You are a direct, hyper-practical Personal Copilot & Business Partner.
1. Answer directly and concisely without moral lectures, generic filler, or repetitive warnings.
2. Provide exact step-by-step solutions, code, calculations, and execution roadmaps.
3. For dropshipping / products: Calculate exact cost, shipping, TikTok/Shopify ad spend, and net profit margins.
"""

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### ⚙️ **AI Studio Settings**")
    api_key = st.text_input("Google AI Studio API Key", type="password", help="Enter your Gemini API key")
    
    # Live Model Fetching Function
    @st.cache_data(show_spinner=False, ttl=600)
    def fetch_live_models(_key):
        model_options = {}
        try:
            genai.configure(api_key=_key)
            models = genai.list_models()
            for m in models:
                if 'generateContent' in m.supported_generation_methods:
                    clean_name = m.name.replace("models/", "")
                    if "flash" in clean_name.lower() or "lite" in clean_name.lower():
                        display_name = f"⚡ {clean_name} (Free Fast)"
                    else:
                        display_name = f"💎 {clean_name} (Pro / Advanced)"
                    model_options[display_name] = m.name
        except Exception:
            pass
        if not model_options:
            model_options = {
                "⚡ gemini-3.8-flash (Free Fast)": "models/gemini-3.8-flash",
                "⚡ gemini-3.7-flash (Free Fast)": "models/gemini-3.7-flash",
                "💎 gemini-3.1-pro-preview (Pro)": "models/gemini-3.1-pro-preview"
            }
        return model_options

    if api_key:
        available_models = fetch_live_models(api_key)
        selected_display = st.selectbox("🤖 Choose AI Model", list(available_models.keys()), index=0)
        selected_model_id = available_models[selected_display]
    else:
        selected_model_id = "models/gemini-3.8-flash"

    st.markdown("---")
    mode = st.radio(
        "Task Mode",
        ["💬 Direct Chat & Business", "🎨 Photo Generator (AI)", "📊 Profit & Sourcing Math"]
    )
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ----------------- SESSION STATE -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- HEADER -----------------
st.markdown(f"""
<div style="text-align: center; margin-bottom: 1rem;">
    <h3 style="color: #1a73e8; margin: 0; font-weight: 700;">✨ AI Studio Copilot</h3>
    <p style="color: #5f6368; font-size: 13px; margin-top: 2px;">Model: <b>{selected_model_id.replace('models/', '')}</b></p>
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.info("👈 Pehle sidebar (>> icon) khol kar apni Google AI Studio API Key paste karein.")
    st.stop()

# Configure API
genai.configure(api_key=api_key)

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

# ----------------- ATTACHMENT & INPUT (MOBILE BOTTOM PINNED) -----------------
with st.expander("📎 Attach Photo / File (Tap to open)", expanded=False):
    uploaded_file = st.file_uploader("Upload Media", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")

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
                        model_name=selected_model_id,
                        system_instruction=SYSTEM_INSTRUCTION,
                        safety_settings=SAFETY_SETTINGS
                    )
                    response = model.generate_content(input_data)
                    output_text = response.text
                    st.markdown(output_text)
                    st.session_state.messages.append({"role": "assistant", "content": output_text})
                except Exception as e:
                    st.error(f"Error ({selected_model_id}): {str(e)}")
