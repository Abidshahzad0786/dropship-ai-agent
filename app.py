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

# ----------------- MOBILE VIEWPORT & VISIBILITY CSS -----------------
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
        color: #1f1f1f;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Fixed Top Margin so nothing gets cut off */
    .block-container {
        padding-top: 3.8rem !important;
        padding-bottom: 7.5rem !important;
        max-width: 850px;
        margin: 0 auto;
    }
    
    /* Clean Cards for Chat */
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid #e3e7ed;
    }
    
    p, span, div, label {
        color: #1f1f1f !important;
    }
    
    /* Pinned Bottom Chat Input */
    div[data-testid="stChatInput"] {
        position: fixed;
        bottom: 10px;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

SYSTEM_INSTRUCTION = """
You are a direct, hyper-practical Personal Copilot & Business Partner.
1. Answer directly and concisely without moral lectures, disclaimers, or conversational fluff.
2. Provide exact step-by-step solutions, code, calculations, and execution roadmaps.
3. For dropshipping / products: Calculate exact cost, shipping, TikTok/Shopify ad spend, and net profit margins.
"""

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### ⚙️ **Studio Key**")
    api_key = st.text_input("Google AI Studio API Key", type="password", help="Paste your Gemini API key")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ----------------- SESSION STATE -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- MAIN TOP BAR (GOOGLE AI STUDIO STYLE) -----------------
st.markdown("<h3 style='margin:0; color:#1a73e8; font-weight:700;'>✨ AI Studio Copilot</h3>", unsafe_allow_html=True)

if not api_key:
    st.warning("👈 Pehle sidebar (>> icon) khol kar apni Google AI Studio API Key paste karein.")
    st.stop()

# Configure API
genai.configure(api_key=api_key)

# Dynamic Model Discovery with Latest Working Models
@st.cache_data(show_spinner=False, ttl=300)
def get_all_models(_key):
    model_dict = {}
    try:
        models = genai.list_models()
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                name = m.name.replace("models/", "")
                # Exclude retired models
                if "2.5-flash" in name:
                    continue
                tag = "⚡ Free Fast" if "flash" in name.lower() or "lite" in name.lower() else "💎 Pro"
                model_dict[f"{name} ({tag})"] = m.name
    except Exception:
        pass
    
    if not model_dict:
        model_dict = {
            "gemini-3.6-flash (⚡ Free Fast)": "models/gemini-3.6-flash",
            "gemini-3.8-flash (⚡ Free Fast)": "models/gemini-3.8-flash",
            "gemini-3.7-flash (⚡ Free Fast)": "models/gemini-3.7-flash",
            "gemini-3.5-flash-lite (⚡ Free Fast)": "models/gemini-3.5-flash-lite"
        }
    return model_dict

available_models = get_all_models(api_key)

# Top Bar Controls
col_model, col_mode = st.columns([2, 2])
with col_model:
    selected_label = st.selectbox("🤖 Model Selection", list(available_models.keys()), index=0)
    selected_model_id = available_models[selected_label]

with col_mode:
    mode = st.selectbox("🎯 Mode", ["💬 Chat & Business", "🎨 Photo Generator", "📊 Profit & Sourcing Math"])

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

# ----------------- ATTACHMENT BOX -----------------
with st.expander("📎 Photo / Document Attach Karein", expanded=False):
    uploaded_file = st.file_uploader("Upload Media", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")

# ----------------- BOTTOM INPUT -----------------
user_prompt = st.chat_input("Message your Copilot...")

# ----------------- EXECUTION LOGIC -----------------
if user_prompt or uploaded_file:
    if mode == "🎨 Photo Generator" and user_prompt:
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
