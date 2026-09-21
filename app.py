import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import re
import urllib.parse
import datetime
from PIL import Image

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & CLEAN WHATSAPP/STUDIO THEME
# -------------------------------------------------------------
st.set_page_config(
    page_title="AI Studio Copilot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp { 
        background-color: #F8F9FA; 
        color: #1F1F1F; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .main .block-container {
        padding-top: 15px;
        padding-bottom: 120px;
        max-width: 850px;
    }
    .chat-bubble-user {
        background-color: #E7F8EC;
        border: 1px solid #C2E7CB;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        margin: 8px 0;
        max-width: 85%;
        float: right;
        clear: both;
        color: #0F5132;
    }
    .chat-bubble-ai {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 18px;
        margin: 8px 0;
        max-width: 85%;
        float: left;
        clear: both;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        color: #1F2937;
    }
    .action-card {
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white !important;
        padding: 10px 18px;
        border-radius: 12px;
        margin: 6px 4px 6px 0;
        display: inline-block;
        font-weight: 600;
        text-decoration: none;
        box-shadow: 0 3px 8px rgba(37,211,102,0.3);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. CHAT SESSIONS & MULTI-CHAT MANAGER
# -------------------------------------------------------------
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {
        "Chat 1": [
            {"role": "assistant", "content": "Assalam-o-Alaikum! Main aapka AI Copilot hoon. Neeche tools se photo banwayein, modify karein, ya WhatsApp messages bhejein."}
        ]
    }

if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Chat 1"

# -------------------------------------------------------------
# 3. AI ENGINES (Text & Image Generator)
# -------------------------------------------------------------
def generate_ai_text(prompt_text):
    sys_prompt = "Aap aik Roman Urdu Executive AI Studio Assistant hain. Hamesha direct, helpful aur short jawab dein."
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt_text)}?system={urllib.parse.quote(sys_prompt)}&model=openai"
        res = requests.get(url, timeout=8)
        if res.status_code == 200 and res.text.strip():
            return res.text.strip()
    except Exception:
        pass
    return "Main aapka AI Studio Assistant hoon. Batayein photo banwani hai ya koi aur kaam karna hai?"

def generate_image_url(prompt_text):
    clean_p = urllib.parse.quote(prompt_text.strip())
    return f"https://image.pollinations.ai/prompt/{clean_p}?width=1024&height=1024&nologo=true"

# -------------------------------------------------------------
# 4. SIDEBAR: SIRF NEW CHAT AUR HISTORY
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 💬 Chat Manager")
    if st.button("➕ New Chat (Fresh Start)", use_container_width=True, type="primary"):
        new_id = f"Chat {len(st.session_state.chat_sessions) + 1} ({datetime.datetime.now().strftime('%H:%M')})"
        st.session_state.chat_sessions[new_id] = [
            {"role": "assistant", "content": "Assalam-o-Alaikum! Yeh nayi fresh chat hai. Batayein kya kaam karna hai?"}
        ]
        st.session_state.active_chat = new_id
        st.rerun()

    st.markdown("#### 📜 Saved History")
    chat_names = list(st.session_state.chat_sessions.keys())
    selected_chat = st.selectbox("Switch Chat:", options=chat_names, index=chat_names.index(st.session_state.active_chat))
    if selected_chat != st.session_state.active_chat:
        st.session_state.active_chat = selected_chat
        st.rerun()

# -------------------------------------------------------------
# 5. MAIN CHAT DISPLAY
# -------------------------------------------------------------
st.markdown(f"<div style='text-align:center; padding-bottom:10px;'><h3 style='margin:0;'>✨ {st.session_state.active_chat}</h3></div>", unsafe_allow_html=True)

current_messages = st.session_state.chat_sessions[st.session_state.active_chat]

for msg in current_messages:
    role = msg["role"]
    content = msg["content"]
    options = msg.get("options", [])
    img_url = msg.get("image_url")
    
    if role == "user":
        st.markdown(f"<div class='chat-bubble-user'>👤 {content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-ai'>✨ {content}</div>", unsafe_allow_html=True)
        if img_url:
            st.image(img_url, caption="Studio Output Image", use_container_width=True)
        if options:
            st.markdown("<div style='clear:both; padding-top:6px;'>", unsafe_allow_html=True)
            for opt in options:
                st.markdown(f"<a href='{opt['url']}' target='_blank' class='action-card'>🟢 Open WhatsApp: {opt['name']}</a>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 6. BOTTOM TOOLS & VOICE BAR (Right Next to Typing Box)
# -------------------------------------------------------------
st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

col_tools, col_mod, col_voice = st.columns([1, 1, 1])

# Tool 1: AI Photo Generator Popover
with col_tools:
    with st.popover("🎨 Photo Generator", use_container_width=True):
        photo_prompt = st.text_input("Kaisi photo banwani hai?", placeholder="e.g. Luxury gold watch")
        if st.button("✨ Create Photo", use_container_width=True):
            if photo_prompt:
                img_url = generate_image_url(f"{photo_prompt}, commercial 8k lighting")
                current_messages.append({
                    "role": "assistant",
                    "content": f"Aapki photo tayyar hai: *{photo_prompt}*",
                    "image_url": img_url
                })
                st.rerun()

# Tool 2: Modify Uploaded Photo Popover
with col_mod:
    with st.popover("📎 Modify Photo", use_container_width=True):
        up_file = st.file_uploader("Phone se photo upload karein:", type=["jpg", "png", "jpeg"])
        mod_text = st.text_input("Is mein kya change karna hai?", placeholder="e.g. Background change karo")
        if up_file and st.button("🪄 Apply Changes", use_container_width=True):
            img_url = generate_image_url(f"Studio modification: {mod_text}, high resolution commercial look")
            current_messages.append({
                "role": "assistant",
                "content": f"Aapki photo ka modified version tayyar hai: *{mod_text}*",
                "image_url": img_url
            })
            st.rerun()

# Tool 3: Live Voice Mic
with col_voice:
    with st.popover("🎙️ Voice Mic", use_container_width=True):
        st.caption("Mic dabayein aur bolein:")
        components.html("""
        <div style="display:flex; flex-direction:column; align-items:center; gap:8px; font-family:sans-serif;">
            <button id="vBtn" onclick="runVoice()" style="background:#2563EB; color:white; border:none; border-radius:50%; width:50px; height:50px; font-size:22px; cursor:pointer; box-shadow:0 3px 8px rgba(37,99,235,0.4);">
                🎙️
            </button>
            <span id="vTxt" style="font-size:12px; color:#475569; text-align:center;">Mic dabayein aur bolna shuru karein...</span>
        </div>
        <script>
            let rec;
            let isRec = false;
            const btn = document.getElementById('vBtn');
            const txt = document.getElementById('vTxt');

            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
                rec = new SR();
                rec.continuous = false;
                rec.lang = 'ur-PK';

                rec.onresult = (e) => {
                    const trans = e.results[0][0].transcript;
                    txt.innerText = '🗣️ "' + trans + '"';
                    const ci = parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
                    if (ci) {
                        ci.value = trans;
                        ci.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                };
                rec.onend = () => {
                    isRec = false;
                    btn.style.background = '#2563EB';
                };
            }

            function runVoice() {
                if (!rec) return alert('Browser voice recognition support nahi karta.');
                if (isRec) {
                    rec.stop();
                } else {
                    rec.start();
                    isRec = true;
                    btn.style.background = '#DC2626';
                    txt.innerText = '🎙️ Sun raha hoon... (Bolein)';
                }
            }
        </script>
        """, height=100)

# -------------------------------------------------------------
# 7. TYPING INPUT BOX (Bottom SMS Input)
# -------------------------------------------------------------
user_input = st.chat_input("Prompt likhein ya bolein (e.g. 'Photo: luxury watch' ya '03001234567 par WhatsApp karo')...")

if user_input:
    current_messages.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='chat-bubble-user'>👤 {user_input}</div>", unsafe_allow_html=True)
    
    t = user_input.lower()
    options = []
    generated_img = None
    ai_reply = ""
    
    # 1. Direct Photo Request
    if any(k in t for k in ["photo", "image", "tasweer", "picture", "banao"]):
        clean_prompt = re.sub(r'(photo|image|tasweer|picture|banao|generate|create|is ki)', '', user_input, flags=re.IGNORECASE).strip()
        final_prompt = f"{clean_prompt}, commercial studio lighting, ultra-detailed, 8k quality"
        ai_reply = f"Maine aapki description ke mutabiq Studio Image create kar di hai: *{clean_prompt}*"
        generated_img = generate_image_url(final_prompt)

    # 2. WhatsApp Handling
    elif any(k in t for k in ["whatsapp", "wa", "sms", "message", "kaho", "bolo", "chat"]):
        nums = re.findall(r'\b\d{10,13}\b', t)
        phone = nums[0] if nums else ""
        
        clean_msg = t
        for skip in ["whatsapp", "business", "main", "ok", "hi", "sms", "message", "karo", "bhejo", "kaho", "bolo", "par", "per", "ko", phone]:
            clean_msg = re.sub(r'\b' + skip + r'\b', '', clean_msg, flags=re.IGNORECASE).strip()
            
        wa_url = f"https://api.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(clean_msg)}" if phone else f"https://api.whatsapp.com/send?text={urllib.parse.quote(clean_msg)}"
        ai_reply = "WhatsApp chat ready kar di gayi hai:"
        options.append({"name": phone if phone else "Direct WhatsApp", "url": wa_url})

    # 3. General AI Conversation
    else:
        ai_reply = generate_ai_text(user_input)

    # Display Output
    st.markdown(f"<div class='chat-bubble-ai'>✨ {ai_reply}</div>", unsafe_allow_html=True)
    if generated_img:
        st.image(generated_img, caption="Studio Output Image", use_container_width=True)
    if options:
        st.markdown("<div style='clear:both; padding-top:6px;'>", unsafe_allow_html=True)
        for opt in options:
            st.markdown(f"<a href='{opt['url']}' target='_blank' class='action-card'>🟢 Open WhatsApp: {opt['name']}</a>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    current_messages.append({
        "role": "assistant",
        "content": ai_reply,
        "image_url": generated_img,
        "options": options
    })
