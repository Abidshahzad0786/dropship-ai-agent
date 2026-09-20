import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image
import streamlit.components.v1 as components

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="AI Copilot Live",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- LIGHT UI CSS -----------------
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
        color: #111b21;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 6rem !important;
        max-width: 750px;
        margin: 0 auto;
    }
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border: 1px solid #e3e7ed;
    }
    p, span, div {
        color: #111b21 !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### ⚙️ **Settings**")
    api_key = st.text_input("Google AI Studio API Key", type="password")
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if not api_key:
    st.info("👈 Pehle sidebar (>> icon) khol kar apni Google AI Studio API Key paste karein.")
    st.stop()

# ----------------- TOP MODE SWITCHER -----------------
app_mode = st.radio(
    "Choose Mode",
    ["📞 Live Voice Call (Real-Time Talk)", "💬 Text & Photo Chat"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

# ==============================================================================
# 1. LIVE VOICE CALL MODE (REAL-TIME PHONE CALL EXPERIENCE)
# ==============================================================================
if app_mode == "📞 Live Voice Call (Real-Time Talk)":
    st.markdown("""
    <div style="text-align: center; margin-top: 1rem; margin-bottom: 1.5rem;">
        <h3 style="color: #0b57d0; margin: 0;">📞 Live Voice Call</h3>
        <p style="color: #5f6368; font-size: 14px;">Neeche button dabayein aur direct bolna shuru karein</p>
    </div>
    """, unsafe_allow_html=True)

    # High Speed Client-Side Live Voice Engine (Zero Latency WebSpeech)
    live_call_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: sans-serif;">
        <button id="callBtn" onclick="toggleCall()" style="
            background: #0b57d0; 
            color: white; 
            border: none; 
            width: 90px; 
            height: 90px; 
            border-radius: 50%; 
            font-size: 32px; 
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(11, 87, 208, 0.35);
            transition: all 0.3s ease;
            outline: none;
        ">🎙️</button>
        
        <p id="statusText" style="margin-top: 18px; font-weight: 600; font-size: 16px; color: #5f6368;">Call Start Karne Ke Liye Mic Dabayein</p>
        <div id="liveTranscript" style="
            margin-top: 15px; 
            padding: 14px; 
            background: #ffffff; 
            border: 1px solid #e0e0e0; 
            border-radius: 12px; 
            width: 90%; 
            min-height: 80px; 
            text-align: center; 
            color: #333; 
            font-size: 15px;
        ">Baat-cheet yahan live nazar aayegi...</div>
    </div>

    <script>
        let isCalling = false;
        let recognition = null;
        const apiKey = "{api_key}";

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRec();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'hi-IN'; // Roman Urdu/Hindi natural recognition

            recognition.onstart = function() {{
                document.getElementById('statusText').innerText = "🟢 Sun raha hoon... Bolein!";
                document.getElementById('statusText').style.color = "#00875a";
                document.getElementById('callBtn').style.background = "#00875a";
            }};

            recognition.onresult = async function(event) {{
                const userSaid = event.results[0][0].transcript;
                document.getElementById('liveTranscript').innerHTML = "<b>Aap:</b> " + userSaid;
                document.getElementById('statusText').innerText = "⏳ Soch raha hoon...";
                document.getElementById('statusText').style.color = "#d97706";

                // Call Gemini API directly (Zero delay)
                try {{
                    const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${{apiKey}}`, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            contents: [{{ parts: [{{ text: userSaid }}] }}],
                            systemInstruction: {{ parts: [{{ text: "You are a real-time conversational phone partner. Reply ONLY in short, natural 1-2 sentences in easy Roman Urdu suitable for live spoken audio. No bullet points." }}] }}
                        }})
                    }});
                    const data = await res.json();
                    let replyText = data.candidates[0].content.parts[0].text.trim();
                    replyText = replyText.replace(/[*_#]/g, '');

                    document.getElementById('liveTranscript').innerHTML += "<br><br><b style='color:#0b57d0;'>AI:</b> " + replyText;
                    document.getElementById('statusText').innerText = "🔊 Bol raha hoon...";
                    document.getElementById('statusText').style.color = "#0b57d0";

                    // Speak out loud
                    window.speechSynthesis.cancel();
                    const utterance = new SpeechSynthesisUtterance(replyText);
                    utterance.lang = 'hi-IN';
                    utterance.rate = 1.05;

                    utterance.onend = function() {{
                        if (isCalling) {{
                            recognition.start();
                        }}
                    }};
                    window.speechSynthesis.speak(utterance);

                }} catch (err) {{
                    document.getElementById('statusText').innerText = "⚠️ Error: Connection issue";
                }}
            }};

            recognition.onerror = function(e) {{
                if (isCalling) {{
                    setTimeout(() => {{ try {{ recognition.start(); }} catch(err){{}} }}, 1000);
                }}
            }};
        }} else {{
            document.getElementById('statusText').innerText = "⚠️ Browser voice support nahi kar raha (Chrome use karein)";
        }}

        function toggleCall() {{
            if (!recognition) return;
            isCalling = !isCalling;
            if (isCalling) {{
                document.getElementById('callBtn').innerText = "🛑";
                recognition.start();
            }} else {{
                document.getElementById('callBtn').innerText = "🎙️";
                document.getElementById('callBtn').style.background = "#0b57d0";
                document.getElementById('statusText').innerText = "Call Band Ho Gayi (Dobaray dabayein)";
                document.getElementById('statusText').style.color = "#5f6368";
                window.speechSynthesis.cancel();
                recognition.stop();
            }}
        }}
    </script>
    """
    components.html(live_call_html, height=350)

# ==============================================================================
# 2. STANDARD TEXT, PHOTO & SOURCING MODE
# ==============================================================================
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "image" in msg:
                st.image(msg["image"], use_container_width=True)

    # Clean Bottom Attachment Bar
    uploaded_file = st.file_uploader("📎 Photo ya Document Attach Karein", type=["png", "jpg", "jpeg", "webp"])
    user_prompt = st.chat_input("Message likhein, photo mangwayein ya link paste karein...")

    genai.configure(api_key=api_key)
    SAFETY_SETTINGS = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

    if user_prompt or uploaded_file:
        if user_prompt and (user_prompt.lower().startswith("photo:") or user_prompt.lower().startswith("image:")):
            clean_prompt = user_prompt.split(":", 1)[1].strip()
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.markdown(user_prompt)
            with st.chat_message("assistant"):
                img_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1024&height=1024&nologo=true"
                st.image(img_url, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": "Photo tayar hai:", "image": img_url})
        elif user_prompt:
            input_data = []
            pil_image = None
            if uploaded_file:
                pil_image = Image.open(uploaded_file)
                input_data.append(pil_image)
            input_data.append(user_prompt)
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.markdown(user_prompt)
                if pil_image:
                    st.image(pil_image, width=280)
            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    try:
                        model = genai.GenerativeModel("gemini-1.5-flash", safety_settings=SAFETY_SETTINGS)
                        res = model.generate_content(input_data)
                        output_text = res.text
                        st.markdown(output_text)
                        st.session_state.messages.append({"role": "assistant", "content": output_text})
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
