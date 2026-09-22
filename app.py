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
    page_title="Universal Master AI Copilot",
    page_icon="👑",
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
            {"role": "assistant", "content": "Assalam-o-Alaikum! Main aapka Master AI Copilot hoon. Software coding, business strategy, viral scripts, world knowledge, photo generation ya WhatsApp control—jo chahein bolein."}
        ]
    }

if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Chat 1"

if "last_image_prompt" not in st.session_state:
    st.session_state.last_image_prompt = None

# -------------------------------------------------------------
# 3. LIVE TIME & WORLD TIMEZONES
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

def get_live_time_and_date(text):
    t = text.lower()
    time_words = ["time", "waqt", "date", "tareekh", "tarikh", "din", "day", "saal", "year", "aj kia", "aaj kya"]
    
    if any(k in t for k in time_words) and not any(img in t for img in ["photo", "pic", "image"]):
        now = datetime.datetime.now()
        month_name = MONTHS_URDU.get(now.month, "")
        day_name = DAYS_URDU.get(now.weekday(), "")
        formatted_date = f"{now.day} {month_name} {now.year}"
        local_time = now.strftime("%I:%M %p")
        
        if "america" in t or "usa" in t or "us" in t:
            us_est = (now - datetime.timedelta(hours=9)).strftime("%I:%M %p")
            us_pst = (now - datetime.timedelta(hours=12)).strftime("%I:%M %p")
            return f"America mein timezones:\n\n• **New York (Eastern Time):** {us_est}\n• **California (Pacific Time):** {us_pst}\n(Pakistan se taqreeban 9 se 12 ghantay peeche)."
        elif "dubai" in t or "uae" in t:
            dubai_time = (now - datetime.timedelta(hours=1)).strftime("%I:%M %p")
            return f"Dubai / UAE mein time **{dubai_time}** ho raha hai."
        elif "london" in t or "uk" in t:
            uk_time = (now - datetime.timedelta(hours=4)).strftime("%I:%M %p")
            return f"London / UK mein time **{uk_time}** ho raha hai."
        elif "time" in t or "waqt" in t:
            return f"Is waqt time **{local_time}** hai aur aaj **{formatted_date}** ({day_name}) hai."
        else:
            return f"Aaj ki tareekh **{formatted_date}** hai aur din **{day_name}** hai."
    return None

# -------------------------------------------------------------
# 4. UNIVERSAL MASTER PROMPT BRAIN (All Personas Included)
# -------------------------------------------------------------
MASTER_SYSTEM_INSTRUCTION = """
Aap aik World-Class Universal Executive AI Copilot hain. Aap Roman Urdu aur English dono mein expert hain.

Aapke Core Roles aur Frameworks:
1. **Software Engineering & Coding:**
   - Jab code maanga jaye to Senior Full-Stack Developer ban kar clean, modular, production-ready code dein (Python, JS, React, PHP, SQL).
   - Error handling, validation aur comments shamil karein.

2. **Business, Marketing & CMO:**
   - Go-to-market (GTM) launch roadmaps, High-converting ad copies (AIDA, PAS hooks), Dropshipping profit economics, Unit economics calculate karein.

3. **Executive Communications & Negotiation:**
   - Professional, authoritative aur firm emails/letters likhein (payment recovery, client proposals, contracts).

4. **Academic Professor & Tutor:**
   - Mushkil topics ko pehle 10 saal ke bache ki tarah asaan misaal (analogy) se samjhayein, phir technical terms explain karein.

5. **Viral Video Scriptwriter:**
   - YouTube / Reels ke scripts likhte waqt brackets mein [Visual cues, B-Roll, Sound effects], 15-second curiosity hooks, aur CTA shamil karein.

6. **Reverse Prompting:**
   - Agar user broad business/life plan maange to pehle 4-5 zaroori sawalat pooch kar samajhein, phir solid roadmap dein.

7. **Tooti-Phooti Zaban Samajhna:**
   - User agar spelling ghalat likhe ya Roman Urdu tooti phooti ho, uska maqsad foran samajh kar seedha mukammal solution dein.
"""

def fetch_wikipedia_knowledge(clean_topic):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_topic)}"
        headers = {"User-Agent": "UniversalMasterCopilot/6.0"}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("extract", "")
    except Exception:
        pass
    return None

def generate_ai_response(user_text, conversation_history):
    t_low = user_text.lower().strip()
    
    # Live Time & Date
    time_ans = get_live_time_and_date(user_text)
    if time_ans:
        return time_ans

    # Geography Quick Answers
    if "philippines" in t_low and ("kahan" in t_low or "kahna" in t_low):
        return (
            "**Philippines Dunya Mein Kahan Waqea Hai?**\n\n"
            "Philippines **Janub Mashriqi Asia (Southeast Asia)** mein waqea aik jazeera numa (archipelago) mulk hai.\n"
            "• **Islands:** Taqreeban **7,641 jazair** par mushtamil hai.\n"
            "• **Capital:** **Manila** hai.\n"
            "• **Location:** Pacific Ocean ke maghribi hissay mein waqea hai."
        )

    # Live Wikipedia Search for Global Knowledge
    extracted_topic = re.sub(r'(kon|hai|kya|kia|batao|kisi|who|is|what|h|wo|kaise|karo|bhi|main|mein|\?|!)', '', user_text, flags=re.IGNORECASE).strip()
    live_info = ""
    if len(extracted_topic) >= 3:
        live_info = fetch_wikipedia_knowledge(extracted_topic) or ""

    # Multi-turn history context
    history_context = ""
    for m in conversation_history[-6:]:
        history_context += f"{m['role']}: {m['content']}\n"

    final_sys_prompt = f"{MASTER_SYSTEM_INSTRUCTION}\n\nLive Fact Reference: {live_info}\nPichla Context:\n{history_context}"

    # Gateway 1: Pollinations OpenAI Gateway
    try:
        url_t = f"https://text.pollinations.ai/{urllib.parse.quote(user_text)}?system={urllib.parse.quote(final_sys_prompt)}&model=openai"
        res_t = requests.get(url_t, timeout=8)
        if res_t.status_code == 200 and len(res_t.text.strip()) > 15:
            txt = res_t.text.strip()
            if "I'm sorry" not in txt and "wazahat" not in txt:
                return txt
    except Exception:
        pass

    # Gateway 2: Gemini API via Secrets (If Set)
    gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    if gemini_key:
        try:
            url_g = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
            headers_g = {"Content-Type": "application/json"}
            payload_g = {
                "system_instruction": {"parts": [{"text": final_sys_prompt}]},
                "contents": [{"role": "user", "parts": [{"text": user_text}]}]
            }
            res_g = requests.post(url_g, headers=headers_g, json=payload_g, timeout=8)
            if res_g.status_code == 200:
                return res_g.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass

    if live_info:
        return f"**{extracted_topic.title()}** ke hawale se maloomat:\n\n{live_info}"

    return f"Aapka sawal '{user_text}' samajh aa gaya hai. Is hawale se mukammal step-by-step detail ke liye batayein main foran guide karta hoon."

# -------------------------------------------------------------
# 5. SMART PROMPT & IMAGE ENGINE (FLUX.1)
# -------------------------------------------------------------
def is_photo_intent(text):
    t = text.lower()
    triggers = [
        "photo", "pic", "pics", "image", "tasweer", "tasvir", "picture",
        "banao", "bano", "bana", "genrate", "generate", "create",
        "dikhao", "draw", "portrait", "naksha", "nakshy", "map"
    ]
    return any(k in t for k in triggers)

def smart_enhance_prompt(raw_text):
    t = raw_text.lower()
    
    if any(c in t for c in ["couple", "larka larki", "romantic"]):
        return "A photorealistic 8k cinematic portrait of a beautiful young couple standing together in love, warm aesthetic lighting, detailed faces, 8k resolution"
    
    if "naksha" in t or "map" in t:
        if "china" in t:
            return "A clean detailed National Geographic style map of China, accurate borders, major cities, 8k cartography"
        elif "pakistan" in t:
            return "A clean detailed National Geographic style map of Pakistan, accurate borders, 8k cartography"
        return f"A detailed National Geographic style map of {raw_text}, 8k"

    celeb_map = {
        "sharu": "Shah Rukh Khan", "shahrukh": "Shah Rukh Khan", "srk": "Shah Rukh Khan",
        "slaman": "Salman Khan", "salman": "Salman Khan", "aswariya": "Aishwarya Rai",
        "kajal": "Kajal Aggarwal", "alo arjun": "Allu Arjun", "imran khan": "Imran Khan handsome portrait"
    }
    
    found = []
    for k, v in celeb_map.items():
        if re.search(r'\b' + re.escape(k) + r'\b', t):
            if v not in found:
                found.append(v)
                
    if len(found) >= 2:
        return f"A realistic 8k photograph of {found[0]} standing together side by side with {found[1]}, studio portrait, detailed authentic face likeness, 8k"
    elif len(found) == 1:
        clean = re.sub(r'(photo|pic|image|tasweer|picture|banao|bano|ki|sath|kay|r|aur)', '', t).strip()
        return f"A realistic 8k photograph portrait of {found[0]}, {clean}, detailed authentic face, 8k resolution"

    clean_p = re.sub(r'(photo|pic|image|tasweer|picture|banao|bano|generate|create|ki|ka)', '', raw_text, flags=re.IGNORECASE).strip()
    return f"A high quality 8k photorealistic image of {clean_p}, cinematic studio lighting, 8k resolution"

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
# 6. SIDEBAR (History & Multi-Chat)
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
# 7. CHAT MESSAGES DISPLAY (With WhatsApp-Style 3-Dots Copy Menu)
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
                <span style='font-size:12px; color:#128C7E; font-weight:600;'>✨ Master AI Copilot</span>
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
# 8. PERFECT SINGLE HORIZONTAL ROW: [+] [INPUT] [MIC]
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
    
    # 1. SMART REGENERATION ("Again try karo", "Dobara bano")
    is_regen = any(k in t for k in ["again", "dobara", "phir se", "pahli nahi", "pehli nahi", "theek nahi", "galat", "dusri", "dusra", "try karo"])
    
    if is_regen and st.session_state.last_image_prompt:
        with st.spinner("🎨 AI FLUX.1 8K Photo Dobara Render Kar Raha Hai..."):
            enhanced_prompt = smart_enhance_prompt(st.session_state.last_image_prompt)
            generated_img = generate_flux_image_url(enhanced_prompt)
            ai_reply = f"Maine **'{st.session_state.last_image_prompt}'** ki FLUX realistic photo dobara tayyar kar di hai:"

    # 2. PHOTO INTENT
    elif is_photo_intent(user_input):
        clean_raw = user_input
        st.session_state.last_image_prompt = clean_raw
        
        with st.spinner("🎨 AI FLUX.1 8K Image Render Kar Raha Hai..."):
            enhanced_prompt = smart_enhance_prompt(clean_raw)
            generated_img = generate_flux_image_url(enhanced_prompt)
            ai_reply = f"Maine aapki request par **'{clean_raw}'** ki HD FLUX photo generate kar di hai:"

    # 3. STRICT WHATSAPP HANDLER
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

    # 4. UNIVERSAL MASTER REASONING & SOLUTIONS (Dev, Marketing, Writing, Education, Knowledge)
    else:
        with st.spinner("AI master framework se solution analyze kar raha hai..."):
            ai_reply = generate_ai_response(user_input, current_messages)

    # Display Output
    escaped_reply = ai_reply.replace("'", "\\'").replace("\n", " ")
    copy_js_now = f"navigator.clipboard.writeText('{escaped_reply}'); alert('Message Copied! ✅');"
    
    st.markdown(f"""
    <div class='chat-bubble-ai'>
        <div class='msg-header'>
            <span style='font-size:12px; color:#128C7E; font-weight:600;'>✨ Master AI Copilot</span>
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