import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.parse

# Sleek Modern Interface
st.set_page_config(page_title="AI Dropship Agent", page_icon="✨", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #131314; color: #E3E3E3; }
    .stChatMessage { background-color: #1E1F20; border-radius: 16px; padding: 12px 18px; margin-bottom: 10px; border: 1px solid #2D2E30; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #4E95FF;'>⚡ Autonomous Dropship AI Agent</h2>", unsafe_allow_html=True)

# 1. API Key Box directly on Main Screen (Easy Mobile Access)
with st.expander("🔑 Click here to Enter / Save your Google Gemini Key", expanded=True):
    gemini_key = st.text_input("Paste your Gemini API Key here (AIzaSy...):", type="password")
    c1, c2 = st.columns(2)
    with c1:
        target_platform = st.selectbox("Marketplace:", ["TikTok Shop", "Shopify", "WooCommerce"])
    with c2:
        target_country = st.selectbox("Target Market:", ["Philippines (PHP ₱)", "USA (USD $)", "UAE (AED)", "UK (GBP £)"])

# Tool 1: AI Image Generator (100% Free)
def generate_ai_image(prompt):
    clean = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{clean}?width=800&height=800&nologo=true&enhance=true"

# Tool 2: Web Scraper
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

# Tool 3: Universal Auto-Fallback Gemini Caller
def call_gemini(prompt, api_key):
    # Try latest stable Gemini models automatically
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-latest", "gemini-pro"]
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=25)
            res = r.json()
            if "candidates" in res and len(res["candidates"]) > 0:
                return res["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            continue
            
    return "Error connecting to AI. Please verify your API key."

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 **Hello! I am your AI Dropshipping Agent.**\n\n- 🔗 Paste any product link to clean specs & write viral TikTok descriptions.\n- 🎨 Ask me to create custom AI product photos.\n- 💬 Ask me anything in English or Roman Urdu!"}
    ]

# Render Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)
        if "images" in msg and msg["images"]:
            cols = st.columns(min(len(msg["images"]), 3))
            for i, im in enumerate(msg["images"][:3]):
                with cols[i]:
                    st.image(im, use_container_width=True)

# Chat Input Box
user_input = st.chat_input("Ask anything, paste product link, or request photo...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        # 1. AI Image Generation
        if any(w in user_input.lower() for w in ["generate image", "create photo", "make picture", "image of", "photo of"]):
            with st.spinner("🎨 Creating studio AI photo..."):
                img_url = generate_ai_image(user_input)
                reply = f"Here is your AI generated product photo for: **'{user_input}'**"
                st.markdown(reply)
                st.image(img_url, width=350)
                st.session_state.messages.append({"role": "assistant", "content": reply + f"<br><img src='{img_url}' style='width:300px; border-radius:10px; margin-top:10px;' />"})

        # 2. Product Link Scraping & Optimization
        elif "http" in user_input:
            url = re.findall(r'(https?://[^\s]+)', user_input)[0]
            with st.spinner("🔍 Fetching product details, images & optimizing..."):
                data = scrape_data(url)
                if "error" in data:
                    st.error(f"Error: {data['error']}")
                else:
                    if gemini_key:
                        prompt = f"""You are an elite E-Commerce Dropshipping Copywriter for {target_platform} in {target_country}.
                        Clean this supplier product data. Delete useless technical tables and messy columns.
                        Write a high-converting sales description with emojis and embed these image URLs inside HTML <img> tags between sections.
                        
                        Product: {data['title']}
                        Raw Info: {data['raw_text']}
                        Images: {data['images'][:3]}
                        
                        Return a clean attractive title, key feature bullet points, and rich visual HTML description."""
                        
                        ai_resp = call_gemini(prompt, gemini_key)
                    else:
                        ai_resp = f"### 🔥 {data['title']}\n\nHigh quality product optimized for {target_platform}."

                    reply_text = f"✅ **Product Processed Successfully!**\n\n{ai_resp}"
                    st.markdown(reply_text)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": reply_text,
                        "images": data.get("images", [])
                    })

        # 3. Conversational Chat
        else:
            if not gemini_key:
                st.warning("⚠️ Please paste your Gemini Key in the top box first!")
            else:
                system_prompt = f"You are an expert autonomous Dropshipping Assistant for {target_platform} ({target_country}). Help the user strategically in friendly English or Roman Urdu.\n\nUser: {user_input}"
                ai_reply = call_gemini(system_prompt, gemini_key)
                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
