import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image
import requests

# ----------------- PAGE CONFIGURATION -----------------
st.set_page_config(
    page_title="Personal Super Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- STRICT DIRECT SYSTEM PROMPT -----------------
SYSTEM_INSTRUCTION = """
You are a direct, highly technical, and completely practical Open-Source Style AI Assistant.
Rules of Engagement:
1. Always give the exact solution, step-by-step roadmap, or code immediately.
2. Do not include unnecessary warnings, moral lectures, or conversational filler.
3. Solve complex technical, eCommerce, automation, and data analysis tasks efficiently.
4. If the user asks how something works technically or how to configure/automate a system, provide the cleanest, most direct technical procedure.
"""

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.title("⚡ Copilot Engine")
    api_key = st.text_input("Google AI Studio API Key", type="password")
    
    selected_model = st.selectbox(
        "AI Model",
        ["gemini-1.5-flash", "gemini-1.5-pro"],
        index=0
    )
    
    st.markdown("---")
    mode = st.radio(
        "Mode", 
        ["🛠️ Direct Technical & Business Copilot", "🎨 AI Image Generator", "📊 Profit & Sourcing Calculator"]
    )
    
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# ----------------- SESSION STATE -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- MAIN UI -----------------
st.title("⚡ My Private Multimodal Assistant")

if not api_key:
    st.info("👈 Sidebar mein apni Google AI Studio API key paste karein.")
    st.stop()

# Configure GenAI
genai.configure(api_key=api_key)

# Relaxed safety settings so standard technical tasks don't get blocked
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

# Image helper
def generate_image(prompt):
    return f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image" in msg:
            st.image(msg["image"], use_container_width=True)

# Input Layout
col1, col2 = st.columns([3, 1])
with col2:
    uploaded_file = st.file_uploader("📎 Media/Document", type=["png", "jpg", "jpeg", "webp"])

with col1:
    user_prompt = st.chat_input("Apna task ya technical sawal likhein...")

# Logic Execution
if user_prompt or uploaded_file:
    if mode == "🎨 AI Image Generator" and user_prompt:
        st.session_state.messages.append({"role": "user", "content": f"🎨 Generate: {user_prompt}"})
        with st.chat_message("user"):
            st.markdown(f"🎨 Generate: {user_prompt}")
            
        with st.chat_message("assistant"):
            with st.spinner("Creating image..."):
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
        if mode == "📊 Profit & Sourcing Calculator":
            final_prompt = f"[TASK: Calculate Exact Unit Economics, Ad Spend, and Sourcing Feasibility]\n{user_prompt}"
            
        input_data.append(final_prompt)
        
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
            if pil_image:
                st.image(pil_image, width=300)
                
        with st.chat_message("assistant"):
            with st.spinner("Processing solution..."):
                try:
                    model = genai.GenerativeModel(
                        model_name=selected_model,
                        system_instruction=SYSTEM_INSTRUCTION,
                        safety_settings=SAFETY_SETTINGS
                    )
                    response = model.generate_content(input_data)
                    output_text = response.text
                    st.markdown(output_text)
                    st.session_state.messages.append({"role": "assistant", "content": output_text})
                except Exception as e:
                    st.error(f"Error: {str(e)}")
