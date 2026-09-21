import os
import sys
import json
import re
import random
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
    page_title="AI Studio Copilot Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CONTACTS_FILE = "my_contacts.json"

st.markdown("""
<style>
    .stApp { 
        background-color: #ECE5DD; 
        color: #111B21; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .main .block-container {
        padding-top: 10px;
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
        padding: 12px 18px;
        margin: 6px 0;
        max-width: 85%;
        float: left;
        clear: both;
        box-shadow: 0 1px 2px rgba(0,0,0,0.08);
        color: #1F2937;
        line-height: 1.5;
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
    div[data-testid="stChatInput"] {
        padding-bottom: 8px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 6px !important;
    }
    div[data-testid="stChatInput"] > div {
        border-radius: 28px !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        flex: 1 !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. CONTACTS & SESSIONS PERSISTENCE
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
            {"role": "assistant", "content": "Assalam-o-Alaikum! Main aapka Advanced Executive AI Assistant hoon. Koi bhi sawal poochein, photo banwayein ya kaam batayein."}
        ]
    }

if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Chat 1"

if "last_image_prompt" not in st.session_state:
    st.session_state.last_image_prompt = None

# -------------------------------------------------------------
# 3. HIGH-INTELLIGENCE BRAIN & PROMPT ENGINE
# -------------------------------------------------------------
CELEBRITY_MAP = {
    "sharu": "Bollywood superstar Shah Rukh Khan",
    "sharu khan": "Bollywood superstar Shah Rukh Khan",
    "sharukh": "Bollywood superstar Shah Rukh Khan",
    "shahrukh": "Bollywood superstar Shah Rukh Khan",
    "srk": "Bollywood superstar Shah Rukh Khan",
    "slaman": "Bollywood superstar Salman Khan",
    "salman": "Bollywood superstar Salman Khan",
    "salman khan": "Bollywood superstar Salman Khan",
    "sallu": "Bollywood superstar Salman Khan",
    "aswariya": "Bollywood actress Aishwarya Rai",
    "aishwarya": "Bollywood actress Aishwarya Rai",
    "kajal": "Indian actress Kajal Aggarwal",
    "kajol": "Bollywood actress Kajol",
    "alo arjun": "South Indian superstar Allu Arjun",
    "allu arjun": "South Indian superstar Allu Arjun",
    "katrina": "Bollywood actress Katrina Kaif",
    "deepika": "Bollywood actress Deepika Padukone",
    "akshay": "Bollywood superstar Akshay Kumar",
    "imran khan": "Imran Khan handsome portrait",
    "babar azam": "Pakistani cricketer Babar Azam",
    "virat kohli": "Indian cricketer Virat Kohli",
    "ronaldo": "Cristiano Ronaldo",
    "messi": "Lionel Messi"
}

def is_photo_intent(text):
    t = text.lower()
    triggers = [
        "photo", "pic", "pics", "image", "tasweer", "tasvir", "picture",
        "banao", "bano", "bana", "genrate", "generate", "create",
        "dikhao", "draw", "portrait", "shakil", "design"
    ]
    return any(k in t for k in triggers)

def smart_enhance_prompt(raw_text):
    t = raw_text.lower()
    found_celebs = []
    for key, val in CELEBRITY_MAP.items():
        if re.search(r'\b' + re.escape(key) + r'\b', t):
            if val not in found_celebs:
                found_celebs.append(val)
                
    if len(found_celebs) >= 2:
        return f"A realistic 8k photograph of {found_celebs[0]} standing together side by side with {found_celebs[1]}, posing together for a studio portrait, highly detailed authentic facial likeness, natural studio lighting, ultra-realistic skin textures, 8k resolution"
    elif len(found_celebs) == 1:
        clean = re.sub(r'(photo|pic|image|tasweer|picture|banao|bano|ki|sath|kay|r|aur)', '', t).strip()
        return f"A realistic 8k photograph portrait of {found_celebs[0]}, {clean}, highly detailed authentic face, sharp focus, cinematic lighting, 8k resolution"
    
    try:
        sys_enh = "You are an expert prompt engineer for FLUX.1. Convert the user request into an ultra-realistic 8k cinematic English prompt. Output ONLY the prompt."
        url = f"https://text.pollinations.ai/{urllib.parse.quote(raw_text)}?system={urllib.parse.quote(sys_enh)}&model=openai"
        res = requests.get(url, timeout=6)
        if res.status_code == 200 and len(res.text.strip()) > 15:
            return res.text.strip()
    except Exception:
        pass
        
    return f"A realistic 8k photograph of {raw_text}, highly detailed authentic features, cinematic lighting, photorealistic 8k"

def generate_ai_response(user_text, conversation_history):
    """High-IQ Roman Urdu response for all knowledge, questions, and conversations"""
    sys_prompt = (
        "Aap aik highly intelligent, knowledgeable aur mature Executive AI Assistant hain. "
        "Aap natural Roman Urdu mein direct aur informative jawab dete hain. "
        "Jab user kisi shakhsiyat (jaise Salman Khan), business, dropshipping ya kisi bhi topic ke baray mein pooche, to foran mukammal, accurate aur dilchasp maloomat Roman Urdu mein dein. "
        "Kabhi robotic phrases (jaise 'sahayata/turant/main aapki baat samajh gaya hoon') na bolein. Seedha sawal ka asal jawab dein."
    )
    
    # Try Endpoint 1: Direct Fast Prompt
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(user_text)}?system={urllib.parse.quote(sys_prompt)}&model=openai"
        res = requests.get(url, timeout=8)
        if res.status_code == 200 and len(res.text.strip()) > 10:
            text = res.text.strip()
            if "I'm sorry" not in text and "I cannot" not in text:
                return text
    except Exception:
        pass

    # Try Endpoint 2: JSON OpenAI Proxy
    try:
        messages_payload = [{"role": "system", "content": sys_prompt}]
        for m in conversation_history[-4:]:
            messages_payload.append({"role": m["role"], "content": m["content"]})
        messages_payload.append({"role": "user", "content": user_text})
            
        url_json = "https://text.pollinations.ai/openai"
        headers = {"Content-Type": "application/json"}
        payload = {"messages": messages_payload, "model": "openai"}
        res_json = requests.post(url_json, headers=headers, json=payload, timeout=10)
        if res_json.status_code == 200:
            reply = res_json.json()["choices"][0]["message"]["content"]
            if len(reply.strip()) > 5:
                return reply
    except Exception:
        pass

    # Knowledge Base Fallback if network hiccups
    t_low = user_text.lower()
    if "salman" in t_low:
        return "Salman Khan Bollywood ke mashhoor aur kamyab tareen superstar hain, jinhein 'Bhaijaan' bhi kaha jata hai. Unho ne 'Maine Pyar Kiya', 'Hum Aapke Hain Koun', 'Bajrangi Bhaijaan', aur 'Sultan' jaisi blockbusters films di hain aur wo 'Being Human' foundation bhi chalate hain."
    elif "shahrukh" in t_low or "sharu" in t_low or "srk" in t_low:
        return "Shah Rukh Khan (SRK) Bollywood ke 'King Khan' aur 'Badshah' hain. Unho ne 'DDLJ', 'Kuch Kuch Hota Hai', 'Chak De India', 'Pathaan' aur 'Jawan' jaisi superhit movies di hain aur wo dunya bhar mein mashhoor hain."
    
    return "Main aapki baat samajh raha hoon. Baraye meherbani thori mazeed wazahat karein taake main mukammal jawab de sakoon."

def generate_flux_image_url(prompt_text):
    clean_p = urllib.parse.quote(prompt_text.strip())
    seed = random.randint(10000, 999999)
    return f"https://image.pollinations.ai/prompt/{clean_p}?model=flux&width=1024&height=1024&nologo=true&seed={seed}"

def search_contacts(query):
    query = query.lower().strip()
    matches = []
    for name, num in st.session_state.contacts.items():
        if query in name.lower():
            matches.append({"name": name.title(), "number": num})
    return matches

# -------------------------------------------------------------
# 4. SIDEBAR (History & Multi-Chat)
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 💬 Chat History")
    if st.button("➕ New Chat (Fresh Start)", use_container_width=True, type="primary"):
        new_id = f"Chat {len(st.session_state.chat_sessions) + 1} ({datetime.datetime.now().strftime('%H:%M')})"
        st.session_state.chat_sessions[new_id] = [
            {"role": "assistant", "content": "Assalam-o-Alaikum! Yeh nayi fresh chat hai."}
        ]
        st.session_state.active_chat = new_id
        st.session_state.last_image_prompt = None
        st.rerun()

    chat_names = list(st.session_state.chat_sessions.keys())
    selected_chat = st.selectbox("Saved Chats:", options=chat_names, index=chat_names.index(st.session_state.active_chat))
    if selected_chat != st.session_state.active_chat:
        st.session_state.active_chat = selected_chat
        st.rerun()

    st.markdown("---")
    up_file = st.file_uploader("📎 Upload Image to Modify:", type=["jpg", "png", "jpeg"], key="sidebar_uploader")
    if up_file:
        st.image(Image.open(up_file), caption="Selected Photo", use_container_width=True)

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
            st.image(img_url, caption="FLUX.1 Photorealistic Output", use_container_width=True)
        if options:
            st.markdown("<div style='clear:both; padding-top:6px;'>", unsafe_allow_html=True)
            for opt in options:
                st.markdown(f"<a href='{opt['url']}' target='_blank' class='action-card'>🟢 Open WhatsApp: {opt['name']}</a>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 6. PERFECT SINGLE HORIZONTAL ROW: [+] [INPUT] [MIC]
# -------------------------------------------------------------
components.html("""
<script>
    function buildWhatsAppDock() {
        const inputContainer = parent.document.querySelector('div[data-testid="stChatInput"]');
        if (!inputContainer || parent.document.getElementById('wa-plus-btn')) return;

        inputContainer.style.display = 'flex';
        inputContainer.style.flexDirection = 'row';
        inputContainer.style.alignItems = 'center';
        inputContainer.style.gap = '8px';
        inputContainer.style.padding = '8px 12px';
        inputContainer.style.background = 'transparent';

        const plusBtn = parent.document.createElement('button');
        plusBtn.id = 'wa-plus-btn';
        plusBtn.innerHTML = `
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#334155" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="16"></line>
                <line x1="8" y1="12" x2="16" y2="12"></line>
            </svg>
        `;
        plusBtn.title = 'Attach Image';
        plusBtn.style.width = '44px';
        plusBtn.style.height = '44px';
        plusBtn.style.borderRadius = '50%';
        plusBtn.style.background = '#FFFFFF';
        plusBtn.style.border = '1px solid #CBD5E1';
        plusBtn.style.cursor = 'pointer';
        plusBtn.style.display = 'flex';
        plusBtn.style.alignItems = 'center';
        plusBtn.style.justifyContent = 'center';
        plusBtn.style.boxShadow = '0 2px 6px rgba(0,0,0,0.06)';
        plusBtn.style.flexShrink = '0';
        plusBtn.onclick = () => {
            const fileInput = parent.document.querySelector('input[type="file"]');
            if (fileInput) fileInput.click();
        };

        const micBtn = parent.document.createElement('button');
        micBtn.id = 'wa-mic-btn';
        micBtn.innerHTML = `
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#111B21" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="22"></line>
            </svg>
        `;
        micBtn.title = 'Voice Input';
        micBtn.style.width = '44px';
        micBtn.style.height = '44px';
        micBtn.style.borderRadius = '50%';
        micBtn.style.background = '#FFFFFF';
        micBtn.style.border = '1px solid #CBD5E1';
        micBtn.style.cursor = 'pointer';
        micBtn.style.display = 'flex';
        micBtn.style.alignItems = 'center';
        micBtn.style.justifyContent = 'center';
        micBtn.style.boxShadow = '0 2px 6px rgba(0,0,0,0.06)';
        micBtn.style.flexShrink = '0';

        let rec;
        let isRec = false;
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            rec = new SR();
            rec.continuous = false;
            rec.lang = 'ur-PK';

            rec.onresult = (e) => {
                const trans = e.results[0][0].transcript;
                const ta = parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
                if (ta) {
                    ta.value = trans;
                    ta.dispatchEvent(new Event('input', { bubbles: true }));
                    setTimeout(() => {
                        const sBtn = parent.document.querySelector('button[data-testid="stChatInputSubmitButton"]');
                        if (sBtn) sBtn.click();
                    }, 200);
                }
            };
            rec.onend = () => {
                isRec = false;
                micBtn.style.background = '#FFFFFF';
            };
        }

        micBtn.onclick = () => {
            if (!rec) return alert('Browser mic support nahi karta.');
            if (isRec) {
                rec.stop();
            } else {
                rec.start();
                isRec = true;
                micBtn.style.background = '#FEE2E2';
            }
        };

        inputContainer.insertBefore(plusBtn, inputContainer.firstChild);
        inputContainer.appendChild(micBtn);
    }

    setTimeout(buildWhatsAppDock, 300);
    setInterval(buildWhatsAppDock, 1000);
</script>
""", height=0, width=0)

# Native Chat Input at Bottom
user_input = st.chat_input("Message likhein ya bolein...", key="wa_main_box")

if user_input:
    current_messages.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='chat-bubble-user'>👤 {user_input}</div>", unsafe_allow_html=True)
    
    t = user_input.lower()
    options = []
    generated_img = None
    ai_reply = ""
    
    # 1. SMART REGENERATION ("Again try karo", "Dobara bano", "Pehli theek nahi")
    is_regen = any(k in t for k in ["again", "dobara", "phir se", "pahli nahi", "pehli nahi", "theek nahi", "galat", "dusri", "dusra", "try karo"])
    
    if is_regen and st.session_state.last_image_prompt:
        with st.spinner("AI FLUX.1 se behtar realistic photo dobara generate kar raha hai..."):
            enhanced_prompt = smart_enhance_prompt(st.session_state.last_image_prompt)
            generated_img = generate_flux_image_url(enhanced_prompt)
            ai_reply = f"Maine **'{st.session_state.last_image_prompt}'** ki FLUX realistic tasweer dobara tayyar kar di hai:"

    # 2. PHOTO INTENT (Captures "Sharu khan r Salman Khan ki pic ak Sath bano", etc.)
    elif is_photo_intent(user_input):
        clean_raw = user_input
        st.session_state.last_image_prompt = clean_raw
        
        with st.spinner("AI FLUX.1 mein realistic photo design kar raha hai..."):
            enhanced_prompt = smart_enhance_prompt(clean_raw)
            generated_img = generate_flux_image_url(enhanced_prompt)
            ai_reply = f"Maine aapki request par FLUX.1 photorealistic photo tayyar kar di hai:"

    # 3. WHATSAPP MULTI-CONTACT HANDLER
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
            ai_reply = f"Maine **{person['name']}** ki direct chat ready kar di hai:"
            options.append({"name": person['name'], "url": wa_url})
        elif len(matches) > 1:
            ai_reply = f"Aapki phonebook mein **'{target_name.capitalize()}'** naam ke **{len(matches)} log** hain. Kis ko bhejna hai?"
            for m in matches:
                wa_url = f"https://api.whatsapp.com/send?phone={m['number']}&text={urllib.parse.quote(msg_text)}"
                options.append({"name": f"{m['name']} ({m['number']})", "url": wa_url})
        else:
            wa_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(msg_text)}"
            ai_reply = f"'{target_name}' ka number phonebook mein nahi mila, WhatsApp launch kiya ja raha hai."
            options.append({"name": "WhatsApp Launch", "url": wa_url})

    # 4. HIGH-INTELLIGENCE GENERAL CONVERSATION
    else:
        with st.spinner("AI soch raha hai..."):
            ai_reply = generate_ai_response(user_input, current_messages)

    # Display Output
    st.markdown(f"<div class='chat-bubble-ai'>✨ {ai_reply}</div>", unsafe_allow_html=True)
    if generated_img:
        st.image(generated_img, caption="FLUX.1 Photorealistic Output", use_container_width=True)
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