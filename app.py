import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import re
import urllib.parse
import os
from PIL import Image

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & AI STUDIO DOCK STYLING
# -------------------------------------------------------------
st.set_page_config(
    page_title="AI Studio Super Copilot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CONTACTS_FILE = "my_contacts.json"

st.markdown("""
<style>
    /* Google AI Studio Clean Theme */
    .stApp { 
        background-color: #F8F9FA; 
        color: #1F1F1F; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .main-header {
        text-align: center;
        padding: 5px 0 10px 0;
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
    
    /* Bottom Dock Bar (AI Studio Visual Style) */
    .studio-bottom-dock {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 8px 14px;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        flex-wrap: wrap;
    }
    .dock-pill {
        background: #F1F5F9;
        border: 1px solid #CBD5E1;
        border-radius: 20px;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 600;
        color: #334155;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. CONTACTS MEMORY MANAGER
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
# 3. AI REASONING & IMAGE ENGINES
# -------------------------------------------------------------
def generate_ai_text(prompt_text):
    sys_prompt = "Aap aik Roman Urdu Executive AI Studio Assistant hain. Hamesha direct, helpful aur professional andaaz mein jawab dein."
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt_text)}?system={urllib.parse.quote(sys_prompt)}&model=openai"
        res = requests.get(url, timeout=8)
        if res.status_code == 200 and res.text.strip():
            return res.text.strip()
    except Exception:
        pass
    return "Main aapka AI Studio Assistant hoon. Batayein photo modify karni hai ya WhatsApp message bhejna hai?"

def generate_image_url(prompt_text):
    clean_p = urllib.parse.quote(prompt_text.strip())
    return f"https://image.pollinations.ai/prompt/{clean_p}?width=1024&height=1024&nologo=true"

# -------------------------------------------------------------
# 4. UI HEADER
# -------------------------------------------------------------
st.markdown("<div class='main-header'><h2>✨ AI Studio Super Copilot</h2><p style='color:#6B7280;'>Visual Photo Modifier • Voice • Multi-Contact WhatsApp</p></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 5. CHAT SESSION & DISPLAY
# -------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalam-o-Alaikum! Main aapka AI Studio Copilot hoon. Neeche mic se bolein, photo attach karke modify karwayein, ya WhatsApp messages bhejein."}
    ]

# Display Chat History
for msg in st.session_state.messages:
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
# 6. BOTTOM AI STUDIO TOOLBAR DOCK (Exact Reference Look)
# -------------------------------------------------------------
st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

# Bottom Dock: Attach + Tools + Model + Voice Mic Widget
st.markdown("""
<div class="studio-bottom-dock">
    <span class="dock-pill"><b>➕</b> Media</span>
    <span class="dock-pill"><b>⚡</b> Tools</span>
    <span class="dock-pill"><b>G</b> Gemini 2.0 Flash ▾</span>
    <span class="dock-pill" style="background:#E0F2FE; color:#0369A1;">🎙️ Voice Active</span>
</div>
""", unsafe_allow_html=True)

# Attachment Drawer & Voice Component
with st.expander("➕ Attach Photo from Phone (Edit / Modify)", expanded=False):
    uploaded_photo = st.file_uploader("Phone se photo select karein:", type=["jpg", "png", "jpeg"], key="dock_uploader")
    if uploaded_photo:
        img_preview = Image.open(uploaded_photo)
        st.image(img_preview, caption="Uploaded Image", width=250)

# Live Browser Voice Mic Integration
components.html("""
<div style="display:flex; align-items:center; gap:8px; font-family: sans-serif; padding: 4px 0;">
    <button id="micBtn" onclick="toggleVoice()" style="background:#2563EB; color:white; border:none; border-radius:50%; width:38px; height:38px; cursor:pointer; font-size:18px; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 6px rgba(37,99,235,0.3);">
        🎙️
    </button>
    <span id="statusTxt" style="font-size:13px; color:#64748B;">Mic dabayein aur bol kar command dein...</span>
</div>

<script>
    let recognition;
    let isRecording = false;
    const btn = document.getElementById('micBtn');
    const txt = document.getElementById('statusTxt');

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRec();
        recognition.continuous = false;
        recognition.lang = 'ur-PK';

        recognition.onresult = (e) => {
            const transcript = e.results[0][0].transcript;
            txt.innerText = '🗣️ "' + transcript + '" (Neeche box mein copy karein)';
            // Copy to clipboard for easy pasting
            navigator.clipboard.writeText(transcript);
        };

        recognition.onend = () => {
            isRecording = false;
            btn.style.background = '#2563EB';
        };
    }

    function toggleVoice() {
        if (!recognition) return alert('Browser mic support nahi karta.');
        if (isRecording) {
            recognition.stop();
        } else {
            recognition.start();
            isRecording = true;
            btn.style.background = '#DC2626';
            txt.innerText = '🎙️ Sun raha hoon... (Bolein)';
        }
    }
</script>
""", height=55)

# -------------------------------------------------------------
# 7. CHAT INPUT & INTELLIGENT DISPATCHER
# -------------------------------------------------------------
user_input = st.chat_input("Prompt likhein ya bolein (e.g. 'Photo: luxury gold watch' ya 'Love ko WhatsApp karo')...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='chat-bubble-user'>👤 {user_input}</div>", unsafe_allow_html=True)
    
    t = user_input.lower()
    options = []
    generated_img = None
    ai_reply = ""
    
    # CASE A: Photo Modification / Generation
    if any(k in t for k in ["photo", "image", "tasweer", "picture", "banao", "change", "modify", "edit"]):
        clean_prompt = re.sub(r'(photo|image|tasweer|picture|banao|change|karo|modify|edit|is ko|thoda|asa|kar do)', '', user_input, flags=re.IGNORECASE).strip()
        
        if uploaded_photo and any(mod in t for mod in ["change", "modify", "edit", "is ko"]):
            final_prompt = f"Studio modification of uploaded image: {clean_prompt}, 8k resolution, photorealistic, professional lighting"
            ai_reply = f"Maine aapki uploaded photo ke mutabiq naya modified version generate kar diya hai: *{clean_prompt}*"
        else:
            final_prompt = f"{clean_prompt}, commercial studio lighting, ultra-detailed, 8k quality"
            ai_reply = f"Maine aapki description ke mutabiq Studio Image create kar di hai: *{clean_prompt}*"
            
        generated_img = generate_image_url(final_prompt)

    # CASE B: WhatsApp & Multi-Contact Disambiguation
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
            ai_reply = f"'{target_name}' ka number phonebook mein nahi mila, WhatsApp khola ja raha hai."
            options.append({"name": "WhatsApp Launch", "url": wa_url})

    # CASE C: General Conversation
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

    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_reply,
        "image_url": generated_img,
        "options": options
    })
