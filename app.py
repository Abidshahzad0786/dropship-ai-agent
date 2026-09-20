import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image
import requests
import streamlit.components.v1 as components

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Personal Copilot",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- MOBILE APP LOOK & VOICE CSS -----------------
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #111b21;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 7rem !important;
        max-width: 800px;
        margin: 0 auto;
    }
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
    div[data-testid="stChatInput"] {
        position: fixed;
        bottom: 12px;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

SYSTEM_INSTRUCTION = """
You are a direct, professional, and friendly Personal Copilot & eCommerce Partner.
Rules:
1. ONLY output the final direct response in natural language (Roman Urdu/English).
2. NEVER output your inner reasoning, thought process, or bullet breakdowns of the prompt.
3. Be helpful, concise, and provide exact calculations and solutions immediately.
"""

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### ⚙️ **Settings**")
    api_key = st.text_input("Google AI Studio API Key", type="password", help="Paste your Gemini key")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- HEADER -----------------
st.markdown("""
<div style="text-align: center; margin-bottom: 1rem;">
    <h3 style="color: #0b57d0; margin: 0; font-weight: 700;">🎙️ My Personal Pocket Copilot</h3>
    <p style="color: #5f6368; font-size: 13px; margin-top: 2px;">Voice | Vision | Autonomous Assistant</p>
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

def generate_image(prompt):
    return f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"

# Display Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image" in msg:
            st.image(msg["image"], use_container_width=True)

# ----------------- ATTACHMENT & VOICE TOOLS -----------------
col_att, col_v = st.columns([1, 1])
with col_att:
    with st.expander("📎 Photo / Document", expanded=False):
        uploaded_file = st.file_uploader("Upload Media", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")
with col_v:
    with st.expander("🎙️ Voice Command (Audio)", expanded=False):
        audio_file = st.audio_input("Mic dabayein aur bolein")

# ----------------- BOTTOM CHAT INPUT -----------------
user_prompt = st.chat_input("Apna task likhein ya mic use karein...")

# ----------------- EXECUTION LOGIC -----------------
if user_prompt or uploaded_file or audio_file:
    # 1. Image Generation
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

    # 2. Text, Photo, or Voice Processing
    else:
        input_data = []
        pil_image = None
        
        # Add Image if uploaded
        if uploaded_file:
            pil_image = Image.open(uploaded_file)
            input_data.append(pil_image)
            
        # Add Voice Audio if recorded
        if audio_file:
            audio_bytes = audio_file.read()
            input_data.append({"mime_type": "audio/wav", "data": audio_bytes})
            input_data.append("Is audio voice command ko suno aur iska mukammal jawab ya task execute karo.")

        # Add Text if provided
        if user_prompt:
            input_data.append(user_prompt)
            display_text = user_prompt
        elif audio_file:
            display_text = "🎙️ [Voice Note Sent]"
        else:
            display_text = "📎 [Photo Sent]"

        st.session_state.messages.append({"role": "user", "content": display_text})
        with st.chat_message("user"):
            st.markdown(display_text)
            if pil_image:
                st.image(pil_image, width=280)
                
        with st.chat_message("assistant"):
            with st.spinner("Thinking & Processing..."):
                response_text = None
                models_to_try = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-8b", "gemini-pro"]
                
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
                    st.error("Error: Connect nahi ho saka. Key check karein.")
