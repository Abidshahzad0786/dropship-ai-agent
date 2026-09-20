import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image
import requests

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="AI Studio Copilot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- WHATSAPP / AI STUDIO LIGHT THEME CSS -----------------
st.markdown("""
<style>
    /* Clean Light Background */
    .stApp {
        background-color: #f0f2f5;
        color: #111b21;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 7rem;
        max-width: 850px;
    }
    
    /* WhatsApp / AI Studio Style Message Bubble */
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.08);
        border: none;
    }
    
    /* Floating Bottom Action Bar */
    .bottom-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #f0f2f5;
        padding: 8px 16px 14px 16px;
        border-top: 1px solid #e0e0e0;
        z-index: 999;
        display: flex;
        align-items: center;
        gap: 8px;
        max-width: 850px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

SYSTEM_INSTRUCTION = """
You are a direct, highly capable Personal Copilot & Business Partner.
1. Answer directly and practically without moral lectures, generic filler, or repetitive warnings.
2. Provide exact step-by-step solutions, code, calculations, and strategies.
3. For dropshipping / products: Calculate exact cost, shipping, TikTok/Shopify ad spend, and net margins.
"""

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.subheader("⚙️ Settings")
    api_key = st.text_input("Google AI Studio API Key", type="password", help="Paste your Gemini API key")
    
    mode = st.radio(
        "Mode",
        ["💬 Direct Chat & Business", "🎨 Photo Generator (AI)", "📊 Profit & Sourcing Math"]
    )
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ----------------- SESSION STATE -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- HEADER -----------------
st.markdown("""
<div style="text-align: center; margin-bottom: 1rem;">
    <h3 style="color: #00a884; margin: 0; font-weight: 700;">✨ AI Studio Copilot</h3>
    <p style="color: #667781; font-size: 13px; margin-top: 2px;">24/7 Autonomous Assistant</p>
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

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image" in msg:
            st.image(msg["image"], use_container_width=True)

# ----------------- WHATSAPP STYLE ATTACHMENT + SMS BAR -----------------
col_attach, col_input = st.columns([1, 4])

with col_attach:
    uploaded_file = st.file_uploader("📎", type=["png", "jpg", "jpeg", "webp"], help="Photo ya Document attach karein")

with col_input:
    user_prompt = st.chat_input("Message your Copilot...")

# ----------------- EXECUTION LOGIC -----------------
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
            with st.spinner("Thinking..."):
                # Strictly try 100% Free Tier Flash models to avoid 429 quota block
                success = False
                for flash_model in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-8b"]:
                    try:
                        model = genai.GenerativeModel(
                            model_name=flash_model,
                            system_instruction=SYSTEM_INSTRUCTION,
                            safety_settings=SAFETY_SETTINGS
                        )
                        response = model.generate_content(input_data)
                        output_text = response.text
                        st.markdown(output_text)
                        st.session_state.messages.append({"role": "assistant", "content": output_text})
                        success = True
                        break
                    except Exception as e:
                        continue
                
                if not success:
                    st.error("Error: Free Flash model connect nahi ho saka. AI Studio se 'Gemini API Key 2' check karein.")
