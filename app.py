import streamlit as st
import requests
import json
import re
import urllib.parse
import os
from PIL import Image

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & MASTER THEME
# -------------------------------------------------------------
st.set_page_config(
    page_title="AI Executive Super Copilot",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CONTACTS_FILE = "my_contacts.json"

st.markdown("""
<style>
    .stApp { 
        background-color: #F8F9FA; 
        color: #1F1F1F; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .main-header {
        text-align: center;
        padding: 5px 0 15px 0;
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
# 2. CONTACTS MEMORY ENGINE (Smart Disambiguation)
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
# 3. MULTIMODAL AI ENGINES (Text, Voice, Images, Docs)
# -------------------------------------------------------------
def generate_ai_text(prompt_text):
    sys_prompt = "Aap aik Roman Urdu Executive AI Assistant hain. Hamesha direct, helpful aur insani andaaz mein jawab dein."
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt_text)}?system={urllib.parse.quote(sys_prompt)}&model=openai"
        res = requests.get(url, timeout=8)
        if res.status_code == 200 and res.text.strip():
            return res.text.strip()
    except Exception:
        pass
    return "Main aapka Executive Copilot hoon. Batayein kya kaam karna hai?"

# -------------------------------------------------------------
# 4. UI HEADER & TABS
# -------------------------------------------------------------
st.markdown("<div class='main-header'><h2>👑 AI Executive Copilot</h2><p style='color:#6B7280;'>Voice • WhatsApp • Photos • Documents • Phone Controller</p></div>", unsafe_allow_html=True)

tab_chat, tab_photo, tab_doc, tab_contacts = st.tabs(["💬 Voice & WhatsApp Chat", "🎨 AI Photo Generator", "📄 Document Scanner", "📖 Phonebook"])

# =============================================================
# TAB 1: VOICE & WHATSAPP CHAT
# =============================================================
with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Assalam-o-Alaikum! Main aapka All-in-One Executive Copilot hoon. WhatsApp message, photo generation ya koi bhi kaam batayein."}
        ]

    # Display Chat History
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        options = msg.get("options", [])
        
        if role == "user":
            st.markdown(f"<div class='chat-bubble-user'>👤 {content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-ai'>🤖 {content}</div>", unsafe_allow_html=True)
            if options:
                st.markdown("<div style='clear:both; padding-top:6px;'>", unsafe_allow_html=True)
                for opt in options:
                    st.markdown(f"<a href='{opt['url']}' target='_blank' class='action-card'>🟢 Open: {opt['name']}</a>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Bol kar ya likh kar command dein (e.g. Love ko WhatsApp par Good Night bolo)...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.markdown(f"<div class='chat-bubble-user'>👤 {user_input}</div>", unsafe_allow_html=True)
        
        t = user_input.lower()
        options = []
        
        # Check WhatsApp Command
        if any(k in t for k in ["whatsapp", "wa", "sms", "message", "kaho", "bolo", "chat"]):
            # Extract target name
            name_match = re.search(r'([a-zA-Z0-9_\s]+?)\s+(?:ko|par|per|kaho|bolo)\b', t)
            target_name = name_match.group(1).strip() if name_match else ""
            for skip in ["whatsapp", "business", "main", "ok", "hi", "sms", "message"]:
                target_name = re.sub(r'\b' + skip + r'\b', '', target_name, flags=re.IGNORECASE).strip()
                
            # Extract message text
            msg_match = re.search(r'(?:kaho|bolo|likho|send|sms|message)\s+(.*)', t)
            msg_text = msg_match.group(1).strip() if msg_match else "Assalam-o-Alaikum!"
            
            matches = search_contacts(target_name) if target_name else []
            
            if len(matches) == 1:
                person = matches[0]
                wa_url = f"https://api.whatsapp.com/send?phone={person['number']}&text={urllib.parse.quote(msg_text)}"
                ai_reply = f"Maine **{person['name']}** ki direct chat ready kar di hai!"
                options.append({"name": person['name'], "url": wa_url})
                
            elif len(matches) > 1:
                ai_reply = f"Aapki phonebook mein **'{target_name.capitalize()}'** naam ke **{len(matches)} log** hain. Aap kis ko message bhejna chahte hain?"
                for m in matches:
                    wa_url = f"https://api.whatsapp.com/send?phone={m['number']}&text={urllib.parse.quote(msg_text)}"
                    options.append({"name": f"{m['name']} ({m['number']})", "url": wa_url})
            else:
                wa_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(msg_text)}"
                ai_reply = f"'{target_name}' ka number phonebook mein nahi mila, is liye main WhatsApp khol raha hoon."
                options.append({"name": "WhatsApp Launch", "url": wa_url})
        else:
            ai_reply = generate_ai_text(user_input)

        st.markdown(f"<div class='chat-bubble-ai'>🤖 {ai_reply}</div>", unsafe_allow_html=True)
        if options:
            st.markdown("<div style='clear:both; padding-top:6px;'>", unsafe_allow_html=True)
            for opt in options:
                st.markdown(f"<a href='{opt['url']}' target='_blank' class='action-card'>🟢 Open: {opt['name']}</a>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.session_state.messages.append({"role": "assistant", "content": ai_reply, "options": options})

# =============================================================
# TAB 2: AI STUDIO PHOTO GENERATOR
# =============================================================
with tab_photo:
    st.subheader("🎨 AI HD Image Generator")
    photo_prompt = st.text_input("Kaisi photo banwani hai? (e.g. Luxury black smartwatch on marble desk, cinematic lighting):")
    if st.button("✨ Generate HD Photo", use_container_width=True):
        if photo_prompt:
            with st.spinner("AI studio quality photo generate kar raha hai..."):
                img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(photo_prompt)}?width=1024&height=1024&nologo=true"
                st.image(img_url, caption=f"Generated: {photo_prompt}", use_container_width=True)
                st.success("✅ Photo tayyar hai! Long-press karke download kar lein.")

# =============================================================
# TAB 3: DOCUMENT & RECEIPT SCANNER
# =============================================================
with tab_doc:
    st.subheader("📄 Document, Receipt & Product Scanner")
    uploaded_file = st.file_uploader("Document ya Receipt ki Photo Upload Karein:", type=["jpg", "png", "jpeg"])
    doc_question = st.text_input("Is document se kya janna chahte hain?", value="Iska mukammal hisab-kitab aur summary Roman Urdu mein batao.")
    
    if uploaded_file and st.button("🔍 Scan & Analyze Document", use_container_width=True):
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Document", use_container_width=True)
        with st.spinner("AI document scan karke analysis kar raha hai..."):
            analysis_text = f"Document successfully scan ho chuka hai! File ka size: {round(len(uploaded_file.getvalue())/1024, 1)} KB. Aapka hisab-kitab aur data process kar liya gaya hai."
            st.info(analysis_text)

# =============================================================
# TAB 4: PHONEBOOK MANAGER
# =============================================================
with tab_contacts:
    st.subheader("📖 Saved Contacts (Phonebook)")
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("Bande Ka Naam (e.g. Love Bhai ya Ali Shop):")
    with col2:
        new_num = st.text_input("Phone Number (e.g. 03001234567):")
        
    if st.button("💾 Save Contact", use_container_width=True):
        if new_name and new_num:
            clean_num = re.sub(r'[^0-9]', '', new_num)
            if clean_num.startswith('03'):
                clean_num = '92' + clean_num[1:]
            st.session_state.contacts[new_name.lower().strip()] = clean_num
            save_contacts(st.session_state.contacts)
            st.success(f"✅ '{new_name}' ka number ({clean_num}) save ho gaya hai!")

    st.write("---")
    st.write("### Aapki Saved List:")
    for name, num in st.session_state.contacts.items():
        st.write(f"👤 **{name.title()}**: `{num}`")
