import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image
import requests

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="AI Copilot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- WHATSAPP / SMS STYLE MOBILE CSS -----------------
st.markdown("""
<style>
    /* Clean background & spacing */
    .stApp {
        background-color: #0e1621;
        color: #ffffff;
    }
    /* Hide top padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }
    /* Chat message bubble styling */
    .stChatMessage {
        border-radius: 14px;
        padding: 8px 12px;
        margin-bottom: 8px;
    }
    /* Fixed bottom input bar */
    div[data-testid="stChatInput"] {
        position: fixed;
        bottom: 10px;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- DIRECT SYSTEM PROMPT -----------------
SYSTEM_INSTRUCTION = """
You are a direct, practical, and highly capable Personal Copilot & Business Partner.
1. Answer directly and practically without moral lectures, generic filler, or repetitive warnings.
2. Provide exact step-by-step solutions, code, calculations, and business insights.
3. For dropshipping / products: Calculate exact cost, shipping, TikTok/Shopify ad spend, and net margins.
"""

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.subheader("⚙️ Settings")
    api_key = st.text_input("Google AI Studio API Key", type="password", help="Gemini API Key 2 yahan paste karein")
    
    # Default model is gemini-1.5-flash (Free & 100% working)
    selected_model = st.selectbox(
        "Model",
        ["gemini-1.5-flash", "gemini-1.5-flash-latest"],
        index=0
    )
    
    mode = st.radio(
        "Mode",
        ["💬 Direct Chat & Business", "🎨 Photo Generator (AI)", "📊 Profit & Sourcing Math"]
    )
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ----------------- SESSION STATE -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- HEADER -----------------
st.markdown("<h4 style='text-align: center; margin-bottom: 0;'>⚡ My Pocket Copilot</h4>", unsafe_allow_html=True)
st.caption("<div style='text-align: center;'>24/7 Smart Autonomous Assistant</div>", unsafe_allow_html=True)

# API Key check
if not api_key:
    st.warning("👈 Pehle sidebar (>> icon) khol kar apni Gemini API Key paste karein.")
    st.stop()

# Configure API
genai.configure(api_key=api_key)

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

# Image Gen Helper
def generate_image(prompt):
    return f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image" in msg:
            st.image(msg["image"], use_container_width=True)

# ----------------- ATTACHMENT UPLOAD BAR (SMS Style) -----------------
with st.expander("📎 Photo ya Document Attach Karein (Camera / Upload)", expanded=False):
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")

# ----------------- BOTTOM CHAT INPUT BAR -----------------
user_prompt = st.chat_input("Message...")

# ----------------- EXECUTION -----------------
if user_prompt or uploaded_file:
    if mode == "🎨 Photo Generator (AI)" and user_prompt:
        st.session_state.messages.append({"role": "user", "content": f"🎨 {user_prompt}"})
        with st.chat_message("user"):
            st.markdown(f"🎨 {user_prompt}")
            
        with st.chat_message("assistant"):
            with st.spinner("Photo generate ho rahi hai..."):
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
                st.image(pil_image, width=260)
                
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Uses gemini-1.5-flash to completely avoid 404 errors
                    model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        system_instruction=SYSTEM_INSTRUCTION,
                        safety_settings=SAFETY_SETTINGS
                    )
                    response = model.generate_content(input_data)
                    output_text = response.text
                    st.markdown(output_text)
                    st.session_state.messages.append({"role": "assistant", "content": output_text})
                except Exception as e:
                    st.error(f"Error: {str(e)}")
