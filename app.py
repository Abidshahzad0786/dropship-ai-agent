import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.parse

# Sleek Modern Gemini-Style Theme
st.set_page_config(page_title="Dropship AI", page_icon="✨", layout="centered")

st.markdown("""
<style>
    /* Premium Modern Dark/Slate Theme (Not Pitch Black) */
    .stApp { background-color: #1A1D24; color: #ECEFF4; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    
    /* Clean Chat Bubbles */
    .stChatMessage { background-color: #242933; border-radius: 16px; padding: 14px 18px; margin-bottom: 12px; border: 1px solid #3B4252; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    
    /* Header Title */
    .header-box { text-align: center; padding: 15px 0 25px 0; }
    .header-title { font-size: 26px; font-weight: 700; background: linear-gradient(90deg, #88C0D0, #81A1C1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .header-subtitle { font-size: 13px; color: #D8DEE9; opacity: 0.8; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
    <div class="header-title">✨ Dropship AI Copilot</div>
    <div class="header-subtitle">Your Smart Dropshipping Assistant (Chat, Scrape & Create)</div>
</div>
""", unsafe_allow_html=True)

# API Key Auto-Setup (Direct from Secrets or Sidebar)
api_key = st.secrets.get("GROQ_API_KEY", "") or st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.markdown("### ⚙️ Quick Settings")
    custom_key = st.text_input("Gemini API Key:", value=api_key, type="password", placeholder="AIzaSy...")
    if custom_key:
        api_key = custom_key
    target_platform = st.selectbox("Marketplace:", ["TikTok Shop", "Shopify", "WooCommerce"])
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# 1. AI Image Generator (100% Free)
def generate_ai_image(prompt):
    clean = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{clean}?width=800&height=800&nologo=true&enhance=true"

# 2. Web Scraper
def scrape_data(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else (soup.find('title').get_text(strip=True) if soup.find('title') else "Product Item")
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

# 3. Robust Multi-Model Gemini Engine
def call_gemini(prompt, key):
    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-flash-lite"]
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    for m in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=25)
            data = r.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            elif "error" in data:
                last_err = data["error"].get("message", "API Error")
        except Exception as e:
            last_err = str(e)
            continue
            
    return f"AI Response: {last_err if 'last_err' in locals() else 'Connection failed. Please check your API key.'}"

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 **Hello! I am your Dropshipping AI Agent.**\n\nHow can I help you today?\n- 💬 Ask me dropshipping questions or ideas.\n- 🔗 Paste any product link to clean specs & create high-converting descriptions.\n- 🎨 Tell me: *'Generate photo of a luxury perfume'*"}
    ]

# Render Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)
        if "images" in msg and msg["images"]:
            cols = st.columns(min(len(msg["images"]), 3))
            for i, im in enumerate(msg["images"][:3]):
                with cols[i]:
                    st.image(im, use_container_width=True)

# User Chat Input
user_input = st.chat_input("Message your AI Agent (or paste a link)...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        # 1. Image Generation Intent
        if any(w in user_input.lower() for w in ["generate image", "create photo", "make picture", "image of", "photo of"]):
            with st.spinner("🎨 Creating studio AI photo..."):
                img_url = generate_ai_image(user_input)
                reply = f"Here is your AI generated product photo for: **'{user_input}'**"
                st.markdown(reply)
                st.image(img_url, width=350)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": reply + f"<br><img src='{img_url}' style='width:300px; border-radius:12px; margin-top:10px;' />"
                })

        # 2. Link Scraping Intent
        elif "http" in user_input:
            url = re.findall(r'(https?://[^\s]+)', user_input)[0]
            with st.spinner("🔍 Fetching product & generating clean description..."):
                data = scrape_data(url)
                if "error" in data:
                    st.error(f"Error: {data['error']}")
                else:
                    if api_key:
                        prompt = f"""You are an elite E-Commerce Dropshipping Specialist for {target_platform}.
                        Clean this product info. Delete all messy supplier spec tables and columns.
                        Write a viral, high-converting product description with emojis and embedded HTML images.
                        
                        Product: {data['title']}
                        Raw Info: {data['raw_text']}
                        Images: {data['images'][:3]}
                        
                        Output a clean title, 4 benefit bullet points, and an attractive HTML description."""
                        
                        ai_resp = call_gemini(prompt, api_key)
                    else:
                        ai_resp = f"### 🔥 {data['title']}\n\nHigh-quality product optimized for {target_platform}."

                    reply_text = f"✅ **Product Processed Successfully!**\n\n{ai_resp}"
                    st.markdown(reply_text)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": reply_text,
                        "images": data.get("images", [])
                    })

        # 3. Direct Natural Conversation
        else:
            if not api_key:
                st.warning("👉 Please add your Gemini API Key in the left sidebar menu (>> icon) to chat freely!")
            else:
                system_prompt = f"You are an expert autonomous Dropshipping Assistant for {target_platform}. Help the user in friendly English or Roman Urdu.\n\nUser: {user_input}"
                ai_reply = call_gemini(system_prompt, api_key)
                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
