import os
import sys
import json
import re
import random
import urllib.parse
import urllib.request
import datetime
import requests
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & WHATSAPP THEME
# -------------------------------------------------------------
st.set_page_config(
    page_title="Universal AI Executive Copilot Pro",
    page_icon="🌍",
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
        line-height: 1.65;
        position: relative;
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
    .dots-menu:hover {
        color: #111B21;
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
            {"role": "assistant", "content": "Assalam-o-Alaikum! Main aapka Universal Executive AI Assistant hoon. Dunya ki kisi bhi cheez ke baray mein poochein, maslay ka hal janayein, photo banwayein ya WhatsApp message bhejein."}
        ]
    }

if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Chat 1"

if "last_image_prompt" not in st.session_state:
    st.session_state.last_image_prompt = None

# -------------------------------------------------------------
# 3. GLOBAL CELEBRITY & IMAGE RESOLVER (FLUX.1)
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
    "imran khan": "Imran Khan legendary Pakistani cricketer and former Prime Minister",
    "imran": "Imran Khan legendary Pakistani cricketer and former Prime Minister",
    "babar azam": "Pakistani cricketer Babar Azam",
    "virat kohli": "Indian cricketer Virat Kohli",
    "ronaldo": "Cristiano Ronaldo",
    "messi": "Lionel Messi",
    "elon musk": "Elon Musk tech billionaire",
    "trump": "Donald Trump"
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

# -------------------------------------------------------------
# 4. UNIVERSAL WEB KNOWLEDGE & DEEP SOLUTION BRAIN
# -------------------------------------------------------------
def fetch_global_knowledge(query_text):
    """World-wide knowledge search from Wikipedia & DuckDuckGo APIs"""
    try:
        clean = re.sub(r'(kon|hai|kya|batao|kisi|who|is|what|h|wo|kaise|karo|bhi|\?|!)', '', query_text, flags=re.IGNORECASE).strip()
        if len(clean) >= 3:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean)}"
            headers = {"User-Agent": "UniversalAIStudio/4.0"}
            res = requests.get(url, headers=headers, timeout=4)
            if res.status_code == 200:
                data = res.json()
                extract = data.get("extract", "")
                if extract:
                    return f"**{data.get('title', clean)}**: {extract}"
    except Exception:
        pass
    return None

def generate_ai_response(user_text, conversation_history):
    """Deep problem solving, world knowledge, and broken Roman Urdu understanding"""
    
    # 1. Fetch World Live Knowledge Context
    world_facts = fetch_global_knowledge(user_text)
    
    # 2. Compile Chat History for Long-Term Memory Recall
    history_context = ""
    for m in conversation_history[-8:]:
        role = "User" if m["role"] == "user" else "Assistant"
        history_context += f"{role}: {m['content']}\n"

    sys_prompt = (
        "Aap aik dunya ke sab se behtareen, ultra-intelligent aur solution-oriented Executive AI Assistant hain. "
        "Aap natural, mature aur authentic Roman Urdu mein baat karte hain.\n\n"
        "Aapke Qawaid (Rules):\n"
        "1. **Tooti-Phooti Zaban Samajhna:** User agar spelling ghalat likhe, slang bole ya tooti phooti Roman Urdu likhe, aap foran uska maqsad samajh kar seedha jawab dein.\n"
        "2. **Dunya Ka Har Ilm (Global Knowledge):** Science, Tareekh, Dunya ki Siyasat, E-commerce, Dropshipping, Technology, Sehat (Health), ya Daily life masle ka mukammal aur wazeh bayan karein.\n"
        "3. **Practical Solutions:** Jab koi masla pooche, to sirf baat na karein balkay step-by-step 1, 2, 3 karke mukammal practical hal samjhayein.\n"
        "4. **Long Memory:** Pichli guftagu ka mukammal dhyan rakhein taake agar user 'pehle kya baat hui' ya follow-up pooche to context yaad ho.\n"
        f"Pichla Context:\n{history_context}\n"
    )
    
    user_payload = f"World Fact Context: {world_facts}\nUser Query: {user_text}" if world_facts else user_text

    # Tier 1: Gemini REST API (If Key in Secrets)
    gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    if gemini_key:
        try:
            url_g = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
            headers_g = {"Content-Type": "application/json"}
            payload_g = {
                "system_instruction": {"parts": [{"text": sys_prompt}]},
                "contents": [{"role": "user", "parts": [{"text": user_payload}]}]
            }
            res_g = requests.post(url_g, headers=headers_g, json=payload_g, timeout=8)
            if res_g.status_code == 200:
                return res_g.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass

    # Tier 2: Cloud Neural Model Gateway
    try:
        url_t2 = f"https://text.pollinations.ai/{urllib.parse.quote(user_payload)}?system={urllib.parse.quote(sys_prompt)}&model=openai"
        res_t2 = requests.get(url_t2, timeout=8)
        if res_t2.status_code == 200 and len(res_t2.text.strip()) > 15:
            txt = res_t2.text.strip()
            if "I'm sorry" not in txt and "wazahat" not in txt:
                return txt
    except Exception:
        pass

    # Tier 3: Direct JSON Multi-Turn Payload
    try:
        messages_payload = [{"role": "system", "content": sys_prompt}]
        for m in conversation_history[-4:]:
            messages_payload.append({"role": m["role"], "content": m["content"]})
        messages_payload.append({"role": "user", "content": user_payload})
            
        url_t3 = "https://text.pollinations.ai/openai"
        headers_t3 = {"Content-Type": "application/json"}
        payload_t3 = {"messages": messages_payload, "model": "openai"}
        res_t3 = requests.post(url_t3, headers=headers_t3, json=payload_t3, timeout=8)
        if res_t3.status_code == 200:
            reply = res_t3.json()["choices"][0]["message"]["content"]
            if len(reply.strip()) > 10 and "wazahat" not in reply:
                return reply
    except Exception:
        pass

    if world_facts:
        return f"{world_facts}\n\nIs baray mein aapka koi makhsoos sawal ho to batayein, main step-by-step guide karta hoon."

    return f"Aapka sawal '{user_text}' samajh aa gaya hai. Is hawale se mukammal solution aur detail hasil karne ke liye mazeed batayein main foran guide karta hoon."

def generate_flux_image_url(prompt_text):
    clean_p = urllib.parse.quote(prompt_text.strip())
    seed = random.randint(10000, 999999)
    return f"https://image.pollinations.ai/prompt/{clean_p}?width=1024&height=1024&nologo=true&seed={seed}&model=flux"

def search_contacts(query):
    query = query.lower().strip()
    matches = []
    for name, num in st.session_state.contacts.items():
        if query in name.lower():
            matches.append({"name": name.title(), "number": num})
    return matches

# -------------------------------------------------------------
# 5. SIDEBAR (History & Multi-Chat)
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
# 6. CHAT MESSAGES DISPLAY (With WhatsApp-Style 3-Dots Copy Menu)
# -------------------------------------------------------------
st.markdown(f"<div style='text-align:center; padding-bottom:8px;'><h3 style='margin:0; color:#111B21;'>✨ {st.session_state.active_chat}</h3></div>", unsafe_allow_html=True)

current_messages = st.session_state.chat_sessions[st.session_state.active_chat]

for idx, msg in enumerate(current_messages):
    role = msg["role"]
    content = msg["content"]
    options = msg.get("options", [])
    img_url = msg.get("image_url")
    
    if role == "user":
        st.markdown(f"<div class='chat-bubble-user'>👤 {content}</div>", unsafe_allow_html=True)
    else:
        escaped_txt = content.replace("'", "\\'").replace("\n", " ")
        copy_js = f"navigator.clipboard.writeText('{escaped_txt}'); alert('Message Copied! ✅');"
        
        st.markdown(f"""
        <div class='chat-bubble-ai'>
            <div class='msg-header'>
                <span style='font-size:12px; color:#128C7E; font-weight:600;'>✨ AI Executive Copilot</span>
                <button onclick="{copy_js}" title="Copy Message" class="dots-menu">⋮</button>
            </div>
            {content}
        </div>
        """, unsafe_allow_html=True)
        
        if img_url:
            st.image(img_url, caption="FLUX.1 Photorealistic Output", use_container_width=True)
        if options:
            st.markdown("<div style='clear:both; padding-top:6px;'>", unsafe_allow_html=True)
            for opt in options:
                st.markdown(f"<a href='{opt['url']}' target='_blank' class='action-card'>🟢 Open WhatsApp: {opt['name']}</a>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 7. PERFECT SINGLE HORIZONTAL ROW: [+] [INPUT] [MIC]
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
    
    # 1. SMART REGENERATION ("Again try karo", "Dobara bano", "Pehle wali theek nahi")
    is_regen = any(k in t for k in ["again", "dobara", "phir se", "pahli nahi", "pehli nahi", "theek nahi", "galat", "dusri", "dusra", "try karo"])
    
    if is_regen and st.session_state.last_image_prompt:
        with st.spinner("🎨 AI FLUX.1 8K Photo Dobara Generate Kar Raha Hai..."):
            enhanced_prompt = smart_enhance_prompt(st.session_state.last_image_prompt)
            generated_img = generate_flux_image_url(enhanced_prompt)
            ai_reply = f"Maine **'{st.session_state.last_image_prompt}'** ki FLUX realistic photo dobara tayyar kar di hai:"

    # 2. PHOTO INTENT (Captures "Salman Khan ki photo", etc.)
    elif is_photo_intent(user_input):
        clean_raw = user_input
        st.session_state.last_image_prompt = clean_raw
        
        with st.spinner("🎨 AI FLUX.1 8K Photorealistic Image Render Kar Raha Hai..."):
            enhanced_prompt = smart_enhance_prompt(clean_raw)
            generated_img = generate_flux_image_url(enhanced_prompt)
            ai_reply = f"Maine **'{clean_raw}'** ke asal logon ko pehchan kar FLUX realistic photo tayyar kar di hai:"

    # 3. STRICT WHATSAPP HANDLER (Only when user explicitly says WhatsApp / Message)
    elif re.search(r'\b(whatsapp|wa\s+message)\b', t) and any(act in t for act in ["karo", "bhejo", "open", "kholo", "send", "chat"]):
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

    # 4. HIGH-INTELLIGENCE UNIVERSAL WORLD CONVERSATION & PROBLEM SOLVING
    else:
        with st.spinner("AI deep solution aur global knowledge analyze kar raha hai..."):
            ai_reply = generate_ai_response(user_input, current_messages)

    # Display Output
    escaped_reply = ai_reply.replace("'", "\\'").replace("\n", " ")
    copy_js_now = f"navigator.clipboard.writeText('{escaped_reply}'); alert('Message Copied! ✅');"
    
    st.markdown(f"""
    <div class='chat-bubble-ai'>
        <div class='msg-header'>
            <span style='font-size:12px; color:#128C7E; font-weight:600;'>✨ AI Executive Copilot</span>
            <button onclick="{copy_js_now}" title="Copy Message" class="dots-menu">⋮</button>
        </div>
        {ai_reply}
    </div>
    """, unsafe_allow_html=True)

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