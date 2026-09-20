import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.parse
from groq import Groq

# Sleek Modern ChatGPT/Gemini Style Theme
st.set_page_config(page_title="AI Dropship Copilot", page_icon="✨", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #131314; color: #E3E3E3; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stChatMessage { background-color: #1E1F20; border-radius: 18px; padding: 12px 18px; margin-bottom: 12px; border: 1px solid #2D2E30; }
    .quick-btn { background: #282A2C; border: 1px solid #3C4043; border-radius: 20px; padding: 6px 14px; font-size: 13px; color: #C4C7C5; margin-right: 6px; cursor: pointer; }
    .product-box { background: #18191A; border: 1px solid #00D2FF; border-radius: 12px; padding: 15px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# API Key Auto-Detection (Sidebar or Secrets)
api_key = st.secrets.get("GROQ_API_KEY", "")
with st.sidebar:
    st.markdown("### ✨ AI Control Center")
    if not api_key:
        api_key = st.text_input("Groq API Key (Free):", type="password", help="console.groq.com سے حاصل کریں")
    target_platform = st.selectbox("Marketplace:", ["TikTok Shop", "Shopify", "WooCommerce"])
    target_country = st.selectbox("Target Market:", ["Philippines (PHP)", "USA (USD)", "UAE (AED)", "UK (GBP)"])
    if st.button("🗑️ New Chat"):
        st.session_state.messages = []
        st.rerun()

# Tools
def generate_ai_image(prompt):
    clean = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{clean}?width=800&height=800&nologo=true&enhance=true"

def scrape_data(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Trending Product"
        images = []
        for img in soup.find_all('img'):
            s = img.get('src') or img.get('data-src') or img.get('data-original')
            if s and any(ext in s.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                if s.startswith('//'): s = 'https:' + s
                elif s.startswith('/'): s = url.rstrip('/') + s
                if s not in images and not any(j in s.lower() for j in ['logo', 'icon', 'badge', 'avatar']):
                    images.append(s)
        text = " ".join([p.get_text(strip=True) for p in soup.find_all(['p', 'li', 'span']) if len(p.get_text(strip=True)) > 20])
        return {"title": title, "images": images[:6], "raw_text": text[:3000]}
    except Exception as e:
        return {"error": str(e)}

# Chat State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 **Hello! I am your AI Dropshipping Agent.**\n\nI can do anything you ask:\n- 🔗 Paste any product link to clean specs & write viral TikTok/Shopify descriptions with pictures.\n- 🎨 Ask me to create custom AI product photos.\n- 💬 Ask me to research, rewrite or publish items live."}
    ]

st.markdown("<h2 style='text-align: center; color: #4E95FF;'>⚡ Dropship AI Assistant</h2>", unsafe_allow_html=True)

# Render Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)
        if "images" in msg and msg["images"]:
            cols = st.columns(min(len(msg["images"]), 3))
            for i, im in enumerate(msg["images"][:3]):
                with cols[i]:
                    st.image(im, use_container_width=True)

# User Chat Input
user_input = st.chat_input("Ask anything, paste link, or command photo creation...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        # Image Generation Intent
        if any(w in user_input.lower() for w in ["generate image", "create photo", "make picture", "image of", "photo of"]):
            with st.spinner("🎨 Creating studio-quality AI photo..."):
                img_url = generate_ai_image(user_input)
                reply = f"Here is your AI generated product photo for: **'{user_input}'**"
                st.markdown(reply)
                st.image(img_url, width=350)
                st.session_state.messages.append({"role": "assistant", "content": reply + f"<br><img src='{img_url}' style='width:300px; border-radius:10px; margin-top:10px;' />"})

        # URL Scraping Intent
        elif "http" in user_input:
            url = re.findall(r'(https?://[^\s]+)', user_input)[0]
            with st.spinner("🔍 Fetching product, removing columns & optimizing with AI..."):
                data = scrape_data(url)
                if "error" in data:
                    st.error(f"Error scraping: {data['error']}")
                else:
                    if api_key:
                        client = Groq(api_key=api_key)
                        prompt = f"""You are an elite E-commerce AI Copywriter for {target_platform}.
                        Clean this product info. Delete useless supplier spec tables and ugly columns.
                        Write a viral, high-converting description with emojis and embedded HTML image tags.
                        Title: {data['title']}
                        Data: {data['raw_text']}
                        Images: {json.dumps(data['images'][:3])}
                        Return JSON: {{"title": "Catchy Title", "description": "HTML description with embedded <img> tags"}}"""
                        
                        resp = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                            response_format={"type": "json_object"}
                        )
                        res_json = json.loads(resp.choices[0].message.content)
                        clean_title = res_json.get("title", data["title"])
                        clean_desc = res_json.get("description", "")
                    else:
                        clean_title = f"🔥 {data['title']}"
                        clean_desc = f"<p>{data['title']}</p>"

                    reply_text = f"✅ **Product Processed Successfully!**\n\n📌 **Optimized Title:** {clean_title}\n\n📝 **Live Preview:**"
                    st.markdown(reply_text)
                    st.components.v1.html(clean_desc, height=350, scrolling=True)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": reply_text + f"<br>{clean_desc}",
                        "images": data.get("images", [])
                    })

        # Smart Conversation
        else:
            if not api_key:
                st.warning("Please provide your free Groq API key in the sidebar or Streamlit Secrets so I can chat with full intelligence!")
            else:
                client = Groq(api_key=api_key)
                system_prompt = f"You are an expert AI Dropshipping partner assisting the user with {target_platform} for {target_country}. You can chat naturally in English or Roman Urdu, suggest winning products, plan strategies, and execute e-commerce tasks."
                
                resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ]
                )
                ai_reply = resp.choices[0].message.content
                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
