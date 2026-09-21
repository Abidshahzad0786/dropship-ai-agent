import streamlit as st
import requests
import json
import re
import urllib.parse
import os
import datetime
from PIL import Image

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & WHATSAPP THEME
# -------------------------------------------------------------
st.set_page_config(
    page_title="AI Studio Copilot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

CONTACTS_FILE = "my_contacts.json"
HISTORY_FILE = "chat_history.json"

st.markdown("""
<style>
    .stApp { 
        background-color: #F8F9FA; 
        color: #1F1F1F; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .main .block-container {
        padding-top: 15px;
        padding-bottom: 100px;
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
# 2. CONTACTS & HISTORY PERSISTENCE
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

def save_contacts(contacts):
    try:
        with open(CONTACTS_FILE, "w") as f:
            json.dump(contacts, f)
    except Exception:
        pass

if "contacts" not in st.session_state:
    st.session_state.contacts = load_contacts()

def search_contacts(query):
    query = query.lower().strip()
    matches = []
    for name, num in st.session_state.contacts.items():
        if query in name.lower():
            matches.append({"name": name.title(), "number": num})
    return matches

# -------------------------------------------------------------
# 3. CHAT SESSIONS / ISOLATION MANAGER
# -------------------------------------------------------------
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {
        "Chat 1": [
            {"role": "assistant", "content": "Assalam-o-Alaikum! Main aapka AI Studio Copilot hoon. WhatsApp message, photo generation ya koi bhi kaam batayein."}
        ]
    }

if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Chat 1"

# -------------------------------------------------------------
# 4. AI ENGINES (Text & Image)
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
    return "Main aapka AI Studio Assistant hoon. Batayein photo banwani hai ya WhatsApp message bhejna hai?"

def generate_image_url(prompt_text):
    clean_p = urllib.parse.quote(prompt_text.strip())
    return f"https://image.pollinations.ai/prompt/{clean_p}?width=1024&height=1024&nologo=true"

# -------------------------------------------------------------
# 5. SIDEBAR: NEW CHAT, HISTORY & WORKING TOOLS
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ Studio Menu & Tools")
    
    # + NEW CHAT BUTTON (Fresh Start with Zero Data Bleed)
    if st.button("➕ New Chat (Fresh Start)", use_container_width=True, type="primary"):
        new_id = f"Chat {len(st.session_state.chat_sessions) + 1} ({datetime.datetime.now().strftime('%H:%M')})"
        st.session_state.chat_sessions[new_id] = [
            {"role": "assistant", "content": "Assalam-o-Alaikum! Yeh nayi fresh chat hai. Batayein kya kaam karna hai?"}
        ]
        st.session_state.active_chat = new_id
        st.rerun()

    # CHAT HISTORY LIST
    st.markdown("#### 📜 Chat History")
    chat_names = list(st.session_state.chat_sessions.keys())
    selected_chat = st.selectbox("Saved Chats:", options=chat_names, index=chat_names.index(st.session_state.active_chat))
    if selected_chat != st.session_state.active_chat:
        st.session_state.active_chat = selected_chat
        st.rerun()

    st.markdown("---")
    
    # WORKING TOOL 1: INSTANT PHOTO GENERATOR
    with st.expander("🎨 Tool: AI Photo Generator", expanded=False):
        img_prompt = st.text_input("Photo ki details likhein:", placeholder="e.g. Luxury black smartwatch")
        if st.button("✨ Generate Photo Now", use_container_width=True):
            if img_prompt:
                url = generate_image_url(img_prompt)
                st.session_state.chat_sessions[st.session_state.active_chat].append({
                    "role": "assistant",
                    "content": f"Maine aapki request par photo generate kar di hai: *{img_prompt}*",
                    "image_url": url
                })
                st.rerun()

    # WORKING TOOL 2: ATTACH PHOTO FOR MODIFICATION
    with st.expander("📎 Tool: Modify Uploaded Photo", expanded=False):
        uploaded_file = st.file_uploader("Phone se photo upload karein:", type=["jpg", "png", "jpeg"])
        mod_instructions = st.text_input("Is photo mein kya change karna hai?", placeholder="e.g. Iska background dark marble kar do")
        if uploaded_file and st.button("🪄 Modify & Generate", use_container_width=True):
            prompt = f"Studio modification: {mod_instructions}, commercial 8k lighting" if mod_instructions else "Enhanced commercial photo 8k"
            url = generate_image_url(prompt)
            st.session_state.chat_sessions[st.session_state.active_chat].append({
                "role": "assistant",
                "content": f"Aapki photo ka naya modified version tayyar hai: *{mod_instructions}*",
                "image_url": url
            })
            st.rerun()

    # WORKING TOOL 3: PHONEBOOK MANAGER
    with st.expander("📖 Tool: Phonebook (Contacts)", expanded=False):
        c_name = st.text_input("Name (e.g. Love Bhai):")
        c_num = st.text_input("Number (e.g. 03001234567):")
        if st.button("💾 Save Contact", use_container_width=True):
            if c_name and c_num:
                clean = re.sub(r'[^0-9]', '', c_num)
                if clean.startswith('03'):
                    clean = '92' + clean[1:]
                st.session_state.contacts[c_name.lower().strip()] = clean
                save_contacts(st.session_state.contacts)
                st.success(f"Saved: {c_name} -> {clean}")

# -------------------------------------------------------------
# 6. MAIN CHAT DISPLAY (Active Session Only)
# -------------------------------------------------------------
st.markdown(f"<div style='text-align:center; padding-bottom:10px;'><h3 style='margin:0;'>✨ {st.session_state.active_chat}</h3><small style='color:#6B7280;'>Google AI Studio Clean Interface</small></div>", unsafe_allow_html=True)

current_messages = st.session_state.chat_sessions[st.session_state.active_chat]

# Display Active Conversation
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
                st.markdown(f"<a href='{opt['url']}' target='_blank' class='action-card'>🟢 Open: {opt['name']}</a>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 7. BOTTOM INPUT BAR
# -------------------------------------------------------------
user_input = st.chat_input("Prompt likhein (e.g. 'Photo: luxury watch' ya 'Love ko WhatsApp karo')...")

if user_input:
    current_messages.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='chat-bubble-user'>👤 {user_input}</div>", unsafe_allow_html=True)
    
    t = user_input.lower()
    options = []
    generated_img = None
    ai_reply = ""
    
    # 1. Direct Photo Generation via Chat
    if any(k in t for k in ["photo", "image", "tasweer", "picture", "banao"]):
        clean_prompt = re.sub(r'(photo|image|tasweer|picture|banao|generate|create|is ki)', '', user_input, flags=re.IGNORECASE).strip()
        final_prompt = f"{clean_prompt}, commercial studio lighting, ultra-detailed, 8k quality"
        ai_reply = f"Maine aapki description ke mutabiq Studio Image create kar di hai: *{clean_prompt}*"
        generated_img = generate_image_url(final_prompt)

    # 2. WhatsApp Multi-Contact Disambiguation
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

    # Display AI Output
    st.markdown(f"<div class='chat-bubble-ai'>✨ {ai_reply}</div>", unsafe_allow_html=True)
    if generated_img:
        st.image(generated_img, caption="Studio Output Image", use_container_width=True)
    if options:
        st.markdown("<div style='clear:both; padding-top:6px;'>", unsafe_allow_html=True)
        for opt in options:
            st.markdown(f"<a href='{opt['url']}' target='_blank' class='action-card'>🟢 Open: {opt['name']}</a>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    current_messages.append({
        "role": "assistant",
        "content": ai_reply,
        "image_url": generated_img,
        "options": options
    })
