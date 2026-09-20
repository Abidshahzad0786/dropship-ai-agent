import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image
import requests
import streamlit.components.v1 as components

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="AI Pocket Assistant",
    page_icon="🎙️",
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
        padding-top: 1.5rem !important;
        padding-bottom: 8rem !important;
        max-width: 800px;
        margin: 0 auto;
    }
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border: 1px solid #e3e7ed;
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

# Function to speak aloud using browser TTS
def play_voice_response(text):
    clean_text = text.replace('"', '').replace("'", "").replace("\n", " ")
    js_code = f"""
    <script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{clean_text}");
        msg.lang = 'hi-IN'; // Natural Urdu/Hindi accent
        msg.rate = 1.0;
        window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(js_code, height=0)

SYSTEM_INSTRUCTION = """
You are a direct, professional Personal Voice Assistant & eCommerce Partner.
Rules:
1. ALWAYS reply in natural, easy Roman Urdu (e.g., 'Salam! Main aapki kya madad kar sakta hoon?').
2. NEVER use Hindi script (Devanagari) or Arabic script. Strictly Roman Urdu/English.
3. Keep spoken replies short, natural, and direct.
4. Execute calculations, photo prompts, and business advice immediately.
"""

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### ⚙️ **Settings**")
    api_key = st.text_input("Google AI Studio API Key", type="password", help="Paste your Gemini key")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- HEADER -----------------
st.markdown("""
<div style="text-align: center; margin-bottom: 1rem;">
    <h3 style="color: #0b57d0; margin: 0; font-weight: 700;">🎙️ Personal Voice & Task Assistant</h3>
    <p style="color: #5f6368; font-size: 13px; margin-top: 2px;">Voice In | Voice Out | Task Automation</p>
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

# ----------------- BOTTOM CONTROLS (Right above Chat Input) -----------------
st.markdown("---")
col1, col2 = st.columns([1, 1])
with col1:
    with st.expander("📎 Photo / File Attach", expanded=False):
        uploaded_file = st.file_uploader("Upload", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")
with col2:
    with st.expander("🎙️ Live Voice Mic", expanded=False):
        audio_file = st.audio_input("Mic dabayein aur bolein", label_visibility="collapsed")

# Bottom Input
user_prompt = st.chat_input("Message or ask anything...")

# ----------------- EXECUTION -----------------
if user_prompt or uploaded_file or audio_file:
    # 1. Image Generation
    if user_prompt and (user_prompt.lower().startswith("photo:") or user_prompt.lower().startswith("image:")):
        clean_prompt = user_prompt.split(":", 1)[1].strip()
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Photo bana raha hoon..."):
                img_url = generate_image(clean_prompt)
                st.image(img_url, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": "Photo tayar hai:", "image": img_url})
                play_voice_response("Photo tayar hai")

    # 2. Voice & Text Conversation
    else:
        input_data = []
        pil_image = None
        
        if uploaded_file:
            pil_image = Image.open(uploaded_file)
            input_data.append(pil_image)
            
        if audio_file:
            audio_bytes = audio_file.read()
            input_data.append({"mime_type": "audio/wav", "data": audio_bytes})
            input_data.append("Is audio ko sun kar sirf Roman Urdu mein direct aasan jawab do.")

        if user_prompt:
            input_data.append(user_prompt)
            display_text = user_prompt
        elif audio_file:
            display_text = "🎙️ [Voice Command]"
        else:
            display_text = "📎 [Photo Uploaded]"

        st.session_state.messages.append({"role": "user", "content": display_text})
        with st.chat_message("user"):
            st.markdown(display_text)
            if pil_image:
                st.image(pil_image, width=280)
                
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                response_text = None
                models_to_try = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-3.6-flash", "gemini-pro"]
                
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
                    # Plays voice out of mobile speaker
                    play_voice_response(response_text)
                else:
                    st.error("Error: Connect nahi ho saka.")
