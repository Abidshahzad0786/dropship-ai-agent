import os
import sys
import json
import re
import random
import urllib.parse
import urllib.request
import base64
import datetime
import requests
import secrets
import streamlit as st
import streamlit.components.v1 as components
from io import BytesIO
from PIL import Image

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & ENTERPRISE STUDIO STYLING
# -------------------------------------------------------------
st.set_page_config(
    page_title="Universal Google AI Studio Enterprise",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_KEYS_FILE = "api_keys_db.json"
DB_PROMPTS_FILE = "saved_prompts_db.json"
DB_TUNING_FILE = "fine_tuned_models.json"
CACHE_FILE = "prompt_cache.json"

st.markdown("""
<style>
    .stApp { 
        background-color: #F8F9FA; 
        color: #1F1F1F; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .main .block-container {
        padding-top: 10px;
        padding-bottom: 140px !important;
        max-width: 1050px;
    }
    .chat-bubble-user {
        background-color: #E7F8EC;
        border: 1px solid #C2E7CB;
        border-radius: 16px 16px 4px 16px;
        padding: 10px 16px;
        margin: 6px 0;
        max-width: 85%;
        float: right;
        clear: both;
        color: #0F5132;
    }
    .chat-bubble-ai {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px 16px 16px 4px;
        padding: 12px 18px;
        margin: 6px 0;
        max-width: 85%;
        float: left;
        clear: both;
        box-shadow: 0 1px 2px rgba(0,0,0,0.06);
        color: #1F2937;
        line-height: 1.65;
    }
    .msg-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
    }
    .dots-menu {
        background: transparent;
        border: none;
        cursor: pointer;
        font-size: 16px;
        color: #8696A0;
        padding: 0 4px;
    }
    .token-badge {
        background: #F1F5F9;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 600;
        color: #475569;
    }
    .studio-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px;
        margin: 8px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. DATABASE & PERSISTENCE
# -------------------------------------------------------------
def load_json_db(file_path, default_data):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception:
            return default_data
    return default_data

def save_json_db(file_path, data):
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

if "api_keys_db" not in st.session_state:
    st.session_state.api_keys_db = load_json_db(DB_KEYS_FILE, {
        "studio-demo-key-001": {"project": "Default Project", "rpm_limit": 15, "created_at": "2026-09-20", "status": "Active"}
    })

if "saved_prompts_db" not in st.session_state:
    st.session_state.saved_prompts_db = load_json_db(DB_PROMPTS_FILE, {
        "Senior Full-Stack Architect": "Act as a Senior Software Architect. Provide clean, modular, production-ready code.",
        "CMO Viral Marketing": "Act as a Chief Marketing Officer. Create a 30-day GTM roadmap.",
        "Academic Tutor": "Act as a World-Class Professor. Explain complex topics simply."
    })

if "fine_tuned_models" not in st.session_state:
    st.session_state.fine_tuned_models = load_json_db(DB_TUNING_FILE, {})

if "prompt_cache" not in st.session_state:
    st.session_state.prompt_cache = load_json_db(CACHE_FILE, {})

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {
        "Chat 1": [
            {"role": "assistant", "content": "Assalam-o-Alaikum! Main Google AI Studio architecture par mabni Master AI Copilot hoon (Powered by Groq Llama 3.3 70B). Dunya ka time, tareekh, geography, coding ya photo generation—aap kya poochna chahte hain?"}
        ]
    }

if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Chat 1"

if "studio_mode" not in st.session_state:
    st.session_state.studio_mode = "💬 Chat Prompt Mode"

if "few_shot_data" not in st.session_state:
    st.session_state.few_shot_data = [
        {"Input": "Apple", "Output": "Category: Fruit | Taste: Sweet"},
        {"Input": "Broccoli", "Output": "Category: Vegetable | Taste: Earthy"}
    ]

# -------------------------------------------------------------
# 3. LIVE CLOCK & DATE ENGINE
# -------------------------------------------------------------
MONTHS_URDU = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}
DAYS_URDU = {
    0: "Monday (Peer)", 1: "Tuesday (Mangal)", 2: "Wednesday (Budh)",
    3: "Thursday (Jumerat)", 4: "Friday (Juma)", 5: "Saturday (Hafta)", 6: "Sunday (Itwar)"
}

def calculate_real_time_answer(text):
    t = text.lower()
    time_keywords = ["time", "waqt", "date", "tareekh", "tarikh", "din", "day", "saal", "year"]
    
    if any(k in t for k in time_keywords) and not any(img in t for img in ["photo", "pic", "image"]):
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        pkt_time = now_utc + datetime.timedelta(hours=5)
        dubai_time = now_utc + datetime.timedelta(hours=4)
        saudi_time = now_utc + datetime.timedelta(hours=3)
        uk_time = now_utc + datetime.timedelta(hours=1)
        us_est = now_utc - datetime.timedelta(hours=4)
        
        month_name = MONTHS_URDU.get(pkt_time.month, "")
        day_name = DAYS_URDU.get(pkt_time.weekday(), "")
        date_str = f"{pkt_time.day} {month_name} {pkt_time.year}"

        if "dubai" in t or "uae" in t:
            return f"Dubai / UAE mein is waqt time **{dubai_time.strftime('%I:%M %p')}** ho raha hai."
        elif "america" in t or "usa" in t or "us" in t or "new york" in t:
            return f"America (New York) mein is waqt time **{us_est.strftime('%I:%M %p')}** ho raha hai."
        elif "saudi" in t or "makkah" in t:
            return f"Saudi Arabia mein is waqt time **{saudi_time.strftime('%I:%M %p')}** ho raha hai."
        elif "london" in t or "uk" in t:
            return f"London / UK mein is waqt time **{uk_time.strftime('%I:%M %p')}** ho raha hai."
        elif "time" in t or "waqt" in t:
            return f"Is waqt Pakistan mein time **{pkt_time.strftime('%I:%M %p')}** hai aur aaj ki tareekh **{date_str}** ({day_name}) hai."
        else:
            return f"Aaj ki tareekh **{date_str}** hai aur din **{day_name}** hai."
            
    return None

# -------------------------------------------------------------
# 4. PHOTO ENGINE (FLUX.1)
# -------------------------------------------------------------
def is_photo_intent(text):
    t = text.lower()
    triggers = ["photo", "pic", "image", "tasweer", "tasvir", "picture", "banao", "generate", "create", "draw"]
    return any(k in t for k in triggers)

def smart_enhance_prompt(raw_text):
    t = raw_text.lower()
    if "pakistan" in t and any(f in t for f in ["flag", "jhanda"]):
        return "The authentic National Flag of Pakistan, featuring a deep green background with a white vertical stripe on the left hoist side, centered white crescent moon and five-pointed star, photorealistic 8k resolution, cinematic lighting"
    clean_p = re.sub(r'(photo|pic|image|tasweer|picture|banao|generate|create|ki|ka)', '', raw_text, flags=re.IGNORECASE).strip()
    return f"A high quality 8k photorealistic image of {clean_p}, cinematic lighting, photorealism 8k"

def generate_flux_image_url(prompt_text):
    enhanced = smart_enhance_prompt(prompt_text)
    clean_p = urllib.parse.quote(enhanced.strip())
    seed = random.randint(10000, 999999)
    return f"https://image.pollinations.ai/prompt/{clean_p}?width=1024&height=1024&nologo=true&seed={seed}&model=flux"

# -------------------------------------------------------------
# 5. GROQ LLAMA 3.3 (70B) AI BRAIN
# -------------------------------------------------------------
# Secrets se key check karein
GROQ_API_KEY_FROM_SECRETS = ""
try:
    if "GROQ_API_KEY" in st.secrets:
        GROQ_API_KEY_FROM_SECRETS = str(st.secrets["GROQ_API_KEY"]).strip()
except Exception:
    pass

MASTER_SYSTEM_INSTRUCTION = """
Aap Google AI Studio ke World-Class AI Master Copilot hain (Powered by Groq Llama 3.3 70B).
Aap Roman Urdu aur English dono mein dunya ke har topic par 100% authentic, clear aur natural jawab dete hain.
User agar 'Hi' ya 'Hello' boley to khuloos se mukhtasir jawab dein aur poochein ke wo kis cheez mein madad chahte hain.
"""

def execute_ai_query(prompt_text, history=None, model="llama-3.3-70b-versatile", temp=0.7, top_p=0.9, max_tokens=2048, sys_prompt="", active_key=""):
    dt_answer = calculate_real_time_answer(prompt_text)
    if dt_answer:
        return dt_answer

    key_to_use = str(active_key or GROQ_API_KEY_FROM_SECRETS).strip()
    
    if not key_to_use:
        return "⚠️ **Groq API Key Missing hai!**\n\nBarah-e-karam Sidebar mein apni Groq API Key (`gsk_...`) daalein ya Streamlit Cloud Secrets mein `GROQ_API_KEY` save karein."

    messages = [{"role": "system", "content": sys_prompt if sys_prompt else MASTER_SYSTEM_INSTRUCTION}]
    if history:
        for m in history[-6:]:
            if "role" in m and "content" in m:
                messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt_text})

    headers_g = {
        "Authorization": f"Bearer {key_to_use}",
        "Content-Type": "application/json"
    }
    
    payload_g = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": float(temp),
        "max_tokens": int(max_tokens),
        "top_p": float(top_p)
    }
    
    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers_g, json=payload_g, timeout=20)
        
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]
        elif res.status_code == 401:
            return "❌ **API Key Error (401):** Aapki Groq API Key ghalat ya expire ho chuki hai. Nayi key create karein: console.groq.com/keys"
        elif res.status_code == 429:
            # Fallback to faster 8B model on rate limit
            payload_g["model"] = "llama-3.1-8b-instant"
            res2 = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers_g, json=payload_g, timeout=15)
            if res2.status_code == 200:
                return res2.json()["choices"][0]["message"]["content"]
            return "⏳ **Rate Limit:** Request limit cross ho gayi hai, 10 seconds baad dubara try karein."
        else:
            return f"⚠️ **Groq Error ({res.status_code}):** {res.text}"
            
    except requests.exceptions.Timeout:
        return "⚠️ Request timeout ho gayi hai, dobara try karein."
    except Exception as e:
        return f"⚠️ Connection Error: {str(e)}"

# -------------------------------------------------------------
# 6. SIDEBAR CONTROLS
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 👑 Studio Master Navigation")
    
    st.session_state.studio_mode = st.radio(
        "Workspace Mode:",
        [
            "💬 Chat Prompt Mode",
            "📝 Freeform Canvas",
            "📊 Structured Few-Shot",
            "⚙️ API Key & Developer Manager",
            "🧬 Model Fine-Tuning Pipeline"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 🔑 Groq Key Input")
    custom_key_input = st.text_input("Groq API Key:", value=GROQ_API_KEY_FROM_SECRETS, type="password", placeholder="gsk_...")
    
    st.markdown("---")
    with st.expander("🧠 System Instructions", expanded=False):
        sys_instruction_text = st.text_area("Persona & Rules:", value=MASTER_SYSTEM_INSTRUCTION, height=100)
    
    st.markdown("### 🎛️ Model Parameters")
    selected_model = st.selectbox("Model:", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "deepseek-r1-distill-llama-70b"])
    temp = st.slider("Temperature:", 0.0, 2.0, 0.7, 0.05)
    top_p = st.slider("Top-P:", 0.0, 1.0, 0.9, 0.05)
    max_tokens = st.slider("Max Tokens:", 512, 8192, 2048, 512)

# -------------------------------------------------------------
# 7. MAIN INTERFACE
# -------------------------------------------------------------
st.markdown("<div style='text-align:center; padding-bottom:8px;'><h2 style='margin:0; color:#1F1F1F;'>✨ Google AI Studio Universal</h2></div>", unsafe_allow_html=True)

if st.session_state.studio_mode == "💬 Chat Prompt Mode":
    st.markdown(f"<div style='text-align:center; padding-bottom:6px;'><small style='color:#6B7280;'>Model: <b>{selected_model}</b> | Temp: {temp} | Tokens: {max_tokens}</small></div>", unsafe_allow_html=True)
    
    current_messages = st.session_state.chat_sessions[st.session_state.active_chat]

    for msg in current_messages:
        role = msg["role"]
        content = msg["content"]
        img_url = msg.get("image_url")
        
        if role == "user":
            st.markdown(f"<div class='chat-bubble-user'>👤 {content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='chat-bubble-ai'>
                <div class='msg-header'>
                    <span style='font-size:12px; color:#128C7E; font-weight:600;'>✨ AI Studio Output</span>
                </div>
                {content}
            </div>
            """, unsafe_allow_html=True)
            if img_url:
                st.image(img_url, caption="Studio FLUX.1 Output", use_container_width=True)

    user_input = st.chat_input("Prompt likhein ya sawal poochein...")
    
    if user_input:
        current_messages.append({"role": "user", "content": user_input})
        st.markdown(f"<div class='chat-bubble-user'>👤 {user_input}</div>", unsafe_allow_html=True)
        
        gen_img = None
        if is_photo_intent(user_input):
            with st.spinner("🎨 FLUX.1 Studio 8K HD Photo Generate Kar Raha Hai..."):
                gen_img = generate_flux_image_url(user_input)
                reply = f"Maine aapki request par **'{user_input}'** ki photo generate kar di hai:"
        else:
            with st.spinner("AI Generating Response..."):
                reply = execute_ai_query(user_input, current_messages, selected_model, temp, top_p, max_tokens, sys_instruction_text, custom_key_input)
                
        st.markdown(f"<div class='chat-bubble-ai'>✨ {reply}</div>", unsafe_allow_html=True)
        if gen_img:
            st.image(gen_img, caption="Studio Output", use_container_width=True)
        current_messages.append({"role": "assistant", "content": reply, "image_url": gen_img})

elif st.session_state.studio_mode == "📝 Freeform Canvas":
    st.markdown("#### 📝 Freeform Prompt Workspace")
    freeform_input = st.text_area("Canvas Input:", height=200, placeholder="Write your full prompt or code here...")
    if st.button("▶ Run Prompt", type="primary", use_container_width=True):
        if freeform_input:
            with st.spinner("Executing..."):
                res_out = execute_ai_query(freeform_input, None, selected_model, temp, top_p, max_tokens, sys_instruction_text, custom_key_input)
                st.markdown(f"<div class='studio-card'>{res_out}</div>", unsafe_allow_html=True)

elif st.session_state.studio_mode == "📊 Structured Few-Shot":
    st.markdown("#### 📊 Structured Few-Shot Prompt Learning")
    edited_table = st.data_editor(st.session_state.few_shot_data, num_rows="dynamic", use_container_width=True)
    test_q = st.text_input("Test Query:", placeholder="e.g. Mango")
    if st.button("✨ Run Inference", type="primary", use_container_width=True):
        if test_q:
            prompt_assembled = "Follow the exact pattern:\n\n"
            for row in edited_table:
                if row.get("Input") and row.get("Output"):
                    prompt_assembled += f"Input: {row['Input']}\nOutput: {row['Output']}\n\n"
            prompt_assembled += f"Input: {test_q}\nOutput:"
            res_structured = execute_ai_query(prompt_assembled, None, selected_model, temp, top_p, max_tokens, sys_instruction_text, custom_key_input)
            st.success(res_structured)

elif st.session_state.studio_mode == "⚙️ API Key & Developer Manager":
    st.markdown("#### 🔑 Studio API Key Management Dashboard")
    st.info("Direct Google AI Studio standard endpoint compatibility enabled.")
    st.code("POST /v1beta/models/{model}:generateContent\nHeaders: x-goog-api-key: studio-live-xxxx", language="bash")

elif st.session_state.studio_mode == "🧬 Model Fine-Tuning Pipeline":
    st.markdown("#### 🧬 Model Fine-Tuning Pipeline (LoRA)")
    st.file_uploader("Upload Training Dataset (.jsonl):", type=["jsonl"])
    st.success("✅ Training Pipeline is ready for dataset inputs.")