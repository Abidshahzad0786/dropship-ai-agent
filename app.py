import os
import sys
import json
import re
import urllib.parse
import datetime
import requests
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & WHATSAPP THEME
# -------------------------------------------------------------
st.set_page_config(
    page_title="AI Studio Copilot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CONTACTS_FILE = "my_contacts.json"

st.markdown("""
<style>
    .stApp { 
        background-color: #ECE5DD; /* WhatsApp Classic Background */
        color: #111B21; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .main .block-container {
        padding-top: 15px;
        padding-bottom: 140px !important;
        max-width: 850px;
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
        box-shadow: 0 1px 2px rgba(0,0,0,0.08);
    }
    .chat-bubble-ai {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px 16px 16px 4px;
        padding: 10px 16px;
        margin: 6px 0;
        max-width: 85%;
        float: left;
        clear: both;
        box-shadow: 0 1px 2px rgba(0,0,0,0.08);
        color: #1F2937;
    }
    .action-card {
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white !important;
        padding: 8px 16px;
        border-radius: 12px;
        margin: 6px 4px 6px 0;
        display: inline-block;
        font-weight: 600;
        text-decoration: none;
        box-shadow: 0 2px 6px rgba(37,211,102,0.3);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. CONTACTS & PERSISTENCE
# -------------------------------------------------------------
def load_contacts():
    if os.path.exists(CONTACTS_FILE):
        try:
            with open(CONTACTS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {
        "love (personal)": "923001234567",
        "love (office)": "923219876543",
        "ghulam rasool": "923123456789"
    }

if "contacts" not in st.session_state:
    st.session_state.contacts = load_contacts()

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {
        "Chat 1": [
            {"role": "assistant", "content": "Assalam-o-Alaikum! Main aapka AI Copilot hoon. Neeche WhatsApp bar se bolein, photo attach karein ya commands dein."}
        ]
    }

if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Chat 1"

# -------------------------------------------------------------
# 3. AI ENGINES (Text & Image Generator)
# -------------------------------------------------------------
def generate_ai_text(prompt_text):
    sys_prompt = "Aap aik Roman Urdu Executive AI Assistant hain. Hamesha direct, helpful aur short jawab dein."
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt_text)}?system={urllib.parse.quote(sys_prompt)}&model=openai"
        res = requests.get(url, timeout=8)
        if res.status_code == 200 and res.text.strip():
            return res.text.strip()
    except Exception:
        pass
    return "Main aapka AI Assistant hoon. Batayein kya kaam karna hai?"

def generate_image_url(prompt_text):
    clean_p = urllib.parse.quote(prompt_text.strip())
    return f"https://image.pollinations.ai/prompt/{clean_p}?width=1024&height=1024&nologo=true"

def search_contacts(query):
    query = query.lower().strip()
    matches = []
    for name, num in st.session_state.contacts.items():
        if query in name.lower():
            matches.append({"name": name.title(), "number": num})
    return matches

# -------------------------------------------------------------
# 4. SIDEBAR (Chat History & Media Attachment)
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 💬 Chat History")
    if st.button("➕ New Chat (Fresh Start)", use_container_width=True, type="primary"):
        new_id = f"Chat {len(st.session_state.chat_sessions) + 1} ({datetime.datetime.now().strftime('%H:%M')})"
        st.session_state.chat_sessions[new_id] = [
            {"role": "assistant", "content": "Assalam-o-Alaikum! Yeh nayi fresh chat hai. Batayein kya kaam karna hai?"}
        ]
        st.session_state.active_chat = new_id
        st.rerun()

    chat_names = list(st.session_state.chat_sessions.keys())
    selected_chat = st.selectbox("Saved Chats:", options=chat_names, index=chat_names.index(st.session_state.active_chat))
    if selected_chat != st.session_state.active_chat:
        st.session_state.active_chat = selected_chat
        st.rerun()

    st.markdown("---")
    with st.expander("📎 Photo Attachment (To Modify)", expanded=False):
        up_file = st.file_uploader("Select Photo:", type=["jpg", "png", "jpeg"])
        if up_file:
            st.image(Image.open(up_file), caption="Attached Base Photo", use_container_width=True)

# -------------------------------------------------------------
# 5. CHAT MESSAGES DISPLAY
# -------------------------------------------------------------
st.markdown(f"<div style='text-align:center; padding-bottom:8px;'><h3 style='margin:0; color:#111B21;'>✨ {st.session_state.active_chat}</h3></div>", unsafe_allow_html=True)

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
# 6. EXACT WHATSAPP BOTTOM INPUT BAR + CIRCULAR MIC BUTTON
# -------------------------------------------------------------
components.html("""
<div style="position:fixed; bottom:12px; left:0; right:0; width:95%; max-width:750px; margin:0 auto; display:flex; align-items:center; gap:8px; z-index:99999; font-family:sans-serif;">
    
    <!-- White Rounded Pill Bar -->
    <div style="flex:1; background:#FFFFFF; border-radius:30px; padding:6px 14px; display:flex; align-items:center; gap:10px; box-shadow:0 2px 6px rgba(0,0,0,0.12); border:1px solid #E2E8F0;">
        <span title="Emoji" style="font-size:20px; cursor:pointer; color:#54656F;">😊</span>
        
        <input type="text" id="waInput" placeholder="Message..." style="flex:1; border:none; outline:none; font-size:15px; color:#111B21; background:transparent;" onkeypress="if(event.key==='Enter') submitMsg()">
        
        <!-- Clip / Attachment Icon -->
        <span title="Attach Photo" onclick="parent.document.querySelector('input[type=file]')?.click();" style="font-size:20px; cursor:pointer; color:#54656F;">📎</span>
        
        <!-- Camera / AI Photo Generator Icon -->
        <span title="Generate AI Photo" onclick="triggerPhotoGen()" style="font-size:20px; cursor:pointer; color:#54656F;">📷</span>
    </div>

    <!-- Black Circular Floating Mic Button -->
    <button id="waMicBtn" onclick="runVoice()" style="width:48px; height:48px; border-radius:50%; background:#111B21; border:none; color:white; font-size:20px; cursor:pointer; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 8px rgba(0,0,0,0.25); flex-shrink:0;">
        🎙️
    </button>
</div>

<script>
    let rec;
    let isRec = false;
    const micBtn = document.getElementById('waMicBtn');
    const input = document.getElementById('waInput');

    function submitMsg() {
        const txt = input.value.trim();
        if(!txt) return;
        const chatInput = parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
        if (chatInput) {
            chatInput.value = txt;
            chatInput.dispatchEvent(new Event('input', { bubbles: true }));
            input.value = '';
            setTimeout(() => {
                const sendBtn = parent.document.querySelector('button[data-testid="stChatInputSubmitButton"]');
                if (sendBtn) sendBtn.click();
            }, 100);
        }
    }

    function triggerPhotoGen() {
        input.value = "Photo: ";
        input.focus();
    }

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        rec = new SR();
        rec.continuous = false;
        rec.lang = 'ur-PK';

        rec.onresult = (e) => {
            const trans = e.results[0][0].transcript;
            input.value = trans;
            submitMsg();
        };
        rec.onend = () => {
            isRec = false;
            micBtn.style.background = '#111B21';
        };
    }

    function runVoice() {
        if (!rec) return alert('Browser voice recognition support nahi karta.');
        if (isRec) {
            rec.stop();
        } else {
            rec.start();
            isRec = true;
            micBtn.style.background = '#DC2626';
        }
    }
</script>
""", height=70)

# Hidden Native Chat Input used by JavaScript Bridge
user_input = st.chat_input("Message...", key="real_input")

if user_input:
    current_messages.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='chat-bubble-user'>👤 {user_input}</div>", unsafe_allow_html=True)
    
    t = user_input.lower()
    options = []
    generated_img = None
    ai_reply = ""
    
    # 1. Direct Photo Generation
    if any(k in t for k in ["photo", "image", "tasweer", "picture", "banao"]):
        clean_prompt = re.sub(r'(photo|image|tasweer|picture|banao|generate|create|is ki)', '', user_input, flags=re.IGNORECASE).strip()
        final_prompt = f"{clean_prompt}, commercial studio lighting, ultra-detailed, 8k quality"
        ai_reply = f"Maine aapki description ke mutabiq Studio Image create kar di hai: *{clean_prompt}*"
        generated_img = generate_image_url(final_prompt)

    # 2. WhatsApp Multi-Contact Handling
    elif any(k in t for k in ["whatsapp", "wa", "sms", "message", "kaho", "bolo", "chat"]):
        name_match = re.search(r'([a-zA-Z0-9_\s]+?)\s+(?:ko|par|per|kaho|bolo)\b', t)
        target_name = name_match.group(1).strip() if name_match else ""
        for skip in ["whatsapp", "business", "main", "ok", "hi", "sms", "message"]:
            target_name = re.sub(r'\b' + skip + r'\b', '', target_name, flags=re.IGNORECASE).strip()
            
        msg_match = re.search(r'(?:kaho|bolo|likho|send|sms|message)\s+(.*)', t)
        msg_text = msg_match.group(1).strip() if msg_match else "Assalam-o-Alaikum!"
        
        matches = search_contacts(target_name) if target_name else []
        
        if len(matches) == 1:
            person = matches[0]
            wa_url = f"https://api.whatsapp.com/send?phone={person['number']}&text={urllib.parse.quote(msg_text)}"
            ai_reply = f"Maine **{person['name']}** ki direct chat ready kar di hai!"
            options.append({"name": person['name'], "url": wa_url})
        elif len(matches) > 1:
            ai_reply = f"Aapki phonebook mein **'{target_name.capitalize()}'** naam ke **{len(matches)} log** hain. Kis ko bhejna hai?"
            for m in matches:
                wa_url = f"https://api.whatsapp.com/send?phone={m['number']}&text={urllib.parse.quote(msg_text)}"
                options.append({"name": f"{m['name']} ({m['number']})", "url": wa_url})
        else:
            wa_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(msg_text)}"
            ai_reply = f"'{target_name}' ka number phonebook mein nahi mila, WhatsApp open kiya ja raha hai."
            options.append({"name": "WhatsApp Launch", "url": wa_url})

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
